# Requirements Document: RVU Lookup (Utah-Adjusted)

**Version:** 1.0
**Date:** 2025-11-12
**Status:** Approved & Implemented

---

## 1. Project Overview

### 1.1 Purpose
Build a fast, single-code RVU lookup application that displays:
1. CMS base Relative Value Units (RVUs)
2. Utah-adjusted RVUs via Geographic Practice Cost Index (GPCI)
3. Clear explanation of adjustments and calculations
4. Optional payment estimation using Conversion Factor

### 1.2 Goals
- Provide instant RVU lookups with geographic adjustment for Utah
- Eliminate manual GPCI calculations
- Enable quick reimbursement schedule verification
- Deliver a simple, self-contained tool requiring no server infrastructure

### 1.3 Target Users
- Healthcare administrators
- Medical billing specialists
- Practice managers
- Physicians reviewing reimbursement rates
- Anyone needing Utah-adjusted RVU calculations

---

## 2. Functional Requirements

### 2.1 Core Features

#### FR-1: CPT/HCPCS Code Lookup
**Priority:** Critical
**Description:** User can enter a 5-character CPT or HCPCS code and retrieve associated RVU data.

**Requirements:**
- Accept alphanumeric codes (5 characters max)
- Case-insensitive input
- Typeahead autocomplete with code descriptions
- Support instant lookup on Enter key
- Display code description with results

**Acceptance Criteria:**
- Valid code displays results within 300ms (first lookup) or 150ms (subsequent)
- Invalid code shows clear error message
- Autocomplete appears for partial matches (≥2 characters typed)

#### FR-2: Place of Service Selection
**Priority:** Critical
**Description:** User can toggle between Facility and Non-Facility settings to use the appropriate Practice Expense (PE) RVU value.

**Requirements:**
- Two-option toggle: Facility | Non-Facility
- Default: Non-Facility
- Visual indication of selected option
- Immediate recalculation when toggled

**Acceptance Criteria:**
- Toggle updates PE value used in calculations
- Results update without requiring re-entry of code
- Selected state clearly visible to user

#### FR-3: RVU Calculation with Utah GPCI
**Priority:** Critical
**Description:** Calculate Utah-adjusted RVUs using CMS base values and Utah GPCI.

**Formula:**
```
Adjusted Work RVU = Work RVU × Utah Work GPCI
Adjusted PE RVU   = PE RVU (by POS) × Utah PE GPCI
Adjusted MP RVU   = MP RVU × Utah MP GPCI

Total Adjusted RVUs = Adjusted Work + Adjusted PE + Adjusted MP
```

**Requirements:**
- Use exact GPCI values for Utah locality
- Apply correct PE value based on POS selection
- Display all intermediate values (base, GPCI, adjusted)
- Show Total Adjusted RVUs prominently

**Acceptance Criteria:**
- Calculations match test vectors (see Section 7)
- All adjusted components displayed to 4 decimal places
- Total Adjusted RVUs displayed to 4 decimal places
- No calculation errors for edge cases (MP=0, etc.)

#### FR-4: Conversion Factor Calculator (Match Helper)
**Priority:** High
**Description:** Optional field for entering Conversion Factor to calculate estimated payment.

**Formula:**
```
Estimated Payment = Total Adjusted RVUs × Conversion Factor
```

**Requirements:**
- Optional numeric input field
- Accept decimal values (e.g., 39.69)
- Show/hide result based on CF presence
- Display calculation formula used

**Acceptance Criteria:**
- Payment displayed to $0.01 precision
- Formula shows exact values used (e.g., "2.5295 × $39.69")
- Updates immediately when CF changes
- Hidden when CF field is empty or invalid

#### FR-5: Results Display
**Priority:** Critical
**Description:** Display comprehensive results in organized sections.

**Required Sections:**
1. **Code Information Card**
   - CPT/HCPCS code
   - Full description
   - Current POS setting

2. **CMS Base RVUs**
   - Work RVU
   - PE RVU (Facility)
   - PE RVU (Non-Facility)
   - MP RVU

3. **Utah GPCI**
   - Work GPCI
   - PE GPCI
   - MP GPCI

