#!/usr/bin/env python3
"""Independent audit of corrected Stage 2R without importing its analysis."""

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


CENSOR = date(2026, 6, 1)
REPS = 50_000
SEED = 20_260_721
Z = 1.959963984540054


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse(value: str) -> date | None:
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


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def bootstrap_difference(left: list[int], right: list[int]) -> tuple[float, float, float]:
    rng = random.Random(SEED)
    estimates = []
    for _ in range(REPS):
        p1 = sum(left[rng.randrange(len(left))] for _ in left) / len(left)
        p0 = sum(right[rng.randrange(len(right))] for _ in right) / len(right)
        estimates.append(p1 - p0)
    point = sum(left) / len(left) - sum(right) / len(right)
    return point, percentile(estimates, 0.025), percentile(estimates, 0.975)


def wilson(successes: int, total: int) -> tuple[float, float]:
    p = successes / total
    denominator = 1.0 + Z * Z / total
    center = (p + Z * Z / (2 * total)) / denominator
    half = Z * math.sqrt(p * (1 - p) / total + Z * Z / (4 * total * total)) / denominator
    return center - half, center + half


def newcombe(a: int, n1: int, c: int, n0: int) -> tuple[float, float]:
    p1, p0 = a / n1, c / n0
    l1, u1 = wilson(a, n1)
    l0, u0 = wilson(c, n0)
    lower = p1 - p0 - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    upper = p1 - p0 + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return lower, upper


def aj(records: list[tuple[float, int]], horizon: float) -> tuple[float, int]:
    grouped: dict[float, list[int]] = defaultdict(list)
    for time, status in records:
        grouped[time].append(status)
    risk = len(records)
    survival = 1.0
    cumulative = 0.0
    for time in sorted(grouped):
        if time > horizon:
            break
        statuses = grouped[time]
        target = sum(status == 1 for status in statuses)
        competing = sum(status == 2 for status in statuses)
        cumulative += survival * target / risk
        survival *= 1.0 - (target + competing) / risk
        risk -= len(statuses)
    under_observation = sum(time >= horizon for time, _ in records)
    return cumulative, under_observation


