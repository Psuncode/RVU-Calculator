# RVU Calculator & Audit Timeline (2019-2025)

A powerful, single-page RVU calculator and audit timeline tool for payer negotiations. Calculate GPCI-adjusted RVUs for any CPT code across multiple years and localities, or track year-over-year RVU changes.

## Live Demo (GitHub Pages)

- Repository root (redirects to the app): `https://psuncode.github.io/RVU-Calculator/`
- App (recommended/share this): `https://psuncode.github.io/RVU-Calculator/app/`

Note: the trailing slash on `/app/` matters for some browsers/hosts. If you use `/app` (no slash), relative data loads can resolve to the wrong folder.

## Quick Start

**IMPORTANT:** Due to browser security (CORS), you need to run a local web server:

### Option 1: Use the Built-in Server (Recommended)

```bash
python scripts/serve.py
```

This will:
- Start a local server at http://localhost:8000
- Automatically open your browser
- Load all CPT codes from CMS data (2019-2025)

### Option 2: Use Python's Built-in Server

```bash
python3 -m http.server 8000
```

Then open: http://localhost:8000

Tip: if you want the same URL structure as GitHub Pages locally, open `http://localhost:8000/app/`.

## Features

### RVU Calculator
Calculate GPCI-adjusted RVUs for any CPT code with flexibility for payer negotiations.

- ✅ **Multi-year data** - Select from 2019-2025 CMS data
- ✅ **Multi-locality GPCI** - Choose from 50+ geographic localities
- ✅ **Instant lookups** - Client-side processing with 18,000+ CPT codes
- ✅ **Typeahead search** - Autocomplete with CPT code descriptions
- ✅ **Place of Service toggle** - Switch between Facility/Non-Facility PE values
- ✅ **Custom conversion factors** - Enter your own CF for negotiation scenarios
- ✅ **4-decimal precision** - Follows CMS rounding standards
- ✅ **Copy to clipboard** - One-click copy of Total Adjusted RVUs
- ✅ **Responsive design** - Works on desktop and mobile

### RVU Audit Timeline (2019-2025)
Track year-over-year RVU changes to support payer negotiations.

- ✅ **Year-over-year RVU visibility** - Work / PE / MP components by year
- ✅ **New / Modified flags** - Highlights CPT introductions and changes
- ✅ **No backfill** - Years before introduction show blank (not 0)
- ✅ **CMS base only** - No GPCI adjustments, pure RVU data
- ✅ **Column filtering** - Show/hide RVU components and deltas
- ✅ **Year range selection** - Focus on specific time periods
- ✅ **Explorer mode** - Find all new or modified codes in a year

## Using the Calculator

1. **Select Data Year**: Choose from 2019-2025
2. **Select GPCI Locality**: Choose your geographic locality (default: Utah)
3. **Enter a CPT code**: Type in a code (e.g., 99213) and select from autocomplete
4. **Choose Place of Service**: Toggle between Facility and Non-Facility
5. **Enter Conversion Factor** (optional): Input your negotiated or target CF
6. **View results**: See base RVUs, GPCI values, adjusted RVUs, and estimated payment

**Example:** Code `99213` (2022, Utah, Non-Facility, CF $39.69) → **$100.73**

## Using the Audit Timeline

1. Click **"Audit Timeline (2019-2025)"** tab
2. **Enter a CPT code** to see its RVU history
3. **Adjust filters**:
   - Year range (From/To)
   - Place of Service (Facility/Non-Facility)
   - Status filters (New/Existing/Modified)
   - Column visibility (Work/PE/MP/Total/Delta)
4. **Use Explorer** to find all new or modified codes in a specific year

### Timeline Status Indicators

- **New** (Green): CPT code introduced this year
- **Modified** (Amber): RVU value or description changed from previous year
- **Existing** (Gray): No changes from previous year

## Files

```
RVU Calculator/
├── app/
│   ├── index.html                          # Main app (single-page)
│   └── data/
│       └── processed/
│           ├── rvu_data_2019.json          # RVU data by year
│           ├── rvu_data_2020.json
│           ├── rvu_data_2021.json
│           ├── rvu_data_2022.json
│           ├── rvu_data_2023.json
│           ├── rvu_data_2024.json
│           ├── rvu_data_2025.json
│           ├── gpci_data_2019.json         # GPCI data by year
│           ├── gpci_data_2020.json
│           ├── gpci_data_2021.json
│           ├── gpci_data_2022.json
│           ├── gpci_data_2023.json
│           ├── gpci_data_2024.json
│           ├── gpci_data_2025.json
│           ├── rvu_timeline_2019_2025.json # Consolidated timeline
│           └── metadata.json               # Data metadata
├── scripts/
│   ├── serve.py                            # Development server
│   ├── parse_cms_data.py                   # CSV-to-JSON parser
│   ├── build_rvu_timeline.py               # Timeline builder
│   └── build_all_data.py                   # Batch processing
├── tests/
│   ├── test_calculations.js                # RVU calculation tests
│   └── test_rvu_timeline.js                # Timeline tests
└── README.md                               # This file
```

