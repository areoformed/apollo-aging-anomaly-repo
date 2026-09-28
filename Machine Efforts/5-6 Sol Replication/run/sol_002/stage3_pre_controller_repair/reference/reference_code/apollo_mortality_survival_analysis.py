#!/usr/bin/env python3
"""
Apollo mortality, survival, and late-life vitality analysis.

Reads the locally archived Apollo Aging Anomaly TSVs and writes reproducible
outputs into this GPT 5-5 workspace.

Method notes:
- General population baseline is the local SSA 1930 male cohort life table,
  conditional on survival to age 30.
- Astronaut-vs-general comparisons keep accidental deaths in the astronaut
  cohorts, because the SSA all-cause table includes accidents.
- Apollo-vs-other-astronaut comparisons also report an "Apollo-available"
  comparator that removes pre-1970 accidental deaths from the non-Apollo pool.
  This operationalizes the user's training-accident exclusion with the fields
  available in the data: Accidental Death = Y and Date of Death before 1970.
- "Space Grandpa" is treated as the dataset's proxy for retained public mental
  vitality at age 80+. SSA has mortality only, so no general-population mental
  vitality rate is inferred.
"""

from __future__ import annotations

import csv
import html
import math
import random
import statistics
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = (
    WORKSPACE_ROOT
    / "data"
    / "source_inputs"
    / "analysis_inputs_2026-06-16"
    / "upstream_processed_data"
)
ENRICHED = ARCHIVE_ROOT / "Final - Analysis - Enriched Datasets"
SSA_FILE = ARCHIVE_ROOT / "data" / "ssa-1930-male-cohort-lifetable.tsv"
ANALYSIS_DATE = date(2026, 6, 4)
OUT_DIR = WORKSPACE_ROOT / "analysis_outputs" / "mortality_survival_run1_2026-06-04"

ENTRY_AGE = 30.0
MC_ITERATIONS = 200_000
MC_SEED = 15170505


SOURCE_FILES = [
    {
        "key": "other_core_nasa",
        "label": "Core NASA non-Apollo",
        "primary": "other",
        "file": ENRICHED / "03E-non-apollo-enriched.tsv",
    },
    {
        "key": "apollo_lunar",
        "label": "Apollo lunar-program crew",
        "primary": "apollo",
        "file": ENRICHED / "07E-lunar-enriched.tsv",
    },
    {
        "key": "apollo_non_lunar",
        "label": "Apollo 7/9 non-lunar crew",
        "primary": "apollo",
        "file": ENRICHED / "08E-non-lunar-apollo-enriched.tsv",
    },
    {
        "key": "military_x15",
        "label": "X-15/high-speed pilots",
        "primary": "other",
        "file": ENRICHED / "09-x15-pilots-enriched.tsv",
    },
    {
        "key": "military_dyna_soar",
        "label": "X-20 Dyna-Soar pilots",
        "primary": "other",
        "file": ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    },
    {
        "key": "military_mol",
        "label": "MOL military astronauts",
        "primary": "other",
        "file": ENRICHED / "11-mol-full-enriched.tsv",
    },
]


@dataclass(frozen=True)
class Person:
    name: str
    source_key: str
    source_label: str
    primary: str
    astronaut_group: str
    dob: date | None
    dod: date | None
    reported_age: float | None
    status: str
    accidental_death: bool
    cause_note: str
    space_grandpa: str
    space_grandpa_citation: str
    birth_year: int | None

    @property
    def deceased(self) -> bool:
        return self.status.lower() == "deceased" or self.dod is not None

    @property
    def endpoint_age(self) -> float:
        if self.dob and self.dod:
            return age_between(self.dob, self.dod)
        if self.dob and not self.deceased:
            return age_between(self.dob, ANALYSIS_DATE)
        if self.reported_age is not None:
            return self.reported_age
        raise ValueError(f"No usable age for {self.name}")

    @property
    def reached_80(self) -> bool:
        return self.endpoint_age >= 80.0

    @property
    def reached_90(self) -> bool:
        return self.endpoint_age >= 90.0

    @property
    def pre1970_accidental_death(self) -> bool:
        return bool(
            self.accidental_death and self.dod is not None and self.dod.year < 1970
        )


class LifeTable:
    def __init__(self, rows: list[dict[str, float]]):
        self.rows = rows
        self.by_age = {int(r["age"]): r for r in rows}
        self.ages = sorted(self.by_age)
        self.min_age = min(self.ages)
        self.max_age = max(self.ages)
        self.l30 = self.lx_at(ENTRY_AGE)
        if self.l30 <= 0:
            raise ValueError("Life table has no survivors at age 30")

        death_ages: list[int] = []
        weights: list[float] = []
        for age in self.ages:
            if age >= int(ENTRY_AGE):
                dx = self.by_age[age]["dx"]
                if dx > 0:
                    death_ages.append(age)
                    weights.append(dx / self.l30)

        total = sum(weights)
        if total < 0.999:
            # Rounded SSA tables can leave a tiny terminal remainder.
            death_ages.append(self.max_age)
            weights.append(1.0 - total)

        cumulative = []
        running = 0.0
        for w in weights:
            running += w
            cumulative.append(running)
        cumulative[-1] = 1.0

        self.death_ages = death_ages
        self.cumulative = cumulative

    @classmethod
    def load(cls, path: Path) -> "LifeTable":
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = []
            for row in reader:
                rows.append(
                    {
                        "age": float(row["age"]),
                        "qx": float(row["qx"]),
                        "lx": float(row["lx"]),
                        "dx": float(row["dx"]),
                    }
                )
        return cls(rows)

    def lx_at(self, age: float) -> float:
        if age <= self.min_age:
            return self.by_age[self.min_age]["lx"]
        if age >= self.max_age:
            return self.by_age[self.max_age]["lx"]
        lo = int(math.floor(age))
        hi = lo + 1
        if hi not in self.by_age:
            return self.by_age.get(lo, {"lx": 0.0})["lx"]
        frac = age - lo
        lx_lo = self.by_age[lo]["lx"]
        lx_hi = self.by_age[hi]["lx"]
        return max(0.0, lx_lo + frac * (lx_hi - lx_lo))

    def survival_from_30(self, age: float) -> float:
        if age <= ENTRY_AGE:
            return 1.0
        return clamp(self.lx_at(age) / self.l30, 0.0, 1.0)

    def death_probability_by_age(self, age: float) -> float:
        return clamp(1.0 - self.survival_from_30(age), 0.0, 1.0)

    def cumulative_hazard_from_30(self, age: float) -> float:
        # Conventional SMR uses expected deaths from person-time at risk. With
        # a life table, the integrated hazard is -log(S(age) / S(30)).
        survival = max(self.survival_from_30(age), 1e-12)
        return -math.log(survival)

    def expected_events_by_endpoints(self, endpoints: Iterable[float]) -> float:
        return sum(self.cumulative_hazard_from_30(age) for age in endpoints)

    def sample_death_age(self, rng: random.Random) -> float:
        u = rng.random()
        idx = bisect_left(self.cumulative, u)
        if idx >= len(self.death_ages):
            idx = len(self.death_ages) - 1
        return self.death_ages[idx] + rng.random()

    def mean_death_age_from_30(self) -> float:
        return sum(
            (age + 0.5) * self.by_age[age]["dx"]
            for age in self.ages
            if age >= int(ENTRY_AGE)
        ) / self.l30

    def median_death_age_from_30(self) -> float:
        target = self.l30 / 2.0
        for age in self.ages:
            if age < int(ENTRY_AGE):
                continue
            if self.by_age[age]["lx"] <= target:
                prev_age = age - 1
                lx_prev = self.by_age[prev_age]["lx"]
                lx_curr = self.by_age[age]["lx"]
                if lx_prev == lx_curr:
                    return float(age)
                return prev_age + (lx_prev - target) / (lx_prev - lx_curr)
        return float(self.max_age)


