# Changelog

All notable changes to the RVU Calculator project will be documented in this file.

---

## [1.1.0] - 2025-11-12

### Added

#### Year Indicator
- ✅ **Year badge** in header showing "2022" for data transparency
- ✅ **Metadata file** (`data/processed/metadata.json`) with year info
- ✅ Year shown in payer dropdown options ("CMS Medicare 2022", "Regence 2022")

#### Multi-Payer Support
- ✅ **Payment schedule selector** - Dropdown to switch between payers
- ✅ **Payment schedules configuration** (`data/processed/payment_schedules.json`)
- ✅ **Scalable architecture** - Easy to add new payers

#### Regence Payment Schedule
- ✅ **Category-based conversion factors** - 8 different CPT categories
  - Anesthesia: $72.00
  - Surgery: $57.85
  - Radiology: $62.10
  - Lab: $40.00
  - Medicine: $52.30
  - Medicine (Chiro): $28.00
  - E&M: $39.69
  - All Other: $40.00
- ✅ **Fixed carve-outs** - Specific codes with pre-set fees
  - 90837: $149.90 (Psychotherapy 60 minutes)
- ✅ **Provider type adjustments** - Optional multipliers
  - Physician (MD/DO): 100%
  - PA/CRNA/Acupuncturist: 85%
  - Midwife: 90%
  - Psychologist (PhD): 80%
  - Master's level Mental Health: 75%
  - Chiropractor: 80%
- ✅ **Automatic calculation** - No manual CF input needed for Regence
- ✅ **Smart category matching** - Priority-based range matching

#### UI Improvements
- ✅ **Payer selection dropdown** at top of form
- ✅ **Provider type dropdown** (shown only for Regence)
- ✅ **Conditional CF input** (hidden for Regence, shown for CMS)
- ✅ **Enhanced payment display** - Shows calculation method used
- ✅ **Year badge** in header

#### Testing
- ✅ **Regence test suite** (`tests/test_regence.js`)
  - Tests category matching
  - Tests carve-out override
  - Tests provider adjustments
  - All 4 tests passing

#### Documentation
- ✅ **REGENCE_GUIDE.md** - Complete guide to Regence pricing
  - Examples for all scenarios
  - Category reference table
  - Provider adjustment guide
  - Troubleshooting section
- ✅ **Updated README.md** - New features section
- ✅ **CHANGELOG.md** (this file)

### Changed

- **Payment calculation logic** - Now supports multiple payer types
- **CF input behavior** - Conditional based on payer selection
- **Results display** - Shows calculation method ("E&M (CF $39.69)", "Fixed Fee (Carve-out)", etc.)

### Technical Details

**Files Added:**
```
data/processed/metadata.json
data/processed/payment_schedules.json
docs/REGENCE_GUIDE.md
docs/CHANGELOG.md
tests/test_regence.js
```

**Files Modified:**
```
app/index.html (major update)
  - Added payer dropdown UI
  - Added provider type dropdown UI
  - Added year badge
  - Implemented Regence calculation logic
  - Updated payment display logic

README.md
  - Added year to title
  - Added multi-payer features section
  - Updated quick start guide
```

**Functions Added (index.html):**
- `handlePayerChange()` - Handles payer selection changes
- `findRegenceCategory(code, categories)` - Matches CPT to category
- `calculateRegencePayment(code, totalAdj)` - Calculates Regence payment

**Global Variables Added:**
- `metadata` - Year and source info
- `paymentSchedules` - All payer configurations
- `currentPayer` - Currently selected payer

### Performance

- ✅ No impact on load time (additional 10KB data)
- ✅ Category matching is O(n) where n=8 (negligible)
- ✅ Carve-out lookup is O(1) (array find)

### Compatibility

- ✅ **Backward compatible** - CMS Medicare still works exactly as before
- ✅ **No breaking changes** - Default payer is CMS (existing behavior)
- ✅ **Future-proof** - Easy to add more payers without code changes

---

## [1.0.0] - 2025-11-12 (Initial Release)

### Features

- ✅ CPT/HCPCS code lookup with 17,601 codes
- ✅ Utah GPCI adjustment (2022 data)
- ✅ Facility/Non-Facility place of service
- ✅ Typeahead autocomplete
- ✅ Conversion factor calculator
- ✅ Copy to clipboard
- ✅ Collapsible legend
- ✅ Responsive design
- ✅ Single-file HTML application
- ✅ Client-side processing

### Data

- 17,601 CPT codes from PPRRVU22_JAN.xlsx
- 53 GPCI localities from GPCI2022.xlsx
- Utah GPCI: Work 1.000, PE 0.919, MP 0.799

### Testing

- ✅ Test suite for CMS calculations
- ✅ All acceptance criteria met
- ✅ Data validated against CSV source

---

## Version Comparison

| Feature | v1.0 | v1.1 |
|---------|------|------|
| CMS Medicare pricing | ✓ | ✓ |
| Regence pricing | ✗ | ✓ |
| Year indicator | ✗ | ✓ |
| Multi-payer support | ✗ | ✓ |
| Provider adjustments | ✗ | ✓ |
| Carve-outs | ✗ | ✓ |
| Category-based CF | ✗ | ✓ |
| Total CPT codes | 17,601 | 17,601 |
| GPCI localities | 53 | 53 |

---

## Upgrade Instructions

### From v1.0 to v1.1

**If you're running the app:**

1. **Stop the server** (Ctrl+C)
2. **Refresh browser** or restart server
3. **Try new features:**
   - Select "Regence 2022" from dropdown
   - Enter code 99213 → See auto-calculated payment
   - Try 90837 → See carve-out in action

**No data migration needed** - All changes are additions.

---

## Planned Features (Future Versions)

### v1.2 (Planned)
- [ ] Additional payers (Aetna, UHC, etc.)
- [ ] Percentage-based categories (CLAB, DME, Drug)
- [ ] Multi-year support (2023, 2024 data)
- [ ] Export results to PDF/CSV

### v1.3 (Planned)
- [ ] Multiple locality selection (not just Utah)
- [ ] Batch code lookup
- [ ] Favorite codes feature
- [ ] Dark mode

### v2.0 (Planned)
- [ ] Database backend option
- [ ] Multi-user support
- [ ] Historical comparison
- [ ] Analytics dashboard

---

## Migration Guide

### Adding a New Payer

**Example: Adding Aetna**

1. **Edit payment_schedules.json:**
```json
{
  "schedules": {
    "aetna_2023": {
      "id": "aetna_2023",
      "name": "Aetna",
      "year": 2023,
      "type": "category_based",
      "categories": [...],
      "carveouts": [],
      "provider_adjustments": []
    }
  }
}
```

2. **Update dropdown in index.html:**
```html
<option value="aetna_2023">Aetna 2023</option>
```

**Done!** No other code changes needed.

---

## Breaking Changes

### v1.1
- **None** - All changes are additive and backward compatible

---

## Contributors

- **Initial Development**: Based on PRD requirements
- **v1.1 Enhancements**: Multi-payer support and year indicator

---

## Support

For questions or issues:
- See [README.md](../README.md) for quick start
- See [REGENCE_GUIDE.md](REGENCE_GUIDE.md) for Regence details
- See [requirements.md](requirements.md) for full specifications
- Run tests: `node tests/test_regence.js`

---

**Last Updated:** 2025-11-12
**Current Version:** 1.1.0
