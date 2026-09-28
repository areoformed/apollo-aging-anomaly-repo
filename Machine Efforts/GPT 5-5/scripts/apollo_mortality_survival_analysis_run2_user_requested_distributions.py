#!/usr/bin/env python3
"""
User-requested run-level distributions with censored Apollo markers.

Outputs are intentionally separate:

    analysis_outputs/group29_sensitivity_run2_2026-06-04/
      user_requested_run_distributions_censored/

Graphs:
- y-axis = number of simulated 29-person groups; x-axis = age statistic.
- y-axis = number of simulated 29-person groups; x-axis = count with mental vitality.

Age statistic:
- 22nd-longest-lived member's age: age at which the group still has 22
  survivors. This maps to Apollo's observed N80 >= 22 longevity threshold.
- 13th-longest-lived member's age: age at which the group still has 13
  survivors. This maps to Apollo's observed N90 >= 13 threshold.

Observed Apollo markers are right-censored/lower-bound markers because some
Apollo astronauts are still alive as of the analysis date.
"""

from __future__ import annotations

import csv
import html
import importlib.util
import math
import random
import statistics
import sys
import time
from bisect import bisect_left
from collections import Counter, defaultdict
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
RUN2_SCRIPT = WORKSPACE_ROOT / "scripts" / "apollo_mortality_survival_analysis_run2.py"
OUT_DIR = (
    WORKSPACE_ROOT
    / "analysis_outputs"
    / "group29_sensitivity_run2_2026-06-04"
    / "user_requested_run_distributions_censored"
)

ITERATIONS = 1_000_000
SEED = 15170507
GROUP_N = 29
MHAS_LOWER_RATE = 54 / 334
UPPER_RATE = 0.68
VITALITY_RATES = [
    ("mhas_lower_16_17pct", MHAS_LOWER_RATE),
    ("interior_low_33_45pct", MHAS_LOWER_RATE + (UPPER_RATE - MHAS_LOWER_RATE) / 3.0),
    ("interior_high_50_72pct", MHAS_LOWER_RATE + 2.0 * (UPPER_RATE - MHAS_LOWER_RATE) / 3.0),
    ("hcap_upper_68pct", UPPER_RATE),
]


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


def esc(value: object) -> str:
    return html.escape(str(value))


def fmt(value: object, digits: int = 2) -> str:
    if isinstance(value, float):
        if value != 0 and abs(value) < 0.000001:
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
                cells.append(fmt(value, 2 if digits is None else digits))
            else:
                cells.append(str(value))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + body)


def binom_cdf(n: int, p: float) -> list[float]:
    probs = [math.comb(n, k) * (p**k) * ((1.0 - p) ** (n - k)) for k in range(n + 1)]
    cdf = []
    running = 0.0
    for prob in probs:
        running += prob
        cdf.append(running)
    cdf[-1] = 1.0
    return cdf


def sample_from_cdf(cdf: list[float], rng: random.Random) -> int:
    idx = bisect_left(cdf, rng.random())
    if idx >= len(cdf):
        return len(cdf) - 1
    return idx


class ScaledLifeSampler:
    def __init__(self, life, hazard_scale: float):
        self.death_ages: list[int] = []
        weights: list[float] = []
        for age in life.ages:
            if age < 30:
                continue
            survival_now = life.survival_from_30(age) ** hazard_scale
            if age >= life.max_age:
                survival_next = 0.0
            else:
                survival_next = life.survival_from_30(age + 1) ** hazard_scale
            weight = max(0.0, survival_now - survival_next)
            if weight > 0:
                self.death_ages.append(age)
                weights.append(weight)
        total = sum(weights)
        if total <= 0:
            raise ValueError("No usable death-age weights")
        cumulative = []
        running = 0.0
        for weight in weights:
            running += weight / total
            cumulative.append(running)
        cumulative[-1] = 1.0
        self.cumulative = cumulative

    def sample(self, rng: random.Random) -> float:
        idx = bisect_left(self.cumulative, rng.random())
        if idx >= len(self.death_ages):
            idx = len(self.death_ages) - 1
        return self.death_ages[idx] + rng.random()


