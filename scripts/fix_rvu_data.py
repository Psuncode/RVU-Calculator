#!/usr/bin/env python3
"""
Quick script to fix RVU data from the 2022 CSV file
"""

import csv
import json

# File paths
input_csv = "app/data/raw/PPRRVU22_JAN.csv"
output_json = "app/data/processed/rvu_data_2022.json"

print(f"Processing {input_csv}...")

rvu_data = {}

with open(input_csv, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)

    # Skip the first 10 header rows
    for _ in range(10):
        next(reader)

    # Column indices based on the CSV structure
    # Col 0: HCPCS
    # Col 2: DESCRIPTION
    # Col 5: WORK RVU
    # Col 6: PE RVU NON-FAC
    # Col 8: PE RVU FACILITY
    # Col 10: MP RVU

    count = 0
    for row in reader:
        try:
            if len(row) < 11:
                continue

            cpt_code = row[0].strip()
            if not cpt_code:
                continue

            # Extract RVU values - convert to float, handle empty/invalid values
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
            if count % 1000 == 0:
                print(f"  Processed {count} codes...")

        except (ValueError, IndexError) as e:
            # Skip rows with invalid data
            continue

print(f"Processed {count} total CPT/HCPCS codes")

# Write JSON output
print(f"Writing to {output_json}...")
with open(output_json, 'w') as f:
    json.dump(rvu_data, f, indent=2)

print("✓ Done!")

# Show sample data for verification
print("\nSample entries:")
sample_codes = ['99213', '99214', '99215']
for code in sample_codes:
    if code in rvu_data:
        print(f"  {code}: {rvu_data[code]}")
