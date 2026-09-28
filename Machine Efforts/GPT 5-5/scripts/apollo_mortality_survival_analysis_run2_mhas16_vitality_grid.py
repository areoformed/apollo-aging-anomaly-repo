#!/usr/bin/env python3
"""
Run2 simple 80+ vitality grid using the MHAS 54/334 lower-bound anchor.

This preserves the previous simple_80plus_vitality_grid output and writes a
new directory:

    analysis_outputs/group29_sensitivity_run2_2026-06-04/
      simple_80plus_mhas16_vitality_grid/

The lower bound is treated as MHAS-derived but user-supplied in this run:
54 / 334 = 16.17%. The local MHAS documentation saved in references verifies
the MHAS cohort/cognitive-status construct, but this script does not reproduce
the 54/334 count from MHAS microdata.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SIMPLE_SCRIPT = WORKSPACE_ROOT / "scripts" / "apollo_mortality_survival_analysis_run2_simple_vitality_grid.py"
OUT_DIR = (
    WORKSPACE_ROOT
    / "analysis_outputs"
    / "group29_sensitivity_run2_2026-06-04"
    / "simple_80plus_mhas16_vitality_grid"
)

MHAS_LOWER_COUNT = 54
MHAS_LOWER_DENOMINATOR = 334
LOWER_RATE = MHAS_LOWER_COUNT / MHAS_LOWER_DENOMINATOR
UPPER_RATE = 0.68
RATE_GRID = [
    LOWER_RATE,
    LOWER_RATE + (UPPER_RATE - LOWER_RATE) / 3.0,
    LOWER_RATE + 2.0 * (UPPER_RATE - LOWER_RATE) / 3.0,
    UPPER_RATE,
]


def load_simple_module():
    spec = importlib.util.spec_from_file_location("apollo_run2_simple_grid", SIMPLE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load simple-grid script: {SIMPLE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rate_grid_rows() -> list[dict[str, object]]:
    return [
        {
            "rate_key": "lower_mhas_54_of_334_youthful_cognition",
            "mental_vitality_rate": RATE_GRID[0],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[0],
            "basis": (
                "MHAS-derived user-supplied lower anchor: 54 of 334 age-80+ "
                "individuals retained youthful cognitive function. Not "
                "recomputed from MHAS microdata in this run."
            ),
        },
        {
            "rate_key": "interior_low_between_mhas_and_hcap",
            "mental_vitality_rate": RATE_GRID[1],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[1],
            "basis": "Evenly spaced interior point between MHAS lower anchor and HRS-HCAP upper anchor.",
        },
        {
            "rate_key": "interior_high_between_mhas_and_hcap",
            "mental_vitality_rate": RATE_GRID[2],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[2],
            "basis": "Evenly spaced interior point between MHAS lower anchor and HRS-HCAP upper anchor.",
        },
        {
            "rate_key": "upper_hcap_normal_cognition_overall",
            "mental_vitality_rate": RATE_GRID[3],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[3],
            "basis": (
                "HRS-HCAP broad normal-cognition anchor for U.S. adults 65+: "
                "1 - dementia 10 pct - MCI 22 pct. Optimistic for 80+."
            ),
        },
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_report(simple, path: Path, bucket_rows: list[dict[str, object]], rate_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> None:
    selected = [
        row
        for row in summary_rows
        if row["mortality_scenario_key"]
        in {"ssa_general_age30", "healthy_30pct_lower_hazard", "apollo_smr_like_54pct_lower_hazard"}
    ]
    lines = [
        "# Simple 80+ Mental-Vitality Rate Grid: MHAS 16% Lower Anchor",
        "",
        "## Simplification",
        "",
        "This run applies one blanket 80+ mental-vitality probability rather than assigning age-bucket-specific probabilities. That avoids pretending the available sources can support precise rates for 80-84, 85-89, 90-94, 95-99, 100-104, and 105-110.",
        "",
        "## Lower And Upper Bounds",
        "",
        f"Lower bound: {MHAS_LOWER_COUNT}/{MHAS_LOWER_DENOMINATOR} = {100.0 * LOWER_RATE:.2f}%. This is treated here as an MHAS-derived/user-supplied lower anchor. The saved MHAS documentation verifies the cohort and cognitive-status machinery, but the 54/334 count has not yet been reproduced from the MHAS microdata in this workspace.",
        "",
        "Upper bound: 68.0%, from the broad HRS-HCAP normal-cognition anchor among U.S. adults 65+ (10% dementia and 22% MCI). This remains optimistic for 80+.",
        "",
        "## Dementia-Free Context",
        "",
        "Cao/GBD dementia-free values remain upper-bound context only; dementia-free is looser than mental vitality.",
        "",
        simple.markdown_table(
            bucket_rows,
            [
                ("requested_age_bucket", "Requested bucket", None),
                ("source_age_bucket", "Source bucket", None),
                ("dementia_free_upper_bound_estimate_pct", "Dementia-free %", 1),
                ("dementia_free_upper_bound_low95_pct", "Low 95 %", 1),
                ("dementia_free_upper_bound_high95_pct", "High 95 %", 1),
                ("note", "Note", None),
            ],
        ),
        "",
        "## Simulation Rate Grid",
        "",
        simple.markdown_table(
            rate_rows,
            [
                ("rate_key", "Rate key", None),
                ("mental_vitality_rate_pct", "Rate %", 2),
                ("basis", "Basis", None),
            ],
        ),
        "",
        "## Key Results",
        "",
        "Probability shown here is exact probability of Apollo-like longevity plus vitality: N80 >= 22, N90 >= 13, and vitality count >= 21.",
        "",
        simple.markdown_table(
            selected,
            [
                ("mortality_scenario", "Mortality scenario", None),
                ("mental_vitality_rate_pct", "Vitality %", 2),
                ("expected_reached80", "Expected N80", 2),
                ("expected_vitality_count", "Expected vital count", 2),
                ("p_n80_ge_22_n90_ge_13_and_vitality_ge_21", "P(long+vital)", 10),
            ],
        ),
        "",
        "## Graphs",
        "",
        "- `mhas16_probability_heatmap.svg`",
        "- `mhas16_expected_vital_count.svg`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    simple = load_simple_module()
    simple.OUT_DIR = OUT_DIR
    simple.LOWER_RATE = LOWER_RATE
    simple.UPPER_RATE = UPPER_RATE
    simple.RATE_GRID = RATE_GRID
    simple.rate_grid_rows = rate_grid_rows

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bucket_rows = simple.load_gbd_dementia_free_context()
    rates = rate_grid_rows()
    summary_rows, dist_rows = simple.build_summary_rows(simple.load_run2_module())

    write_csv(OUT_DIR / "mhas16_age_bucket_context.csv", bucket_rows)
    write_csv(OUT_DIR / "mhas16_rate_grid_assumptions.csv", rates)
    write_csv(OUT_DIR / "mhas16_rate_grid_summary.csv", summary_rows)
    write_csv(OUT_DIR / "mhas16_vitality_count_distribution.csv", dist_rows)
    simple.write_probability_heatmap(OUT_DIR / "mhas16_probability_heatmap.svg", summary_rows)
    simple.write_expected_count_chart(OUT_DIR / "mhas16_expected_vital_count.svg", summary_rows)
    build_report(simple, OUT_DIR / "mhas16_rate_grid_report.md", bucket_rows, rates, summary_rows)
    print(f"Wrote MHAS 16% 80+ vitality grid outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
