# Data Schema Documentation

This document describes the data structure for the RVU Calculator application, based on CMS 2022 data.

## Overview

The application uses two JSON data files:
- `data/rvu_data.json` - CPT/HCPCS codes with RVU values (17,601 codes from CMS)
- `data/gpci_data.json` - Geographic Practice Cost Indices by state (53 localities)

---

## RVU Data Schema

**File:** `data/rvu_data.json`

### Structure

```json
{
  "CPT_CODE": {
    "desc": "string",
    "work_rvu": number,
    "pe_rvu_fac": number,
    "pe_rvu_nonfac": number,
    "mp_rvu": number
  }
}
```

### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `CPT_CODE` | string (key) | CPT or HCPCS code | `"99213"` |
| `desc` | string | Short description of the procedure | `"Office o/p est low 20-29 min"` |
| `work_rvu` | number | Work Relative Value Unit | `1.30` |
| `pe_rvu_fac` | number | Practice Expense RVU (Facility setting) | `0.55` |
| `pe_rvu_nonfac` | number | Practice Expense RVU (Non-Facility setting) | `1.26` |
| `mp_rvu` | number | Malpractice RVU | `0.10` |

### Example Entry

```json
{
  "99213": {
    "desc": "Office o/p est low 20-29 min",
    "work_rvu": 1.3,
    "pe_rvu_fac": 0.55,
    "pe_rvu_nonfac": 1.26,
    "mp_rvu": 0.1
  }
}
```

### Data Source

- **Source:** CMS Physician Fee Schedule Relative Value File
- **File:** `PPRRVU22_JAN.xlsx`
- **Year:** 2022
- **Release:** January 2022 (Released 12/15/2021)
- **Sheet:** PPRRVU22_V1215
- **Total Codes:** 17,601

### Column Mapping (Excel to JSON)

| Excel Column | Header | JSON Field | Notes |
|--------------|--------|------------|-------|
| A | HCPCS | CPT_CODE (key) | 5-10 character alphanumeric |
| C | DESCRIPTION | desc | Truncated for brevity |
| F | WORK RVU | work_rvu | Float value |
| G | NON-FAC PE RVU | pe_rvu_nonfac | Float value |
| I | FACILITY PE RVU | pe_rvu_fac | Float value |
| K | MP RVU | mp_rvu | Float value |

### Parsing Notes

- Header row is at line 10 in the Excel file
- Data starts at row 11
- Codes with 0.0 values for all RVUs are included (e.g., ambulance codes)
- Some descriptions are abbreviated due to Excel cell limits

### Value Ranges

| Field | Typical Range | Notes |
|-------|---------------|-------|
| work_rvu | 0.0 - 50.0+ | Most E/M codes: 0.5 - 5.0 |
| pe_rvu_fac | 0.0 - 100.0+ | Facility setting (lower) |
| pe_rvu_nonfac | 0.0 - 200.0+ | Office setting (higher) |
| mp_rvu | 0.0 - 20.0+ | Varies by specialty risk |

---

## RVU Timeline Data Schema (2019–2025)

This feature powers the **Audit Timeline** view (CMS base RVUs only; no GPCI; no reimbursement dollars).

**File:** `app/data/processed/rvu_timeline_2019_2025.json`

### Structure

```json
{
  "meta": {
    "years": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "generated_at": "2025-12-17T00:00:00+00:00",
    "sources": {"2022": "rvu_data_2022.json"},
    "total_codes": 0,
    "missing_years": [2019, 2020]
  },
  "codes": {
    "99213": {
      "desc": "Office o/p est low 20-29 min",
      "desc_overrides": {"2021": "Office visit established"},
      "work_rvu": [null, null, 1.2, 1.3, 1.3, null, null],
      "pe_rvu_fac": [null, null, 0.5, 0.55, 0.55, null, null],
      "pe_rvu_nonfac": [null, null, 1.1, 1.26, 1.26, null, null],
      "mp_rvu": [null, null, 0.09, 0.1, 0.1, null, null],
      "status": [null, null, "new", "modified", "existing", null, null]
    }
  }
}
```

### Field Definitions

| Field | Type | Description |
|------|------|-------------|
| `meta.years` | number[] | Column years emitted by the build script |
| `meta.generated_at` | string | ISO timestamp for reproducibility |
| `meta.sources` | object | Source filename per year input |
| `meta.total_codes` | number | Count of CPT/HCPCS codes in `codes` |
| `meta.missing_years` | number[] | Years requested but not provided as inputs |
| `codes[CODE].desc` | string | Canonical description (taken from latest year present) |
| `codes[CODE].desc_overrides` | object | Year→description overrides when a year’s desc differs from canonical |
| `codes[CODE].*_rvu` | (number\|null)[] | Arrays aligned to `meta.years`; `null` means code did not exist that year |
| `codes[CODE].status` | (string\|null)[] | Arrays aligned to `meta.years`; `new`/`existing`/`modified` when present |

