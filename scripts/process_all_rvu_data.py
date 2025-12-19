#!/usr/bin/env python3
"""
Process all 7 years of RVU data from CMS CSV files to JSON
"""

import csv
import json
import os
from pathlib import Path

# Source and output directories
SOURCE_DIR = "/Users/philipsun/Downloads/Validation/Granger work Folder/RVU Look up/RVU DATA/RVUs by year"
OUTPUT_DIR = "app/data/processed"

# File mappings
FILES = {
    2019: "PPRRVU19_OCT.csv",
    2020: "PPRRVU20_OCT.csv",
    2021: "PPRRVU21_OCT.csv",
    2022: "PPRRVU22_OCT.csv",
    2023: "PPRRVU23_OCT.csv",
    2024: "PPRRVU24_OCT.csv",
    2025: "PPRRVU2025_Oct.csv"
}

def process_year(year, filename):
    """Process a single year of RVU data"""
    input_path = os.path.join(SOURCE_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, f"rvu_data_{year}.json")

    print(f"\n{'='*60}")
    print(f"Processing {year}: {filename}")
    print(f"{'='*60}")

    # Check if source file exists
    if not os.path.exists(input_path):
        print(f"❌ ERROR: File not found: {input_path}")
        return False

    rvu_data = {}

    # Try multiple encodings
    encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    f = None
    for encoding in encodings_to_try:
        try:
            f = open(input_path, 'r', encoding=encoding, errors='replace')
            # Try reading to verify encoding works
            _ = f.read(1000)
            f.close()
            # Reopen for actual processing
            f = open(input_path, 'r', encoding=encoding, errors='replace')
            print(f"  Using encoding: {encoding}")
            break
        except Exception as e:
            if f:
                f.close()
            f = None
            continue

    if f is None:
        print(f"❌ ERROR: Could not open file with any encoding")
        return False

    with f:
        reader = csv.reader(f)

        # Skip first 10 header rows
        for _ in range(10):
            next(reader)

        count = 0
        for row in reader:
            try:
                if len(row) < 11:
                    continue

                cpt_code = row[0].strip()
                if not cpt_code:
                    continue

                # Extract RVU values
                work_rvu = float(row[5].strip() or 0)
                pe_nonfac = float(row[6].strip() or 0)
                pe_fac = float(row[8].strip() or 0)
                mp_rvu = float(row[10].strip() or 0)

                # Get description
                description = row[2].strip()

                rvu_data[cpt_code] = {
                    "desc": description,
                    "work_rvu": work_rvu,
                    "pe_rvu_fac": pe_fac,
                    "pe_rvu_nonfac": pe_nonfac,
                    "mp_rvu": mp_rvu
                }

                count += 1
                if count % 2000 == 0:
                    print(f"  Processed {count} codes...")

            except (ValueError, IndexError) as e:
                continue

    # Write JSON output
    with open(output_path, 'w') as f:
        json.dump(rvu_data, f, indent=2)

    print(f"✓ Completed: {count} codes written to {output_path}")

    # Show sample verification data
    sample_codes = ['99213', '99214', '99215']
    print(f"\nSample data for {year}:")
    for code in sample_codes:
        if code in rvu_data:
            data = rvu_data[code]
            print(f"  {code}: Work={data['work_rvu']:.2f}, PE(Fac)={data['pe_rvu_fac']:.2f}, PE(NonFac)={data['pe_rvu_nonfac']:.2f}, MP={data['mp_rvu']:.2f}")

    return True

def main():
    print("="*60)
    print("RVU DATA PROCESSOR - ALL YEARS (2019-2025)")
    print("="*60)

    # Create output directory if needed
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Process each year
    success_count = 0
    for year in sorted(FILES.keys()):
        if process_year(year, FILES[year]):
            success_count += 1

    # Final summary
    print("\n" + "="*60)
    print(f"PROCESSING COMPLETE: {success_count}/{len(FILES)} years successful")
    print("="*60)

    if success_count == len(FILES):
        print("\n✓ All RVU data files processed successfully!")
        print(f"\nGenerated files in {OUTPUT_DIR}/:")
        for year in sorted(FILES.keys()):
            print(f"  - rvu_data_{year}.json")
        print("\nNext steps:")
        print("  1. Restart the RVU Calculator server")
        print("  2. Refresh browser (Cmd+Shift+R)")
        print("  3. Test with CPT codes: 99213, 99214, 99215")
    else:
        print(f"\n⚠️  Some files failed to process")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
