#!/usr/bin/env python3
"""
Run2 simple 80+ mental-vitality rate grid.

This is a deliberately simpler follow-up to run2:
- Do not apply different mental-vitality rates by age threshold.
- Use one blanket 80+ rate in the Monte Carlo/exact mixture.
- Evaluate four rates: lower bound, upper bound, and two evenly spaced
  intermediate values.

The age-bucket dementia-free values are retained only as context, because
"dementia-free" is not the same construct as mental vitality.
"""

from __future__ import annotations

import csv
import html
import importlib.util
import math
import sys
from collections import defaultdict
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
RUN2_SCRIPT = WORKSPACE_ROOT / "scripts" / "apollo_mortality_survival_analysis_run2.py"
OUT_DIR = (
    WORKSPACE_ROOT
    / "analysis_outputs"
    / "group29_sensitivity_run2_2026-06-04"
    / "simple_80plus_vitality_grid"
)
RESEARCH_DIR = WORKSPACE_ROOT / "source_research" / "mental_vitality_medical_data_2026-06-04"
GBD_FORECAST_CSV = RESEARCH_DIR / "extracted" / "pmc11336039_cao2024_supplement_forecast_tables.csv"

LOWER_RATE = 0.35
UPPER_RATE = 0.68
RATE_GRID = [LOWER_RATE, 0.46, 0.57, UPPER_RATE]


