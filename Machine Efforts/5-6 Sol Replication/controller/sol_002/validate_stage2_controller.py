#!/usr/bin/env python3
"""Independent mechanical audit of the locked sol_002 Stage 2 results.

This intentionally does not import the experimenter's analysis module.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import fmean


LANDMARK = date(1973, 1, 1)
CENSOR = date(2026, 6, 1)
HORIZON = 50.0
REPS = 50_000
SEED = 20_260_721


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def d(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def age(birth: date, when: date) -> float:
    whole = when.year - birth.year
    if (when.month, when.day) < (birth.month, birth.day):
        whole -= 1
    lower = add_years(birth, whole)
    upper = add_years(birth, whole + 1)
    return whole + (when - lower).days / (upper - lower).days


def elapsed(start: date, end: date) -> float:
    return (end - start).days / 365.2425


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = p * (len(ordered) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def rmst(observations: list[tuple[float, int]]) -> float:
    at_risk = len(observations)
    survival = 1.0
    prior = 0.0
    area = 0.0
    grouped: dict[float, list[int]] = defaultdict(list)
    for time, event in observations:
        grouped[time].append(event)
    for time in sorted(grouped):
        if time > HORIZON:
            break
        area += survival * (time - prior)
        statuses = grouped[time]
        deaths = sum(statuses)
        if deaths:
            survival *= 1.0 - deaths / at_risk
        at_risk -= len(statuses)
        prior = time
    return area + survival * max(0.0, HORIZON - prior)


def cif(observations: list[tuple[float, int]]) -> float:
    at_risk = len(observations)
    event_free = 1.0
    value = 0.0
    grouped: dict[float, list[int]] = defaultdict(list)
    for time, status in observations:
        grouped[time].append(status)
    for time in sorted(grouped):
        if time >= 5.0:
            break
        statuses = grouped[time]
        target = sum(status == 1 for status in statuses)
        competing = sum(status == 2 for status in statuses)
        value += event_free * target / at_risk
        event_free *= 1.0 - (target + competing) / at_risk
        at_risk -= len(statuses)
    return value


def boot(
    first: list[tuple[float, int]],
    second: list[tuple[float, int]],
    metric,
) -> tuple[float, float, float]:
    rng = random.Random(SEED)
    estimates = []
    for _ in range(REPS):
        left = [first[rng.randrange(len(first))] for _ in first]
        right = [second[rng.randrange(len(second))] for _ in second]
        estimates.append(metric(left) - metric(right))
    return (
        metric(first) - metric(second),
        percentile(estimates, 0.025),
        percentile(estimates, 0.975),
    )


def invert_2x2(matrix: list[list[float]]) -> list[list[float]]:
    det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return [
        [matrix[1][1] / det, -matrix[0][1] / det],
        [-matrix[1][0] / det, matrix[0][0] / det],
    ]


def cox_score_information(
    times: list[float],
    statuses: list[int],
    covariates: list[list[float]],
    beta: list[float],
) -> tuple[list[float], list[list[float]]]:
    weights = [
        math.exp(beta[0] * x[0] + beta[1] * x[1])
        for x in covariates
    ]
    score = [0.0, 0.0]
    information = [[0.0, 0.0], [0.0, 0.0]]
    for current in sorted({times[i] for i, status in enumerate(statuses) if status}):
        deaths = [i for i in range(len(times)) if statuses[i] and times[i] == current]
        risk = [i for i in range(len(times)) if times[i] >= current]
        tied = len(deaths)
        s0 = sum(weights[i] for i in risk)
        s1 = [sum(weights[i] * covariates[i][j] for i in risk) for j in range(2)]
        s2 = [
            [
                sum(weights[i] * covariates[i][j] * covariates[i][k] for i in risk)
                for k in range(2)
            ]
            for j in range(2)
        ]
        e0 = sum(weights[i] for i in deaths)
        e1 = [sum(weights[i] * covariates[i][j] for i in deaths) for j in range(2)]
        e2 = [
            [
                sum(weights[i] * covariates[i][j] * covariates[i][k] for i in deaths)
                for k in range(2)
            ]
            for j in range(2)
        ]
        for j in range(2):
            score[j] += sum(covariates[i][j] for i in deaths)
        for tie_index in range(tied):
            fraction = tie_index / tied
            denominator = s0 - fraction * e0
            mean = [(s1[j] - fraction * e1[j]) / denominator for j in range(2)]
            for j in range(2):
                score[j] -= mean[j]
                for k in range(2):
                    moment = (s2[j][k] - fraction * e2[j][k]) / denominator
                    information[j][k] += moment - mean[j] * mean[k]
    return score, information


def close(actual: float, expected: float, tolerance: float = 8e-7) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    cohort = rows(root / "stage1/cohort.csv")
    worklist = rows(root / "stage1c/research_worklist.csv")
    outcomes = rows(root / "stage1c/PERSON_OUTCOMES.csv")
    events = rows(root / "stage1c/EVIDENCE_EVENTS.csv")
    research = {row["person_id"]: row["research_id"] for row in worklist}
    outcome = {row["person_id"]: row for row in outcomes}
    function_by_person: dict[str, list[date]] = defaultdict(list)
    for row in events:
        if (
            row["qualifies"] == "1"
            and row["evidence_type"] == "QUALIFYING_FUNCTION_EVENT"
        ):
            function_by_person[row["person_id"]].append(d(row["analysis_event_date"]))
    for dates in function_by_person.values():
        dates.sort()

    people = []
    for row in cohort:
        birth = d(row["birth_date"])
        death = d(row["death_date"])
        end = min(death, CENSOR) if death else CENSOR
        apollo = row["apollo_flew"] == "1"
        military = not apollo and any(
            row[name] == "1"
            for name in ("military_x15", "military_dyna_soar", "military_mol")
        )
        people.append({
            "id": row["person_id"],
            "research": research[row["person_id"]],
            "birth": birth,
            "death": death,
            "end": end,
            "function": function_by_person[row["person_id"]],
            "eligible": outcome[row["person_id"]]["eligible_age80"] == "1",
            "groups": {
                "APOLLO_FLEW": apollo,
                "OTHER_ALL": row["other_all"] == "1",
                "CORE_NASA_NON_APOLLO": row["core_nasa_non_apollo"] == "1",
                "MILITARY_ONLY": military,
            },
        })

    problems = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    expected_counts = {
        "APOLLO_FLEW": 29,
        "OTHER_ALL": 66,
        "CORE_NASA_NON_APOLLO": 44,
        "MILITARY_ONLY": 30,
    }
    for group, expected in expected_counts.items():
        require(sum(p["groups"][group] for p in people) == expected, f"{group} count")

    def selected(group: str, predicate=lambda _: True):
        return [p for p in people if p["groups"][group] and predicate(p)]

    alive_landmark = lambda p: p["death"] is None or p["death"] >= LANDMARK

    def survival_observation(p):
        return elapsed(LANDMARK, p["end"]), int(p["death"] is not None)

    rmst_artifact = {
        row["contrast"]: row
        for row in rows(root / "stage2/survival_landmark_rmst.csv")
    }
    for comparator in ("OTHER_ALL", "CORE_NASA_NON_APOLLO", "MILITARY_ONLY"):
        left = [survival_observation(p) for p in selected("APOLLO_FLEW", alive_landmark)]
        right = [survival_observation(p) for p in selected(comparator, alive_landmark)]
        estimate = boot(left, right, rmst)
        artifact = rmst_artifact[f"APOLLO_FLEW vs {comparator}"]
        for key, value in zip(
            ("apollo_minus_comparator_rmst_years", "bootstrap95_lower", "bootstrap95_upper"),
            estimate,
        ):
            try:
                close(value, float(artifact[key]))
            except AssertionError:
                problems.append(f"RMST mismatch {comparator} {key}")

    def public_observation(p):
        b80 = add_years(p["birth"], 80)
        b85 = add_years(p["birth"], 85)
        first = p["function"][0] if p["function"] else None
        if first and b80 <= first < b85 and first <= CENSOR:
            return age(p["birth"], first) - 80.0, 1
        if p["death"] and b80 <= p["death"] < b85:
            return age(p["birth"], p["death"]) - 80.0, 2
        end = min(b85, CENSOR, p["end"])
        return max(0.0, age(p["birth"], end) - 80.0), 0

    public_artifact = {
        row["contrast"]: row
        for row in rows(root / "stage2/public_function_primary.csv")
    }
    for comparator in ("OTHER_ALL", "CORE_NASA_NON_APOLLO", "MILITARY_ONLY"):
        left = [public_observation(p) for p in selected("APOLLO_FLEW", lambda p: p["eligible"])]
        right = [public_observation(p) for p in selected(comparator, lambda p: p["eligible"])]
        estimate = boot(left, right, cif)
        artifact = public_artifact[f"APOLLO_FLEW vs {comparator}"]
        for key, value in zip(
            ("apollo_minus_comparator_risk_difference", "bootstrap95_lower", "bootstrap95_upper"),
            estimate,
        ):
            try:
                close(value, float(artifact[key]))
            except AssertionError:
                problems.append(f"public mismatch {comparator} {key}")

    no_r001 = lambda p: p["eligible"] and p["research"] != "R001"
    left = [public_observation(p) for p in selected("APOLLO_FLEW", no_r001)]
    right = [public_observation(p) for p in selected("OTHER_ALL", no_r001)]
    technical = boot(left, right, cif)
    technical_row = public_artifact["APOLLO_FLEW vs OTHER_ALL, R001 excluded"]
    for key, value in zip(
        ("apollo_minus_comparator_risk_difference", "bootstrap95_lower", "bootstrap95_upper"),
        technical,
    ):
        try:
            close(value, float(technical_row[key]))
        except AssertionError:
            problems.append(f"R001 sensitivity mismatch {key}")

    crude = {
        row["contrast"]: row
        for row in rows(root / "stage2/public_function_crude.csv")
    }
    primary_crude = crude["APOLLO_FLEW vs OTHER_ALL"]
    require(
        (
            int(primary_crude["apollo_detected"]),
            int(primary_crude["apollo_eligible"]),
            int(primary_crude["comparator_detected"]),
            int(primary_crude["comparator_eligible"]),
        ) == (3, 22, 2, 35),
        "crude primary counts",
    )

    cox_people = selected("APOLLO_FLEW", alive_landmark) + selected("OTHER_ALL", alive_landmark)
    times = [survival_observation(p)[0] for p in cox_people]
    statuses = [survival_observation(p)[1] for p in cox_people]
    group_values = [1.0] * len(selected("APOLLO_FLEW", alive_landmark)) + [
        0.0
    ] * len(selected("OTHER_ALL", alive_landmark))
    ages = [age(p["birth"], LANDMARK) for p in cox_people]
    center = fmean(ages)
    covariates = [[group, value - center] for group, value in zip(group_values, ages)]
    cox_rows = rows(root / "stage2/cox_model.csv")
    beta = [math.log(float(cox_rows[0]["hazard_ratio"])), math.log(float(cox_rows[1]["hazard_ratio"]))]
    score, information = cox_score_information(times, statuses, covariates, beta)
    max_cox_score = max(abs(value) for value in score)
    require(max_cox_score < 3e-4, "Cox score not at rounded-artifact optimum")
    variance = invert_2x2(information)
    for index in range(2):
        try:
            close(math.sqrt(variance[index][index]), float(cox_rows[index]["standard_error"]), 2e-6)
        except AssertionError:
            problems.append(f"Cox SE mismatch term {index}")

    life = rows(root / "stage2/ssa_male_cohort_expectations.csv")
    require({int(row["birth_year"]) for row in life} == set(range(1921, 1943)), "SSA year coverage")
    anchors = {1921: (62.75, 0.310608), 1930: (66.09, 0.366750), 1940: (69.55, 0.423550), 1942: (70.46, 0.432310)}
    life_by_year = {int(row["birth_year"]): row for row in life}
    for year, values in anchors.items():
        close(float(life_by_year[year]["male_cohort_life_expectancy_at_birth"]), values[0])
        close(float(life_by_year[year]["male_cohort_survival_to_age80"]), values[1])

    conclusion = (root / "stage2/BLIND_CONCLUSION.md").read_text(encoding="utf-8")
    require("SURVIVAL: **NOT_DETECTED / HIGHER**" in conclusion, "survival classification")
    require("PUBLIC FUNCTION: **NOT_DETECTED / HIGHER**" in conclusion, "public classification")
    require("No prespecified descriptive anomaly is detected." in conclusion, "narrow conclusion")

    stage_complete = (root / "stage2/STAGE_COMPLETE.md").read_text(encoding="utf-8")
    for required in (
        "ANALYSIS_DECISIONS.md", "ANALYSIS_REPORT.md", "RESULTS_SUMMARY.csv",
        "VALIDATION.md", "CONTAMINATION.md", "BLIND_CONCLUSION.md",
        "STAGE_COMPLETE.md", "analysis.py", "validate.py",
    ):
        require(f"`stage2/{required}`" in stage_complete, f"missing artifact declaration {required}")

    print(json.dumps({
        "problems": problems,
        "summary": {
            "people": len(people),
            "apollo": expected_counts["APOLLO_FLEW"],
            "other_all": expected_counts["OTHER_ALL"],
            "rmst_primary": float(rmst_artifact["APOLLO_FLEW vs OTHER_ALL"]["apollo_minus_comparator_rmst_years"]),
            "public_primary": float(public_artifact["APOLLO_FLEW vs OTHER_ALL"]["apollo_minus_comparator_risk_difference"]),
            "bootstrap_replicates_per_contrast": REPS,
            "cox_events": sum(statuses),
            "cox_max_abs_score_at_rounded_coefficients": max_cox_score,
            "ssa_years": len(life),
        },
    }, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