4. **Adjusted RVUs (Utah)**
   - Adjusted Work RVU
   - Adjusted PE RVU
   - Adjusted MP RVU
   - **Total Adjusted RVUs** (emphasized)

5. **Estimated Payment** (conditional)
   - Dollar amount
   - Calculation formula

**Acceptance Criteria:**
- All sections visible simultaneously
- Clear visual hierarchy
- Total Adjusted RVUs stands out visually
- Responsive layout (works on mobile)

#### FR-6: Copy to Clipboard
**Priority:** Medium
**Description:** One-click copy of Total Adjusted RVUs value.

**Requirements:**
- Copy button next to Total Adjusted RVUs
- Visual feedback on successful copy
- Copy exact value with 4 decimal precision

**Acceptance Criteria:**
- Copies full precision value (e.g., "2.5295")
- Shows visual confirmation (checkmark animation)
- Works in all modern browsers

#### FR-7: Educational Legend
**Priority:** High
**Description:** Collapsible section explaining calculation methodology.

**Requirements:**
- Expand/collapse toggle
- Contains complete explanation (see Section 6.3)
- Includes formula, POS explanation, rounding rules
- Accessible without scrolling past results

**Acceptance Criteria:**
- Expands/collapses smoothly
- Content matches PRD legend verbatim
- Clear visual indicator of expanded/collapsed state

### 2.2 Error Handling

#### FR-8: Input Validation
**Requirements:**
- Code not found: "Code '[CODE]' not found in database. Please check the code and try again."
- Empty input: No error, no results displayed
- Invalid format: Accept any 5-character alphanumeric input, validate against database
- Data load failure: "Failed to load RVU data. Please ensure data files are present."

**Acceptance Criteria:**
- Error messages are user-friendly
- Clear instructions for resolution
- No technical jargon
- Errors dismissible when valid input entered

---

## 3. Technical Requirements

### 3.1 Architecture

#### TR-1: Single-File Application
**Priority:** Critical
**Description:** Entire application contained in one HTML file for maximum portability.

**Requirements:**
- No external dependencies (except CDN for Tailwind CSS)
- All JavaScript inline in `<script>` tags
- All CSS via Tailwind classes or inline `<style>`
- No build process required

**Acceptance Criteria:**
- File opens directly in browser via `file://` protocol
- No 404 errors or missing resources (except data files)
- Works offline after initial Tailwind CDN load

#### TR-2: Technology Stack
**Specified Technologies:**
- **Frontend Framework:** Vanilla JavaScript (ES6+)
- **UI Framework:** Tailwind CSS (CDN)
- **Data Format:** JSON
- **Browser Target:** Modern browsers (Chrome, Firefox, Safari, Edge)

**Requirements:**
- No TypeScript compilation
- No React/Vue/Angular
- No npm build process
- No webpack/vite bundling

#### TR-3: Performance
**Benchmarks:**
- **First lookup:** < 300ms after data loaded
- **Subsequent lookups:** < 150ms
- **Data load time:** < 2 seconds for 10,000 codes
- **Autocomplete response:** < 50ms

**Requirements:**
- Client-side data caching
- Efficient search algorithms
- Minimal DOM manipulation
- No unnecessary recalculations

### 3.2 Data Requirements

#### TR-4: RVU Data Structure
**File:** `data/rvu_data.json`

**Schema:**
```json
{
  "CPT_CODE": {
    "desc": "string (description)",
    "work_rvu": number,
    "pe_rvu_fac": number,
    "pe_rvu_nonfac": number,
    "mp_rvu": number
  }
}
```

**Example:**
```json
{
  "99213": {
    "desc": "Office/outpatient visit, established patient, 20-29 minutes",
    "work_rvu": 1.30,
    "pe_rvu_fac": 0.72,
    "pe_rvu_nonfac": 1.10,
    "mp_rvu": 0.10
  }
}
```

**Requirements:**
- Keys are CPT/HCPCS codes (string)
- All numeric values are floats
- Description is human-readable string
- File size optimized (minified if needed for large datasets)

#### TR-5: GPCI Data Structure
**File:** `data/gpci_data.json`