def close(actual: float, expected: float, tolerance: float = 8e-9) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    cohort = read(root / "stage1/cohort.csv")
    outcomes = read(root / "stage1c/PERSON_OUTCOMES.csv")
    worklist = read(root / "stage1c/research_worklist.csv")
    evidence = read(root / "stage1c/EVIDENCE_EVENTS.csv")
    outcome = {row["person_id"]: row for row in outcomes}
    research = {row["person_id"]: row["research_id"] for row in worklist}
    function: dict[str, list[date]] = defaultdict(list)
    for row in evidence:
        if row["qualifies"] == "1" and row["evidence_type"] == "QUALIFYING_FUNCTION_EVENT":
            function[row["person_id"]].append(parse(row["analysis_event_date"]))
    for values in function.values():
        values.sort()

    people = []
    for row in cohort:
        if outcome[row["person_id"]]["eligible_age80"] != "1":
            continue
        birth = parse(row["birth_date"])
        death = parse(row["death_date"])
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
            "function": function[row["person_id"]],
            "groups": {
                "APOLLO_FLEW": apollo,
                "OTHER_ALL": row["other_all"] == "1",
                "CORE_NASA_NON_APOLLO": row["core_nasa_non_apollo"] == "1",
                "MILITARY_ONLY": military,
            },
        })

    def group(name: str, without_r001: bool = False):
        return [
            person for person in people
            if person["groups"][name]
            and (not without_r001 or person["research"] != "R001")
        ]

    def detected(person) -> int:
        return int(bool(person["function"]))

    problems = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    require(len(people) == 57, "eligible total")
    require(len(group("APOLLO_FLEW")) == 22, "Apollo eligible")
    require(len(group("OTHER_ALL")) == 35, "Other eligible")

    summary = read(root / "stage2r/RESULTS_SUMMARY.csv")
    result = {
        (row["section"], row["analysis"], row["metric"]): row
        for row in summary
    }
    primary = result[("PRIMARY_CONTRAST", "UNRESTRICTED_AGE_80_PLUS", "risk_difference")]
    bootstrap = result[("PRIMARY_CONTRAST", "UNRESTRICTED_AGE_80_PLUS", "risk_difference_bootstrap")]

    left = [detected(person) for person in group("APOLLO_FLEW")]
    right = [detected(person) for person in group("OTHER_ALL")]
    require((sum(left), len(left), sum(right), len(right)) == (3, 22, 2, 35), "primary counts")
    point, boot_low, boot_high = bootstrap_difference(left, right)
    new_low, new_high = newcombe(3, 22, 2, 35)
    for actual, expected, label in (
        (point, float(primary["estimate"]), "primary point"),
        (new_low, float(primary["ci_lower"]), "Newcombe lower"),
        (new_high, float(primary["ci_upper"]), "Newcombe upper"),
        (boot_low, float(bootstrap["ci_lower"]), "bootstrap lower"),
        (boot_high, float(bootstrap["ci_upper"]), "bootstrap upper"),
    ):
        try:
            close(actual, expected)
        except AssertionError:
            problems.append(label)

    expected_sensitivities = {
        "CORE_NASA_NON_APOLLO": (3, 22, 2, 28, 0.064935065),
        "MILITARY_ONLY": (3, 22, 1, 13, 0.059440559),
    }
    for name, expected in expected_sensitivities.items():
        detected_left = sum(detected(person) for person in group("APOLLO_FLEW"))
        detected_right = sum(detected(person) for person in group(name))
        observed = (detected_left, 22, detected_right, len(group(name)))
        require(observed == expected[:4], f"{name} counts")
        close(detected_left / 22 - detected_right / len(group(name)), expected[4])
    require(
        (
            sum(detected(person) for person in group("APOLLO_FLEW", True)),
            len(group("APOLLO_FLEW", True)),
            sum(detected(person) for person in group("OTHER_ALL", True)),
            len(group("OTHER_ALL", True)),
        ) == (2, 21, 2, 35),
        "R001 sensitivity counts",
    )

    def competing_record(person) -> tuple[float, int]:
        b80 = add_years(person["birth"], 80)
        end = person["death"] if person["death"] and person["death"] <= CENSOR else CENSOR
        first = person["function"][0] if person["function"] else None
        if first and first <= end:
            return age(person["birth"], first) - 80.0, 1
        if person["death"] and person["death"] <= CENSOR:
            return age(person["birth"], person["death"]) - 80.0, 2
        return age(person["birth"], CENSOR) - 80.0, 0

    readouts = {
        (row["group"], int(row["years_after_80"])): row
        for row in read(root / "stage2r/AALEN_JOHANSEN_READOUTS.csv")
    }
    for name in ("APOLLO_FLEW", "OTHER_ALL"):
        records = [competing_record(person) for person in group(name)]
        for horizon in (5, 10, 15):
            value, at_risk = aj(records, horizon)
            artifact = readouts[(name, horizon)]
            try:
                close(value, float(artifact["cumulative_incidence"]))
            except AssertionError:
                problems.append(f"AJ {name} {horizon}")
            require(at_risk == int(artifact["n_under_observation"]), f"risk set {name} {horizon}")

    detected_people = [person for person in people if detected(person)]
    event_ages = sorted(
        (person["function"][-1] - person["birth"]).days / 365.2425
        for person in detected_people
    )
    expected_ages = [81.978411603, 83.585563016, 88.431658419, 88.615098188, 90.641149373]
    require(len(event_ages) == 5, "event-age count")
    for actual, expected in zip(event_ages, expected_ages):
        try:
            close(actual, expected)
        except AssertionError:
            problems.append("event age mismatch")

    manifest = read(root / "stage2r/LOCKED_INPUT_HASHES.csv")
    for row in manifest:
        digest = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
        require(
            digest == row["sha256_before"] == row["sha256_after"]
            and row["unchanged"] == "1",
            f"locked hash {row['path']}",
        )

    conclusion = (root / "stage2r/CORRECTED_CONCLUSION.md").read_text(encoding="utf-8")
    require("**NOT_DETECTED**" in conclusion and "**HIGHER**" in conclusion, "classification")
    require("age 80 or older" in conclusion, "unrestricted conclusion")

    print(json.dumps({
        "problems": problems,
        "summary": {
            "eligible": len(people),
            "apollo_detected": sum(left),
            "apollo_eligible": len(left),
            "other_detected": sum(right),
            "other_eligible": len(right),
            "risk_difference": point,
            "newcombe_95": [new_low, new_high],
            "bootstrap_95": [boot_low, boot_high],
            "latest_detected_age": max(event_ages),
            "locked_input_files": len(manifest),
        },
    }, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
