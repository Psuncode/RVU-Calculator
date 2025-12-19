# Repository Guidelines

## Project Structure & Module Organization
- `app/` – shipping single-page app (`index.html`) plus embedded loaders; treat this as the source of truth for UI/logic.
- `app/data/processed/` – checked-in CMS/GPCI JSON snapshots for years 2019-2025; regenerate when upstream CSVs change.
- `scripts/` – Python utilities (`serve.py`, `parse_cms_data.py`, `build_rvu_timeline.py`, `build_all_data.py`) for hosting and transforming source files.
- `tests/` – Node-based calculation checks (see `test_calculations.js` and `test_rvu_timeline.js`).
- `docs/` – user guides and documentation.

## Build, Test & Development Commands
- `python scripts/serve.py` – launches the bundled dev server at `http://localhost:8000` and auto-opens the SPA for quick UX checks.
- `python3 -m http.server 8000` – minimal fallback static host when you only need CORS-free file serving.
- `node tests/test_calculations.js` – runs deterministic RVU math assertions; add new scenarios here before shipping pricing changes.
- `python scripts/build_all_data.py` – automated batch processing to parse all 7 years of RVU/GPCI data and build the timeline.
- `python scripts/parse_cms_data.py <csv> <output_json>` – converts individual CMS CSV exports into JSON format.

## Coding Style & Naming Conventions
- **HTML/JS**: keep Tailwind utility classes inline, prefer semantic containers, and use `const`/`let` + camelCase identifiers (`handlePayerChange`).  
- **Python**: 4-space indentation, snake_case naming, docstrings on helper functions (see existing parser scripts).  
- **Data files**: lowercase keys with underscores (e.g., `work_rvu`). Run files through `python -m json.tool` before committing.  
- Avoid feature flags or dead code; delete unused helpers instead of commenting them out.

## Testing Guidelines
- Target parity with CMS published RVUs; every new calculation scenario gets at least one regression in `tests/test_calculations.js` (name cases `test_<scenario>`).
- For parser updates, add representative fixtures under `tests/fixtures/` (create directory if missing) and validate via ad-hoc Python asserts.
- Manual smoke checklist: load 99213 non-facility across different years and localities, verify timeline displays correctly, and ensure copy-to-clipboard still fires.

## Commit & Pull Request Guidelines
- Use short, imperative commit subjects (`Add 2025 RVU data`, `Fix GPCI rounding`, `Update timeline builder`); include context bullets if multiple data files change.
- Reference tracker IDs or CMS release notes in the body when importing new data years or schedules.
- Pull requests should summarize scope, list data sources/versions touched, mention new scripts/tests, and include before/after screenshots for UI work or sample CPT outputs for backend-only changes.
- Block merges until `node tests/test_calculations.js` passes and manual smoke checks are noted in the PR description.

## Security & Configuration Tips
- Never embed PHI or proprietary payer data directly; keep JSON inputs limited to publicly distributable RVU/GPCI schedules.  
- When sharing standalone HTML builds, verify that data signatures (hash printed by the parser scripts) match the CMS release to prevent tampering.