**Schema:**
```json
{
  "LOCALITY_CODE": {
    "name": "string (locality name)",
    "state": "string (state name)",
    "work_gpci": number,
    "pe_gpci": number,
    "mp_gpci": number
  }
}
```

**Example:**
```json
{
  "UT": {
    "name": "Utah",
    "state": "Utah",
    "work_gpci": 1.020,
    "pe_gpci": 1.005,
    "mp_gpci": 0.980
  }
}
```

**Requirements:**
- Keys are locality codes (string)
- All GPCI values are floats (typically 0.8-1.2 range)
- Must include Utah ("UT") locality
- Supports multiple localities (future enhancement)

#### TR-6: Data Loading
**Requirements:**
- Load both JSON files on page load
- Handle missing files gracefully
- Display loading state if needed
- Cache data in memory for session duration

**Acceptance Criteria:**
- User sees error if data files missing
- No duplicate data loads
- Data accessible to all functions
- Console logs data load success

---

## 4. Calculation Specifications

### 4.1 RVU Adjustment Formula

**Step 1: Select Base RVU Values**
```
Work_RVU = cms_data[code].work_rvu
PE_RVU   = cms_data[code].pe_rvu_fac    (if POS = Facility)
           cms_data[code].pe_rvu_nonfac (if POS = Non-Facility)
MP_RVU   = cms_data[code].mp_rvu
```

**Step 2: Apply GPCI Adjustments**
```
Adjusted_Work = Work_RVU × Utah_Work_GPCI
Adjusted_PE   = PE_RVU × Utah_PE_GPCI
Adjusted_MP   = MP_RVU × Utah_MP_GPCI
```

**Step 3: Calculate Total**
```
Total_Adjusted_RVUs = Adjusted_Work + Adjusted_PE + Adjusted_MP
```

**Step 4: Calculate Payment (Optional)**
```
Estimated_Payment = Total_Adjusted_RVUs × Conversion_Factor
```

### 4.2 Rounding Rules

| Value | Precision | Example |
|-------|-----------|---------|
| Adjusted Work RVU | 4 decimals | 1.3260 |
| Adjusted PE RVU | 4 decimals | 1.1055 |
| Adjusted MP RVU | 4 decimals | 0.0980 |
| Total Adjusted RVUs | 4 decimals | 2.5295 |
| Estimated Payment | $0.01 | $100.40 |

**Implementation:**
- Use `.toFixed(4)` for RVU values
- Use `.toFixed(2)` for payment amounts
- Display base values to 2 decimals for readability

### 4.3 Edge Cases

| Case | Handling |
|------|----------|
| MP RVU = 0 | Calculate as 0.0000, include in total |
| PE RVU = 0 | Calculate as 0.0000, include in total |
| GPCI = 1.000 | Apply normally (adjusted = base) |
| Invalid CF | Hide payment section, no calculation |
| Missing POS selection | Use default (Non-Facility) |

---

## 5. User Interface Requirements

### 5.1 Layout Structure

```
┌─────────────────────────────────────────────────┐
│              HEADER                              │
│  RVU Lookup (Utah-Adjusted)                     │
│  Subtitle text                                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              INPUT SECTION                       │
│  [CPT/HCPCS Input]  [POS Toggle]                │
│  [Conversion Factor (Optional)]                  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              CODE INFO CARD                      │
│  99213 - Description                   [POS]     │
└─────────────────────────────────────────────────┘

┌────────────┬─────────────┬────────────────────┐
│ CMS Base   │ Utah GPCI   │ Adjusted RVUs      │
│ RVUs       │             │ (Utah)             │
│            │             │                     │
│ Work: 1.30 │ Work: 1.020 │ Work: 1.3260       │
│ PE F: 0.72 │ PE:   1.005 │ PE:   1.1055       │
│ PE N: 1.10 │ MP:   0.980 │ MP:   0.0980       │
│ MP:   0.10 │             │                     │
│            │             │ Total: 2.5295 [📋] │
└────────────┴─────────────┴────────────────────┘

┌─────────────────────────────────────────────────┐
│         ESTIMATED PAYMENT (Optional)             │
│  $100.40                                         │
│  2.5295 × $39.69                                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  ▼ How We Calculate Adjusted RVUs               │
│  (Collapsible legend content)                    │
└─────────────────────────────────────────────────┘
```