def load_run2_module():
    spec = importlib.util.spec_from_file_location("apollo_run2", RUN2_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load run2 script: {RUN2_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def fmt(value: object, digits: int = 3) -> str:
    if isinstance(value, float):
        if abs(value) < 0.000001 and value != 0:
            return f"{value:.3e}"
        return f"{value:.{digits}f}"
    return str(value)


def markdown_table(rows: list[dict[str, object]], columns: list[tuple[str, str, int | None]]) -> str:
    header = "| " + " | ".join(label for _, label, _ in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        cells = []
        for key, _, digits in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                cells.append(fmt(value, 3 if digits is None else digits))
            else:
                cells.append(str(value))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + body)


def esc(value: object) -> str:
    return html.escape(str(value))


def load_gbd_dementia_free_context() -> list[dict[str, object]]:
    """Return requested bucket context from Cao/GBD.

    The source has 80-84, 85-89, 90-94, and 95+ only. The requested
    95-99/100-104/105-110 buckets are therefore marked as sharing the source's
    95+ aggregate rather than falsely split.
    """
    source_rows: dict[str, dict[str, float]] = {}
    wanted = {"80-84 years", "85-89 years", "90-94 years", "95+ years"}
    with GBD_FORECAST_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["metric"] != "prevalence_rate_per_100k":
                continue
            if row["sex"] != "Male" or row["year"] != "2020":
                continue
            if row["age_group"] not in wanted:
                continue
            dementia_rate = float(row["estimate"]) / 100000.0
            dementia_low = float(row["lower_95ci"]) / 100000.0
            dementia_high = float(row["upper_95ci"]) / 100000.0
            source_rows[row["age_group"]] = {
                "dementia_free_est": 1.0 - dementia_rate,
                "dementia_free_low": 1.0 - dementia_high,
                "dementia_free_high": 1.0 - dementia_low,
            }

    requested = [
        ("80-84", "80-84 years", "Source age band exists."),
        ("85-89", "85-89 years", "Source age band exists."),
        ("90-94", "90-94 years", "Source age band exists."),
        ("95-99", "95+ years", "Source aggregates 95+; not separately estimable here."),
        ("100-104", "95+ years", "Source aggregates 95+; not separately estimable here."),
        ("105-110", "95+ years", "Source aggregates 95+; not separately estimable here."),
    ]

    rows: list[dict[str, object]] = []
    for requested_bucket, source_bucket, note in requested:
        values = source_rows[source_bucket]
        rows.append(
            {
                "requested_age_bucket": requested_bucket,
                "source_age_bucket": source_bucket,
                "dementia_free_upper_bound_estimate_pct": 100.0 * values["dementia_free_est"],
                "dementia_free_upper_bound_low95_pct": 100.0 * values["dementia_free_low"],
                "dementia_free_upper_bound_high95_pct": 100.0 * values["dementia_free_high"],
                "source": "Cao et al. 2024 supplement eTable 4, U.S. male 2020 GBD forecast",
                "note": note,
            }
        )
    return rows


def rate_grid_rows() -> list[dict[str, object]]:
    return [
        {
            "rate_key": "lower_strict_public_participation_sensitivity",
            "mental_vitality_rate": LOWER_RATE,
            "mental_vitality_rate_pct": 100.0 * LOWER_RATE,
            "basis": "Deliberately conservative sensitivity for public/participatory vitality; not a direct medical prevalence estimate.",
        },
        {
            "rate_key": "interior_low",
            "mental_vitality_rate": RATE_GRID[1],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[1],
            "basis": "Evenly spaced interior point between lower and upper simple bounds.",
        },
        {
            "rate_key": "interior_high",
            "mental_vitality_rate": RATE_GRID[2],
            "mental_vitality_rate_pct": 100.0 * RATE_GRID[2],
            "basis": "Evenly spaced interior point between lower and upper simple bounds.",
        },
        {
            "rate_key": "upper_hcap_normal_cognition_overall",
            "mental_vitality_rate": UPPER_RATE,
            "mental_vitality_rate_pct": 100.0 * UPPER_RATE,
            "basis": "HRS-HCAP broad normal-cognition anchor from 65+ adults: 1 - dementia 10 pct - MCI 22 pct. Optimistic for 80+.",
        },
    ]


def dist_from_exact_n80(run2, exact_n80_dist: dict[int, float], rate: float) -> dict[int, float]:
    return run2.vitality_distribution(exact_n80_dist, rate)


def build_summary_rows(run2) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    run1 = run2.load_run1_module()
    life = run1.LifeTable.load(run1.SSA_FILE)
    observed = run2.load_apollo_observed(run1)
    apollo_smr = run2.load_apollo_smr()

    summary_rows: list[dict[str, object]] = []
    dist_rows: list[dict[str, object]] = []

    for mortality in run2.mortality_scenarios(apollo_smr):
        p80, p90, p95 = run2.scenario_survival_probabilities(life, mortality.hazard_scale)
        exact_joint = run2.exact_joint_distribution(run2.GROUP_N, p80, p90, p95)
        exact80 = run2.marginal_from_joint(exact_joint, 0)
        for rate in RATE_GRID:
            vital_dist = dist_from_exact_n80(run2, exact80, rate)
            rate_key = next(row["rate_key"] for row in rate_grid_rows() if row["mental_vitality_rate"] == rate)
            row = {
                "mortality_scenario_key": mortality.key,
                "mortality_scenario": mortality.label,
                "hazard_scale": mortality.hazard_scale,
                "mental_vitality_rate": rate,
                "mental_vitality_rate_pct": 100.0 * rate,
                "rate_key": rate_key,
                "observed_n": observed["n"],
                "observed_reached80": observed["reached80"],
                "observed_reached90": observed["reached90"],
                "observed_reached95": observed["reached95"],
                "observed_vitality_count": observed["space_grandpa_all"],
                "p_survive80": p80,
                "expected_reached80": run2.GROUP_N * p80,
                "expected_vitality_count": run2.dist_mean(vital_dist),
                "vitality_count_p02_5": run2.dist_quantile(vital_dist, 0.025),
                "vitality_count_p50": run2.dist_quantile(vital_dist, 0.50),
                "vitality_count_p97_5": run2.dist_quantile(vital_dist, 0.975),
                "p_vitality_ge_21": run2.dist_tail(vital_dist, int(observed["space_grandpa_all"])),
                "p_n80_ge_22_and_vitality_ge_21": run2.joint_vitality_probability_exact(
                    exact_joint,
                    rate,
                    int(observed["space_grandpa_all"]),
                    obs80=int(observed["reached80"]),
                ),
                "p_n80_ge_22_n90_ge_13_and_vitality_ge_21": run2.joint_vitality_probability_exact(
                    exact_joint,
                    rate,
                    int(observed["space_grandpa_all"]),
                    obs80=int(observed["reached80"]),
                    obs90=int(observed["reached90"]),
                ),
                "p_n80_ge_22_n90_ge_13_n95_ge_3_and_vitality_ge_21": run2.joint_vitality_probability_exact(
                    exact_joint,
                    rate,
                    int(observed["space_grandpa_all"]),
                    obs80=int(observed["reached80"]),
                    obs90=int(observed["reached90"]),
                    obs95=int(observed["reached95"]),
                ),
            }
            summary_rows.append(row)
            for count in range(0, run2.GROUP_N + 1):
                dist_rows.append(
                    {
                        "mortality_scenario_key": mortality.key,
                        "mortality_scenario": mortality.label,
                        "mental_vitality_rate": rate,
                        "vitality_count": count,
                        "probability": vital_dist.get(count, 0.0),
                    }
                )
    return summary_rows, dist_rows


def probability_color(value: float, min_log: float, max_log: float) -> str:
    if value <= 0:
        t = 0.0
    else:
        t = (math.log10(value) - min_log) / (max_log - min_log)
    t = max(0.0, min(1.0, t))
    # Blue-gray to red-orange.
    r = int(235 * t + 50 * (1 - t))
    g = int(84 * t + 96 * (1 - t))
    b = int(60 * t + 140 * (1 - t))
    return f"#{r:02x}{g:02x}{b:02x}"


def write_probability_heatmap(path: Path, rows: list[dict[str, object]]) -> None:
    mortality_order = []
    for row in rows:
        if row["mortality_scenario"] not in mortality_order:
            mortality_order.append(row["mortality_scenario"])
    rate_order = RATE_GRID
    values = {
        (row["mortality_scenario"], row["mental_vitality_rate"]): float(
            row["p_n80_ge_22_n90_ge_13_and_vitality_ge_21"]
        )
        for row in rows
    }
    positive = [v for v in values.values() if v > 0]
    min_log = math.log10(min(positive))
    max_log = math.log10(max(positive))

    cell_w = 170
    cell_h = 56
    left = 260
    top = 92
    width = left + cell_w * len(rate_order) + 40
    height = top + cell_h * len(mortality_order) + 74

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="28" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">Apollo-like longevity plus vitality probability</text>',
        '<text x="28" y="58" font-family="Arial, sans-serif" font-size="13" fill="#52616b">Exact probability of N80 >= 22, N90 >= 13, and vitality count >= 21. Color scale is log10 probability.</text>',
    ]
    for j, rate in enumerate(rate_order):
        x = left + j * cell_w + cell_w / 2
        parts.append(
            f'<text x="{x:.1f}" y="{top - 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#263238">{rate*100:.0f}%</text>'
        )
    for i, scenario in enumerate(mortality_order):
        y = top + i * cell_h
        parts.append(
            f'<text x="{left - 14}" y="{y + 34}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#263238">{esc(scenario)}</text>'
        )
        for j, rate in enumerate(rate_order):
            x = left + j * cell_w
            value = values[(scenario, rate)]
            color = probability_color(value, min_log, max_log)
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 3}" height="{cell_h - 3}" fill="{color}"/>')
            parts.append(
                f'<text x="{x + cell_w / 2:.1f}" y="{y + 34}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#ffffff">{esc(fmt(value, 6))}</text>'
            )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_expected_count_chart(path: Path, rows: list[dict[str, object]]) -> None:
    mortality_order = []
    for row in rows:
        if row["mortality_scenario"] not in mortality_order:
            mortality_order.append(row["mortality_scenario"])
    colors = ["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#d62728"]
    width = 980
    height = 620
    left = 76
    right = 270
    top = 74
    bottom = 72
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_min = min(RATE_GRID) * 100.0
    x_max = max(RATE_GRID) * 100.0
    y_max = 22.5

    def xmap(rate_pct: float) -> float:
        return left + (rate_pct - x_min) / (x_max - x_min) * plot_w

    def ymap(value: float) -> float:
        return top + (y_max - value) / y_max * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="76" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">Expected vital count in a 29-person group</text>',
        '<text x="76" y="58" font-family="Arial, sans-serif" font-size="13" fill="#52616b">Blanket 80+ mental-vitality rate applied to age-80 survivors. Apollo target is 21.</text>',
    ]
    for i in range(0, 6):
        y_val = i * 4
        yy = ymap(y_val)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left + plot_w}" y2="{yy:.1f}" stroke="#e5ebef" stroke-width="1"/>')
        parts.append(f'<text x="{left - 10}" y="{yy + 4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#52616b">{y_val}</text>')
    for rate in RATE_GRID:
        xx = xmap(rate * 100.0)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top + plot_h}" stroke="#f1f4f6" stroke-width="1"/>')
        parts.append(f'<text x="{xx:.1f}" y="{top + plot_h + 26}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#52616b">{rate*100:.0f}%</text>')
    target_y = ymap(21.0)
    parts.append(f'<line x1="{left}" y1="{target_y:.1f}" x2="{left + plot_w}" y2="{target_y:.1f}" stroke="#111111" stroke-width="2" stroke-dasharray="7 5"/>')
    parts.append(f'<text x="{left + plot_w - 4}" y="{target_y - 8:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#111111">Apollo target 21</text>')

    for idx, scenario in enumerate(mortality_order):
        series = [
            row
            for row in rows
            if row["mortality_scenario"] == scenario
        ]
        series.sort(key=lambda r: float(r["mental_vitality_rate"]))
        points = " ".join(
            f"{xmap(float(row['mental_vitality_rate_pct'])):.1f},{ymap(float(row['expected_vitality_count'])):.1f}"
            for row in series
        )
        color = colors[idx % len(colors)]
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        for row in series:
            cx = xmap(float(row["mental_vitality_rate_pct"]))
            cy = ymap(float(row["expected_vitality_count"]))
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{color}"/>')
        legend_y = top + 16 + idx * 33
        legend_x = left + plot_w + 34
        parts.append(f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 28}" y2="{legend_y}" stroke="{color}" stroke-width="4"/>')
        parts.append(f'<text x="{legend_x + 38}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="12" fill="#263238">{esc(scenario)}</text>')

    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<text x="{left + plot_w/2}" y="{height - 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#263238">Blanket 80+ mental-vitality rate</text>')
    parts.append(f'<text x="23" y="{top + plot_h/2}" text-anchor="middle" transform="rotate(-90 23 {top + plot_h/2})" font-family="Arial, sans-serif" font-size="13" fill="#263238">Expected count</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def build_report(path: Path, bucket_rows: list[dict[str, object]], rate_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> None:
    selected = [
        row
        for row in summary_rows
        if row["mortality_scenario_key"] in {"ssa_general_age30", "healthy_30pct_lower_hazard", "apollo_smr_like_54pct_lower_hazard"}
    ]
    lines = [
        "# Simple 80+ Mental-Vitality Rate Grid",
        "",
        "## Simplification",
        "",
        "This run treats mental vitality as one blanket 80+ probability, rather than applying age-bucket rates. That avoids false precision: the archived sources do not support reliable 80-84, 85-89, 90-94, 95-99, 100-104, and 105-110 mental-vitality rates.",
        "",
        "## Source Context",
        "",
        "Cao/GBD gives dementia-free rates by age band. These are upper-bound context only, because a person can be dementia-free and still have MCI, functional limitation, or low public/participatory vitality.",
        "",
        markdown_table(
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
        "For the simple Monte Carlo/exact mixture, I used a broad blanket 80+ grid: 35%, 46%, 57%, and 68%. The upper value is the broad HRS-HCAP normal-cognition anchor for U.S. adults 65+ (68%), which is probably optimistic for 80+. The lower value is a conservative public/participatory-vitality sensitivity, not a direct medical prevalence estimate.",
        "",
        markdown_table(
            rate_rows,
            [
                ("rate_key", "Rate key", None),
                ("mental_vitality_rate_pct", "Rate %", 1),
                ("basis", "Basis", None),
            ],
        ),
        "",
        "## Key Results",
        "",
        "Probability shown here is exact probability of Apollo-like longevity plus vitality: N80 >= 22, N90 >= 13, and vitality count >= 21.",
        "",
        markdown_table(
            selected,
            [
                ("mortality_scenario", "Mortality scenario", None),
                ("mental_vitality_rate_pct", "Vitality %", 0),
                ("expected_reached80", "Expected N80", 2),
                ("expected_vitality_count", "Expected vital count", 2),
                ("p_n80_ge_22_n90_ge_13_and_vitality_ge_21", "P(long+vital)", 8),
            ],
        ),
        "",
        "## Graphs",
        "",
        "- `simple_80plus_probability_heatmap.svg`",
        "- `simple_80plus_expected_vital_count.svg`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run2 = load_run2_module()
    bucket_rows = load_gbd_dementia_free_context()
    rates = rate_grid_rows()
    summary_rows, dist_rows = build_summary_rows(run2)

    write_csv(OUT_DIR / "simple_80plus_age_bucket_context.csv", bucket_rows)
    write_csv(OUT_DIR / "simple_80plus_rate_grid_assumptions.csv", rates)
    write_csv(OUT_DIR / "simple_80plus_rate_grid_summary.csv", summary_rows)
    write_csv(OUT_DIR / "simple_80plus_vitality_count_distribution.csv", dist_rows)
    write_probability_heatmap(OUT_DIR / "simple_80plus_probability_heatmap.svg", summary_rows)
    write_expected_count_chart(OUT_DIR / "simple_80plus_expected_vital_count.svg", summary_rows)
    build_report(OUT_DIR / "simple_80plus_rate_grid_report.md", bucket_rows, rates, summary_rows)
    print(f"Wrote simple 80+ vitality grid outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