### Status Semantics

- `new`: first year the code appears in the timeline
- `modified`: any RVU component changed vs prior present year, or description changed
- `existing`: present and unchanged vs prior present year
- Years before introduction are `null` (blank in UI; never backfilled)

### Build Command

The timeline is built from per-year RVU JSON snapshots (same schema as `rvu_data.json`):

```bash
python3 scripts/build_rvu_timeline.py \
  --year 2019 app/data/processed/rvu_data_2019.json \
  --year 2020 app/data/processed/rvu_data_2020.json \
  --year 2021 app/data/processed/rvu_data_2021.json \
  --year 2022 app/data/processed/rvu_data_2022.json \
  --year 2023 app/data/processed/rvu_data_2023.json \
  --year 2024 app/data/processed/rvu_data_2024.json \
  --year 2025 app/data/processed/rvu_data_2025.json \
  --out app/data/processed/rvu_timeline_2019_2025.json
```

---

## GPCI Data Schema

**File:** `data/gpci_data.json`

### Structure

```json
{
  "STATE_CODE": {
    "name": "string",
    "state": "string",
    "locality": "string",
    "work_gpci": number,
    "pe_gpci": number,
    "mp_gpci": number
  }
}
```

### Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `STATE_CODE` | string (key) | 2-letter state abbreviation | `"UT"` |
| `name` | string | Locality name | `"UTAH"` |
| `state` | string | State abbreviation (same as key) | `"UT"` |
| `locality` | string | CMS locality number | `"09"` |
| `work_gpci` | number | Work GPCI adjustment factor | `1.000` |
| `pe_gpci` | number | Practice Expense GPCI adjustment factor | `0.919` |
| `mp_gpci` | number | Malpractice GPCI adjustment factor | `0.799` |

### Example Entry

```json
{
  "UT": {
    "name": "UTAH",
    "state": "UT",
    "locality": "09",
    "work_gpci": 1.0,
    "pe_gpci": 0.919,
    "mp_gpci": 0.799
  }
}
```

### Data Source

- **Source:** CMS Geographic Practice Cost Indices
- **File:** `GPCI2022.xlsx`
- **Year:** 2022
- **Sheet:** Addendum E. GPCIs
- **Total Localities:** 53

### Column Mapping (Excel to JSON)

| Excel Column | Header | JSON Field | Notes |
|--------------|--------|------------|-------|
| B | State | state | 2-letter code |
| C | Locality Number | locality | 2-digit code |
| D | Locality Name | name | Full locality name |
| E | 2022 PW GPCI (with 1.0 Floor) | work_gpci | Work adjustment |
| F | 2022 PE GPCI | pe_gpci | PE adjustment |
| G | 2022 MP GPCI | mp_gpci | MP adjustment |

### Parsing Notes

- Header row is at line 3 in the Excel file
- Data starts at row 4
- Work GPCI has a 1.0 floor applied by CMS
- Some states have multiple localities (e.g., CA, FL, NY)
- **Parser uses first locality per state** for simplicity

### GPCI Value Ranges

| Component | Typical Range | Notes |
|-----------|---------------|-------|
| work_gpci | 1.0 - 1.5 | Floor of 1.0 applied |
| pe_gpci | 0.8 - 1.3 | Reflects cost of living |
| mp_gpci | 0.2 - 2.5 | Highly variable by state |

### Special Cases

- **Alaska (AK):** Highest work GPCI (1.5)
- **Montana, Nevada, North/South Dakota, Wyoming:** Floor states (marked with **)
- **New York (Manhattan):** Highest MP GPCI (2.031)
- **Minnesota:** Lowest MP GPCI (0.353)

---

## Utah-Specific Data (2022)

### Utah GPCI Values

```json
{
  "UT": {
    "name": "UTAH",
    "state": "UT",
    "locality": "09",
    "work_gpci": 1.000,
    "pe_gpci": 0.919,
    "mp_gpci": 0.799
  }
}
```

### Calculation Example: 99213 Non-Facility

**Base CMS RVUs:**
- Work: 1.30
- PE (Non-Facility): 1.26
- MP: 0.10

**Utah GPCI Adjustment:**
- Adjusted Work = 1.30 × 1.000 = **1.3000**
- Adjusted PE = 1.26 × 0.919 = **1.1579**
- Adjusted MP = 0.10 × 0.799 = **0.0799**

**Total Adjusted RVUs = 2.5378**

**With CF $39.69:**
- Estimated Payment = 2.5378 × $39.69 = **$100.73**

---

## Data Update Process

### Step 1: Download CMS Files

1. Visit: https://www.cms.gov/medicare/payment/fee-schedules/physician
2. Download latest RVU file (e.g., `PPRRVU23_JAN.xlsx`)
3. Download GPCI file (usually in same zip as RVU file)

