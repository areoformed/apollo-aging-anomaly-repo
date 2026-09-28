#!/usr/bin/env python3
"""
Run 2: group-of-29 longevity and vitality sensitivity simulation.

This script intentionally leaves the original 2026-06-04 mortality/survival
analysis untouched. It reuses the run1 data loader and SSA life table, then
writes a new set of sub-outputs under:

    analysis_outputs/group29_sensitivity_run2_2026-06-04/

Question:
If 29 healthy U.S. males from the 1930 birth cohort are selected at age 30,
how often would the group display Apollo 7-17's observed level of:

1. Longevity: survivors to ages 80, 90, and 95.
2. Mental vitality: a range of possible population proxies among age-80
   survivors, compared with Apollo's Space Grandpa count.

Important boundary:
SSA supplies mortality only. The vitality rates here are sensitivity anchors
from clinical/survey/public-health sources; they are not direct equivalents of
the astronaut dataset's public-activity "Space Grandpa" construct.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
RUN1_SCRIPT = WORKSPACE_ROOT / "scripts" / "apollo_mortality_survival_analysis.py"
RUN1_OUT_DIR = WORKSPACE_ROOT / "analysis_outputs" / "mortality_survival_run1_2026-06-04"
OUT_DIR = WORKSPACE_ROOT / "analysis_outputs" / "group29_sensitivity_run2_2026-06-04"
RESEARCH_DIR = WORKSPACE_ROOT / "source_research" / "mental_vitality_medical_data_2026-06-04"
GBD_FORECAST_CSV = RESEARCH_DIR / "extracted" / "pmc11336039_cao2024_supplement_forecast_tables.csv"

ANALYSIS_DATE = "2026-06-04"
DEFAULT_ITERATIONS = 1_000_000
DEFAULT_SEED = 15170506
GROUP_N = 29


@dataclass(frozen=True)
class MortalityScenario:
    key: str
    label: str
    hazard_scale: float
    note: str


@dataclass(frozen=True)
class VitalityScenario:
    key: str
    label: str
    probability: float
    source: str
    construct: str
    denominator: str
    note: str
    probability_low: float | None = None
    probability_high: float | None = None


def load_run1_module():
    spec = importlib.util.spec_from_file_location("apollo_run1", RUN1_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load run1 script: {RUN1_SCRIPT}")
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


def binom_probs(n: int, p: float) -> list[float]:
    p = max(0.0, min(1.0, p))
    if n < 0:
        raise ValueError("n must be non-negative")
    if p == 0.0:
        return [1.0] + [0.0] * n
    if p == 1.0:
        return [0.0] * n + [1.0]
    q = 1.0 - p
    return [math.comb(n, k) * (p**k) * (q ** (n - k)) for k in range(n + 1)]


def binom_tail(n: int, p: float, threshold: int) -> float:
    if threshold <= 0:
        return 1.0
    if threshold > n:
        return 0.0
    return sum(binom_probs(n, p)[threshold:])


def dist_quantile(dist: dict[int, float] | Counter[int], q: float) -> int:
    total = sum(dist.values())
    if total <= 0:
        return 0
    target = q * total
    running = 0.0
    for value in sorted(dist):
        running += dist[value]
        if running >= target:
            return value
    return max(dist)


def dist_tail(dist: dict[int, float] | Counter[int], threshold: int) -> float:
    total = sum(dist.values())
    if total <= 0:
        return 0.0
    return sum(weight for value, weight in dist.items() if value >= threshold) / total


def dist_mean(dist: dict[int, float] | Counter[int]) -> float:
    total = sum(dist.values())
    if total <= 0:
        return 0.0
    return sum(value * weight for value, weight in dist.items()) / total


def exact_joint_distribution(n: int, p80: float, p90: float, p95: float) -> dict[tuple[int, int, int], float]:
    """Exact multinomial distribution for nested survival counts."""
    cat_probs = [
        max(0.0, 1.0 - p80),
        max(0.0, p80 - p90),
        max(0.0, p90 - p95),
        max(0.0, p95),
    ]
    norm = sum(cat_probs)
    if norm <= 0:
        raise ValueError("Survival probabilities produced no valid categories")
    cat_probs = [p / norm for p in cat_probs]

    dist: dict[tuple[int, int, int], float] = {(0, 0, 0): 1.0}
    for _ in range(n):
        next_dist: dict[tuple[int, int, int], float] = defaultdict(float)
        for (n80, n90, n95), prob in dist.items():
            next_dist[(n80, n90, n95)] += prob * cat_probs[0]
            next_dist[(n80 + 1, n90, n95)] += prob * cat_probs[1]
            next_dist[(n80 + 1, n90 + 1, n95)] += prob * cat_probs[2]
            next_dist[(n80 + 1, n90 + 1, n95 + 1)] += prob * cat_probs[3]
        dist = dict(next_dist)
    return dist


def marginal_from_joint(
    joint: dict[tuple[int, int, int], float],
    index: int,
) -> dict[int, float]:
    out: dict[int, float] = defaultdict(float)
    for state, prob in joint.items():
        out[state[index]] += prob
    return dict(out)


def simulate_survival_counts(
    n: int,
    p80: float,
    p90: float,
    p95: float,
    iterations: int,
    seed: int,
) -> dict[str, object]:
    rng = random.Random(seed)
    random_value = rng.random
    dist80: Counter[int] = Counter()
    dist90: Counter[int] = Counter()
    dist95: Counter[int] = Counter()
    joint8090: Counter[tuple[int, int]] = Counter()
    joint809095: Counter[tuple[int, int, int]] = Counter()

    for _ in range(iterations):
        n80 = 0
        n90 = 0
        n95 = 0
        for _person in range(n):
            u = random_value()
            if u < p95:
                n80 += 1
                n90 += 1
                n95 += 1
            elif u < p90:
                n80 += 1
                n90 += 1
            elif u < p80:
                n80 += 1
        dist80[n80] += 1
        dist90[n90] += 1
        dist95[n95] += 1
        joint8090[(n80, n90)] += 1
        joint809095[(n80, n90, n95)] += 1

    return {
        "dist80": dist80,
        "dist90": dist90,
        "dist95": dist95,
        "joint8090": joint8090,
        "joint809095": joint809095,
    }


def exact_state_probability(
    joint: dict[tuple[int, int, int], float],
    obs80: int,
    obs90: int,
    obs95: int | None = None,
) -> float:
    total = 0.0
    for n80, n90, n95 in joint:
        if n80 < obs80 or n90 < obs90:
            continue
        if obs95 is not None and n95 < obs95:
            continue
        total += joint[(n80, n90, n95)]
    return total


def simulated_state_probability(
    joint: Counter[tuple[int, int, int]],
    iterations: int,
    obs80: int,
    obs90: int,
    obs95: int | None = None,
) -> float:
    count = 0
    for (n80, n90, n95), value in joint.items():
        if n80 < obs80 or n90 < obs90:
            continue
        if obs95 is not None and n95 < obs95:
            continue
        count += value
    return count / iterations


def vitality_distribution(
    n80_dist: dict[int, float] | Counter[int],
    vitality_probability: float,
) -> dict[int, float]:
    out: dict[int, float] = defaultdict(float)
    for n80, weight in n80_dist.items():
        for vital_count, prob in enumerate(binom_probs(n80, vitality_probability)):
            out[vital_count] += weight * prob
    return dict(out)


def joint_vitality_probability_exact(
    joint: dict[tuple[int, int, int], float],
    vitality_probability: float,
    vital_threshold: int,
    obs80: int | None = None,
    obs90: int | None = None,
    obs95: int | None = None,
) -> float:
    total = 0.0
    for (n80, n90, n95), state_prob in joint.items():
        if obs80 is not None and n80 < obs80:
            continue
        if obs90 is not None and n90 < obs90:
            continue
        if obs95 is not None and n95 < obs95:
            continue
        total += state_prob * binom_tail(n80, vitality_probability, vital_threshold)
    return total


def joint_vitality_probability_simulated(
    joint: Counter[tuple[int, int, int]],
    iterations: int,
    vitality_probability: float,
    vital_threshold: int,
    obs80: int | None = None,
    obs90: int | None = None,
    obs95: int | None = None,
) -> float:
    total = 0.0
    for (n80, n90, n95), state_count in joint.items():
        if obs80 is not None and n80 < obs80:
            continue
        if obs90 is not None and n90 < obs90:
            continue
        if obs95 is not None and n95 < obs95:
            continue
        total += state_count * binom_tail(n80, vitality_probability, vital_threshold)
    return total / iterations


def load_apollo_observed(run1_module) -> dict[str, object]:
    people = run1_module.load_people()
    apollo = [person for person in people if person.primary == "apollo"]
    if len(apollo) != GROUP_N:
        raise RuntimeError(f"Expected {GROUP_N} Apollo people, found {len(apollo)}")
    reached80 = [person for person in apollo if person.endpoint_age >= 80.0]
    reached90 = [person for person in apollo if person.endpoint_age >= 90.0]
    reached95 = [person for person in apollo if person.endpoint_age >= 95.0]
    sg_all = [person for person in apollo if person.space_grandpa == "Y"]
    sg80 = [person for person in reached80 if person.space_grandpa == "Y"]
    return {
        "n": len(apollo),
        "reached80": len(reached80),
        "reached90": len(reached90),
        "reached95": len(reached95),
        "space_grandpa_all": len(sg_all),
        "space_grandpa_among80": len(sg80),
        "space_grandpa_rate_among80": len(sg80) / len(reached80),
        "names_reached95": "; ".join(sorted(person.name for person in reached95)),
    }


def mortality_scenarios(apollo_smr: float) -> list[MortalityScenario]:
    return [
        MortalityScenario(
            "ssa_general_age30",
            "SSA general male, age-30 selected",
            1.00,
            "Unscreened SSA 1930 male cohort table, conditional on survival to age 30.",
        ),
        MortalityScenario(
            "modestly_healthy_15pct_lower_hazard",
            "Modestly healthy, 15 pct lower hazard",
            0.85,
            "Sensitivity point: all-cause post-30 cumulative hazard scaled down by 15 pct.",
        ),
        MortalityScenario(
            "healthy_30pct_lower_hazard",
            "Healthy, 30 pct lower hazard",
            0.70,
            "Sensitivity point for healthier-than-average men.",
        ),
        MortalityScenario(
            "very_healthy_45pct_lower_hazard",
            "Very healthy, 45 pct lower hazard",
            0.55,
            "Aggressive healthy-selection sensitivity point.",
        ),
        MortalityScenario(
            "apollo_smr_like_54pct_lower_hazard",
            "Apollo-SMR-like hazard scale",
            apollo_smr,
            "Uses run1 Apollo SMR as a hazard-scale sensitivity; not a general-population estimate.",
        ),
    ]


def load_apollo_smr() -> float:
    path = RUN1_OUT_DIR / "smr_summary.csv"
    if not path.exists():
        return 0.45717072413853527
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("cohort_key") == "apollo":
                return float(row["smr"])
    return 0.45717072413853527


def load_gbd_dementia_free_assumptions() -> list[VitalityScenario]:
    out: list[VitalityScenario] = []
    wanted = {
        "80-84 years": "80_84",
        "85-89 years": "85_89",
        "90-94 years": "90_94",
        "95+ years": "95_plus",
    }
    if not GBD_FORECAST_CSV.exists():
        return out
    with GBD_FORECAST_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["metric"] != "prevalence_rate_per_100k":
                continue
            if row["sex"] != "Male" or row["year"] != "2020":
                continue
            age_group = row["age_group"]
            if age_group not in wanted:
                continue
            rate = float(row["estimate"]) / 100000.0
            lower_rate = float(row["lower_95ci"]) / 100000.0
            upper_rate = float(row["upper_95ci"]) / 100000.0
            out.append(
                VitalityScenario(
                    key=f"cao_gbd_2020_male_{wanted[age_group]}_dementia_free",
                    label=f"Cao/GBD male {age_group} dementia-free",
                    probability=1.0 - rate,
                    probability_low=1.0 - upper_rate,
                    probability_high=1.0 - lower_rate,
                    source="Cao et al. 2024 supplement eTable 4, GBD 2019 forecast, U.S. male 2020",
                    construct="Dementia-free only",
                    denominator=f"Men in age band {age_group}",
                    note="Upper-bound mental-vitality proxy because it excludes dementia but not MCI or functional limitation.",
                )
            )
    return out


def vitality_scenarios(observed_sg_rate_among80: float) -> list[VitalityScenario]:
    scenarios = load_gbd_dementia_free_assumptions()
    scenarios.extend(
        [
            VitalityScenario(
                "hcap_65plus_normal_cognition_overall",
                "HRS-HCAP 65+ normal cognition overall",
                0.68,
                "HRS-HCAP prevalence paper: 10 pct dementia and 22 pct MCI among U.S. adults 65+ in 2016",
                "No dementia and no MCI",
                "U.S. adults 65+, not age-80 male survivors",
                "Broad national anchor; likely too optimistic or mis-aged for 80+ men.",
            ),
            VitalityScenario(
                "sciencedirect_80_94_no_mmse_impairment",
                "ScienceDirect long-lived 80-94 no MMSE impairment",
                1.0 - 58.0 / 165.0,
                "Campos et al. 2024, Journal of Affective Disorders, n=165 age 80-94; 58 poor MMSE adjusted for education",
                "No poor MMSE performance",
                "Community-dwelling long-lived adults age 80-94",
                "Non-U.S. and very low education sample; included as a cautionary lower clinical anchor.",
            ),
            VitalityScenario(
                "functional_vitality_sensitivity_50pct",
                "Functional/participatory vitality sensitivity, 50 pct",
                0.50,
                "Sensitivity assumption, not a single-source estimate",
                "Normal cognition plus functional/participatory reserve",
                "Age-80 survivors",
                "Conservative placeholder for a stricter vitality construct pending HRS/NHATS extraction.",
            ),
            VitalityScenario(
                "public_activity_sensitivity_35pct",
                "Public-activity sensitivity, 35 pct",
                0.35,
                "Sensitivity assumption, not a single-source estimate",
                "Visible late-life activity",
                "Age-80 survivors",
                "Very conservative public-visibility proxy; helps bracket the Space Grandpa construct.",
            ),
            VitalityScenario(
                "apollo_observed_space_grandpa_among80",
                "Apollo observed Space Grandpa among 80+",
                observed_sg_rate_among80,
                "Run1 astronaut dataset Space Grandpa field",
                "Publicly documented late-life activity",
                "Apollo age-80 survivors",
                "Self-calibrating check only; not a population baseline.",
            ),
        ]
    )
    return scenarios


def probability_rows_from_survival_dist(
    scenario: MortalityScenario,
    threshold: str,
    sim_dist: Counter[int],
    exact_dist: dict[int, float],
    iterations: int,
) -> list[dict[str, object]]:
    rows = []
    for count in range(0, GROUP_N + 1):
        rows.append(
            {
                "mortality_scenario_key": scenario.key,
                "mortality_scenario": scenario.label,
                "threshold": threshold,
                "count": count,
                "simulated_count": sim_dist.get(count, 0),
                "simulated_probability": sim_dist.get(count, 0) / iterations,
                "exact_probability": exact_dist.get(count, 0.0),
            }
        )
    return rows


def exact_vitality_dist_from_joint(
    exact_n80_dist: dict[int, float],
    scenario: VitalityScenario,
) -> dict[int, float]:
    return vitality_distribution(exact_n80_dist, scenario.probability)


def simulated_vitality_dist_from_n80(
    sim_n80_dist: Counter[int],
    scenario: VitalityScenario,
) -> dict[int, float]:
    return vitality_distribution(sim_n80_dist, scenario.probability)


def probability_rows_from_vitality_dist(
    mortality: MortalityScenario,
    vitality: VitalityScenario,
    sim_dist: dict[int, float],
    exact_dist: dict[int, float],
    iterations: int,
) -> list[dict[str, object]]:
    rows = []
    for count in range(0, GROUP_N + 1):
        sim_weight = sim_dist.get(count, 0.0)
        rows.append(
            {
                "mortality_scenario_key": mortality.key,
                "mortality_scenario": mortality.label,
                "vitality_scenario_key": vitality.key,
                "vitality_scenario": vitality.label,
                "vitality_count": count,
                "simulated_probability": sim_weight / iterations,
                "exact_probability": exact_dist.get(count, 0.0),
            }
        )
    return rows


def scenario_survival_probabilities(life, hazard_scale: float) -> tuple[float, float, float]:
    p80 = life.survival_from_30(80.0) ** hazard_scale
    p90 = life.survival_from_30(90.0) ** hazard_scale
    p95 = life.survival_from_30(95.0) ** hazard_scale
    return p80, p90, p95


def build_report(
    output_path: Path,
    observed: dict[str, object],
    survival_rows: list[dict[str, object]],
    vitality_rows: list[dict[str, object]],
    assumption_rows: list[dict[str, object]],
    iterations: int,
    seed: int,
    elapsed_seconds: float,
) -> None:
    key_survival = [
        {
            "scenario": row["mortality_scenario"],
            "hazard_scale": row["hazard_scale"],
            "survival_to_80": row["p_survive80"],
            "expected_n80": row["expected_n80"],
            "exact_p_n80_ge_obs": row["exact_p_n80_ge_observed"],
            "exact_p_profile80_90": row["exact_p_n80_ge_obs_and_n90_ge_obs"],
            "exact_p_profile80_90_95": row["exact_p_n80_ge_obs_n90_ge_obs_n95_ge_obs"],
        }
        for row in survival_rows
    ]
    key_vitality = [
        {
            "mortality": row["mortality_scenario"],
            "vitality": row["vitality_scenario"],
            "vitality_rate": row["vitality_probability"],
            "expected_vital": row["exact_expected_vitality_count"],
            "p_vital_ge21": row["exact_p_vitality_ge_observed"],
            "p_longevity_vitality": row["exact_p_n80_ge_obs_n90_ge_obs_and_vitality_ge_obs"],
        }
        for row in vitality_rows
        if row["vitality_scenario_key"]
        in {
            "hcap_65plus_normal_cognition_overall",
            "sciencedirect_80_94_no_mmse_impairment",
            "functional_vitality_sensitivity_50pct",
            "cao_gbd_2020_male_85_89_dementia_free",
            "apollo_observed_space_grandpa_among80",
        }
    ]

    lines = [
        "# Run 2: Group-of-29 Longevity and Mental-Vitality Sensitivity",
        "",
        f"Analysis date: {ANALYSIS_DATE}",
        f"Monte Carlo iterations per mortality scenario: {iterations:,}",
        f"Seed base: {seed}",
        f"Runtime: {elapsed_seconds:.1f} seconds",
        "",
        "## Why This Is a Separate Run",
        "",
        "Run1 is preserved as the astronaut-vs-astronaut and astronaut-vs-SSA analysis. This run asks a narrower probability question: if we draw 29 age-30-selected men from the 1930 male SSA cohort, under several healthier-than-average hazard assumptions and several mental-vitality proxy assumptions, how often do we see Apollo-like group outcomes?",
        "",
        "The script writes exact probabilities alongside the Monte Carlo estimates. The exact probabilities are useful because Apollo-like outcomes can be rare under the unscreened SSA baseline, and simulation alone can under-resolve tails.",
        "",
        "## Observed Apollo 7-17 Targets",
        "",
        f"- N: {observed['n']}",
        f"- Reached age 80: {observed['reached80']}",
        f"- Reached age 90: {observed['reached90']}",
        f"- Reached age 95: {observed['reached95']} ({observed['names_reached95']})",
        f"- Space Grandpa count among all Apollo astronauts: {observed['space_grandpa_all']}",
        f"- Space Grandpa count among Apollo age-80 survivors: {observed['space_grandpa_among80']} / {observed['reached80']} = {100 * float(observed['space_grandpa_rate_among80']):.1f}%",
        "",
        "## Mortality Model",
        "",
        "SSA survival is conditional on survival to age 30. Healthier-selection scenarios scale post-30 cumulative hazard by a constant factor h, equivalent to S_adjusted(age) = S_SSA(age) ** h. Lower h means better survival. These are sensitivity points, not claims that SSA has a health-screened table.",
        "",
        markdown_table(
            key_survival,
            [
                ("scenario", "Scenario", None),
                ("hazard_scale", "h", 3),
                ("survival_to_80", "P80", 3),
                ("expected_n80", "Exp N80", 2),
                ("exact_p_n80_ge_obs", "P(N80 >= 22)", 6),
                ("exact_p_profile80_90", "P(N80 >= 22,N90 >= 13)", 6),
                ("exact_p_profile80_90_95", "P(+N95 >= obs)", 6),
            ],
        ),
        "",
        "## Vitality Model",
        "",
        "Vitality is modeled conditional on surviving to age 80. The Apollo target is 21 Space Grandpa positives, which is a public-activity construct. The population rates below are deliberately a range: dementia-free is permissive, normal cognition/no MCI is stricter, functional or public-activity rates are sensitivity placeholders pending HRS/NHATS extraction.",
        "",
        markdown_table(
            key_vitality,
            [
                ("mortality", "Mortality scenario", None),
                ("vitality", "Vitality scenario", None),
                ("vitality_rate", "Rate", 3),
                ("expected_vital", "Exp vital count", 2),
                ("p_vital_ge21", "P(vital >= 21)", 6),
                ("p_longevity_vitality", "P(long+vital)", 6),
            ],
        ),
        "",
        "## Assumption Inventory",
        "",
        markdown_table(
            assumption_rows,
            [
                ("vitality_scenario_key", "Key", None),
                ("vitality_probability", "Rate", 3),
                ("construct", "Construct", None),
                ("denominator", "Denominator", None),
                ("source", "Source", None),
            ],
        ),
        "",
        "## Interpretation Guardrails",
        "",
        "- SSA mortality can answer longevity only; it cannot infer mental vitality.",
        "- Dementia-free rates are upper-bound vitality proxies because they do not exclude MCI, functional dependence, or low participation.",
        "- The ScienceDirect 80-94 MMSE anchor is useful as a clinical caution but is not a U.S. high-education male population baseline.",
        "- The age/cognition review supports the construct boundary: normal aging can preserve knowledge and speech while reducing speed, working memory, and executive function, so public late-life activity is not reducible to 'no dementia'.",
        "",
        "## Output Files",
        "",
        "- `run2_survival_scenario_summary.csv`",
        "- `run2_survival_count_distributions.csv`",
        "- `run2_observed_apollo_targets.csv`",
        "- `run2_vitality_assumptions.csv`",
        "- `run2_vitality_scenario_summary.csv`",
        "- `run2_vitality_count_distributions.csv`",
        "- `run2_method_notes.md`",
        "- `run2_group29_report.md`",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def build_method_notes(
    output_path: Path,
    observed: dict[str, object],
    iterations: int,
    seed: int,
) -> None:
    lines = [
        "# Run 2 Method Notes",
        "",
        f"Analysis date: {ANALYSIS_DATE}",
        "",
        "## Inputs",
        "",
        f"- Run1 parser/script: `{RUN1_SCRIPT.relative_to(WORKSPACE_ROOT)}`",
        "- Astronaut source data: run1 `load_people()` over the enriched Apollo/non-Apollo TSVs.",
        "- Mortality source: local SSA 1930 male cohort life table from the processed-data folder, conditional on age 30.",
        f"- Cao/GBD extracted supplement table: `{GBD_FORECAST_CSV.relative_to(WORKSPACE_ROOT)}`",
        "- ScienceDirect local HTML: `source_research/mental_vitality_medical_data_2026-06-04/references/sciencedirect_2024_prevalence_cognitive_impairment_older_people.html`",
        "- Murman local HTML: `source_research/mental_vitality_medical_data_2026-06-04/references/pmc4906299_impact_of_age_on_cognition.html`",
        "",
        "## Apollo Targets",
        "",
        f"- Group size: {observed['n']}",
        f"- Reached age 80: {observed['reached80']}",
        f"- Reached age 90: {observed['reached90']}",
        f"- Reached age 95: {observed['reached95']}",
        f"- Space Grandpa positives among all 29: {observed['space_grandpa_all']}",
        f"- Space Grandpa positives among age-80 survivors: {observed['space_grandpa_among80']}",
        "",
        "## Mortality Sensitivity",
        "",
        "SSA survival from age 30 to age A is S_SSA(A). A health-selection scenario uses a hazard scale h:",
        "",
        "```text",
        "S_adjusted(A) = S_SSA(A) ** h",
        "```",
        "",
        "The Monte Carlo draw for each simulated person uses one uniform random number and the nested probabilities for reaching ages 80, 90, and 95. This is enough for the run2 question because the requested endpoint is count of people reaching Apollo-like age thresholds, not full death-age curves.",
        "",
        "Exact probabilities are computed from the multinomial distribution over four mutually exclusive categories: death before 80, reached 80 but not 90, reached 90 but not 95, and reached 95. This prevents rare-tail conclusions from depending only on Monte Carlo resolution.",
        "",
        "## Vitality Sensitivity",
        "",
        "Vitality is modeled conditional on being an age-80 survivor. If k people in the simulated group reach age 80, and p is a chosen vitality proxy probability, the vitality count is Binomial(k, p). The final distribution is a mixture over the survival-count distribution.",
        "",
        "```text",
        "P(V = v) = sum_k P(N80 = k) * BinomialPMF(v | k, p)",
        "```",
        "",
        "The core output probabilities include:",
        "",
        "- `P(vitality >= 21)` regardless of the exact age-threshold profile.",
        "- `P(N80 >= 22 and vitality >= 21)`.",
        "- `P(N80 >= 22 and N90 >= 13 and vitality >= 21)`.",
        "- `P(N80 >= 22 and N90 >= 13 and N95 >= 3 and vitality >= 21)`.",
        "",
        "## Construct Boundary",
        "",
        "The astronaut `Space Grandpa` field is public late-life activity. Cao/GBD dementia-free rates, HRS-HCAP normal cognition, and the ScienceDirect MMSE anchor are clinical or survey-health proxies. They should be read as sensitivity bounds, not a direct substitution for public activity.",
        "",
        "## Reproducibility",
        "",
        f"- Monte Carlo iterations per mortality scenario: {iterations:,}",
        f"- Seed base: {seed}",
        "- Exact probabilities are deterministic and do not depend on the seed.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run2 group-of-29 Apollo longevity/vitality simulation")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    run1 = load_run1_module()
    life = run1.LifeTable.load(run1.SSA_FILE)
    observed = load_apollo_observed(run1)
    apollo_smr = load_apollo_smr()
    mortality_rows: list[dict[str, object]] = []
    survival_distribution_rows: list[dict[str, object]] = []
    vitality_assumption_rows: list[dict[str, object]] = []
    vitality_summary_rows: list[dict[str, object]] = []
    vitality_distribution_rows: list[dict[str, object]] = []

    vitality_options = vitality_scenarios(float(observed["space_grandpa_rate_among80"]))
    write_csv(OUT_DIR / "run2_observed_apollo_targets.csv", [observed])
    for option in vitality_options:
        vitality_assumption_rows.append(
            {
                "vitality_scenario_key": option.key,
                "vitality_scenario": option.label,
                "vitality_probability": option.probability,
                "vitality_probability_low": "" if option.probability_low is None else option.probability_low,
                "vitality_probability_high": "" if option.probability_high is None else option.probability_high,
                "construct": option.construct,
                "denominator": option.denominator,
                "source": option.source,
                "note": option.note,
            }
        )

    for idx, scenario in enumerate(mortality_scenarios(apollo_smr)):
        p80, p90, p95 = scenario_survival_probabilities(life, scenario.hazard_scale)
        exact_joint = exact_joint_distribution(GROUP_N, p80, p90, p95)
        exact80 = marginal_from_joint(exact_joint, 0)
        exact90 = marginal_from_joint(exact_joint, 1)
        exact95 = marginal_from_joint(exact_joint, 2)
        seed = args.seed + idx * 1009
        sim = simulate_survival_counts(GROUP_N, p80, p90, p95, args.iterations, seed)
        sim80: Counter[int] = sim["dist80"]
        sim90: Counter[int] = sim["dist90"]
        sim95: Counter[int] = sim["dist95"]
        sim_joint: Counter[tuple[int, int, int]] = sim["joint809095"]

        row = {
            "mortality_scenario_key": scenario.key,
            "mortality_scenario": scenario.label,
            "hazard_scale": scenario.hazard_scale,
            "note": scenario.note,
            "iterations": args.iterations,
            "seed": seed,
            "p_survive80": p80,
            "p_survive90": p90,
            "p_survive95": p95,
            "expected_n80": GROUP_N * p80,
            "expected_n90": GROUP_N * p90,
            "expected_n95": GROUP_N * p95,
            "observed_n80": observed["reached80"],
            "observed_n90": observed["reached90"],
            "observed_n95": observed["reached95"],
            "sim_mean_n80": dist_mean(sim80),
            "sim_mean_n90": dist_mean(sim90),
            "sim_mean_n95": dist_mean(sim95),
            "sim_n80_p02_5": dist_quantile(sim80, 0.025),
            "sim_n80_p50": dist_quantile(sim80, 0.50),
            "sim_n80_p97_5": dist_quantile(sim80, 0.975),
            "sim_n90_p02_5": dist_quantile(sim90, 0.025),
            "sim_n90_p50": dist_quantile(sim90, 0.50),
            "sim_n90_p97_5": dist_quantile(sim90, 0.975),
            "sim_n95_p02_5": dist_quantile(sim95, 0.025),
            "sim_n95_p50": dist_quantile(sim95, 0.50),
            "sim_n95_p97_5": dist_quantile(sim95, 0.975),
            "sim_p_n80_ge_observed": dist_tail(sim80, int(observed["reached80"])),
            "sim_p_n90_ge_observed": dist_tail(sim90, int(observed["reached90"])),
            "sim_p_n95_ge_observed": dist_tail(sim95, int(observed["reached95"])),
            "sim_p_n80_ge_obs_and_n90_ge_obs": simulated_state_probability(
                sim_joint,
                args.iterations,
                int(observed["reached80"]),
                int(observed["reached90"]),
            ),
            "sim_p_n80_ge_obs_n90_ge_obs_n95_ge_obs": simulated_state_probability(
                sim_joint,
                args.iterations,
                int(observed["reached80"]),
                int(observed["reached90"]),
                int(observed["reached95"]),
            ),
            "exact_mean_n80": dist_mean(exact80),
            "exact_mean_n90": dist_mean(exact90),
            "exact_mean_n95": dist_mean(exact95),
            "exact_p_n80_ge_observed": dist_tail(exact80, int(observed["reached80"])),
            "exact_p_n90_ge_observed": dist_tail(exact90, int(observed["reached90"])),
            "exact_p_n95_ge_observed": dist_tail(exact95, int(observed["reached95"])),
            "exact_p_n80_ge_obs_and_n90_ge_obs": exact_state_probability(
                exact_joint,
                int(observed["reached80"]),
                int(observed["reached90"]),
            ),
            "exact_p_n80_ge_obs_n90_ge_obs_n95_ge_obs": exact_state_probability(
                exact_joint,
                int(observed["reached80"]),
                int(observed["reached90"]),
                int(observed["reached95"]),
            ),
        }
        mortality_rows.append(row)

        survival_distribution_rows.extend(
            probability_rows_from_survival_dist(scenario, "survive_to_80", sim80, exact80, args.iterations)
        )
        survival_distribution_rows.extend(
            probability_rows_from_survival_dist(scenario, "survive_to_90", sim90, exact90, args.iterations)
        )
        survival_distribution_rows.extend(
            probability_rows_from_survival_dist(scenario, "survive_to_95", sim95, exact95, args.iterations)
        )

        for vitality in vitality_options:
            exact_vital_dist = exact_vitality_dist_from_joint(exact80, vitality)
            sim_vital_dist = simulated_vitality_dist_from_n80(sim80, vitality)
            vitality_distribution_rows.extend(
                probability_rows_from_vitality_dist(
                    scenario,
                    vitality,
                    sim_vital_dist,
                    exact_vital_dist,
                    args.iterations,
                )
            )
            vital_threshold = int(observed["space_grandpa_all"])
            vitality_summary_rows.append(
                {
                    "mortality_scenario_key": scenario.key,
                    "mortality_scenario": scenario.label,
                    "hazard_scale": scenario.hazard_scale,
                    "vitality_scenario_key": vitality.key,
                    "vitality_scenario": vitality.label,
                    "vitality_probability": vitality.probability,
                    "construct": vitality.construct,
                    "denominator": vitality.denominator,
                    "observed_vitality_count": vital_threshold,
                    "observed_apollo_reached80": observed["reached80"],
                    "observed_apollo_reached90": observed["reached90"],
                    "exact_expected_vitality_count": dist_mean(exact_vital_dist),
                    "sim_expected_vitality_count": dist_mean(sim_vital_dist),
                    "exact_vitality_count_p02_5": dist_quantile(exact_vital_dist, 0.025),
                    "exact_vitality_count_p50": dist_quantile(exact_vital_dist, 0.50),
                    "exact_vitality_count_p97_5": dist_quantile(exact_vital_dist, 0.975),
                    "sim_vitality_count_p02_5": dist_quantile(sim_vital_dist, 0.025),
                    "sim_vitality_count_p50": dist_quantile(sim_vital_dist, 0.50),
                    "sim_vitality_count_p97_5": dist_quantile(sim_vital_dist, 0.975),
                    "exact_p_vitality_ge_observed": dist_tail(exact_vital_dist, vital_threshold),
                    "sim_p_vitality_ge_observed": dist_tail(sim_vital_dist, vital_threshold),
                    "exact_p_n80_ge_obs_and_vitality_ge_obs": joint_vitality_probability_exact(
                        exact_joint,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                    ),
                    "sim_p_n80_ge_obs_and_vitality_ge_obs": joint_vitality_probability_simulated(
                        sim_joint,
                        args.iterations,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                    ),
                    "exact_p_n80_ge_obs_n90_ge_obs_and_vitality_ge_obs": joint_vitality_probability_exact(
                        exact_joint,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                        obs90=int(observed["reached90"]),
                    ),
                    "sim_p_n80_ge_obs_n90_ge_obs_and_vitality_ge_obs": joint_vitality_probability_simulated(
                        sim_joint,
                        args.iterations,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                        obs90=int(observed["reached90"]),
                    ),
                    "exact_p_n80_ge_obs_n90_ge_obs_n95_ge_obs_and_vitality_ge_obs": joint_vitality_probability_exact(
                        exact_joint,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                        obs90=int(observed["reached90"]),
                        obs95=int(observed["reached95"]),
                    ),
                    "sim_p_n80_ge_obs_n90_ge_obs_n95_ge_obs_and_vitality_ge_obs": joint_vitality_probability_simulated(
                        sim_joint,
                        args.iterations,
                        vitality.probability,
                        vital_threshold,
                        obs80=int(observed["reached80"]),
                        obs90=int(observed["reached90"]),
                        obs95=int(observed["reached95"]),
                    ),
                    "source": vitality.source,
                    "note": vitality.note,
                }
            )

    write_csv(OUT_DIR / "run2_survival_scenario_summary.csv", mortality_rows)
    write_csv(OUT_DIR / "run2_survival_count_distributions.csv", survival_distribution_rows)
    write_csv(OUT_DIR / "run2_vitality_assumptions.csv", vitality_assumption_rows)
    write_csv(OUT_DIR / "run2_vitality_scenario_summary.csv", vitality_summary_rows)
    write_csv(OUT_DIR / "run2_vitality_count_distributions.csv", vitality_distribution_rows)

    elapsed = time.time() - start
    build_report(
        OUT_DIR / "run2_group29_report.md",
        observed,
        mortality_rows,
        vitality_summary_rows,
        vitality_assumption_rows,
        args.iterations,
        args.seed,
        elapsed,
    )
    build_method_notes(
        OUT_DIR / "run2_method_notes.md",
        observed,
        args.iterations,
        args.seed,
    )
    print(f"Wrote run2 outputs to {OUT_DIR}")
    print(f"Iterations per mortality scenario: {args.iterations:,}")
    print(f"Elapsed seconds: {elapsed:.1f}")


if __name__ == "__main__":
    main()