### 5.2 Color Scheme

**Primary Colors:**
- Primary Blue: `#3b82f6` (buttons, highlights)
- Success Green: `#10b981` (payment section)
- Warning Red: `#ef4444` (errors)
- Neutral Gray: `#6b7280` (text)

**Backgrounds:**
- Page: `#f9fafb` (light gray)
- Cards: `#ffffff` (white)
- Adjusted RVUs card: Blue gradient `from-blue-50 to-indigo-50`
- Payment section: `#f0fdf4` (light green)

### 5.3 Typography

**Font Family:** System fonts (Tailwind default)
```
font-family: ui-sans-serif, system-ui, -apple-system, ...
```

**Font Sizes:**
- Page title: 2.25rem (text-4xl)
- Section headers: 1.125rem (text-lg)
- Body text: 0.875rem (text-sm)
- Total Adjusted RVUs: 1.25rem (text-xl)
- Estimated Payment: 1.875rem (text-3xl)

### 5.4 Interactive Elements

#### Typeahead Autocomplete
- **Trigger:** 2+ characters typed
- **Display:** Up to 10 matches
- **Format:** Code (bold) + description (smaller gray text)
- **Interaction:** Click to select, keyboard navigation
- **Styling:** White background, shadow, hover state

#### POS Toggle
- **Style:** Button group with rounded corners
- **Active state:** Blue background, white text
- **Inactive state:** Transparent background, gray text
- **Transition:** Smooth color change (0.2s)

#### Copy Button
- **Icon:** Clipboard SVG
- **Hover:** Light blue background
- **Click:** Checkmark animation, green color
- **Reset:** Return to clipboard icon after 1.5s

#### Legend Toggle
- **Closed:** Down arrow icon
- **Open:** Up arrow icon (rotated 180°)
- **Animation:** Smooth expand/collapse
- **Hover:** Gray background on header

---

## 6. Content Requirements

### 6.1 Header Text

**Title:** "RVU Lookup (Utah-Adjusted)"
**Subtitle:** "Enter a CPT/HCPCS code to see CMS RVUs and Utah-adjusted RVUs."

### 6.2 Input Labels

- **CPT/HCPCS Input:** "CPT / HCPCS Code"
  Placeholder: "Enter code (e.g., 99213)"

- **POS Toggle:** "Place of Service"
  Options: "Non-Facility" | "Facility"

- **CF Input:** "Conversion Factor (optional) — Match Helper"
  Placeholder: "e.g., 39.69"
  Helper text: "Enter your CF to see estimated payment (Total Adjusted RVUs × CF)"

### 6.3 Legend Content (Exact Copy)

**Title:** "How We Calculate Adjusted RVUs"

**Body:**

We start with the **CMS base RVUs** for this CPT/HCPCS code: Work, Practice Expense (PE), and Malpractice (MP). Because PE is different by place of service, select **Facility** or **Non-facility** to use the right PE value.

Then we apply **Utah's GPCI** (Geographic Practice Cost Index) to each component:

- **Adjusted Work RVU** = Work RVU × Utah Work GPCI
- **Adjusted PE RVU** = PE RVU (by POS) × Utah PE GPCI
- **Adjusted MP RVU** = MP RVU × Utah MP GPCI

**Total Adjusted RVUs** = Adjusted Work + Adjusted PE + Adjusted MP.

If you enter a **Conversion Factor (CF)**, we show an **Estimated Payment** = Total Adjusted RVUs × CF. (This helps you quickly compare to your own reimbursement schedule.)

**Rounding**
Adjusted components and Total Adjusted RVUs are displayed to **4 decimals**. Estimated payment is shown to **$0.01**.

### 6.4 Error Messages

**Code Not Found:**
```
Code "[CODE]" not found in database. Please check the code and try again.
```

**Data Load Failure:**
```
Failed to load RVU data. Please ensure data files are present.
```

**No Results:**
```
Enter a CPT/HCPCS code to see results.
```

---

## 7. Test Cases & Acceptance Criteria