def binned_quantile(hist: Counter[int], q: float) -> int:
    total = sum(hist.values())
    target = q * total
    running = 0
    for bin_value in sorted(hist):
        running += hist[bin_value]
        if running >= target:
            return bin_value
    return max(hist)


def binned_mean(hist: Counter[int]) -> float:
    total = sum(hist.values())
    if total <= 0:
        return 0.0
    return sum((bin_value + 0.5) * count for bin_value, count in hist.items()) / total


def observed_apollo_markers(run2, run1) -> list[dict[str, object]]:
    people = [person for person in run1.load_people() if person.primary == "apollo"]
    rows = []
    sorted_people = sorted(people, key=lambda person: person.endpoint_age, reverse=True)
    for order_key, rank, label in [
        ("age_22nd_longest_lived", 22, "22nd-longest-lived Apollo member"),
        ("age_13th_longest_lived", 13, "13th-longest-lived Apollo member"),
    ]:
        top_k = sorted_people[:rank]
        marker_person = sorted_people[rank - 1]
        rows.append(
            {
                "order_statistic": order_key,
                "rank_from_oldest": rank,
                "label": label,
                "observed_age_or_censor_age": marker_person.endpoint_age,
                "marker_person": marker_person.name,
                "right_censored_lower_bound": any(not person.deceased for person in top_k),
                "living_people_in_top_rank_set": sum(1 for person in top_k if not person.deceased),
                "note": (
                    "Right-censored lower-bound marker because one or more living Apollo "
                    "members are in the rank set."
                ),
            }
        )
    rows.append(
        {
            "order_statistic": "mental_vitality_count",
            "rank_from_oldest": "",
            "label": "Apollo Space Grandpa count",
            "observed_age_or_censor_age": "",
            "marker_person": "",
            "right_censored_lower_bound": False,
            "living_people_in_top_rank_set": "",
            "note": "Observed Space Grandpa positives among all 29 Apollo 7-17 astronauts.",
            "observed_count": run2.load_apollo_observed(run1)["space_grandpa_all"],
        }
    )
    return rows


