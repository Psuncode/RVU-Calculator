#!/usr/bin/env python3
"""
CSV to JSON Parser for CMS RVU Data
====================================
This script converts CMS RVU CSV files into the JSON format needed by the RVU Calculator app.

Usage:
    python parse_cms_data.py <input_csv> <output_json>

Expected CSV columns for RVU data:
    - CPT/HCPCS (code)
    - Description
    - Work RVU
    - PE RVU Facility (or similar)
    - PE RVU Non-Facility (or similar)
    - MP RVU (or Malpractice RVU)

The script will attempt to auto-detect column names with flexible matching.
"""

import csv
import json
import sys
import re
from pathlib import Path


def normalize_header(header):
    """Normalize column header for flexible matching"""
    return re.sub(r'[^a-z0-9]', '', header.lower())


def find_column(headers, *patterns):
    """Find column index by matching against multiple patterns"""
    normalized = [normalize_header(h) for h in headers]

    for pattern in patterns:
        pattern_norm = normalize_header(pattern)
        for idx, header in enumerate(normalized):
            if not header:
                continue
            if pattern_norm in header or header in pattern_norm:
                return idx
    return None


def parse_rvu_csv(csv_path, output_path):
    """Parse RVU CSV file into JSON format"""

    print(f"Reading CSV file: {csv_path}")

    # Try multiple encodings to handle different file formats
    # Use latin-1 which can handle all byte values, or utf-8 with error replacement
    encodings_to_try = [
        ('utf-8-sig', 'strict'),
        ('utf-8', 'strict'),
        ('latin-1', 'strict'),
        ('cp1252', 'strict'),
        ('utf-8', 'replace'),  # Fallback: replace bad characters
    ]

    f = None
    for encoding, errors in encodings_to_try:
        try:
            f = open(csv_path, 'r', encoding=encoding, errors=errors)
            # Try to read entire file to verify encoding works
            content = f.read()
            f.close()
            # Reopen for actual processing
            f = open(csv_path, 'r', encoding=encoding, errors=errors)
            print(f"Successfully opened file with encoding={encoding}, errors={errors}")
            break
        except (UnicodeDecodeError, Exception) as e:
            if f:
                f.close()
            f = None
            continue

    if f is None:
        print(f"ERROR: Could not open file with any supported encoding")
        sys.exit(1)

    with f:
        # Read CSV
        reader = csv.reader(f)
        headers = next(reader)

        print(f"Found {len(headers)} columns")
        print(f"Headers: {headers[:5]}...")  # Show first 5

        # Auto-detect column indices
        cpt_idx = find_column(headers, 'cpt', 'hcpcs', 'code', 'cpt/hcpcs', 'cpthcpcs')
        desc_idx = find_column(headers, 'description', 'desc', 'descriptor')
        work_idx = find_column(headers, 'work rvu', 'workrvu', 'work')
        pe_fac_idx = find_column(headers, 'pe rvu facility', 'perfacility', 'pe fac', 'facility pe')
        pe_nonfac_idx = find_column(headers, 'pe rvu non-facility', 'pe rvu nonfacility', 'penonfacility', 'non-facility pe', 'nonfacility pe')
        mp_idx = find_column(headers, 'mp rvu', 'mprvu', 'malpractice rvu', 'malpractice', 'mp')

        # Validate required columns found
        if cpt_idx is None:
            print("ERROR: Could not find CPT/HCPCS column")
            print("Available headers:", headers)
            sys.exit(1)

        print(f"\nColumn mapping:")
        print(f"  CPT/HCPCS: Column {cpt_idx} ({headers[cpt_idx]})")
        if desc_idx is not None:
            print(f"  Description: Column {desc_idx} ({headers[desc_idx]})")
        if work_idx is not None:
            print(f"  Work RVU: Column {work_idx} ({headers[work_idx]})")
        if pe_fac_idx is not None:
            print(f"  PE Facility: Column {pe_fac_idx} ({headers[pe_fac_idx]})")
        if pe_nonfac_idx is not None:
            print(f"  PE Non-Facility: Column {pe_nonfac_idx} ({headers[pe_nonfac_idx]})")
        if mp_idx is not None:
            print(f"  MP RVU: Column {mp_idx} ({headers[mp_idx]})")

        # Parse data
        rvu_data = {}
        skipped = 0

        for row_num, row in enumerate(reader, start=2):
            try:
                if len(row) <= cpt_idx:
                    continue

                cpt_code = row[cpt_idx].strip()

                # Skip empty codes or header-like rows
                if not cpt_code or cpt_code.lower() in ['cpt', 'code', 'hcpcs']:
                    continue

                # Get values with safe defaults
                def safe_float(idx):
                    if idx is None or idx >= len(row):
                        return 0.0
                    try:
                        val = row[idx].strip()
                        # Remove any non-numeric characters except . and -
                        val = re.sub(r'[^\d.\-]', '', val)
                        return float(val) if val else 0.0
                    except (ValueError, AttributeError):
                        return 0.0

                def safe_str(idx):
                    if idx is None or idx >= len(row):
                        return ""
                    return row[idx].strip()

                rvu_data[cpt_code] = {
                    "desc": safe_str(desc_idx),
                    "work_rvu": safe_float(work_idx),
                    "pe_rvu_fac": safe_float(pe_fac_idx),
                    "pe_rvu_nonfac": safe_float(pe_nonfac_idx),
                    "mp_rvu": safe_float(mp_idx)
                }

            except Exception as e:
                skipped += 1
                if skipped <= 5:  # Show first 5 errors
                    print(f"Warning: Skipped row {row_num}: {e}")

        print(f"\nParsed {len(rvu_data)} CPT codes")
        if skipped > 0:
            print(f"Skipped {skipped} rows due to errors")

        # Write JSON
        print(f"\nWriting JSON to: {output_path}")
        with open(output_path, 'w') as out:
            json.dump(rvu_data, out, indent=2)

        print(f"✓ Success! Created {output_path}")
        print(f"\nSample codes included:")
        for code in list(rvu_data.keys())[:5]:
            print(f"  - {code}: {rvu_data[code]['desc'][:50]}...")