def parse_date(raw: str | None) -> date | None:
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def age_between(start: date, end: date) -> float:
    return (end - start).days / 365.2425


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def pct(num: float, den: float) -> float:
    return 100.0 * num / den if den else 0.0


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def load_people() -> list[Person]:
    people: list[Person] = []
    for source in SOURCE_FILES:
        with source["file"].open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                name = row.get("Name", "").strip()
                if not name:
                    continue
                birth_year = None
                by_raw = row.get("Birth Year", "").strip()
                if by_raw:
                    try:
                        birth_year = int(float(by_raw))
                    except ValueError:
                        birth_year = None
                people.append(
                    Person(
                        name=name,
                        source_key=source["key"],
                        source_label=source["label"],
                        primary=source["primary"],
                        astronaut_group=row.get("Astronaut Group", "").strip(),
                        dob=parse_date(row.get("Date of Birth")),
                        dod=parse_date(row.get("Date of Death")),
                        reported_age=parse_float(row.get("Current Age or Age at Death")),
                        status=row.get("Status", "").strip(),
                        accidental_death=row.get("Accidental Death", "").strip().upper()
                        == "Y",
                        cause_note=row.get("Mort / cause note", "").strip(),
                        space_grandpa=row.get("Space Grandpa", "").strip().upper(),
                        space_grandpa_citation=row.get(
                            "Space Grandpa Citation", ""
                        ).strip(),
                        birth_year=birth_year,
                    )
                )
    return people


def cohort_summary(key: str, label: str, people: list[Person]) -> dict[str, object]:
    ages = [p.endpoint_age for p in people]
    deaths = [p for p in people if p.deceased]
    acc = [p for p in deaths if p.accidental_death]
    pre1970 = [p for p in deaths if p.pre1970_accidental_death]
    sg_y = [p for p in people if p.space_grandpa == "Y"]
    age80 = [p for p in people if p.reached_80]
    sg80 = [p for p in age80 if p.space_grandpa == "Y"]
    return {
        "cohort_key": key,
        "cohort": label,
        "n": len(people),
        "deaths_all_cause": len(deaths),
        "living_or_censored": len(people) - len(deaths),
        "accidental_deaths": len(acc),
        "pre1970_accidental_deaths": len(pre1970),
        "mean_age_death_or_censor": statistics.mean(ages) if ages else None,
        "median_age_death_or_censor": statistics.median(ages) if ages else None,
        "min_age_death_or_censor": min(ages) if ages else None,
        "max_age_death_or_censor": max(ages) if ages else None,
        "reached_80": len(age80),
        "reached_80_pct": pct(len(age80), len(people)),
        "reached_90": len([p for p in people if p.reached_90]),
        "reached_90_pct": pct(len([p for p in people if p.reached_90]), len(people)),
        "space_grandpa_y_all": len(sg_y),
        "space_grandpa_y_all_pct": pct(len(sg_y), len(people)),
        "space_grandpa_y_among_80": len(sg80),
        "space_grandpa_y_among_80_pct": pct(len(sg80), len(age80)),
        "age80_denominator": len(age80),
    }


def smr_summary(key: str, label: str, people: list[Person], life: LifeTable) -> dict[str, object]:
    endpoints = [p.endpoint_age for p in people]
    observed = sum(1 for p in people if p.deceased)
    expected = life.expected_events_by_endpoints(endpoints)
    smr = observed / expected if expected else None
    if observed > 0 and smr is not None:
        ci_low = smr * math.exp(-1.96 / math.sqrt(observed))
        ci_high = smr * math.exp(1.96 / math.sqrt(observed))
    else:
        ci_low = None
        ci_high = None
    return {
        "cohort_key": key,
        "cohort": label,
        "n": len(people),
        "observed_deaths": observed,
        "expected_deaths_ssa_1930_male_age30": expected,
        "smr": smr,
        "smr_ci95_low_log_approx": ci_low,
        "smr_ci95_high_log_approx": ci_high,
    }