def simulate_distributions(run2, iterations: int, seed: int):
    run1 = run2.load_run1_module()
    life = run1.LifeTable.load(run1.SSA_FILE)
    apollo_smr = run2.load_apollo_smr()
    rng = random.Random(seed)
    binom_tables = {
        rate_key: [binom_cdf(n, rate) for n in range(GROUP_N + 1)]
        for rate_key, rate in VITALITY_RATES
    }

    age22_hists: dict[str, Counter[int]] = {}
    age13_hists: dict[str, Counter[int]] = {}
    vitality_hists: dict[tuple[str, str], Counter[int]] = {}
    summary_rows: list[dict[str, object]] = []

    for scenario_index, scenario in enumerate(run2.mortality_scenarios(apollo_smr)):
        sampler = ScaledLifeSampler(life, scenario.hazard_scale)
        age22_hist: Counter[int] = Counter()
        age13_hist: Counter[int] = Counter()
        scenario_vitality_hists = {
            rate_key: Counter()
            for rate_key, _rate in VITALITY_RATES
        }

        for _ in range(iterations):
            ages = [sampler.sample(rng) for _person in range(GROUP_N)]
            ages.sort(reverse=True)
            age22 = ages[21]
            age13 = ages[12]
            age22_hist[int(math.floor(age22))] += 1
            age13_hist[int(math.floor(age13))] += 1
            n80 = sum(1 for age in ages if age >= 80.0)
            for rate_key, _rate in VITALITY_RATES:
                count = sample_from_cdf(binom_tables[rate_key][n80], rng)
                scenario_vitality_hists[rate_key][count] += 1

        age22_hists[scenario.key] = age22_hist
        age13_hists[scenario.key] = age13_hist
        for rate_key, hist in scenario_vitality_hists.items():
            vitality_hists[(scenario.key, rate_key)] = hist

        summary_rows.append(
            {
                "mortality_scenario_key": scenario.key,
                "mortality_scenario": scenario.label,
                "hazard_scale": scenario.hazard_scale,
                "iterations": iterations,
                "seed": seed,
                "age22_mean_bin_midpoint": binned_mean(age22_hist),
                "age22_p02_5_bin": binned_quantile(age22_hist, 0.025),
                "age22_p50_bin": binned_quantile(age22_hist, 0.5),
                "age22_p97_5_bin": binned_quantile(age22_hist, 0.975),
                "age13_mean_bin_midpoint": binned_mean(age13_hist),
                "age13_p02_5_bin": binned_quantile(age13_hist, 0.025),
                "age13_p50_bin": binned_quantile(age13_hist, 0.5),
                "age13_p97_5_bin": binned_quantile(age13_hist, 0.975),
            }
        )
        for rate_key, rate in VITALITY_RATES:
            hist = scenario_vitality_hists[rate_key]
            total = sum(hist.values())
            summary_rows.append(
                {
                    "mortality_scenario_key": scenario.key,
                    "mortality_scenario": scenario.label,
                    "hazard_scale": scenario.hazard_scale,
                    "iterations": iterations,
                    "seed": seed,
                    "vitality_rate_key": rate_key,
                    "vitality_rate": rate,
                    "vitality_rate_pct": 100.0 * rate,
                    "vitality_count_mean": sum(k * v for k, v in hist.items()) / total,
                    "vitality_count_p02_5": binned_quantile(hist, 0.025),
                    "vitality_count_p50": binned_quantile(hist, 0.5),
                    "vitality_count_p97_5": binned_quantile(hist, 0.975),
                    "p_vitality_count_ge_21": sum(v for k, v in hist.items() if k >= 21) / total,
                }
            )

    return run1, age22_hists, age13_hists, vitality_hists, summary_rows


def histogram_rows_age(hists: dict[str, Counter[int]], scenario_labels: dict[str, str], statistic: str) -> list[dict[str, object]]:
    rows = []
    for scenario_key, hist in hists.items():
        total = sum(hist.values())
        for age_bin in range(min(hist), max(hist) + 1):
            count = hist.get(age_bin, 0)
            rows.append(
                {
                    "mortality_scenario_key": scenario_key,
                    "mortality_scenario": scenario_labels[scenario_key],
                    "age_statistic": statistic,
                    "age_bin_floor": age_bin,
                    "group_count": count,
                    "group_probability": count / total,
                }
            )
    return rows


def histogram_rows_vitality(hists: dict[tuple[str, str], Counter[int]], scenario_labels: dict[str, str]) -> list[dict[str, object]]:
    rows = []
    rate_lookup = dict(VITALITY_RATES)
    for (scenario_key, rate_key), hist in hists.items():
        total = sum(hist.values())
        for count_value in range(0, GROUP_N + 1):
            count = hist.get(count_value, 0)
            rows.append(
                {
                    "mortality_scenario_key": scenario_key,
                    "mortality_scenario": scenario_labels[scenario_key],
                    "vitality_rate_key": rate_key,
                    "vitality_rate": rate_lookup[rate_key],
                    "vitality_rate_pct": 100.0 * rate_lookup[rate_key],
                    "vitality_count": count_value,
                    "group_count": count,
                    "group_probability": count / total,
                }
            )
    return rows