## Building the Data Files

All data files have been pre-generated from CMS sources (2019-2025). To rebuild or update:

### Option 1: Automated Build (Recommended)

```bash
python3 scripts/build_all_data.py
```

This will:
1. Parse all 7 years of RVU CSV files
2. Parse all 7 years of GPCI CSV files
3. Build the consolidated timeline JSON
4. Update metadata.json

### Option 2: Manual Build

Parse individual years:

```bash
# Parse RVU data
python3 scripts/parse_cms_data.py \
  "/path/to/PPRRVU22_OCT.csv" \
  "app/data/processed/rvu_data_2022.json"

# Parse GPCI data
python3 scripts/parse_cms_data.py \
  "/path/to/GPCI2022.csv" \
  "app/data/processed/gpci_data_2022.json"
```

Build timeline:

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

## How It Works

### Calculation Formula

For each CPT code, we:

1. Start with **CMS base RVUs** (selected year):
   - Work RVU
   - PE RVU (Facility or Non-Facility)
   - MP RVU

2. Apply **selected locality's GPCI** to each component:
   - Adjusted Work = Work RVU × Locality Work GPCI
   - Adjusted PE = PE RVU × Locality PE GPCI
   - Adjusted MP = MP RVU × Locality MP GPCI

3. Sum to get **Total Adjusted RVUs**:
   - Total = Adjusted Work + Adjusted PE + Adjusted MP

4. (Optional) Multiply by **Conversion Factor**:
   - Estimated Payment = Total Adjusted RVUs × CF

### Example Calculation

**Code:** 99213 (Non-Facility)
**Year:** 2022
**Locality:** Utah

```
Base RVUs:           Work: 1.30    PE: 1.26    MP: 0.10
Utah GPCI:           Work: 1.000   PE: 0.919   MP: 0.799

Adjusted RVUs:       Work: 1.3000  PE: 1.1579  MP: 0.0799
Total Adjusted RVUs: 2.5378

With CF $39.69:      Estimated Payment = $100.73
```

## Testing

Run the test suite to verify calculations:

```bash
node tests/test_calculations.js
```

Run timeline builder regression tests:

```bash
node tests/test_rvu_timeline.js
```

All tests should pass with the included data.

## Technical Details

- **Framework**: Vanilla JavaScript (no build step required)
- **Styling**: Tailwind CSS (via CDN)
- **Data**: Client-side JSON (no database needed)
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Customization

### Switching Data Years

The app automatically loads data for the selected year. Change years using the year selector dropdown, and the app will load the corresponding data files.

### Adding More Localities

All 50+ CMS localities are pre-loaded for each year. Use the locality selector dropdown to choose your geographic area.

### Updating Conversion Factor Default

Edit the HTML `cfInput` placeholder value to show your typical CF, or leave it blank for negotiation scenarios.

## Troubleshooting

### "Failed to load RVU data"

**Problem:** Browser blocking fetch() due to CORS policy.

**Solution:** Run a local web server (see Quick Start above):
```bash
python scripts/serve.py
```

### Audit Timeline not loading on GitHub Pages

Open DevTools → Network and confirm this request returns **200** (not 404) and is not HTML:

- `app/data/processed/rvu_timeline_2019_2025.json`

If you’re linking someone else, prefer sharing the URL with the trailing slash:

- `https://psuncode.github.io/RVU-Calculator/app/`

### Data Validation

To verify your data matches CMS source:

```bash
# Check 99213 values in CSV
grep "^99213," /path/to/PPRRVU22_OCT.csv

# Check parsed data
grep -A 6 '"99213"' app/data/processed/rvu_data_2022.json
```

### Code Not Found

- Verify code exists in CMS data for the selected year
- Check for typos (codes are case-insensitive)
- Some codes may be deleted/added between years
- Use autocomplete to see available codes

### Wrong Calculations

- Verify GPCI values match CMS source for selected locality
- Check correct PE value used (Facility vs Non-Facility)
- Run test suite: `node tests/test_calculations.js`

## Data Sources

- **CMS Physician Fee Schedule**: https://www.cms.gov/medicare/payment/fee-schedules/physician
- **GPCI Locality Files**: Available in CMS PFS zip files
- **Years Covered**: 2019-2025 (October releases)

## Version

**v2.0** - Multi-year RVU Calculator & Audit Timeline

### What's New in v2.0

- **Multi-year support** - Select from 2019-2025 data
- **Multi-locality GPCI** - Choose from 50+ localities
- **RVU Audit Timeline** - Track year-over-year changes
- **18,000+ CPT codes** - Complete CMS data across all years
- **Simplified payment** - User-entered conversion factors for negotiations

---

Built for payer negotiation teams to quickly assess RVU trends and calculate GPCI-adjusted payments.