def kaplan_meier_points(people: list[Person], x_max: float = 100.0) -> list[tuple[float, float]]:
    event_times = sorted({p.endpoint_age for p in people if p.deceased})
    survival = 1.0
    points: list[tuple[float, float]] = [(ENTRY_AGE, survival)]
    for t in event_times:
        if t < ENTRY_AGE:
            continue
        at_risk = sum(1 for p in people if p.endpoint_age >= t)
        deaths = sum(1 for p in people if p.deceased and abs(p.endpoint_age - t) < 1e-9)
        if at_risk <= 0 or deaths <= 0:
            continue
        points.append((t, survival))
        survival *= 1.0 - (deaths / at_risk)
        points.append((t, survival))
    if points[-1][0] < x_max:
        points.append((x_max, points[-1][1]))
    return points


def logrank_test(a: list[Person], b: list[Person]) -> dict[str, float]:
    times = sorted({p.endpoint_age for p in a + b if p.deceased})
    observed_a = 0.0
    expected_a = 0.0
    variance = 0.0
    for t in times:
        n_a = sum(1 for p in a if p.endpoint_age >= t)
        n_b = sum(1 for p in b if p.endpoint_age >= t)
        d_a = sum(1 for p in a if p.deceased and abs(p.endpoint_age - t) < 1e-9)
        d_b = sum(1 for p in b if p.deceased and abs(p.endpoint_age - t) < 1e-9)
        n_total = n_a + n_b
        d_total = d_a + d_b
        if n_total <= 1 or d_total <= 0:
            continue
        observed_a += d_a
        expected_a += d_total * n_a / n_total
        variance += (
            n_a
            * n_b
            * d_total
            * (n_total - d_total)
            / (n_total * n_total * (n_total - 1))
        )
    if variance <= 0:
        return {
            "observed_a": observed_a,
            "expected_a": expected_a,
            "z": 0.0,
            "chi_square": 0.0,
            "p_value": 1.0,
        }
    z = (observed_a - expected_a) / math.sqrt(variance)
    chi = z * z
    p_value = math.erfc(math.sqrt(chi / 2.0))
    return {
        "observed_a": observed_a,
        "expected_a": expected_a,
        "z": z,
        "chi_square": chi,
        "p_value": p_value,
    }


def quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def monte_carlo(
    key: str,
    label: str,
    people: list[Person],
    life: LifeTable,
    iterations: int,
    seed: int,
) -> tuple[dict[str, object], Counter[int]]:
    rng = random.Random(seed)
    endpoints = [p.endpoint_age for p in people]
    observed_deaths = sum(1 for p in people if p.deceased)
    observed_mean_age_or_censor = statistics.mean(endpoints)
    observed_survive80 = sum(1 for p in people if p.reached_80)
    observed_survive90 = sum(1 for p in people if p.reached_90)

    death_counts: list[int] = []
    mean_ages: list[float] = []
    survive80_counts: list[int] = []
    survive90_counts: list[int] = []
    death_dist: Counter[int] = Counter()

    for _ in range(iterations):
        deaths = 0
        sum_age_or_censor = 0.0
        survive80 = 0
        survive90 = 0
        for endpoint in endpoints:
            death_age = life.sample_death_age(rng)
            if death_age <= endpoint:
                deaths += 1
                sum_age_or_censor += death_age
            else:
                sum_age_or_censor += endpoint
            if death_age >= 80.0:
                survive80 += 1
            if death_age >= 90.0:
                survive90 += 1
        mean_age = sum_age_or_censor / len(endpoints)
        death_counts.append(deaths)
        mean_ages.append(mean_age)
        survive80_counts.append(survive80)
        survive90_counts.append(survive90)
        death_dist[deaths] += 1

    summary = {
        "cohort_key": key,
        "cohort": label,
        "n": len(people),
        "iterations": iterations,
        "seed": seed,
        "observed_deaths": observed_deaths,
        "sim_mean_deaths": statistics.mean(death_counts),
        "sim_deaths_p02_5": quantile(death_counts, 0.025),
        "sim_deaths_p50": quantile(death_counts, 0.5),
        "sim_deaths_p97_5": quantile(death_counts, 0.975),
        "p_sim_deaths_le_observed": sum(d <= observed_deaths for d in death_counts)
        / iterations,
        "p_sim_deaths_ge_observed": sum(d >= observed_deaths for d in death_counts)
        / iterations,
        "observed_mean_age_death_or_censor": observed_mean_age_or_censor,
        "sim_mean_age_death_or_censor": statistics.mean(mean_ages),
        "sim_mean_age_p02_5": quantile(mean_ages, 0.025),
        "sim_mean_age_p50": quantile(mean_ages, 0.5),
        "sim_mean_age_p97_5": quantile(mean_ages, 0.975),
        "p_sim_mean_age_ge_observed": sum(
            value >= observed_mean_age_or_censor for value in mean_ages
        )
        / iterations,
        "observed_survive80": observed_survive80,
        "sim_mean_survive80": statistics.mean(survive80_counts),
        "sim_survive80_p02_5": quantile(survive80_counts, 0.025),
        "sim_survive80_p50": quantile(survive80_counts, 0.5),
        "sim_survive80_p97_5": quantile(survive80_counts, 0.975),
        "p_sim_survive80_ge_observed": sum(
            value >= observed_survive80 for value in survive80_counts
        )
        / iterations,
        "observed_survive90": observed_survive90,
        "sim_mean_survive90": statistics.mean(survive90_counts),
        "sim_survive90_p02_5": quantile(survive90_counts, 0.025),
        "sim_survive90_p50": quantile(survive90_counts, 0.5),
        "sim_survive90_p97_5": quantile(survive90_counts, 0.975),
        "p_sim_survive90_ge_observed": sum(
            value >= observed_survive90 for value in survive90_counts
        )
        / iterations,
    }
    return summary, death_dist


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    # Table:
    #   group 1 success/fail = a/b
    #   group 2 success/fail = c/d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    n = row1 + row2

    def prob(x: int) -> float:
        return (
            math.comb(col1, x)
            * math.comb(n - col1, row1 - x)
            / math.comb(n, row1)
        )

    lo = max(0, row1 - (n - col1))
    hi = min(row1, col1)
    observed_p = prob(a)
    return sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= observed_p + 1e-15)


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
        for row in rows:
            writer.writerow(row)


def s(value: object) -> str:
    return html.escape(str(value))


