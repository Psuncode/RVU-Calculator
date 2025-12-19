#!/usr/bin/env python3
"""Build a multi-year RVU timeline JSON (CPT × Year) from per-year RVU JSON snapshots.

This script is intentionally CMS-only:
- No reimbursement dollars
- No geographic adjustment (GPCI)
- No payer-specific rates

Input format (per-year JSON):
{
  "99213": {"desc": "...", "work_rvu": 1.3, "pe_rvu_fac": 0.55, "pe_rvu_nonfac": 1.26, "mp_rvu": 0.1},
  ...
}

Output format (timeline JSON):
{
  "meta": {"years": [...], "generated_at": "...", "sources": {...}, "total_codes": N},
  "codes": {
    "99213": {
      "desc": "<canonical desc>",
      "desc_overrides": {"2019": "<optional>"},
      "work_rvu": [null, 1.3, ...],
      "pe_rvu_fac": [...],
      "pe_rvu_nonfac": [...],
      "mp_rvu": [...],
      "status": [null, "new", "existing", "modified", ...]
    }
  }
}

Status rules (per CPT×Year where the CPT exists that year):
- "new": first year present
- "modified": any component changed vs previous present year OR description changed
- "existing": unchanged vs previous present year

Years before the code exists are null (not backfilled).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REQUIRED_RVU_FIELDS = ("desc", "work_rvu", "pe_rvu_fac", "pe_rvu_nonfac", "mp_rvu")


@dataclass(frozen=True)
class YearInput:
    year: int
    path: Path
    source: str


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a 2019–2025 RVU audit timeline JSON from per-year RVU JSON snapshots.",
    )
    parser.add_argument(
        "--year",
        action="append",
        nargs=2,
        metavar=("YEAR", "PATH"),
        help="Add an input snapshot: --year 2022 app/data/processed/rvu_data_2022.json",
        required=True,
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output timeline JSON path (e.g., app/data/processed/rvu_timeline_2019_2025.json)",
    )
    parser.add_argument(
        "--years",
        default="2019-2025",
        help="Year range to emit as columns (default: 2019-2025). Format: 2019-2025",
    )
    parser.add_argument(
        "--float-tol",
        type=float,
        default=1e-4,
        help="Tolerance for comparing RVU component floats (default: 1e-4).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default: 2). Use 0 for compact output.",
    )
    return parser.parse_args()


def _parse_year_range(value: str) -> List[int]:
    if "-" not in value:
        year = int(value)
        return [year]
    start_s, end_s = value.split("-", 1)
    start = int(start_s)
    end = int(end_s)
    if end < start:
        raise ValueError("Invalid --years range: end < start")
    return list(range(start, end + 1))


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _coerce_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid numeric value: {value!r}") from exc


def _validate_year_snapshot(year: int, data: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(data, dict):
        raise ValueError(f"Year {year}: expected top-level object (dict)")
    cleaned: Dict[str, Dict[str, Any]] = {}
    for code, row in data.items():
        if not isinstance(code, str) or not code.strip():
            continue
        if not isinstance(row, dict):
            continue
        missing = [k for k in REQUIRED_RVU_FIELDS if k not in row]
        if missing:
            continue
        cleaned[code.strip().upper()] = {
            "desc": str(row.get("desc") or "").strip(),
            "work_rvu": _coerce_float(row.get("work_rvu")),
            "pe_rvu_fac": _coerce_float(row.get("pe_rvu_fac")),
            "pe_rvu_nonfac": _coerce_float(row.get("pe_rvu_nonfac")),
            "mp_rvu": _coerce_float(row.get("mp_rvu")),
        }
    return cleaned


def _nearly_equal(a: float, b: float, tol: float) -> bool:
    if math.isfinite(a) and math.isfinite(b):
        return abs(a - b) <= tol
    return a == b


def _components_changed(prev: Dict[str, Any], cur: Dict[str, Any], tol: float) -> bool:
    for k in ("work_rvu", "pe_rvu_fac", "pe_rvu_nonfac", "mp_rvu"):
        if not _nearly_equal(float(prev[k]), float(cur[k]), tol):
            return True
    return False


def _build_year_inputs(pairs: Iterable[Tuple[str, str]]) -> List[YearInput]:
    year_inputs: List[YearInput] = []
    for year_s, path_s in pairs:
        year = int(year_s)
        path = Path(path_s)
        if not path.exists():
            raise FileNotFoundError(f"Input not found for year {year}: {path}")
        year_inputs.append(YearInput(year=year, path=path, source=path.name))
    year_inputs.sort(key=lambda yi: yi.year)
    return year_inputs


def main() -> int:
    args = _parse_args()
    try:
        output_years = _parse_year_range(args.years)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    year_inputs = _build_year_inputs(args.year)
    input_years = {yi.year for yi in year_inputs}
    missing_inputs = [y for y in output_years if y not in input_years]
    if missing_inputs:
        print(
            f"WARNING: Missing inputs for years: {', '.join(map(str, missing_inputs))}. "
            "Those years will be emitted as null across all codes.",
            file=sys.stderr,
        )

    per_year: Dict[int, Dict[str, Dict[str, Any]]] = {}
    sources: Dict[str, str] = {}
    for yi in year_inputs:
        with yi.path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        per_year[yi.year] = _validate_year_snapshot(yi.year, raw)
        sources[str(yi.year)] = yi.source

    all_codes = set()
    for year, snapshot in per_year.items():
        _ = year
        all_codes.update(snapshot.keys())

    years_index = {y: i for i, y in enumerate(output_years)}

    codes_out: Dict[str, Dict[str, Any]] = {}
    for code in sorted(all_codes):
        work: List[Optional[float]] = [None] * len(output_years)
        pe_fac: List[Optional[float]] = [None] * len(output_years)
        pe_nonfac: List[Optional[float]] = [None] * len(output_years)
        mp: List[Optional[float]] = [None] * len(output_years)
        status: List[Optional[str]] = [None] * len(output_years)

        # Canonical desc chosen from the latest year where the code is present.
        present_years = [y for y in output_years if y in per_year and code in per_year[y]]
        canonical_desc = ""
        if present_years:
            latest_year = present_years[-1]
            canonical_desc = per_year[latest_year][code]["desc"]

        desc_overrides: Dict[str, str] = {}
        prev_row: Optional[Dict[str, Any]] = None
        prev_desc: Optional[str] = None

        for y in output_years:
            idx = years_index[y]
            row = per_year.get(y, {}).get(code)
            if row is None:
                continue

            work[idx] = float(row["work_rvu"])
            pe_fac[idx] = float(row["pe_rvu_fac"])
            pe_nonfac[idx] = float(row["pe_rvu_nonfac"])
            mp[idx] = float(row["mp_rvu"])

            row_desc = str(row.get("desc") or "")
            if canonical_desc and row_desc and row_desc != canonical_desc:
                desc_overrides[str(y)] = row_desc

            if prev_row is None:
                status[idx] = "new"
            else:
                changed = _components_changed(prev_row, row, tol=float(args.float_tol))
                desc_changed = (prev_desc or "") != row_desc
                status[idx] = "modified" if (changed or desc_changed) else "existing"

            prev_row = row
            prev_desc = row_desc

        codes_out[code] = {
            "desc": canonical_desc,
            "desc_overrides": desc_overrides,
            "work_rvu": work,
            "pe_rvu_fac": pe_fac,
            "pe_rvu_nonfac": pe_nonfac,
            "mp_rvu": mp,
            "status": status,
        }

    out = {
        "meta": {
            "years": output_years,
            "generated_at": _now_iso(),
            "sources": sources,
            "total_codes": len(codes_out),
            "missing_years": missing_inputs,
        },
        "codes": codes_out,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    indent = None if int(args.indent) <= 0 else int(args.indent)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=indent, sort_keys=False)
        f.write("\n")

    print(f"Wrote timeline: {out_path} ({len(codes_out)} codes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