### Step 2: Parse to JSON

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Parse RVU file
python parse_cms_excel.py PPRRVU23_JAN.xlsx data/rvu_data.json

# Parse GPCI file
python parse_cms_excel.py GPCI2023.xlsx data/gpci_data.json
```

### Step 3: Verify

```bash
# Run test suite
node test_calculations.js

# Check Utah GPCI values
grep -A 6 '"UT"' data/gpci_data.json

# Spot-check common codes
grep -A 6 '"99213"' data/rvu_data.json
grep -A 6 '"99214"' data/rvu_data.json
```

### Step 4: Update Application

1. Refresh `index.html` in browser
2. Test lookups for common codes
3. Verify POS toggle works
4. Check CF calculator
5. Test copy functionality

**No code changes required!**

---

## File Sizes

| File | Size | Records | Notes |
|------|------|---------|-------|
| `rvu_data.json` | ~1.5 MB | 17,601 | Minified: ~1.2 MB |
| `gpci_data.json` | ~4 KB | 53 | One entry per state |
| `PPRRVU22_JAN.xlsx` | ~1.2 MB | 17,611 rows | Source file |
| `GPCI2022.xlsx` | ~25 KB | 125 rows | Source file |

---

## Validation

### Required Checks

✓ **Schema Validation:**
- All CPT codes are alphanumeric strings
- All RVU values are numbers (float)
- No missing required fields
- JSON is valid and parseable

✓ **Data Validation:**
- RVU values are ≥ 0
- GPCI values are typically 0.2 - 2.5
- Utah entry exists in GPCI data
- Common E/M codes (99213-99215) exist in RVU data

✓ **Calculation Validation:**
- Test vectors pass
- 4-decimal precision maintained
- Payment calculations round to $0.01
- POS switching uses correct PE value

### Test Codes (2022 Data)

| Code | Description | Work | PE NF | PE F | MP |
|------|-------------|------|-------|------|-----|
| 99213 | Est low | 1.30 | 1.26 | 0.55 | 0.10 |
| 99214 | Est mod | 1.92 | 1.71 | 0.82 | 0.12 |
| 99215 | Est high | 2.80 | 2.28 | 1.24 | 0.21 |
| 99203 | New low | 1.60 | 1.52 | 0.67 | 0.17 |
| 99204 | New mod | 2.60 | 2.06 | 1.11 | 0.24 |
| 99205 | New high | 3.50 | 2.64 | 1.76 | 0.24 |

---

## Technical Notes

### JSON Precision

- All numeric values stored as JSON numbers (not strings)
- JavaScript handles up to 15-17 significant digits
- Display formatting uses `.toFixed(4)` for RVUs
- No precision loss in calculations for typical RVU ranges

### Performance

- **Load time:** < 500ms for 17K codes (client-side)
- **Search time:** O(1) for direct code lookup
- **Autocomplete:** O(n) linear scan, acceptable for < 20K codes
- **Memory usage:** ~5 MB for all data in memory

### Browser Compatibility

- JSON.parse() supported in all modern browsers
- Fetch API for loading data files
- No IE11 support required

---

## Troubleshooting

### Common Issues

**"Code not found"**
- Verify code exists in CMS data for that year
- Check for typos (codes are case-insensitive in app)
- Some codes may be deleted/added between years

**"Failed to load RVU data"**
- Check that `data/rvu_data.json` exists
- Verify JSON is valid (use JSON linter)
- Check browser console for specific error

**Wrong calculations**
- Verify Utah GPCI values match CMS source
- Check that correct PE value used (Facility vs Non-Facility)
- Ensure no rounding errors (should be 4 decimals)

### Parser Issues

**"Could not find header row"**
- CMS may change Excel format between years
- Manually inspect first 20 rows
- Update column detection logic in parser

**Missing values**
- CMS sometimes uses blank cells for 0.0
- Parser treats blank as 0.0 by default
- Verify this is correct for your use case

---

## Changelog

### 2022 CMS Data (January Release)

- **Date:** December 15, 2021
- **RVU Codes:** 17,601
- **GPCI Localities:** 53
- **Utah GPCI:** Work 1.000, PE 0.919, MP 0.799

### Parser Updates

- **v1.0:** Initial Excel parser with openpyxl
- Support for PPRRVU and GPCI formats
- Automatic column detection
- Progress reporting for large files

---

## References

- [CMS Physician Fee Schedule](https://www.cms.gov/medicare/payment/fee-schedules/physician)
- [RVU Overview](https://www.cms.gov/Medicare/Medicare-Fee-for-Service-Payment/PhysicianFeeSched/PFS-Relative-Value-Files)
- [GPCI Documentation](https://www.cms.gov/Medicare/Medicare-Fee-for-Service-Payment/PhysicianFeeSched/PFS-Federal-Regulation-Notices-Items/CMS-1751-FC)

---

**Last Updated:** 2025-11-12
**Data Year:** 2022
**Parser Version:** 1.0