def svg_line_chart(
    path: Path,
    title: str,
    subtitle: str,
    series: list[dict[str, object]],
    x_min: float = 30.0,
    x_max: float = 100.0,
    y_min: float = 0.0,
    y_max: float = 1.0,
) -> None:
    width = 1080
    height = 640
    left = 76
    right = 270
    top = 72
    bottom = 70
    plot_w = width - left - right
    plot_h = height - top - bottom

    def xmap(x: float) -> float:
        return left + (x - x_min) / (x_max - x_min) * plot_w

    def ymap(y: float) -> float:
        return top + (y_max - y) / (y_max - y_min) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">{s(title)}</text>',
        f'<text x="{left}" y="58" font-family="Arial, sans-serif" font-size="13" fill="#52616b">{s(subtitle)}</text>',
    ]

    for i in range(0, 11):
        y = i / 10
        yy = ymap(y)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="#e7ecef" stroke-width="1"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#6b7780">{int(y*100)}%</text>')
    for age in range(int(x_min), int(x_max) + 1, 10):
        xx = xmap(age)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+plot_h}" stroke="#f0f3f5" stroke-width="1"/>')
        parts.append(f'<text x="{xx:.1f}" y="{top+plot_h+24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#6b7780">{age}</text>')

    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#263238">Age</text>')
    parts.append(f'<text x="22" y="{top+plot_h/2}" text-anchor="middle" transform="rotate(-90 22 {top+plot_h/2})" font-family="Arial, sans-serif" font-size="13" fill="#263238">Survival from age 30</text>')

    for item in series:
        points = item["points"]
        color = item["color"]
        dash = item.get("dash", "")
        stroke_dash = f' stroke-dasharray="{dash}"' if dash else ""
        clipped = [
            (clamp(float(x), x_min, x_max), clamp(float(y), y_min, y_max))
            for x, y in points
            if float(x) >= x_min and float(x) <= x_max
        ]
        if not clipped:
            continue
        poly = " ".join(f"{xmap(x):.1f},{ymap(y):.1f}" for x, y in clipped)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="3"{stroke_dash} stroke-linejoin="round" stroke-linecap="round"/>')

    legend_x = left + plot_w + 34
    legend_y = top + 18
    for idx, item in enumerate(series):
        y = legend_y + idx * 32
        color = item["color"]
        dash = item.get("dash", "")
        stroke_dash = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x+28}" y2="{y}" stroke="{color}" stroke-width="4"{stroke_dash}/>')
        parts.append(f'<text x="{legend_x+38}" y="{y+4}" font-family="Arial, sans-serif" font-size="12" fill="#263238">{s(item["label"])}</text>')

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_smr_chart(path: Path, rows: list[dict[str, object]]) -> None:
    width = 980
    height = 560
    left = 78
    right = 36
    top = 70
    bottom = 150
    plot_w = width - left - right
    plot_h = height - top - bottom
    chart_rows = [r for r in rows if r["cohort_key"] in {"apollo", "other_all", "all_astronauts", "other_available"}]
    y_max = max(float(r["smr_ci95_high_log_approx"] or r["smr"]) for r in chart_rows) * 1.18
    y_max = max(1.4, y_max)

    def x_center(i: int) -> float:
        return left + (i + 0.5) * plot_w / len(chart_rows)

    def ymap(y: float) -> float:
        return top + (y_max - y) / y_max * plot_h

    colors = ["#1b75bb", "#c94c4c", "#4c8f5a", "#8a63b8"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">Standardized mortality ratio vs SSA 1930 male baseline</text>',
        f'<text x="{left}" y="57" font-family="Arial, sans-serif" font-size="13" fill="#52616b">Expected deaths use summed cumulative all-cause hazard from age 30 to each observed/censor age. Error bars are log-Poisson approximations.</text>',
    ]
    for i in range(0, 6):
        y = y_max * i / 5
        yy = ymap(y)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="#e7ecef" stroke-width="1"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#6b7780">{y:.1f}</text>')
    parts.append(f'<line x1="{left}" y1="{ymap(1.0):.1f}" x2="{left+plot_w}" y2="{ymap(1.0):.1f}" stroke="#263238" stroke-width="1.4" stroke-dasharray="6 5"/>')
    parts.append(f'<text x="{left+plot_w-4}" y="{ymap(1.0)-7:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#263238">SMR = 1.0</text>')
    for i, r in enumerate(chart_rows):
        xc = x_center(i)
        bar_w = min(112, plot_w / len(chart_rows) * 0.52)
        smr = float(r["smr"])
        low = float(r["smr_ci95_low_log_approx"])
        high = float(r["smr_ci95_high_log_approx"])
        y0 = ymap(0)
        y1 = ymap(smr)
        parts.append(f'<rect x="{xc-bar_w/2:.1f}" y="{y1:.1f}" width="{bar_w:.1f}" height="{y0-y1:.1f}" fill="{colors[i]}" opacity="0.88"/>')
        parts.append(f'<line x1="{xc:.1f}" y1="{ymap(low):.1f}" x2="{xc:.1f}" y2="{ymap(high):.1f}" stroke="#263238" stroke-width="1.5"/>')
        parts.append(f'<line x1="{xc-12:.1f}" y1="{ymap(low):.1f}" x2="{xc+12:.1f}" y2="{ymap(low):.1f}" stroke="#263238" stroke-width="1.5"/>')
        parts.append(f'<line x1="{xc-12:.1f}" y1="{ymap(high):.1f}" x2="{xc+12:.1f}" y2="{ymap(high):.1f}" stroke="#263238" stroke-width="1.5"/>')
        parts.append(f'<text x="{xc:.1f}" y="{y1-8:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#17202a">{smr:.2f}</text>')
        label = str(r["cohort"]).replace(" including ", " incl. ")
        lines = wrap_label(label, 18)
        for j, line in enumerate(lines[:4]):
            parts.append(f'<text x="{xc:.1f}" y="{top+plot_h+28+j*15:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#263238">{s(line)}</text>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def wrap_label(label: str, width: int) -> list[str]:
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= width:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def svg_bar_chart(
    path: Path,
    title: str,
    subtitle: str,
    rows: list[dict[str, object]],
    value_key: str,
    value_label: str,
    color: str,
) -> None:
    width = 900
    height = 520
    left = 76
    right = 34
    top = 72
    bottom = 130
    plot_w = width - left - right
    plot_h = height - top - bottom
    y_max = max(float(r[value_key]) for r in rows) * 1.18
    y_max = max(10.0, y_max)

    def x_center(i: int) -> float:
        return left + (i + 0.5) * plot_w / len(rows)

    def ymap(y: float) -> float:
        return top + (y_max - y) / y_max * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">{s(title)}</text>',
        f'<text x="{left}" y="57" font-family="Arial, sans-serif" font-size="13" fill="#52616b">{s(subtitle)}</text>',
    ]
    for i in range(0, 6):
        y = y_max * i / 5
        yy = ymap(y)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="#e7ecef" stroke-width="1"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#6b7780">{y:.0f}</text>')
    for i, r in enumerate(rows):
        xc = x_center(i)
        bar_w = min(120, plot_w / len(rows) * 0.48)
        val = float(r[value_key])
        y1 = ymap(val)
        y0 = ymap(0)
        parts.append(f'<rect x="{xc-bar_w/2:.1f}" y="{y1:.1f}" width="{bar_w:.1f}" height="{y0-y1:.1f}" fill="{color}" opacity="0.9"/>')
        parts.append(f'<text x="{xc:.1f}" y="{y1-8:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#17202a">{val:.1f}</text>')
        lines = wrap_label(str(r["cohort"]), 18)
        for j, line in enumerate(lines[:4]):
            parts.append(f'<text x="{xc:.1f}" y="{top+plot_h+27+j*15:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#263238">{s(line)}</text>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<text x="23" y="{top+plot_h/2}" text-anchor="middle" transform="rotate(-90 23 {top+plot_h/2})" font-family="Arial, sans-serif" font-size="13" fill="#263238">{s(value_label)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def svg_histogram(
    path: Path,
    title: str,
    subtitle: str,
    distribution: Counter[int],
    iterations: int,
    observed: int,
    color: str,
) -> None:
    width = 920
    height = 520
    left = 70
    right = 34
    top = 72
    bottom = 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    min_x = min(distribution)
    max_x = max(distribution)
    max_prob = max(count / iterations for count in distribution.values())

    def xmap(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x + 1) * plot_w

    def ymap(y: float) -> float:
        return top + (max_prob - y) / max_prob * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#17202a">{s(title)}</text>',
        f'<text x="{left}" y="57" font-family="Arial, sans-serif" font-size="13" fill="#52616b">{s(subtitle)}</text>',
    ]
    for i in range(0, 6):
        y = max_prob * i / 5
        yy = ymap(y)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke="#e7ecef" stroke-width="1"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#6b7780">{100*y:.1f}%</text>')
    bar_w = max(4.0, plot_w / (max_x - min_x + 1) * 0.78)
    for deaths in range(min_x, max_x + 1):
        prob = distribution.get(deaths, 0) / iterations
        x = xmap(deaths + 0.5)
        y1 = ymap(prob)
        y0 = ymap(0)
        parts.append(f'<rect x="{x-bar_w/2:.1f}" y="{y1:.1f}" width="{bar_w:.1f}" height="{y0-y1:.1f}" fill="{color}" opacity="0.82"/>')
        if deaths % 5 == 0:
            parts.append(f'<text x="{x:.1f}" y="{top+plot_h+22}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#6b7780">{deaths}</text>')
    obs_x = xmap(observed + 0.5)
    parts.append(f'<line x1="{obs_x:.1f}" y1="{top}" x2="{obs_x:.1f}" y2="{top+plot_h}" stroke="#111111" stroke-width="2.2"/>')
    parts.append(f'<text x="{obs_x+6:.1f}" y="{top+18}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#111111">Observed {observed}</text>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#263238" stroke-width="1.2"/>')
    parts.append(f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#263238">Deaths by observed/censor ages</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def markdown_table(rows: list[dict[str, object]], columns: list[tuple[str, str, int | None]]) -> str:
    header = "| " + " | ".join(label for _, label, _ in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        cells = []
        for key, _, digits in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                cells.append(fmt(value, digits if digits is not None else 2))
            else:
                cells.append(str(value))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep] + body)