### 7.1 Test Vector: Non-Facility

**Input:**
- Code: 99213
- POS: Non-Facility
- CF: 39.69

**CMS Base Values:**
- Work RVU: 1.30
- PE RVU (Non-Facility): 1.10
- MP RVU: 0.10

**Utah GPCI:**
- Work: 1.020
- PE: 1.005
- MP: 0.980

**Expected Results:**
- Adjusted Work: 1.3260 (1.30 × 1.020)
- Adjusted PE: 1.1055 (1.10 × 1.005)
- Adjusted MP: 0.0980 (0.10 × 0.980)
- **Total Adjusted RVUs: 2.5295**
- **Estimated Payment: $100.40** (2.5295 × 39.69)

**Acceptance:** All values match to specified precision.

### 7.2 Test Vector: Facility

**Input:**
- Code: 99213
- POS: Facility
- CF: 39.69

**CMS Base Values:**
- Work RVU: 1.30
- PE RVU (Facility): 0.72
- MP RVU: 0.10

**Utah GPCI:**
- Work: 1.020
- PE: 1.005
- MP: 0.980

**Expected Results:**
- Adjusted Work: 1.3260 (1.30 × 1.020)
- Adjusted PE: 0.7236 (0.72 × 1.005)
- Adjusted MP: 0.0980 (0.10 × 0.980)
- **Total Adjusted RVUs: 2.1476**
- **Estimated Payment: $85.24** (2.1476 × 39.69)

**Acceptance:** All values match to specified precision.

### 7.3 Test Vector: No MP (Edge Case)

**Input:**
- Code: [Any code with MP = 0]
- POS: Non-Facility

**Expected:**
- Adjusted MP: 0.0000
- Total still calculates correctly (Work + PE + 0)
- No errors or NaN values

### 7.4 Functional Acceptance Criteria

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| AC-1 | Code lookup | Valid code displays results < 300ms |
| AC-2 | Code lookup | Invalid code shows error message |
| AC-3 | Autocomplete | Appears for 2+ characters typed |
| AC-4 | Autocomplete | Shows up to 10 matches |
| AC-5 | POS toggle | Updates PE value immediately |
| AC-6 | POS toggle | Recalculates without re-entering code |
| AC-7 | Calculations | Match test vectors exactly |
| AC-8 | Rounding | Adjusted RVUs to 4 decimals |
| AC-9 | Rounding | Payment to $0.01 |
| AC-10 | CF calculator | Shows only when CF entered |
| AC-11 | CF calculator | Updates immediately on CF change |
| AC-12 | Copy button | Copies full precision value |
| AC-13 | Copy button | Shows visual confirmation |
| AC-14 | Legend | Expands/collapses smoothly |
| AC-15 | Responsive | Works on mobile/tablet/desktop |
| AC-16 | Error handling | User-friendly messages |
| AC-17 | Performance | Subsequent lookups < 150ms |

---

## 8. Implementation Requirements

### 8.1 File Structure

```
RVU Calculator/
├── index.html              # Main application (single file)
├── data/
│   ├── rvu_data.json      # CPT/HCPCS codes with RVU values
│   └── gpci_data.json     # Geographic Practice Cost Indices
├── parse_cms_data.py      # CSV-to-JSON converter
├── test_calculations.js   # Automated test suite
├── requirements.md        # This document
└── README.md              # User documentation
```

### 8.2 Parser Script Requirements

**File:** `parse_cms_data.py`

**Capabilities:**
- Accept CMS CSV files as input
- Auto-detect column headers (flexible matching)
- Handle common CMS format variations
- Output properly formatted JSON
- Provide progress feedback
- Error handling for malformed rows

**Usage:**
```bash
python parse_cms_data.py input.csv output.json
```

**Acceptance:**
- Successfully parses CMS RVU files (10,000+ codes)
- Successfully parses GPCI locality files (100+ localities)
- Outputs valid JSON with correct schema
- Handles missing/empty values gracefully

### 8.3 Test Suite Requirements

**File:** `test_calculations.js`

**Test Coverage:**
- Verify calculation formulas
- Check rounding precision
- Validate test vectors from Section 7
- Test edge cases (MP=0, etc.)
- Verify POS switching logic

