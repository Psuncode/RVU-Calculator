# Quick Start Guide - RVU Calculator

## 🚀 Start the App (5 seconds)

```bash
python scripts/serve.py
```

**That's it!** Your browser will open automatically to http://localhost:8000

---

## ✅ What Just Happened?

1. ✅ Loaded **17,601 CPT codes** from CMS 2022
2. ✅ Loaded **Utah GPCI values** (Work 1.000, PE 0.919, MP 0.799)
3. ✅ Server running (no CORS issues)
4. ✅ Ready to calculate!

---

## 🧪 Test It (10 seconds)

### Example 1: Office Visit (Non-Facility)

1. **Enter code:** `99213`
2. **Leave on:** Non-Facility
3. **Enter CF:** `39.69`
4. **Result:** **$100.73**

### Example 2: Office Visit (Facility)

1. **Same code:** `99213`
2. **Click:** Facility
3. **Same CF:** `39.69`
4. **Result:** **$74.83**

### Why Different?

- **Facility:** Lower PE (0.55) → Lower total
- **Non-Facility:** Higher PE (1.26) → Higher total

---

## 📊 Data Validation

### Your data is correct!

**From CSV (`PPRRVU22_JAN.csv`):**
```
99213: Work 1.30, PE NF 1.26, PE F 0.55, MP 0.10
```

**Our Parsed Data:**
```json
{
  "99213": {
    "desc": "Office o/p est low 20-29 min",
    "work_rvu": 1.3,
    "pe_rvu_nonfac": 1.26,
    "pe_rvu_fac": 0.55,
    "mp_rvu": 0.1
  }
}
```

**✓ Perfect match!**

---

## 🔧 Troubleshooting

### "Failed to load RVU data"

**Problem:** You tried to open `index.html` directly.

**Solution:** Use the server:
```bash
python scripts/serve.py
```

### "Port already in use"

Try a different port:
```bash
python scripts/serve.py 8001
```

---

## 🧭 Audit Timeline (2019–2025)

The Audit Timeline tab shows **CMS base RVUs** year-over-year (Work / PE / MP) and flags codes as **New / Existing / Modified**.

To enable it, generate the timeline JSON:

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

Then refresh the app and click **Audit Timeline (2019–2025)**.

Then open: http://localhost:8001

### Data seems wrong

Verify with CSV:
```bash
grep "^99213," "/Users/philipsun/Downloads/RVU22A (1)/PPRRVU22_JAN.csv"
```

Should show: `99213,,Office o/p est low 20-29 min,A,,1.30,1.26,,0.55,,0.10,...`

---

## 📝 Common Codes to Try

| Code | Description | Non-Fac Payment* | Fac Payment* |
|------|-------------|------------------|--------------|
| 99213 | Est low (20-29 min) | $100.73 | $74.83 |
| 99214 | Est mod (30-39 min) | $142.33 | $112.30 |
| 99215 | Est high (40-54 min) | $202.90 | $167.31 |
| 99203 | New low (30-44 min) | $130.65 | $100.18 |
| 99204 | New mod (45-59 min) | $192.42 | $156.57 |
| 99205 | New high (60-74 min) | $257.61 | $217.46 |

*Based on CF $39.69 (2022 Medicare CF)

---

## 🎯 Features You Can Use

### 1. Typeahead Search
- Type just `992` → See all matching codes
- Shows descriptions as you type
- Up to 10 suggestions

### 2. Place of Service Toggle
- **Non-Facility:** Office setting (higher PE)
- **Facility:** Hospital setting (lower PE)
- Instant recalculation

### 3. Conversion Factor Calculator
- Enter your CF (e.g., 39.69)
- See estimated payment
- Updates live

### 4. Copy to Clipboard
- Click 📋 next to Total Adjusted RVUs
- Copies full precision (4 decimals)
- Shows ✓ when copied

### 5. Educational Legend
- Click to expand explanation
- Shows exact formula
- Explains rounding rules

---

## 📈 Utah GPCI Values (2022)

| Component | GPCI | Effect |
|-----------|------|--------|
| Work | 1.000 | No adjustment |
| Practice Expense | 0.919 | 8.1% decrease |
| Malpractice | 0.799 | 20.1% decrease |

**Net effect:** Utah RVUs are typically **lower** than national average.

---

## 🔄 Calculation Example

**Code:** 99213 (Non-Facility)

**Step 1: CMS Base RVUs**
- Work: 1.30
- PE: 1.26 (Non-Facility)
- MP: 0.10

**Step 2: Apply Utah GPCI**
- Adj Work = 1.30 × 1.000 = **1.3000**
- Adj PE = 1.26 × 0.919 = **1.1579**
- Adj MP = 0.10 × 0.799 = **0.0799**

**Step 3: Total**
- Total = 1.3000 + 1.1579 + 0.0799 = **2.5378**

**Step 4: Payment (if CF entered)**
- Payment = 2.5378 × $39.69 = **$100.73**

---

## 🛑 When to Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

```
^C
✓ Server stopped.
```

---

## 📚 More Information

- **Full documentation:** `README.md`
- **Data schema:** `DATA_SCHEMA.md`
- **Requirements:** `requirements.md`
- **Build summary:** `BUILD_SUMMARY.md`

---

## ⚡ That's It!

You now have a fully functional RVU calculator with:
- ✅ 17,601 real CMS codes
- ✅ Utah GPCI adjustment
- ✅ Validated data
- ✅ Fast lookups
- ✅ No errors

**Happy calculating!** 🎉