def parse_gpci_csv(csv_path, output_path):
    """Parse GPCI CSV file into JSON format"""

    print(f"Reading GPCI CSV file: {csv_path}")

    # Try multiple encodings to handle different file formats
    # Use latin-1 which can handle all byte values, or utf-8 with error replacement
    encodings_to_try = [
        ('utf-8-sig', 'strict'),
        ('utf-8', 'strict'),
        ('latin-1', 'strict'),
        ('cp1252', 'strict'),
        ('utf-8', 'replace'),  # Fallback: replace bad characters
    ]

    f = None
    for encoding, errors in encodings_to_try:
        try:
            f = open(csv_path, 'r', encoding=encoding, errors=errors)
            # Try to read entire file to verify encoding works
            content = f.read()
            f.close()
            # Reopen for actual processing
            f = open(csv_path, 'r', encoding=encoding, errors=errors)
            print(f"Successfully opened file with encoding={encoding}, errors={errors}")
            break
        except (UnicodeDecodeError, Exception) as e:
            if f:
                f.close()
            f = None
            continue

    if f is None:
        print(f"ERROR: Could not open file with any supported encoding")
        sys.exit(1)

    def extract_gpci_headers(rows, max_scan=80):
        """Extract the effective header row from a CMS GPCI CSV.

        Some CMS exports include preamble/title lines and, in older years, split the header across 2 lines.
        Returns: (header_start_index, header_line_count, headers, data_start_index)
        """
        scan_limit = min(max_scan, len(rows))

        def has_gpci_cols(norm_cells):
            has_pw = any(('pw' in c or 'work' in c) and 'gpci' in c for c in norm_cells)
            has_pe = any(('pe' in c) and 'gpci' in c for c in norm_cells)
            has_mp = any(('mp' in c or 'pl' in c or 'malpractice' in c) and 'gpci' in c for c in norm_cells)
            return has_pw and has_pe and has_mp

        for i in range(scan_limit):
            row = rows[i]
            if not row or len(row) < 3:
                continue

            cells = [normalize_header(c or '') for c in row]
            has_locality_number = any(c.startswith('localitynumber') or c in ('localityno',) for c in cells)
            has_locality_name = any(c.startswith('localityname') for c in cells)
            if not (has_locality_number and has_locality_name):
                continue

            if has_gpci_cols(cells):
                return i, 1, row, i + 1

            # Older exports may have GPCI columns on the next row.
            if i + 1 < scan_limit:
                row2 = rows[i + 1]
                if row2 and len(row2) >= 3:
                    cells2 = [normalize_header(c or '') for c in row2]
                    if has_gpci_cols(cells2):
                        width = max(len(row), len(row2))
                        merged = []
                        for j in range(width):
                            a = (row[j] if j < len(row) else '')
                            b = (row2[j] if j < len(row2) else '')
                            a_clean = (a or '').strip()
                            b_clean = (b or '').strip()
                            if (not a_clean) or a_clean.isdigit():
                                merged.append(b_clean or a_clean)
                            else:
                                merged.append(a_clean)
                        return i, 2, merged, i + 2

        return None

    def derive_state_from_name(locality_name):
        """Infer 2-letter state code from the Locality Name field (older GPCI exports)."""
        if not locality_name:
            return ''

        cleaned = locality_name.strip()
        cleaned = re.sub(r'\*+$', '', cleaned).strip()

        if ',' in cleaned:
            tail = cleaned.rsplit(',', 1)[-1].strip().upper()
            if len(tail) == 2 and tail.isalpha():
                return tail

        name_upper = re.sub(r'[^A-Z ]', '', cleaned.upper()).strip()
        state_by_name = {
            'ALABAMA': 'AL',
            'ALASKA': 'AK',
            'ARIZONA': 'AZ',
            'ARKANSAS': 'AR',
            'CALIFORNIA': 'CA',
            'COLORADO': 'CO',
            'CONNECTICUT': 'CT',
            'DELAWARE': 'DE',
            'DISTRICT OF COLUMBIA': 'DC',
            'FLORIDA': 'FL',
            'GEORGIA': 'GA',
            'HAWAII': 'HI',
            'IDAHO': 'ID',
            'ILLINOIS': 'IL',
            'INDIANA': 'IN',
            'IOWA': 'IA',
            'KANSAS': 'KS',
            'KENTUCKY': 'KY',
            'LOUISIANA': 'LA',
            'MAINE': 'ME',
            'MARYLAND': 'MD',
            'MASSACHUSETTS': 'MA',
            'MICHIGAN': 'MI',
            'MINNESOTA': 'MN',
            'MISSISSIPPI': 'MS',
            'MISSOURI': 'MO',
            'MONTANA': 'MT',
            'NEBRASKA': 'NE',
            'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH',
            'NEW JERSEY': 'NJ',
            'NEW MEXICO': 'NM',
            'NEW YORK': 'NY',
            'NORTH CAROLINA': 'NC',
            'NORTH DAKOTA': 'ND',
            'OHIO': 'OH',
            'OKLAHOMA': 'OK',
            'OREGON': 'OR',
            'PENNSYLVANIA': 'PA',
            'RHODE ISLAND': 'RI',
            'SOUTH CAROLINA': 'SC',
            'SOUTH DAKOTA': 'SD',
            'TENNESSEE': 'TN',
            'TEXAS': 'TX',
            'UTAH': 'UT',
            'VERMONT': 'VT',
            'VIRGINIA': 'VA',
            'WASHINGTON': 'WA',
            'WEST VIRGINIA': 'WV',
            'WISCONSIN': 'WI',
            'WYOMING': 'WY',
        }
        return state_by_name.get(name_upper, '')

    with f:
        reader = csv.reader(f)
        rows = list(reader)

        header_info = extract_gpci_headers(rows)
        if header_info is None:
            print("ERROR: Could not detect GPCI header row (file may not be a CMS GPCI export)")
            sys.exit(1)

        header_idx, header_line_count, headers, data_start = header_info
        data_rows = rows[data_start:]

        print(f"Detected header starting at line {header_idx + 1} ({header_line_count} line(s))")
        print(f"Found {len(headers)} columns")

        # Auto-detect column indices
        mac_idx = find_column(headers, 'medicare administrative contractor', 'mac')
        state_idx = find_column(headers, 'state')
        locality_num_idx = find_column(headers, 'locality number', 'locality no', 'locality')
        locality_name_idx = find_column(headers, 'locality name', 'name')

        work_gpci_idx = find_column(headers, 'pw gpci', 'work gpci', 'pwgpci', 'workgpci')
        pe_gpci_idx = find_column(headers, 'pe gpci', 'pegpci', 'practice expense gpci', 'practiceexpensegpci')
        mp_gpci_idx = find_column(headers, 'mp gpci', 'mpgpci', 'pl gpci', 'plmgpci', 'malpractice gpci', 'malpracticegpci')

        required = {
            'locality_number': locality_num_idx,
            'locality_name': locality_name_idx,
            'pw/work gpci': work_gpci_idx,
            'pe gpci': pe_gpci_idx,
            'mp gpci': mp_gpci_idx,
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            print("ERROR: Missing required GPCI columns:")
            for k in missing:
                print(f"  - {k}")
            print("Available headers:", headers)
            sys.exit(1)

        print(f"\nColumn mapping:")
        if mac_idx is not None:
            print(f"  MAC: Column {mac_idx} ({headers[mac_idx]})")
        if state_idx is not None:
            print(f"  State: Column {state_idx} ({headers[state_idx]})")
        else:
            print("  State: (not present) — deriving from Locality Name")
        print(f"  Locality Number: Column {locality_num_idx} ({headers[locality_num_idx]})")
        print(f"  Locality Name: Column {locality_name_idx} ({headers[locality_name_idx]})")
        print(f"  PW/Work GPCI: Column {work_gpci_idx} ({headers[work_gpci_idx]})")
        print(f"  PE GPCI: Column {pe_gpci_idx} ({headers[pe_gpci_idx]})")
        print(f"  MP GPCI: Column {mp_gpci_idx} ({headers[mp_gpci_idx]})")

        # Parse data
        gpci_data = {}

        def safe_float(row, idx):
            if idx is None or idx >= len(row):
                return None
            try:
                val = (row[idx] or '').strip()
                val = re.sub(r'[^\d.\-]', '', val)
                return float(val) if val else None
            except (ValueError, AttributeError):
                return None

        def safe_str(row, idx):
            if idx is None or idx >= len(row):
                return ""
            return (row[idx] or '').strip()

        skipped = 0
        for row in data_rows:
            if not row:
                continue

            state = safe_str(row, state_idx) if state_idx is not None else ''
            locality_num = safe_str(row, locality_num_idx)
            locality_name = safe_str(row, locality_name_idx)

            # Skip non-data lines / notes
            if not locality_num or not locality_name:
                continue
            if state_idx is not None and not state:
                continue
            if state_idx is not None and normalize_header(state) == 'state':
                continue

            if not state:
                state = derive_state_from_name(locality_name)

            work_gpci = safe_float(row, work_gpci_idx)
            pe_gpci = safe_float(row, pe_gpci_idx)
            mp_gpci = safe_float(row, mp_gpci_idx)
            if work_gpci is None or pe_gpci is None or mp_gpci is None:
                skipped += 1
                continue

            # Stable unique key across years.
            locality_key = str(int(float(locality_num))) if locality_num.replace('.', '', 1).isdigit() else locality_num
            key = f"{state}-{locality_key}" if state else f"{locality_name}-{locality_key}"

            gpci_data[key] = {
                "name": locality_name,
                "state": state,
                "locality": locality_num,
                "work_gpci": work_gpci,
                "pe_gpci": pe_gpci,
                "mp_gpci": mp_gpci,
            }
            if mac_idx is not None:
                mac = safe_str(row, mac_idx)
                if mac:
                    gpci_data[key]["mac"] = mac

        print(f"\nParsed {len(gpci_data)} localities")
        if skipped:
            print(f"Skipped {skipped} rows due to missing/invalid values")

        # Write JSON
        print(f"\nWriting JSON to: {output_path}")
        with open(output_path, 'w') as out:
            json.dump(gpci_data, out, indent=2)

        print(f"✓ Success! Created {output_path}")

        # Show Utah if present
        utah_key = None
        for k, v in gpci_data.items():
            if (v.get('state') or '').upper() == 'UT' or 'utah' in (v.get('name') or '').lower():
                utah_key = k
                break
        if utah_key:
            print(f"\nUtah GPCI values ({utah_key}):")
            print(f"  Work: {gpci_data[utah_key]['work_gpci']}")
            print(f"  PE: {gpci_data[utah_key]['pe_gpci']}")
            print(f"  MP: {gpci_data[utah_key]['mp_gpci']}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nQuick start:")
        print("  For RVU data:")
        print("    python parse_cms_data.py cms_rvu_file.csv data/rvu_data.json")
        print("\n  For GPCI data:")
        print("    python parse_cms_data.py gpci_file.csv data/gpci_data.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Detect file type based on output name or user choice
    if 'gpci' in output_file.lower():
        parse_gpci_csv(input_file, output_file)
    else:
        parse_rvu_csv(input_file, output_file)


if __name__ == '__main__':
    main()