def draw_age_histogram(
    path: Path,
    hists: dict[str, Counter[int]],
    scenario_labels: dict[str, str],
    marker_age: float,
    marker_label: str,
    title: str,
    subtitle: str,
) -> None:
    scenario_order = list(hists.keys())
    min_age = min(min(hist) for hist in hists.values())
    max_age = max(max(hist) for hist in hists.values())
    max_age = max(max_age, int(math.ceil(marker_age)))
    min_age = min(min_age, int(math.floor(marker_age)))
    width = 1180
    panel_h = 132
    left = 86
    right = 32
    top = 82
    bottom = 58
    plot_w = width - left - right
    height = top + panel_h * len(scenario_order) + bottom
    bar_w = plot_w / (max_age - min_age + 1)

    def xmap(age_value: float) -> float:
        return left + (age_value - min_age) / (max_age - min_age + 1) * plot_w

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">{esc(title)}</text>',
        f'<text x="{left}" y="58" font-family="Arial, sans-serif" font-size="13" fill="#52616b">{esc(subtitle)}</text>',
    ]
    marker_x = xmap(marker_age)
    for idx, scenario_key in enumerate(scenario_order):
        hist = hists[scenario_key]
        y0 = top + idx * panel_h
        chart_top = y0 + 18
        chart_h = panel_h - 38
        max_count = max(hist.values())
        parts.append(f'<text x="{left - 10}" y="{chart_top + 14}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#263238">{esc(scenario_labels[scenario_key])}</text>')
        parts.append(f'<line x1="{left}" y1="{chart_top + chart_h}" x2="{left + plot_w}" y2="{chart_top + chart_h}" stroke="#d8e0e5" stroke-width="1"/>')
        for age_bin in range(min_age, max_age + 1):
            count = hist.get(age_bin, 0)
            if count <= 0:
                continue
            bh = chart_h * count / max_count
            x = xmap(age_bin)
            y = chart_top + chart_h - bh
            parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(1.0, bar_w - 1):.2f}" height="{bh:.2f}" fill="#4f7cac" opacity="0.82"/>')
        parts.append(f'<line x1="{marker_x:.1f}" y1="{chart_top}" x2="{marker_x:.1f}" y2="{chart_top + chart_h}" stroke="#111111" stroke-width="2" stroke-dasharray="6 5"/>')
        if idx == 0:
            parts.append(f'<text x="{marker_x + 8:.1f}" y="{chart_top + 13}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#111111">{esc(marker_label)}</text>')
    for age in range((min_age // 5) * 5, max_age + 1, 5):
        if age < min_age:
            continue
        xx = xmap(age)
        parts.append(f'<text x="{xx:.1f}" y="{height - 24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#52616b">{age}</text>')
    parts.append(f'<text x="{left + plot_w/2}" y="{height - 6}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#263238">Age, one-year bins; no artificial upper-age cap</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def draw_vitality_histogram(
    path: Path,
    hists: dict[tuple[str, str], Counter[int]],
    scenario_labels: dict[str, str],
    observed_count: int,
) -> None:
    scenario_order = []
    for scenario_key, _rate_key in hists:
        if scenario_key not in scenario_order:
            scenario_order.append(scenario_key)
    rate_order = [rate_key for rate_key, _rate in VITALITY_RATES]
    rate_lookup = dict(VITALITY_RATES)
    width = 1320
    panel_w = 270
    panel_h = 150
    left = 156
    top = 92
    right = 34
    bottom = 62
    height = top + panel_h * len(scenario_order) + bottom

    def xmap(panel_x: float, count_value: float) -> float:
        return panel_x + 26 + count_value / GROUP_N * (panel_w - 48)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="156" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">Mental-vitality count distribution</text>',
        '<text x="156" y="58" font-family="Arial, sans-serif" font-size="13" fill="#52616b">Each panel is simulated 29-person groups. X-axis is count with mental vitality; dashed line is Apollo observed count 21.</text>',
    ]
    for col, rate_key in enumerate(rate_order):
        x = left + col * panel_w + panel_w / 2
        parts.append(f'<text x="{x:.1f}" y="{top - 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#263238">{100.0 * rate_lookup[rate_key]:.2f}%</text>')
    for row_idx, scenario_key in enumerate(scenario_order):
        y = top + row_idx * panel_h
        parts.append(f'<text x="{left - 12}" y="{y + 24}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#263238">{esc(scenario_labels[scenario_key])}</text>')
        for col, rate_key in enumerate(rate_order):
            hist = hists[(scenario_key, rate_key)]
            panel_x = left + col * panel_w
            chart_top = y + 16
            chart_h = panel_h - 46
            max_count = max(hist.values())
            base_y = chart_top + chart_h
            parts.append(f'<line x1="{panel_x + 24}" y1="{base_y}" x2="{panel_x + panel_w - 20}" y2="{base_y}" stroke="#d8e0e5" stroke-width="1"/>')
            for count_value in range(0, GROUP_N + 1):
                group_count = hist.get(count_value, 0)
                if group_count <= 0:
                    continue
                bar_w = (panel_w - 54) / (GROUP_N + 1)
                bh = chart_h * group_count / max_count
                x = xmap(panel_x, count_value)
                parts.append(f'<rect x="{x:.2f}" y="{base_y - bh:.2f}" width="{max(1.0, bar_w - 1):.2f}" height="{bh:.2f}" fill="#7b5ea7" opacity="0.82"/>')
            marker_x = xmap(panel_x, observed_count)
            parts.append(f'<line x1="{marker_x:.1f}" y1="{chart_top}" x2="{marker_x:.1f}" y2="{base_y}" stroke="#111111" stroke-width="1.8" stroke-dasharray="5 4"/>')
            if row_idx == 0 and col == len(rate_order) - 1:
                parts.append(f'<text x="{marker_x - 6:.1f}" y="{chart_top + 12}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#111111">Apollo 21</text>')
            if row_idx == len(scenario_order) - 1:
                for tick in (0, 10, 20, 29):
                    tx = xmap(panel_x, tick)
                    parts.append(f'<text x="{tx:.1f}" y="{base_y + 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#52616b">{tick}</text>')
    parts.append(f'<text x="{left + (panel_w * len(rate_order))/2}" y="{height - 12}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#263238">Number of people with mental vitality in a 29-person group</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def build_report(
    path: Path,
    iterations: int,
    elapsed: float,
    markers: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
) -> None:
    age_rows = [row for row in summary_rows if "age22_mean_bin_midpoint" in row]
    vitality_rows = [
        row
        for row in summary_rows
        if row.get("vitality_rate_key") in {"mhas_lower_16_17pct", "hcap_upper_68pct"}
    ]
    lines = [
        "# User-Requested Run-Level Distributions",
        "",
        f"Iterations per mortality scenario: {iterations:,}",
        f"Runtime: {elapsed:.1f} seconds",
        "",
        "## Censoring Choice",
        "",
        "The simulated cohorts draw full lifetimes from the SSA 1930 male life table under each hazard-scale scenario. I did not impose a plotting cap such as age 100. The observed Apollo reference ages are shown as right-censored lower-bound markers where living Apollo astronauts are part of the relevant rank set.",
        "",
        "The SSA table itself ends when its survivor count reaches zero, so this is uncapped within the available life table rather than projected beyond the table.",
        "",
        "## Age Statistics",
        "",
        "- `age_22nd_longest_lived`: age of the 22nd-longest-lived person in a simulated 29-person group. This is the age through which the group still has 22 survivors.",
        "- `age_13th_longest_lived`: age of the 13th-longest-lived person in a simulated 29-person group. This is the age through which the group still has 13 survivors.",
        "",
        markdown_table(
            markers,
            [
                ("order_statistic", "Observed marker", None),
                ("observed_age_or_censor_age", "Age/count", 2),
                ("marker_person", "Rank person", None),
                ("right_censored_lower_bound", "Censored?", None),
                ("living_people_in_top_rank_set", "Living in rank set", None),
            ],
        ),
        "",
        markdown_table(
            age_rows,
            [
                ("mortality_scenario", "Scenario", None),
                ("age22_p02_5_bin", "Age22 p2.5", None),
                ("age22_p50_bin", "Age22 p50", None),
                ("age22_p97_5_bin", "Age22 p97.5", None),
                ("age13_p02_5_bin", "Age13 p2.5", None),
                ("age13_p50_bin", "Age13 p50", None),
                ("age13_p97_5_bin", "Age13 p97.5", None),
            ],
        ),
        "",
        "## Vitality Count Distributions",
        "",
        markdown_table(
            vitality_rows,
            [
                ("mortality_scenario", "Scenario", None),
                ("vitality_rate_pct", "Rate %", 2),
                ("vitality_count_mean", "Mean count", 2),
                ("vitality_count_p02_5", "p2.5", None),
                ("vitality_count_p50", "p50", None),
                ("vitality_count_p97_5", "p97.5", None),
                ("p_vitality_count_ge_21", "P(count >= 21)", 8),
            ],
        ),
        "",
        "## Graphs",
        "",
        "- `age_22nd_longest_lived_distribution.svg`",
        "- `age_13th_longest_lived_distribution.svg`",
        "- `mental_vitality_count_distribution.svg`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run2 = load_run2_module()
    run1, age22_hists, age13_hists, vitality_hists, summary_rows = simulate_distributions(
        run2,
        ITERATIONS,
        SEED,
    )
    elapsed = time.time() - start
    apollo_markers = observed_apollo_markers(run2, run1)
    apollo_age22 = next(row for row in apollo_markers if row["order_statistic"] == "age_22nd_longest_lived")
    apollo_age13 = next(row for row in apollo_markers if row["order_statistic"] == "age_13th_longest_lived")
    observed_vitality = next(row for row in apollo_markers if row["order_statistic"] == "mental_vitality_count")
    scenario_labels = {
        scenario.key: scenario.label
        for scenario in run2.mortality_scenarios(run2.load_apollo_smr())
    }

    write_csv(OUT_DIR / "observed_apollo_censored_markers.csv", apollo_markers)
    write_csv(OUT_DIR / "run_distribution_summary.csv", summary_rows)
    write_csv(
        OUT_DIR / "age_22nd_longest_lived_histogram.csv",
        histogram_rows_age(age22_hists, scenario_labels, "age_22nd_longest_lived"),
    )
    write_csv(
        OUT_DIR / "age_13th_longest_lived_histogram.csv",
        histogram_rows_age(age13_hists, scenario_labels, "age_13th_longest_lived"),
    )
    write_csv(
        OUT_DIR / "mental_vitality_count_histogram.csv",
        histogram_rows_vitality(vitality_hists, scenario_labels),
    )

    draw_age_histogram(
        OUT_DIR / "age_22nd_longest_lived_distribution.svg",
        age22_hists,
        scenario_labels,
        float(apollo_age22["observed_age_or_censor_age"]),
        f"Apollo >= {float(apollo_age22['observed_age_or_censor_age']):.1f}",
        "Distribution of the 22nd-longest-lived member's age",
        "Y-axis is number of simulated 29-person groups. Apollo marker is censored/lower-bound when living members are in the rank set.",
    )
    draw_age_histogram(
        OUT_DIR / "age_13th_longest_lived_distribution.svg",
        age13_hists,
        scenario_labels,
        float(apollo_age13["observed_age_or_censor_age"]),
        f"Apollo >= {float(apollo_age13['observed_age_or_censor_age']):.1f}",
        "Distribution of the 13th-longest-lived member's age",
        "Y-axis is number of simulated 29-person groups. Apollo marker is censored/lower-bound when living members are in the rank set.",
    )
    draw_vitality_histogram(
        OUT_DIR / "mental_vitality_count_distribution.svg",
        vitality_hists,
        scenario_labels,
        int(observed_vitality["observed_count"]),
    )
    build_report(
        OUT_DIR / "user_requested_run_distribution_report.md",
        ITERATIONS,
        elapsed,
        apollo_markers,
        summary_rows,
    )
    print(f"Wrote user-requested run distributions to {OUT_DIR}")
    print(f"Iterations per mortality scenario: {ITERATIONS:,}")
    print(f"Elapsed seconds: {elapsed:.1f}")


if __name__ == "__main__":
    main()