**Acceptance:**
- All tests pass with included sample data
- Clear pass/fail reporting
- Shows expected vs actual values
- Runnable via `node test_calculations.js`

---

## 9. Data Sources & Updates

### 9.1 CMS Data Sources

**RVU Data:**
- **Source:** CMS Physician Fee Schedule Relative Value Files
- **URL:** https://www.cms.gov/medicare/payment/fee-schedules/physician
- **Update Frequency:** Annually (usually November for next year)
- **Format:** Excel/CSV

**GPCI Data:**
- **Source:** CMS Geographic Practice Cost Indices
- **URL:** Included in PFS zip files
- **Update Frequency:** Annually
- **Format:** Excel/CSV

### 9.2 Data Update Process

1. Download latest CMS files
2. Run parser script: `python parse_cms_data.py cms_file.csv data/rvu_data.json`
3. Verify JSON output format
4. Run test suite: `node test_calculations.js`
5. Refresh browser to load new data

**No code changes required for data updates.**

---

## 10. Browser Compatibility

### 10.1 Supported Browsers

| Browser | Minimum Version | Notes |
|---------|----------------|-------|
| Chrome | 90+ | Recommended |
| Firefox | 88+ | Fully supported |
| Safari | 14+ | macOS & iOS |
| Edge | 90+ | Chromium-based |

### 10.2 Required Features

- ES6 JavaScript (arrow functions, const/let, async/await)
- Fetch API
- Clipboard API (for copy functionality)
- CSS Grid & Flexbox
- LocalStorage (for future enhancements)

### 10.3 Not Supported

- Internet Explorer (any version)
- Legacy Edge (pre-Chromium)
- Browsers with JavaScript disabled

---

## 11. Future Enhancements (Not in v1.0)

These are explicitly **out of scope** for v1.0 but documented for future consideration:

### 11.1 Nice-to-Have Features
- Multiple locality selection (not just Utah)
- Batch code lookup (CSV upload)
- Save favorite codes
- Export results as PDF/PNG
- Historical RVU comparison (year-over-year)
- Multi-payer support (Medicare, Medicaid, commercial)

### 11.2 Technical Enhancements
- Offline PWA support
- IndexedDB for large datasets
- Server-side API option
- TypeScript conversion
- Unit test coverage
- CI/CD pipeline

---

## 12. Success Metrics

### 12.1 Performance Metrics
- ✅ First lookup: < 300ms
- ✅ Subsequent lookups: < 150ms
- ✅ Autocomplete response: < 50ms
- ✅ Page load: < 2s

### 12.2 Quality Metrics
- ✅ All test vectors pass
- ✅ Zero calculation errors
- ✅ 100% acceptance criteria met
- ✅ No console errors in production

### 12.3 User Experience Metrics
- ✅ Single-page, no navigation required
- ✅ No build/deploy process for users
- ✅ Works offline (after initial load)
- ✅ Mobile responsive

---

## 13. Compliance & Standards

### 13.1 Data Accuracy
- All CMS data sourced from official channels
- GPCI values verified against CMS publications
- Calculation formulas match CMS methodology
- Test vectors validated against manual calculations

### 13.2 Coding Standards
- Vanilla JavaScript (ES6+)
- Semantic HTML5
- Accessible UI (WCAG 2.1 Level A minimum)
- Clean, commented code
- Consistent naming conventions

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **RVU** | Relative Value Unit - The measure of value for physician services |
| **GPCI** | Geographic Practice Cost Index - Geographic adjustment factor |
| **Work RVU** | Physician work component of RVU |
| **PE RVU** | Practice Expense component of RVU |
| **MP RVU** | Malpractice component of RVU |
| **POS** | Place of Service (Facility vs Non-Facility) |
| **CF** | Conversion Factor - Dollar amount per RVU ($) |
| **CPT** | Current Procedural Terminology - Medical procedure codes |
| **HCPCS** | Healthcare Common Procedure Coding System |
| **CMS** | Centers for Medicare & Medicaid Services |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-12 | Initial | Complete requirements document created from PRD |

---

**End of Requirements Document**
