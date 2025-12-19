#!/usr/bin/env python3
"""
Build All RVU and GPCI Data Files
==================================
Automates parsing of all 7 years (2019-2025) of RVU and GPCI data from source CSVs,
then builds the consolidated RVU timeline.

This script:
1. Parses all 7 years of RVU CSVs into per-year JSON files
2. Parses all 7 years of GPCI CSVs into per-year JSON files
3. Builds the consolidated rvu_timeline_2019_2025.json
4. Updates metadata.json

Usage:
    python3 scripts/build_all_data.py
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Source data directories
SOURCE_RVU_DIR = "/Users/philipsun/Downloads/RVU DATA/RVUs by year"
SOURCE_GPCI_DIR = "/Users/philipsun/Downloads/RVU DATA/GPCIs"
OUTPUT_DIR = "app/data/processed"

# File mappings
RVU_FILES = {
    2019: "PPRRVU19_OCT.csv",
    2020: "PPRRVU20_OCT.csv",
    2021: "PPRRVU21_OCT.csv",
    2022: "PPRRVU22_OCT.csv",
    2023: "PPRRVU23_OCT.csv",
    2024: "PPRRVU24_OCT.csv",
    2025: "PPRRVU2025_Oct.csv"
}

GPCI_FILES = {
    2019: "GPCI2019.csv",
    2020: "GPCI2020.csv",
    2021: "GPCI2021.csv",
    2022: "GPCI2022.csv",
    2023: "GPCI2023.csv",
    2024: "GPCI2024.csv",
    2025: "GPCI2025.csv"
}


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        print(f"STDERR: {result.stderr}")
        return False

    print(result.stdout)
    if result.stderr:
        print(f"Warnings: {result.stderr}")

    return True


def parse_rvu_files():
    """Parse all RVU CSV files into JSON"""
    print("\n" + "="*60)
    print("PHASE 1: PARSING RVU DATA FILES")
    print("="*60)

    for year, filename in sorted(RVU_FILES.items()):
        input_path = f"{SOURCE_RVU_DIR}/{filename}"
        output_path = f"{OUTPUT_DIR}/rvu_data_{year}.json"

        # Check if source file exists
        if not Path(input_path).exists():
            print(f"WARNING: Source file not found: {input_path}")
            continue

        # Skip if output already exists (optional - comment out to force regeneration)
        if Path(output_path).exists():
            print(f"✓ {year} RVU data already exists, skipping...")
            continue

        cmd = [
            "python3",
            "scripts/parse_cms_data.py",
            input_path,
            output_path
        ]

        if not run_command(cmd, f"Parsing RVU data for {year}"):
            print(f"Failed to parse RVU data for {year}")
            return False

    print("\n✓ All RVU files parsed successfully!")
    return True


def parse_gpci_files():
    """Parse all GPCI CSV files into JSON"""
    print("\n" + "="*60)
    print("PHASE 2: PARSING GPCI DATA FILES")
    print("="*60)

    for year, filename in sorted(GPCI_FILES.items()):
        input_path = f"{SOURCE_GPCI_DIR}/{filename}"
        output_path = f"{OUTPUT_DIR}/gpci_data_{year}.json"

        # Check if source file exists
        if not Path(input_path).exists():
            print(f"WARNING: Source file not found: {input_path}")
            continue

        # Skip if output already exists (optional - comment out to force regeneration)
        if Path(output_path).exists():
            print(f"✓ {year} GPCI data already exists, skipping...")
            continue

        cmd = [
            "python3",
            "scripts/parse_cms_data.py",
            input_path,
            output_path
        ]

        if not run_command(cmd, f"Parsing GPCI data for {year}"):
            print(f"Failed to parse GPCI data for {year}")
            return False

    print("\n✓ All GPCI files parsed successfully!")
    return True


def build_timeline():
    """Build consolidated RVU timeline from per-year JSON files"""
    print("\n" + "="*60)
    print("PHASE 3: BUILDING RVU TIMELINE")
    print("="*60)

    # Build command with all year inputs
    cmd = ["python3", "scripts/build_rvu_timeline.py"]

    for year in sorted(RVU_FILES.keys()):
        input_path = f"{OUTPUT_DIR}/rvu_data_{year}.json"
        if Path(input_path).exists():
            cmd.extend(["--year", str(year), input_path])
        else:
            print(f"WARNING: Missing RVU data for {year}, timeline will have gaps")

    output_path = f"{OUTPUT_DIR}/rvu_timeline_2019_2025.json"
    cmd.extend(["--out", output_path])

    if not run_command(cmd, "Building consolidated RVU timeline"):
        print("Failed to build timeline")
        return False

    print("\n✓ RVU timeline built successfully!")
    return True


def update_metadata():
    """Update metadata.json with new data structure"""
    print("\n" + "="*60)
    print("PHASE 4: UPDATING METADATA")
    print("="*60)

    metadata_path = Path(f"{OUTPUT_DIR}/metadata.json")

    # Load existing metadata or create new
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}

    # Update with new structure
    metadata.update({
        "rvu_timeline": {
            "years": list(range(2019, 2026)),
            "sources": {str(year): filename for year, filename in RVU_FILES.items()},
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "description": "Multi-year RVU audit timeline (2019-2025)"
        },
        "calculator": {
            "years_available": list(range(2019, 2026)),
            "default_year": 2022,
            "description": "Per-year RVU data for calculator view"
        },
        "gpci_data": {
            "years_available": list(range(2019, 2026)),
            "sources": {str(year): filename for year, filename in GPCI_FILES.items()},
            "description": "CMS Geographic Practice Cost Indices by State and Medicare Locality"
        },
        "last_updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    })

    # Write updated metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, sort_keys=False)
        f.write('\n')

    print(f"✓ Updated metadata at {metadata_path}")
    return True


def main():
    print("\n" + "="*60)
    print("RVU DATA BUILD AUTOMATION")
    print("Building all RVU and GPCI data files (2019-2025)")
    print("="*60)

    # Verify source directories exist
    if not Path(SOURCE_RVU_DIR).exists():
        print(f"ERROR: RVU source directory not found: {SOURCE_RVU_DIR}")
        return 1

    if not Path(SOURCE_GPCI_DIR).exists():
        print(f"ERROR: GPCI source directory not found: {SOURCE_GPCI_DIR}")
        return 1

    # Create output directory if needed
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Run all phases
    if not parse_rvu_files():
        print("\n❌ FAILED: RVU parsing incomplete")
        return 1

    if not parse_gpci_files():
        print("\n❌ FAILED: GPCI parsing incomplete")
        return 1

    if not build_timeline():
        print("\n❌ FAILED: Timeline build incomplete")
        return 1

    if not update_metadata():
        print("\n❌ FAILED: Metadata update incomplete")
        return 1

    # Final summary
    print("\n" + "="*60)
    print("BUILD COMPLETE!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - 7 RVU data files: rvu_data_2019.json through rvu_data_2025.json")
    print(f"  - 7 GPCI data files: gpci_data_2019.json through gpci_data_2025.json")
    print(f"  - 1 Timeline file: rvu_timeline_2019_2025.json")
    print(f"  - Updated metadata.json")
    print(f"\nAll files are in: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Verify data integrity (check file sizes, spot-check CPT codes)")
    print("  2. Proceed to Phase 2: Remove Regence code")
    print("  3. Proceed to Phase 3: Add multi-year Calculator support")

    return 0


if __name__ == "__main__":
    sys.exit(main())
