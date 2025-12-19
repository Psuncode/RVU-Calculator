# Repository Guidelines

## Project Structure & Module Organization
- `app/index.html`: shipping single-page app with Tailwind CDN and inline JS.
- `app/data/processed/`: checked-in CMS RVU + GPCI JSON snapshots (2019–2025) and the consolidated timeline.
- `scripts/parse_cms_data.py`: CSV→JSON converter for CMS RVU or GPCI files; accepts input/output args and logs parsing stats.
- `tests/test_calculations.js`: Node test harness covering calculation correctness and rounding expectations.

## Build, Test, and Development Commands
- `python scripts/serve.py`: run the bundled dev server and open the SPA.
- `python3 -m http.server 8000` (from `app/`): simple static server.
- `python3 scripts/parse_cms_data.py <input.csv> app/data/processed/rvu_data_<year>.json`: regenerate one year.
- `node tests/test_calculations.js`: execute deterministic regression tests.
- `node tests/test_rvu_timeline.js`: verify timeline build rules.

## Coding Style & Naming Conventions
- Keep all app logic inside `index.html` inline `<script>` tags (TR-1) using 4-space indentation and descriptive camelCase (`currentPOS`, `calculateAndDisplay`).
- Favor Tailwind utility classes for layout/color; only add custom CSS when utilities fall short.
- JSON keys stay as raw CPT codes or locality abbreviations; numeric fields remain floats to preserve four-decimal precision.

## Testing Guidelines
- Extend `test_calculations.js` whenever CMS data changes. Name suites after the scenario (e.g., `"99213 Non-Facility"`) and assert to four decimals plus $0.01 for payments.
- Manual smoke checklist: autocomplete timing (≥2 chars, ≤10 results), POS toggle recalculation, CF helper visibility, legend copy, and clipboard feedback across Chrome/Firefox/Safari/Edge on desktop + mobile widths.

## Commit & Pull Request Guidelines
- Use imperative commit subjects referencing scope (`Update parser column mapping`).
- PR descriptions should map changes to requirement IDs (FR-1–FR-8, TR-1–TR-6), list test commands run (`node test_calculations.js`, parser dry-runs), and include screenshots/GIFs for UI adjustments.
- Block PRs until data/scripts/tests are rerun when touching `data/` or calculation logic; document any manual QA performed.

## Security & Configuration Tips
- CMS RVU files exceed 10k codes—avoid inlining data into `index.html` to keep load time within TR-3 budgets; distribute via `data/` JSONs instead.
- Ship release bundles containing `index.html`, `data/`, `parse_cms_data.py`, this guide, and README so downstream teams can refresh data without new tooling.