def write_report(
    out_dir: Path,
    cohort_rows: list[dict[str, object]],
    smr_rows: list[dict[str, object]],
    mc_rows: list[dict[str, object]],
    vitality_rows: list[dict[str, object]],
    sg_tests: list[dict[str, object]],
    exclusions: list[Person],
    logrank_rows: list[dict[str, object]],
    life: LifeTable,
) -> None:
    key_cohorts = {"apollo", "other_all", "other_available", "all_astronauts"}
    cohort_key_rows = [r for r in cohort_rows if r["cohort_key"] in key_cohorts]
    smr_key_rows = [r for r in smr_rows if r["cohort_key"] in key_cohorts]
    mc_key_rows = [r for r in mc_rows if r["cohort_key"] in key_cohorts]
    vitality_key_rows = [r for r in vitality_rows if r["cohort_key"] in key_cohorts]

    lines = [
        "# Apollo 7-17 Mortality, Survival, and Late-Life Vitality Analysis",
        "",
        f"Analysis date: {ANALYSIS_DATE.isoformat()}",
        "",
        "## Methods",
        "",
        "- Apollo 7-17 = all rows in `07E-lunar-enriched.tsv` plus `08E-non-lunar-apollo-enriched.tsv`.",
        "- Other same-era astronauts = core NASA non-Apollo rows plus the deduplicated X-15/high-speed, X-20 Dyna-Soar, and MOL military comparison rows.",
        "- Astronaut-vs-general SMR and Monte Carlo calculations include accidental deaths, matching the all-cause SSA life table.",
        "- Apollo-vs-other direct comparisons use a separate `Other Apollo-available` cohort that removes non-Apollo pre-1970 accidental deaths.",
        "- The exclusion is operationalized from available fields as `Accidental Death=Y` and death date before 1970; the list is shown so narrower training-only exclusions can be audited.",
        "- General-population baseline = local `ssa-1930-male-cohort-lifetable.tsv`, described by its metadata as SSA Actuarial Study 116, Table 7, year of birth 1930, male cohort.",
        f"- Baseline is conditional on survival to age {ENTRY_AGE:.0f}. It is not a health-screened astronaut-candidate table.",
        f"- Monte Carlo uses {MC_ITERATIONS:,} iterations with seed {MC_SEED}.",
        "- Mental vitality is proxied only by the dataset's `Space Grandpa` field. SSA contains mortality only, so no general-population vitality rate is inferred.",
        "",
        "## SSA 1930 Male Baseline Conditional on Age 30",
        "",
        f"- Mean death age from age 30: {life.mean_death_age_from_30():.2f}",
        f"- Median death age from age 30: {life.median_death_age_from_30():.2f}",
        f"- Survival from age 30 to 80: {100 * life.survival_from_30(80):.1f}%",
        f"- Survival from age 30 to 90: {100 * life.survival_from_30(90):.1f}%",
        f"- Survival from age 30 to 95: {100 * life.survival_from_30(95):.1f}%",
        "",
        "## Cohort Summary",
        "",
        markdown_table(
            cohort_key_rows,
            [
                ("cohort", "Cohort", None),
                ("n", "N", None),
                ("deaths_all_cause", "Deaths", None),
                ("living_or_censored", "Living/censored", None),
                ("accidental_deaths", "Accidental deaths", None),
                ("pre1970_accidental_deaths", "Pre-1970 accidents", None),
                ("mean_age_death_or_censor", "Mean age", 1),
                ("median_age_death_or_censor", "Median age", 1),
                ("reached_80_pct", "Reached 80 %", 1),
                ("reached_90_pct", "Reached 90 %", 1),
            ],
        ),
        "",
        "## Pre-1970 Accidental Death Exclusions for Apollo-vs-Other",
        "",
    ]

    if exclusions:
        lines.append(
            markdown_table(
                [
                    {
                        "name": p.name,
                        "source": p.source_label,
                        "date_of_death": p.dod.isoformat() if p.dod else "",
                        "age": p.endpoint_age,
                        "cause": p.cause_note,
                    }
                    for p in exclusions
                ],
                [
                    ("name", "Name", None),
                    ("source", "Source", None),
                    ("date_of_death", "Death date", None),
                    ("age", "Age", 1),
                    ("cause", "Cause note", None),
                ],
            )
        )
    else:
        lines.append("No pre-1970 accidental deaths found in the non-Apollo pool.")

    lines.extend(
        [
            "",
            "## Standardized Mortality Ratio",
            "",
            markdown_table(
                smr_key_rows,
                [
                    ("cohort", "Cohort", None),
                    ("n", "N", None),
                    ("observed_deaths", "Observed deaths", None),
                    ("expected_deaths_ssa_1930_male_age30", "Expected deaths", 2),
                    ("smr", "SMR", 2),
                    ("smr_ci95_low_log_approx", "95% low", 2),
                    ("smr_ci95_high_log_approx", "95% high", 2),
                ],
            ),
            "",
            "Interpretation: SMR below 1.0 means fewer deaths than expected from summed age-specific all-cause hazard under the SSA 1930 male table after conditioning on survival to age 30.",
            "",
            "## Monte Carlo Against SSA 1930 Male Age-30 Baseline",
            "",
            markdown_table(
                mc_key_rows,
                [
                    ("cohort", "Cohort", None),
                    ("n", "N", None),
                    ("observed_deaths", "Observed deaths", None),
                    ("sim_mean_deaths", "Sim mean deaths", 2),
                    ("sim_deaths_p02_5", "Deaths p2.5", 0),
                    ("sim_deaths_p97_5", "Deaths p97.5", 0),
                    ("p_sim_deaths_ge_observed", "P(sim deaths >= obs)", 4),
                    ("observed_mean_age_death_or_censor", "Obs mean age", 2),
                    ("sim_mean_age_death_or_censor", "Sim mean age", 2),
                    ("p_sim_mean_age_ge_observed", "P(sim mean >= obs)", 4),
                ],
            ),
            "",
            "## Retention of Public Mental Vitality Proxy",
            "",
            markdown_table(
                vitality_key_rows,
                [
                    ("cohort", "Cohort", None),
                    ("n", "N", None),
                    ("reached_80", "Reached 80", None),
                    ("space_grandpa_y_among_80", "SG=Y among 80+", None),
                    ("space_grandpa_y_among_80_pct", "SG=Y among 80+ %", 1),
                    ("space_grandpa_y_all", "SG=Y all", None),
                    ("space_grandpa_y_all_pct", "SG=Y all %", 1),
                ],
            ),
            "",
            "Caution: this is a public-evidence proxy for high late-life activity, not a clinical cognition measure.",
            "",
            "### Vitality Proxy Direct Comparison",
            "",
            markdown_table(
                sg_tests,
                [
                    ("comparison", "Comparison", None),
                    ("apollo_sg_y", "Apollo SG=Y", None),
                    ("apollo_sg_den", "Apollo 80+ denom", None),
                    ("other_sg_y", "Other SG=Y", None),
                    ("other_sg_den", "Other 80+ denom", None),
                    ("risk_difference_pct_points", "Risk diff pct pts", 1),
                    ("fisher_two_sided_p", "Fisher p", 4),
                ],
            ),
            "",
            "## Direct Apollo-vs-Other Survival Tests",
            "",
            markdown_table(
                logrank_rows,
                [
                    ("comparison", "Comparison", None),
                    ("apollo_actual_deaths", "Apollo deaths", None),
                    ("other_actual_deaths", "Other deaths", None),
                    ("apollo_logrank_observed_events", "Apollo test events", 1),
                    ("apollo_logrank_expected_events", "Apollo expected events", 1),
                    ("z", "Log-rank z", 2),
                    ("chi_square", "Chi-square", 2),
                    ("p_value", "p", 4),
                ],
            ),
            "",
            "## Generated Files",
            "",
            "- `cohort_summary.csv`",
            "- `smr_summary.csv`",
            "- `monte_carlo_summary.csv`",
            "- `monte_carlo_death_count_distribution.csv`",
            "- `mental_vitality_summary.csv`",
            "- `kaplan_meier_points.csv`",
            "- `person_level_analysis.csv`",
            "- `pre1970_accident_exclusions.csv`",
            "- `km_astronauts_vs_ssa.svg`",
            "- `km_apollo_vs_other_available.svg`",
            "- `smr_summary.svg`",
            "- `mental_vitality_sg80.svg`",
            "- `monte_carlo_deaths_apollo.svg`",
            "- `monte_carlo_deaths_other_all.svg`",
            "",
        ]
    )
    (out_dir / "apollo_mortality_survival_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    life = LifeTable.load(SSA_FILE)
    people = load_people()

    duplicate_names = [name for name, count in Counter(p.name for p in people).items() if count > 1]
    if duplicate_names:
        raise ValueError(f"Duplicate people across final files: {duplicate_names}")

    apollo = [p for p in people if p.primary == "apollo"]
    other_all = [p for p in people if p.primary == "other"]
    military_only = [p for p in other_all if p.source_key.startswith("military_")]
    core_other = [p for p in other_all if p.source_key == "other_core_nasa"]
    other_pre1970_accidents = [p for p in other_all if p.pre1970_accidental_death]
    other_available = [p for p in other_all if not p.pre1970_accidental_death]
    all_astronauts = apollo + other_all

    cohorts = [
        ("apollo", "Apollo 7-17", apollo),
        ("other_all", "Other astronauts including military, all deaths", other_all),
        ("other_available", "Other Apollo-available, excl. pre-1970 accidents", other_available),
        ("all_astronauts", "All same-era astronauts including Apollo and military", all_astronauts),
        ("core_nasa_non_apollo", "Core NASA non-Apollo", core_other),
        ("military_only", "Military comparison rows only", military_only),
    ]

    cohort_rows = [cohort_summary(key, label, rows) for key, label, rows in cohorts]
    smr_rows = [smr_summary(key, label, rows, life) for key, label, rows in cohorts]

    vitality_rows = []
    for key, label, rows in cohorts:
        summary = cohort_summary(key, label, rows)
        vitality_rows.append(
            {
                "cohort_key": key,
                "cohort": label,
                "n": summary["n"],
                "reached_80": summary["reached_80"],
                "age80_denominator": summary["age80_denominator"],
                "space_grandpa_y_among_80": summary["space_grandpa_y_among_80"],
                "space_grandpa_y_among_80_pct": summary["space_grandpa_y_among_80_pct"],
                "space_grandpa_y_all": summary["space_grandpa_y_all"],
                "space_grandpa_y_all_pct": summary["space_grandpa_y_all_pct"],
            }
        )

    logrank_rows = []
    for comparison, comparator in [
        ("Apollo vs other Apollo-available excl. pre-1970 accidents", other_available),
        ("Apollo vs other all deaths included", other_all),
    ]:
        result = logrank_test(apollo, comparator)
        logrank_rows.append(
            {
                "comparison": comparison,
                "apollo_actual_deaths": sum(1 for p in apollo if p.deceased),
                "other_actual_deaths": sum(1 for p in comparator if p.deceased),
                "apollo_logrank_observed_events": result["observed_a"],
                "apollo_logrank_expected_events": result["expected_a"],
                "z": result["z"],
                "chi_square": result["chi_square"],
                "p_value": result["p_value"],
            }
        )

    # Fisher test for the SG proxy among those who reached age 80.
    sg_tests = []
    for comparison, comparator in [
        ("Apollo vs other Apollo-available, SG among 80+", other_available),
        ("Apollo vs other all, SG among 80+", other_all),
    ]:
        a80 = [p for p in apollo if p.reached_80]
        b80 = [p for p in comparator if p.reached_80]
        a_y = sum(1 for p in a80 if p.space_grandpa == "Y")
        b_y = sum(1 for p in b80 if p.space_grandpa == "Y")
        p_value = fisher_two_sided(a_y, len(a80) - a_y, b_y, len(b80) - b_y)
        sg_tests.append(
            {
                "comparison": comparison,
                "apollo_sg_y": a_y,
                "apollo_sg_den": len(a80),
                "other_sg_y": b_y,
                "other_sg_den": len(b80),
                "risk_difference_pct_points": pct(a_y, len(a80)) - pct(b_y, len(b80)),
                "fisher_two_sided_p": p_value,
            }
        )

    mc_rows = []
    mc_distribution_rows = []
    mc_dists: dict[str, Counter[int]] = {}
    for idx, (key, label, rows) in enumerate(
        [
            ("apollo", "Apollo 7-17", apollo),
            ("other_all", "Other astronauts including military, all deaths", other_all),
            ("other_available", "Other Apollo-available, excl. pre-1970 accidents", other_available),
            ("all_astronauts", "All same-era astronauts including Apollo and military", all_astronauts),
        ]
    ):
        summary, dist = monte_carlo(
            key,
            label,
            rows,
            life,
            MC_ITERATIONS,
            MC_SEED + idx * 1009,
        )
        mc_rows.append(summary)
        mc_dists[key] = dist
        for deaths, count in sorted(dist.items()):
            mc_distribution_rows.append(
                {
                    "cohort_key": key,
                    "cohort": label,
                    "deaths": deaths,
                    "simulations": count,
                    "probability": count / MC_ITERATIONS,
                }
            )

    person_rows = []
    for p in sorted(people, key=lambda x: (x.primary, x.source_key, x.name)):
        person_rows.append(
            {
                "name": p.name,
                "primary": p.primary,
                "source_key": p.source_key,
                "source_label": p.source_label,
                "astronaut_group": p.astronaut_group,
                "date_of_birth": p.dob.isoformat() if p.dob else "",
                "date_of_death": p.dod.isoformat() if p.dod else "",
                "endpoint_age": p.endpoint_age,
                "deceased": p.deceased,
                "accidental_death": p.accidental_death,
                "pre1970_accidental_death": p.pre1970_accidental_death,
                "included_in_apollo_vs_other_available": (
                    p.primary == "apollo"
                    or (p.primary == "other" and not p.pre1970_accidental_death)
                ),
                "reached_80": p.reached_80,
                "reached_90": p.reached_90,
                "space_grandpa": p.space_grandpa,
                "cause_note": p.cause_note,
            }
        )

    km_rows = []
    km_series = [
        ("ssa_1930_male_age30", "SSA 1930 male conditional age 30", [(age, life.survival_from_30(age)) for age in range(30, 101)]),
        ("apollo", "Apollo 7-17", kaplan_meier_points(apollo)),
        ("other_all", "Other incl. military, all deaths", kaplan_meier_points(other_all)),
        ("other_available", "Other Apollo-available excl. pre-1970 accidents", kaplan_meier_points(other_available)),
        ("all_astronauts", "All same-era astronauts", kaplan_meier_points(all_astronauts)),
    ]
    for key, label, points in km_series:
        for age, survival in points:
            km_rows.append(
                {
                    "series_key": key,
                    "series": label,
                    "age": age,
                    "survival_from_age30": survival,
                }
            )

    exclusions_rows = [
        {
            "name": p.name,
            "source_key": p.source_key,
            "source_label": p.source_label,
            "date_of_death": p.dod.isoformat() if p.dod else "",
            "endpoint_age": p.endpoint_age,
            "cause_note": p.cause_note,
        }
        for p in sorted(other_pre1970_accidents, key=lambda x: (x.dod or date.max, x.name))
    ]

    baseline_rows = [
        {
            "age": age,
            "survival_from_age30": life.survival_from_30(age),
            "death_probability_by_age_from30": life.death_probability_by_age(age),
        }
        for age in range(30, 101)
    ]

    write_csv(OUT_DIR / "cohort_summary.csv", cohort_rows)
    write_csv(OUT_DIR / "smr_summary.csv", smr_rows)
    write_csv(OUT_DIR / "mental_vitality_summary.csv", vitality_rows)
    write_csv(OUT_DIR / "logrank_tests.csv", logrank_rows)
    write_csv(OUT_DIR / "space_grandpa_fisher_tests.csv", sg_tests)
    write_csv(OUT_DIR / "monte_carlo_summary.csv", mc_rows)
    write_csv(OUT_DIR / "monte_carlo_death_count_distribution.csv", mc_distribution_rows)
    write_csv(OUT_DIR / "person_level_analysis.csv", person_rows)
    write_csv(OUT_DIR / "pre1970_accident_exclusions.csv", exclusions_rows)
    write_csv(OUT_DIR / "kaplan_meier_points.csv", km_rows)
    write_csv(OUT_DIR / "ssa_1930_male_age30_baseline.csv", baseline_rows)

    colors = {
        "ssa": "#343a40",
        "apollo": "#1b75bb",
        "other_all": "#c94c4c",
        "other_available": "#8a63b8",
        "all": "#4c8f5a",
    }
    svg_line_chart(
        OUT_DIR / "km_astronauts_vs_ssa.svg",
        "Kaplan-Meier survival from age 30",
        "Astronaut cohorts compared with SSA 1930 male cohort survival conditional on age 30",
        [
            {
                "label": "SSA 1930 male baseline",
                "points": [(age, life.survival_from_30(age)) for age in range(30, 101)],
                "color": colors["ssa"],
                "dash": "7 5",
            },
            {"label": "Apollo 7-17", "points": kaplan_meier_points(apollo), "color": colors["apollo"]},
            {"label": "Other incl. military, all deaths", "points": kaplan_meier_points(other_all), "color": colors["other_all"]},
            {"label": "All same-era astronauts", "points": kaplan_meier_points(all_astronauts), "color": colors["all"]},
        ],
    )
    svg_line_chart(
        OUT_DIR / "km_apollo_vs_other_available.svg",
        "Apollo vs Apollo-available comparator",
        "The comparator removes non-Apollo pre-1970 accidental deaths; SSA line remains all-cause reference",
        [
            {
                "label": "SSA 1930 male baseline",
                "points": [(age, life.survival_from_30(age)) for age in range(30, 101)],
                "color": colors["ssa"],
                "dash": "7 5",
            },
            {"label": "Apollo 7-17", "points": kaplan_meier_points(apollo), "color": colors["apollo"]},
            {
                "label": "Other Apollo-available",
                "points": kaplan_meier_points(other_available),
                "color": colors["other_available"],
            },
        ],
    )
    svg_smr_chart(OUT_DIR / "smr_summary.svg", smr_rows)
    svg_bar_chart(
        OUT_DIR / "mental_vitality_sg80.svg",
        "Late-life public vitality proxy",
        "Space Grandpa Y rate among astronauts who reached age 80+",
        [r for r in vitality_rows if r["cohort_key"] in {"apollo", "other_all", "other_available", "all_astronauts"}],
        "space_grandpa_y_among_80_pct",
        "SG=Y among 80+ (%)",
        "#2f8f83",
    )
    svg_histogram(
        OUT_DIR / "monte_carlo_deaths_apollo.svg",
        "Monte Carlo death-count distribution: Apollo 7-17",
        "SSA 1930 male cohort, conditional age 30, same observed/censor ages",
        mc_dists["apollo"],
        MC_ITERATIONS,
        sum(1 for p in apollo if p.deceased),
        colors["apollo"],
    )
    svg_histogram(
        OUT_DIR / "monte_carlo_deaths_other_all.svg",
        "Monte Carlo death-count distribution: other astronauts",
        "Includes military rows and accidental deaths for the general-population comparison",
        mc_dists["other_all"],
        MC_ITERATIONS,
        sum(1 for p in other_all if p.deceased),
        colors["other_all"],
    )

    write_report(
        OUT_DIR,
        cohort_rows,
        smr_rows,
        mc_rows,
        vitality_rows,
        sg_tests,
        other_pre1970_accidents,
        logrank_rows,
        life,
    )

    print(f"Wrote analysis outputs to {OUT_DIR}")
    print(f"People loaded: {len(people)}")
    print(f"Apollo: {len(apollo)}")
    print(f"Other all: {len(other_all)}")
    print(f"Other Apollo-available: {len(other_available)}")
    print(f"Pre-1970 accidental exclusions: {len(other_pre1970_accidents)}")


if __name__ == "__main__":
    main()
