#!/usr/bin/env python3
"""Corrected Stage 2R public-function analysis using only the standard library."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path
from statistics import NormalDist, mean, median
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "stage2r"
ADMIN_END = date(2026, 6, 1)
BOOTSTRAP_SEED = 20260721
BOOTSTRAP_REPLICATES = 50_000
ALPHA = 0.05
Z975 = NormalDist().inv_cdf(0.975)
DAY_YEAR = 365.2425
LOCKED_DIRS = ("stage1", "stage1b", "stage1c")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def birthday_80(birth: date) -> date:
    try:
        return birth.replace(year=birth.year + 80)
    except ValueError:
        return date(birth.year + 80, 2, 28)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def locked_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    for dirname in LOCKED_DIRS:
        base = ROOT / dirname
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            result[path.relative_to(ROOT).as_posix()] = file_sha256(path)
    return result


def csv_bytes(fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({key: display_value(row.get(key, "")) for key in fieldnames})
    return buffer.getvalue().encode("utf-8")


def display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{value:.9f}"
    return str(value)


def fmt_num(value: float | None, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NE"
    if math.isinf(value):
        return "∞" if value > 0 else "−∞"
    return f"{value:.{digits}f}"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "NE"
    return f"{100.0 * value:.{digits}f}%"


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def quartiles(values: list[float]) -> tuple[float, float, float]:
    return (
        percentile(values, 0.25),
        percentile(values, 0.50),
        percentile(values, 0.75),
    )


def binomial_cdf(k: int, n: int, probability: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if probability <= 0.0:
        return 1.0
    if probability >= 1.0:
        return 0.0
    return sum(
        math.comb(n, j)
        * probability**j
        * (1.0 - probability) ** (n - j)
        for j in range(k + 1)
    )


def bisect_decreasing(function, target: float) -> float:
    low, high = 0.0, 1.0
    for _ in range(100):
        middle = (low + high) / 2.0
        if function(middle) > target:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def clopper_pearson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    lower = 0.0
    upper = 1.0
    if successes > 0:
        lower = bisect_decreasing(
            lambda p: binomial_cdf(successes - 1, total, p),
            1.0 - ALPHA / 2.0,
        )
    if successes < total:
        upper = bisect_decreasing(
            lambda p: binomial_cdf(successes, total, p),
            ALPHA / 2.0,
        )
    return lower, upper


def wilson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    p = successes / total
    z2 = Z975 * Z975
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half = (
        Z975
        * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total * total))
        / denominator
    )
    return max(0.0, center - half), min(1.0, center + half)


def newcombe_difference(
    x1: int, n1: int, x0: int, n0: int
) -> tuple[float, float, float]:
    p1, p0 = x1 / n1, x0 / n0
    l1, u1 = wilson(x1, n1)
    l0, u0 = wilson(x0, n0)
    difference = p1 - p0
    lower = difference - math.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    upper = difference + math.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    return difference, max(-1.0, lower), min(1.0, upper)


def constrained_null_probability(
    x1: int, n1: int, x0: int, n0: int, ratio: float
) -> float:
    upper = min(1.0, 1.0 / ratio)
    epsilon = max(1e-15, upper * 1e-15)
    low, high = epsilon, upper - epsilon

    def log_likelihood(p0: float) -> float:
        p1 = ratio * p0
        terms = ((x1, n1, p1), (x0, n0, p0))
        value = 0.0
        for x, n, p in terms:
            if x:
                if p <= 0.0:
                    return -math.inf
                value += x * math.log(p)
            if n - x:
                if p >= 1.0:
                    return -math.inf
                value += (n - x) * math.log1p(-p)
        return value

    golden = (math.sqrt(5.0) - 1.0) / 2.0
    c = high - golden * (high - low)
    d = low + golden * (high - low)
    fc, fd = log_likelihood(c), log_likelihood(d)
    for _ in range(160):
        if fc > fd:
            high, d, fd = d, c, fc
            c = high - golden * (high - low)
            fc = log_likelihood(c)
        else:
            low, c, fc = c, d, fd
            d = low + golden * (high - low)
            fd = log_likelihood(d)
    return (low + high) / 2.0


def risk_ratio_score_statistic(
    x1: int, n1: int, x0: int, n0: int, ratio: float
) -> float:
    p0 = constrained_null_probability(x1, n1, x0, n0, ratio)
    p1 = ratio * p0
    observed = x1 / n1 - ratio * (x0 / n0)
    variance = p1 * (1.0 - p1) / n1 + ratio * ratio * p0 * (1.0 - p0) / n0
    if variance <= 0.0:
        return math.inf if observed else 0.0
    return observed * observed / variance


def risk_ratio_score_interval(
    x1: int, n1: int, x0: int, n0: int
) -> tuple[float, float, float]:
    p1, p0 = x1 / n1, x0 / n0
    if p0 == 0.0:
        point = math.inf if p1 > 0.0 else math.nan
    else:
        point = p1 / p0
    if not math.isfinite(point) or point <= 0.0:
        return point, 0.0, math.inf

    critical = Z975 * Z975

    def objective(log_ratio: float) -> float:
        return (
            risk_ratio_score_statistic(x1, n1, x0, n0, math.exp(log_ratio))
            - critical
        )

    center = math.log(point)

    lower_out = center
    step = 0.5
    while lower_out > -60.0 and objective(lower_out) < 0.0:
        lower_out -= step
        step *= 1.25
    if objective(lower_out) < 0.0:
        lower = 0.0
    else:
        outside, inside = lower_out, center
        for _ in range(100):
            middle = (outside + inside) / 2.0
            if objective(middle) > 0.0:
                outside = middle
            else:
                inside = middle
        lower = math.exp((outside + inside) / 2.0)

    upper_out = center
    step = 0.5
    while upper_out < 60.0 and objective(upper_out) < 0.0:
        upper_out += step
        step *= 1.25
    if objective(upper_out) < 0.0:
        upper = math.inf
    else:
        inside, outside = center, upper_out
        for _ in range(100):
            middle = (inside + outside) / 2.0
            if objective(middle) < 0.0:
                inside = middle
            else:
                outside = middle
        upper = math.exp((inside + outside) / 2.0)
    return point, lower, upper


def conditional_distribution(
    n1: int, n0: int, total_successes: int, log_odds_ratio: float
) -> tuple[list[int], list[float]]:
    xmin = max(0, total_successes - n0)
    xmax = min(n1, total_successes)
    support = list(range(xmin, xmax + 1))
    log_weights = [
        math.log(math.comb(n1, x))
        + math.log(math.comb(n0, total_successes - x))
        + x * log_odds_ratio
        for x in support
    ]
    maximum = max(log_weights)
    weights = [math.exp(value - maximum) for value in log_weights]
    total = sum(weights)
    return support, [value / total for value in weights]


def conditional_exact_odds_ratio_interval(
    a: int, b: int, c: int, d: int
) -> tuple[float, float, float]:
    n1, n0, successes = a + b, c + d, a + c
    xmin, xmax = max(0, successes - n0), min(n1, successes)
    if b * c == 0:
        point = math.inf if a * d > 0 else math.nan
    else:
        point = (a * d) / (b * c)

    def survival(log_or: float) -> float:
        support, probabilities = conditional_distribution(n1, n0, successes, log_or)
        return sum(p for x, p in zip(support, probabilities) if x >= a)

    def cdf(log_or: float) -> float:
        support, probabilities = conditional_distribution(n1, n0, successes, log_or)
        return sum(p for x, p in zip(support, probabilities) if x <= a)

    if a == xmin:
        lower = 0.0
    else:
        low, high = -60.0, 60.0
        for _ in range(140):
            middle = (low + high) / 2.0
            if survival(middle) < ALPHA / 2.0:
                low = middle
            else:
                high = middle
        lower = math.exp((low + high) / 2.0)

    if a == xmax:
        upper = math.inf
    else:
        low, high = -60.0, 60.0
        for _ in range(140):
            middle = (low + high) / 2.0
            if cdf(middle) > ALPHA / 2.0:
                low = middle
            else:
                high = middle
        upper = math.exp((low + high) / 2.0)
    return point, lower, upper


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    n1, n0, successes = a + b, c + d, a + c
    support, probabilities = conditional_distribution(n1, n0, successes, 0.0)
    observed = probabilities[support.index(a)]
    tolerance = observed * 1e-12 + 1e-15
    return min(1.0, sum(p for p in probabilities if p <= observed + tolerance))


def bootstrap_difference(
    first: list[int], second: list[int]
) -> tuple[float, float, list[float]]:
    rng = random.Random(BOOTSTRAP_SEED)
    n1, n0 = len(first), len(second)
    replicates: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        p1 = sum(first[rng.randrange(n1)] for _ in range(n1)) / n1
        p0 = sum(second[rng.randrange(n0)] for _ in range(n0)) / n0
        replicates.append(p1 - p0)
    return (
        percentile(replicates, 0.025),
        percentile(replicates, 0.975),
        replicates,
    )


def risk_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    numerator = sum(record["detected"] for record in records)
    denominator = len(records)
    risk = numerator / denominator if denominator else math.nan
    lower, upper = clopper_pearson(numerator, denominator)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "risk": risk,
        "ci_lower": lower,
        "ci_upper": upper,
    }


def comparison_summary(
    first: list[dict[str, Any]],
    second: list[dict[str, Any]],
    bootstrap: bool = False,
) -> dict[str, Any]:
    s1, s0 = risk_summary(first), risk_summary(second)
    x1, n1 = s1["numerator"], s1["denominator"]
    x0, n0 = s0["numerator"], s0["denominator"]
    difference, rd_lower, rd_upper = newcombe_difference(x1, n1, x0, n0)
    rr, rr_lower, rr_upper = risk_ratio_score_interval(x1, n1, x0, n0)
    odds, odds_lower, odds_upper = conditional_exact_odds_ratio_interval(
        x1, n1 - x1, x0, n0 - x0
    )
    result = {
        "first": s1,
        "second": s0,
        "risk_difference": difference,
        "rd_lower": rd_lower,
        "rd_upper": rd_upper,
        "risk_ratio": rr,
        "rr_lower": rr_lower,
        "rr_upper": rr_upper,
        "odds_ratio": odds,
        "or_lower": odds_lower,
        "or_upper": odds_upper,
        "fisher_p": fisher_exact_two_sided(x1, n1 - x1, x0, n0 - x0),
    }
    if bootstrap:
        boot_lower, boot_upper, _ = bootstrap_difference(
            [record["detected"] for record in first],
            [record["detected"] for record in second],
        )
        result["bootstrap_lower"] = boot_lower
        result["bootstrap_upper"] = boot_upper
    return result


def build_person_records(
    cohort_rows: list[dict[str, str]],
    outcome_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    cohort = {row["person_id"]: row for row in cohort_rows}
    outcomes = {row["person_id"]: row for row in outcome_rows}
    events_by_person: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in event_rows:
        events_by_person[event["person_id"]].append(event)

    if len(cohort) != len(cohort_rows):
        errors.append("Duplicate person_id in cohort.csv")
    if len(outcomes) != len(outcome_rows):
        errors.append("Duplicate person_id in PERSON_OUTCOMES.csv")
    if set(cohort) != set(outcomes):
        errors.append("Cohort and outcome person-ID sets differ")

    records: list[dict[str, Any]] = []
    for person_id in sorted(cohort):
        c = cohort[person_id]
        o = outcomes[person_id]
        birth = parse_date(c["birth_date"])
        age80 = birthday_80(birth)
        death = parse_date(c["death_date"]) if c["death_date"] else None
        end = min(death, ADMIN_END) if death else ADMIN_END
        eligible = age80 <= end
        if eligible != (o["eligible_age80"] == "1"):
            errors.append(f"Eligibility mismatch for {person_id}")
        expected_other = (
            c["apollo_flew"] == "0"
            and any(
                c[key] == "1"
                for key in (
                    "core_nasa_non_apollo",
                    "military_x15",
                    "military_dyna_soar",
                    "military_mol",
                )
            )
        )
        if expected_other != (c["other_all"] == "1"):
            errors.append(f"other_all formula mismatch for {person_id}")

        qualifying = [
            event
            for event in events_by_person.get(person_id, [])
            if event["qualifies"] == "1"
        ]
        functions: list[dict[str, Any]] = []
        impairments: list[dict[str, Any]] = []
        for event in qualifying:
            analysis_day = parse_date(event["analysis_event_date"])
            earliest = parse_date(event["event_date_earliest"])
            latest = parse_date(event["event_date_latest"])
            if not earliest <= analysis_day <= latest:
                errors.append(f"Event date bounds do not contain analysis date: {person_id}")
            enriched = {
                **event,
                "analysis_day": analysis_day,
                "earliest_day": earliest,
                "latest_day": latest,
            }
            if event["evidence_type"] == "QUALIFYING_FUNCTION_EVENT":
                functions.append(enriched)
            elif event["evidence_type"] == "QUALIFYING_IMPAIRMENT_EVIDENCE":
                impairments.append(enriched)
            else:
                errors.append(f"Unknown qualifying evidence type for {person_id}")

        in_window_functions = sorted(
            [
                event
                for event in functions
                if eligible and age80 <= event["analysis_day"] <= end
            ],
            key=lambda event: (event["analysis_day"], event["source_url"]),
        )
        in_window_impairments = sorted(
            [
                event
                for event in impairments
                if eligible and age80 <= event["analysis_day"] <= end
            ],
            key=lambda event: (event["analysis_day"], event["source_url"]),
        )
        for event in functions + impairments:
            if eligible and not (age80 <= event["analysis_day"] <= end):
                errors.append(f"Qualifying event outside full evidence window: {person_id}")

        detected = int(bool(in_window_functions))
        first_function = in_window_functions[0]["analysis_day"] if detected else None
        stop = min(
            [candidate for candidate in (first_function, death, ADMIN_END) if candidate is not None]
        )
        stop_type = (
            "FUNCTION_EVENT"
            if first_function is not None and first_function == stop
            else "DEATH_COMPETING"
            if death is not None and death == stop
            else "ADMINISTRATIVE_CENSOR"
        )
        if not eligible:
            stop = age80
            stop_type = "NOT_ELIGIBLE"

        military_only = c["apollo_flew"] == "0" and any(
            c[key] == "1"
            for key in ("military_x15", "military_dyna_soar", "military_mol")
        )
        record: dict[str, Any] = {
            "research_id": o["research_id"],
            "person_id": person_id,
            "full_name": c["full_name"],
            "birth": birth,
            "age80": age80,
            "death": death,
            "end": end,
            "eligible": eligible,
            "apollo": c["apollo_flew"] == "1",
            "other_all": c["other_all"] == "1",
            "core": c["core_nasa_non_apollo"] == "1",
            "military_only": military_only,
            "functions": in_window_functions,
            "impairments": in_window_impairments,
            "detected": detected,
            "first_function": first_function,
            "latest_function": (
                in_window_functions[-1]["analysis_day"] if in_window_functions else None
            ),
            "potential_days": (end - age80).days if eligible else 0,
            "observed_days": (stop - age80).days if eligible else 0,
            "stop": stop,
            "stop_type": stop_type,
            "outcome_state": o["outcome_state"],
            "substantive_sources": int(o["substantive_sources_opened"]),
            "independent_publishers": int(o["independent_publishers"]),
            "documentation_depth": o["documentation_depth"],
            "boundary_sensitive": o["boundary_sensitive"] == "1",
        }

        expected_first = first_function.isoformat() if first_function else ""
        expected_latest = (
            record["latest_function"].isoformat() if record["latest_function"] else ""
        )
        if expected_first != o["first_qualifying_function_date"]:
            errors.append(f"First function mismatch for {person_id}")
        if expected_latest != o["latest_qualifying_function_date"]:
            errors.append(f"Latest function mismatch for {person_id}")

        if eligible:
            if in_window_functions and not in_window_impairments:
                mechanical_state = "FUNCTION_ONLY"
            elif not in_window_functions and in_window_impairments:
                mechanical_state = "IMPAIRMENT_ONLY"
            elif in_window_functions and in_window_impairments:
                fday = in_window_functions[0]["analysis_day"]
                iday = in_window_impairments[0]["analysis_day"]
                if fday < iday:
                    mechanical_state = "FUNCTION_THEN_IMPAIRMENT"
                elif iday < fday:
                    mechanical_state = "IMPAIRMENT_THEN_FUNCTION"
                else:
                    mechanical_state = "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE"
            else:
                mechanical_state = "NEITHER_FOUND"
        else:
            mechanical_state = "NOT_ELIGIBLE_UNDER_80"
        if mechanical_state != o["outcome_state"]:
            errors.append(f"Outcome-state mismatch for {person_id}")

        depth_expected = (
            "LOW"
            if record["substantive_sources"] <= 1
            else "HIGH"
            if record["substantive_sources"] >= 5
            and record["independent_publishers"] >= 2
            else "MEDIUM"
        )
        if depth_expected != record["documentation_depth"]:
            errors.append(f"Documentation-depth mismatch for {person_id}")
        records.append(record)
    return records, errors


def group_records(
    eligible: list[dict[str, Any]], key: str
) -> list[dict[str, Any]]:
    return [record for record in eligible if record[key]]


def aalen_johansen(
    records: list[dict[str, Any]], group: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stops: dict[int, Counter[str]] = defaultdict(Counter)
    for record in records:
        days = record["observed_days"]
        stops[days][record["stop_type"]] += 1

    n_risk = len(records)
    survival = 1.0
    cif_function = 0.0
    cif_death = 0.0
    curve: list[dict[str, Any]] = [
        {
            "group": group,
            "time_days": 0,
            "time_years": 0.0,
            "n_risk_before": n_risk,
            "function_events": 0,
            "death_competing_events": 0,
            "administrative_censors": 0,
            "event_free_probability": survival,
            "function_cumulative_incidence": cif_function,
            "death_cumulative_incidence": cif_death,
            "n_risk_after": n_risk,
        }
    ]
    for days in sorted(stops):
        counts = stops[days]
        d1 = counts["FUNCTION_EVENT"]
        d2 = counts["DEATH_COMPETING"]
        censored = counts["ADMINISTRATIVE_CENSOR"]
        if n_risk <= 0:
            raise ValueError(f"Invalid empty risk set in {group}")
        survival_before = survival
        cif_function += survival_before * d1 / n_risk
        cif_death += survival_before * d2 / n_risk
        survival *= 1.0 - (d1 + d2) / n_risk
        n_after = n_risk - d1 - d2 - censored
        curve.append(
            {
                "group": group,
                "time_days": days,
                "time_years": days / DAY_YEAR,
                "n_risk_before": n_risk,
                "function_events": d1,
                "death_competing_events": d2,
                "administrative_censors": censored,
                "event_free_probability": survival,
                "function_cumulative_incidence": cif_function,
                "death_cumulative_incidence": cif_death,
                "n_risk_after": n_after,
            }
        )
        n_risk = n_after

    readouts: list[dict[str, Any]] = []
    for years in (5, 10, 15):
        milestone_days = years * DAY_YEAR
        at_risk = sum(record["observed_days"] + 1e-12 >= milestone_days for record in records)
        applicable = [row for row in curve if row["time_days"] <= milestone_days + 1e-12]
        estimate = applicable[-1]["function_cumulative_incidence"]
        if at_risk == 0:
            warning = "NON_ESTIMABLE_NO_SUPPORT"
            reported: float | None = None
        elif at_risk < 10 or at_risk < 0.20 * len(records):
            warning = "TAIL_SUPPORT_WARNING"
            reported = estimate
        else:
            warning = "ADEQUATE_SUPPORT"
            reported = estimate
        readouts.append(
            {
                "group": group,
                "years_after_80": years,
                "cumulative_incidence": reported,
                "n_under_observation": at_risk,
                "starting_n": len(records),
                "support_fraction": at_risk / len(records),
                "support_status": warning,
                "note": (
                    "Subordinate curve readout; not an eligibility restriction or primary endpoint."
                ),
            }
        )
    return curve, readouts


def summarize_followup(
    records: list[dict[str, Any]], group: str
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    numeric = {
        "potential_followup_years": [
            record["potential_days"] / DAY_YEAR for record in records
        ],
        "observed_followup_years": [
            record["observed_days"] / DAY_YEAR for record in records
        ],
        "substantive_sources_opened": [
            float(record["substantive_sources"]) for record in records
        ],
        "independent_publishers": [
            float(record["independent_publishers"]) for record in records
        ],
    }
    for metric, values in numeric.items():
        q1, med, q3 = quartiles(values)
        rows.append(
            {
                "group": group,
                "metric": metric,
                "n": len(values),
                "count": "",
                "mean": mean(values),
                "minimum": min(values),
                "q1": q1,
                "median": med,
                "q3": q3,
                "maximum": max(values),
            }
        )
    count_metrics = {
        "function_event_first": sum(
            record["stop_type"] == "FUNCTION_EVENT" for record in records
        ),
        "death_before_function": sum(
            record["stop_type"] == "DEATH_COMPETING" for record in records
        ),
        "administrative_censor_without_function": sum(
            record["stop_type"] == "ADMINISTRATIVE_CENSOR" for record in records
        ),
        "documentation_depth_LOW": sum(
            record["documentation_depth"] == "LOW" for record in records
        ),
        "documentation_depth_MEDIUM": sum(
            record["documentation_depth"] == "MEDIUM" for record in records
        ),
        "documentation_depth_HIGH": sum(
            record["documentation_depth"] == "HIGH" for record in records
        ),
    }
    for metric, count in count_metrics.items():
        rows.append(
            {
                "group": group,
                "metric": metric,
                "n": len(records),
                "count": count,
                "mean": "",
                "minimum": "",
                "q1": "",
                "median": "",
                "q3": "",
                "maximum": "",
            }
        )
    return rows


def scenario_state(
    record: dict[str, Any], date_key: str
) -> tuple[int, str, str, str]:
    functions = sorted(
        event[date_key]
        for event in record["functions"]
        if record["age80"] <= event[date_key] <= record["end"]
    )
    impairments = sorted(
        event[date_key]
        for event in record["impairments"]
        if record["age80"] <= event[date_key] <= record["end"]
    )
    if functions and not impairments:
        state = "FUNCTION_ONLY"
    elif impairments and not functions:
        state = "IMPAIRMENT_ONLY"
    elif functions and impairments:
        if functions[0] < impairments[0]:
            state = "FUNCTION_THEN_IMPAIRMENT"
        elif impairments[0] < functions[0]:
            state = "IMPAIRMENT_THEN_FUNCTION"
        else:
            state = "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE"
    else:
        state = "NEITHER_FOUND"
    return (
        int(bool(functions)),
        state,
        functions[0].isoformat() if functions else "",
        functions[-1].isoformat() if functions else "",
    )


def make_svg(
    curves: list[dict[str, Any]], readouts: list[dict[str, Any]]
) -> bytes:
    width, height = 900, 560
    left, right, top, bottom = 90, 35, 55, 165
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_time = max(15.0, max(row["time_years"] for row in curves))
    max_cif = max(row["function_cumulative_incidence"] for row in curves)
    y_max = min(1.0, max(0.20, math.ceil(max_cif * 5.0) / 5.0))

    def x_pos(value: float) -> float:
        return left + plot_w * value / max_time

    def y_pos(value: float) -> float:
        return top + plot_h * (1.0 - value / y_max)

    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}'
        '.axis{stroke:#374151;stroke-width:1}.grid{stroke:#d1d5db;stroke-width:1}'
        '.label{font-size:13px}.small{font-size:11px}.title{font-size:19px;font-weight:700}'
        '.subtitle{font-size:12px;fill:#4b5563}</style>',
        f'<text x="{left}" y="25" class="title">Aalen–Johansen cumulative incidence of first public function detection</text>',
        f'<text x="{left}" y="44" class="subtitle">Age 80 origin; death first is competing; administrative end is censoring; no age-85 censor</text>',
    ]
    for tick in range(6):
        y_value = y_max * tick / 5.0
        y = y_pos(y_value)
        pieces.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" class="grid"/>'
        )
        pieces.append(
            f'<text x="{left-12}" y="{y+4:.2f}" text-anchor="end" class="label">{y_value:.2f}</text>'
        )
    x_ticks = sorted(set([0, 5, 10, 15, int(max_time)]))
    for value in x_ticks:
        if value > max_time:
            continue
        x = x_pos(float(value))
        pieces.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top+plot_h}" class="grid"/>'
        )
        pieces.append(
            f'<text x="{x:.2f}" y="{top+plot_h+23}" text-anchor="middle" class="label">{value}</text>'
        )
    pieces.extend(
        [
            f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" class="axis"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" class="axis"/>',
            f'<text x="{left+plot_w/2:.2f}" y="{top+plot_h+49}" text-anchor="middle" class="label">Years after age 80</text>',
            f'<text x="22" y="{top+plot_h/2:.2f}" transform="rotate(-90 22 {top+plot_h/2:.2f})" text-anchor="middle" class="label">Cumulative incidence</text>',
        ]
    )
    colors = {"APOLLO_FLEW": "#b91c1c", "OTHER_ALL": "#1d4ed8"}
    for group, color in colors.items():
        group_rows = [row for row in curves if row["group"] == group]
        path_parts = [f"M {x_pos(0):.2f} {y_pos(0):.2f}"]
        prior = 0.0
        for row in group_rows[1:]:
            x = x_pos(row["time_years"])
            path_parts.append(f"L {x:.2f} {y_pos(prior):.2f}")
            current = row["function_cumulative_incidence"]
            path_parts.append(f"L {x:.2f} {y_pos(current):.2f}")
            prior = current
        path_parts.append(f"L {x_pos(max_time):.2f} {y_pos(prior):.2f}")
        pieces.append(
            f'<path d="{escape(" ".join(path_parts))}" fill="none" stroke="{color}" stroke-width="3"/>'
        )
    legend_x = width - 285
    for index, group in enumerate(("APOLLO_FLEW", "OTHER_ALL")):
        y = 69 + index * 22
        pieces.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x+28}" y2="{y}" stroke="{colors[group]}" stroke-width="3"/>'
        )
        pieces.append(
            f'<text x="{legend_x+36}" y="{y+4}" class="label">{group}</text>'
        )
    table_y = top + plot_h + 83
    pieces.append(
        f'<text x="{left}" y="{table_y}" class="label" font-weight="700">Number still under observation immediately before milestone</text>'
    )
    milestone_x = {5: left + 390, 10: left + 510, 15: left + 630}
    for years, x in milestone_x.items():
        pieces.append(
            f'<text x="{x}" y="{table_y}" text-anchor="middle" class="label">{years} y</text>'
        )
    for row_index, group in enumerate(("APOLLO_FLEW", "OTHER_ALL")):
        y = table_y + 25 + row_index * 22
        pieces.append(f'<text x="{left}" y="{y}" class="label">{group}</text>')
        for years, x in milestone_x.items():
            row = next(
                item
                for item in readouts
                if item["group"] == group and item["years_after_80"] == years
            )
            pieces.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" class="label">{row["n_under_observation"]}</text>'
            )
    pieces.append(
        f'<text x="{left}" y="{height-18}" class="small">Curve readouts are subordinate observable-time descriptions, not eligibility restrictions or primary endpoints.</text>'
    )
    pieces.append("</svg>")
    return ("\n".join(pieces) + "\n").encode("utf-8")


def analyze(
    cohort_rows: list[dict[str, str]],
    outcome_rows: list[dict[str, str]],
    event_rows: list[dict[str, str]],
) -> dict[str, Any]:
    records, errors = build_person_records(cohort_rows, outcome_rows, event_rows)
    eligible = [record for record in records if record["eligible"]]
    apollo = group_records(eligible, "apollo")
    other = group_records(eligible, "other_all")
    core = group_records(eligible, "core")
    military = group_records(eligible, "military_only")

    if len(apollo) + len(other) != len(eligible):
        errors.append("Eligible cohort is not partitioned by APOLLO_FLEW and OTHER_ALL")
    if set(record["person_id"] for record in apollo) & set(
        record["person_id"] for record in other
    ):
        errors.append("Primary groups overlap")

    available_ids = {
        row["person_id"]
        for row in outcome_rows
        if row["eligible_age80"] == "1"
        and next(
            c for c in cohort_rows if c["person_id"] == row["person_id"]
        )["other_all"]
        == "1"
    }
    other_ids = {record["person_id"] for record in other}
    other_set_equal = available_ids == other_ids
    if not other_set_equal:
        errors.append("OTHER_AVAILABLE and OTHER_ALL full-window eligible sets differ")

    if not {record["person_id"] for record in core} <= other_ids:
        errors.append("CORE_NASA_NON_APOLLO is not nested in OTHER_ALL")
    if not {record["person_id"] for record in military} <= other_ids:
        errors.append("MILITARY_ONLY is not nested in OTHER_ALL")

    primary = comparison_summary(apollo, other, bootstrap=True)
    composition_core = comparison_summary(apollo, core)
    composition_military = comparison_summary(apollo, military)
    without_r001 = comparison_summary(
        [record for record in apollo if record["research_id"] != "R001"],
        [record for record in other if record["research_id"] != "R001"],
    )

    primary_sign = (
        1
        if primary["risk_difference"] > 0
        else -1
        if primary["risk_difference"] < 0
        else 0
    )
    composition_reversal = any(
        primary_sign
        and summary["risk_difference"] * primary_sign < 0
        for summary in (composition_core, composition_military)
    )
    if errors:
        strength, direction = "INDETERMINATE", "UNCERTAIN"
    else:
        direction = (
            "HIGHER"
            if primary_sign > 0
            else "LOWER"
            if primary_sign < 0
            else "UNCERTAIN"
        )
        material = abs(primary["risk_difference"]) >= 0.10
        excludes_zero = (
            primary["rd_lower"] > 0.0 or primary["rd_upper"] < 0.0
        )
        if material and excludes_zero and not composition_reversal:
            strength = "ROBUST"
        elif material and primary_sign != 0 and not composition_reversal:
            strength = "SUGGESTIVE"
        else:
            strength = "NOT_DETECTED"

    groups = {"APOLLO_FLEW": apollo, "OTHER_ALL": other}
    curves: list[dict[str, Any]] = []
    readouts: list[dict[str, Any]] = []
    followup: list[dict[str, Any]] = []
    for name, group in groups.items():
        curve, group_readouts = aalen_johansen(group, name)
        curves.extend(curve)
        readouts.extend(group_readouts)
        followup.extend(summarize_followup(group, name))

    event_age_rows: list[dict[str, Any]] = []
    latest_rows: list[dict[str, Any]] = []
    age_band_counts: dict[tuple[str, str], int] = defaultdict(int)
    for record in eligible:
        events = record["functions"]
        dates = [event["analysis_day"] for event in events]
        ages = [
            (event["analysis_day"] - record["birth"]).days / DAY_YEAR
            for event in events
        ]
        memberships = [
            name
            for name, condition in (
                ("APOLLO_FLEW", record["apollo"]),
                ("OTHER_ALL", record["other_all"]),
                ("CORE_NASA_NON_APOLLO", record["core"]),
                ("MILITARY_ONLY", record["military_only"]),
            )
            if condition
        ]
        row = {
            "research_id": record["research_id"],
            "person_id": record["person_id"],
            "full_name": record["full_name"],
            "primary_group": "APOLLO_FLEW" if record["apollo"] else "OTHER_ALL",
            "set_memberships": "|".join(memberships),
            "detected_any_age_80_plus": record["detected"],
            "qualifying_function_event_count": len(events),
            "all_event_dates": "|".join(day.isoformat() for day in dates),
            "all_event_ages": "|".join(f"{age:.6f}" for age in ages),
            "first_event_date": dates[0].isoformat() if dates else "",
            "first_event_age": ages[0] if ages else "",
            "latest_event_date": dates[-1].isoformat() if dates else "",
            "latest_event_age": ages[-1] if ages else "",
            "outcome_state": record["outcome_state"],
        }
        event_age_rows.append(row)
        if dates:
            latest_rows.append(
                {
                    "research_id": record["research_id"],
                    "person_id": record["person_id"],
                    "full_name": record["full_name"],
                    "primary_group": row["primary_group"],
                    "first_event_age": ages[0],
                    "latest_event_age": ages[-1],
                    "event_count": len(events),
                }
            )
        for age in ages:
            band = (
                "[80,85)"
                if age < 85
                else "[85,90)"
                if age < 90
                else "[90,95)"
                if age < 95
                else "95+"
            )
            group_name = row["primary_group"]
            age_band_counts[(group_name, band)] += 1
            age_band_counts[("ALL_ELIGIBLE", band)] += 1
    latest_rows.sort(key=lambda row: (row["latest_event_age"], row["person_id"]))

    age_band_rows = [
        {
            "group": group,
            "age_band": band,
            "qualifying_detected_event_count": age_band_counts[(group, band)],
        }
        for group in ("APOLLO_FLEW", "OTHER_ALL", "ALL_ELIGIBLE")
        for band in ("[80,85)", "[85,90)", "[90,95)", "95+")
    ]

    states = (
        "FUNCTION_ONLY",
        "IMPAIRMENT_ONLY",
        "FUNCTION_THEN_IMPAIRMENT",
        "IMPAIRMENT_THEN_FUNCTION",
        "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE",
        "NEITHER_FOUND",
    )
    sequence_rows = [
        {
            "group": group,
            "locked_person_level_state": state,
            "person_count": sum(record["outcome_state"] == state for record in group_records_),
            "interpretation": (
                "Public evidence state; no health ordering is assigned."
                if state == "NEITHER_FOUND"
                else "Locked function/impairment evidence sequence."
            ),
        }
        for group, group_records_ in groups.items()
        for state in states
    ]

    latent_apollo_neither = sum(
        record["outcome_state"] == "NEITHER_FOUND" for record in apollo
    )
    latent_other_neither = sum(
        record["outcome_state"] == "NEITHER_FOUND" for record in other
    )
    latent_lower = (
        primary["first"]["numerator"] / len(apollo)
        - (primary["second"]["numerator"] + latent_other_neither) / len(other)
    )
    latent_upper = (
        (primary["first"]["numerator"] + latent_apollo_neither) / len(apollo)
        - primary["second"]["numerator"] / len(other)
    )

    date_rows: list[dict[str, Any]] = []
    date_changes: list[dict[str, Any]] = []
    for scenario, date_key in (
        ("EARLIEST_PLAUSIBLE_DATES", "earliest_day"),
        ("LATEST_PLAUSIBLE_DATES", "latest_day"),
    ):
        scenario_records: list[dict[str, Any]] = []
        for record in eligible:
            detected, state, first_day, latest_day = scenario_state(record, date_key)
            scenario_record = {**record, "detected": detected}
            scenario_records.append(scenario_record)
            primary_first = (
                record["first_function"].isoformat() if record["first_function"] else ""
            )
            primary_latest = (
                record["latest_function"].isoformat() if record["latest_function"] else ""
            )
            if (
                detected != record["detected"]
                or state != record["outcome_state"]
                or first_day != primary_first
                or latest_day != primary_latest
            ):
                date_changes.append(
                    {
                        "scenario": scenario,
                        "research_id": record["research_id"],
                        "person_id": record["person_id"],
                        "primary_detected": record["detected"],
                        "scenario_detected": detected,
                        "primary_state": record["outcome_state"],
                        "scenario_state": state,
                        "primary_first_function_date": primary_first,
                        "scenario_first_function_date": first_day,
                        "primary_latest_function_date": primary_latest,
                        "scenario_latest_function_date": latest_day,
                        "age85_used_as_boundary": 0,
                    }
                )
        scenario_apollo = group_records(scenario_records, "apollo")
        scenario_other = group_records(scenario_records, "other_all")
        summary = comparison_summary(scenario_apollo, scenario_other)
        scenario_change_rows = [
            row for row in date_changes if row["scenario"] == scenario
        ]
        detection_or_order_changes = sum(
            row["primary_detected"] != row["scenario_detected"]
            or row["primary_state"] != row["scenario_state"]
            for row in scenario_change_rows
        )
        date_only_changes = len(scenario_change_rows) - detection_or_order_changes
        date_rows.append(
            {
                "scenario": scenario,
                "apollo_numerator": summary["first"]["numerator"],
                "apollo_denominator": summary["first"]["denominator"],
                "other_numerator": summary["second"]["numerator"],
                "other_denominator": summary["second"]["denominator"],
                "apollo_minus_other_risk_difference": summary["risk_difference"],
                "age80_eligibility_changes": 0,
                "detection_or_sequence_changes": detection_or_order_changes,
                "date_only_changes": date_only_changes,
                "age85_used_as_boundary": 0,
                "note": (
                    "Eligibility uses exact locked birth/death dates; event timing uses "
                    f"{'earliest' if date_key == 'earliest_day' else 'latest'} locked bounds."
                ),
            }
        )

    set_ids = {
        "APOLLO_FLEW": {record["person_id"] for record in apollo},
        "OTHER_ALL": other_ids,
        "OTHER_AVAILABLE": available_ids,
        "CORE_NASA_NON_APOLLO": {record["person_id"] for record in core},
        "MILITARY_ONLY": {record["person_id"] for record in military},
    }
    set_rows = [
        {
            "set_name": name,
            "eligible_n": len(ids),
            "person_ids": "|".join(sorted(ids)),
            "nested_within": (
                "OTHER_ALL"
                if name in ("OTHER_AVAILABLE", "CORE_NASA_NON_APOLLO", "MILITARY_ONLY")
                else ""
            ),
        }
        for name, ids in set_ids.items()
    ]
    overlap_core_military = len(
        set_ids["CORE_NASA_NON_APOLLO"] & set_ids["MILITARY_ONLY"]
    )

    return {
        "records": records,
        "eligible": eligible,
        "apollo": apollo,
        "other": other,
        "core": core,
        "military": military,
        "primary": primary,
        "composition_core": composition_core,
        "composition_military": composition_military,
        "without_r001": without_r001,
        "other_set_equal": other_set_equal,
        "set_rows": set_rows,
        "overlap_core_military": overlap_core_military,
        "curves": curves,
        "readouts": readouts,
        "followup": followup,
        "event_age_rows": event_age_rows,
        "latest_rows": latest_rows,
        "age_band_rows": age_band_rows,
        "sequence_rows": sequence_rows,
        "latent_lower": latent_lower,
        "latent_upper": latent_upper,
        "latent_apollo_neither": latent_apollo_neither,
        "latent_other_neither": latent_other_neither,
        "date_rows": date_rows,
        "date_changes": date_changes,
        "strength": strength,
        "direction": direction,
        "composition_reversal": composition_reversal,
        "errors": errors,
    }


def results_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    primary = result["primary"]
    rows: list[dict[str, Any]] = []
    for group_name, key in (("APOLLO_FLEW", "first"), ("OTHER_ALL", "second")):
        summary = primary[key]
        rows.append(
            {
                "section": "PRIMARY_GROUP_RISK",
                "analysis": "UNRESTRICTED_AGE_80_PLUS",
                "group_a": group_name,
                "group_b": "",
                "metric": "detected_risk",
                "estimate": summary["risk"],
                "ci_lower": summary["ci_lower"],
                "ci_upper": summary["ci_upper"],
                "p_value": "",
                "numerator_a": summary["numerator"],
                "denominator_a": summary["denominator"],
                "numerator_b": "",
                "denominator_b": "",
                "notes": "95% Clopper-Pearson interval",
            }
        )
    measures = [
        (
            "risk_difference",
            primary["risk_difference"],
            primary["rd_lower"],
            primary["rd_upper"],
            "",
            "95% Newcombe method-10 interval; Apollo minus Other",
        ),
        (
            "risk_difference_bootstrap",
            primary["risk_difference"],
            primary["bootstrap_lower"],
            primary["bootstrap_upper"],
            "",
            f"Group-stratified person bootstrap; {BOOTSTRAP_REPLICATES} replicates; seed {BOOTSTRAP_SEED}; percentile interval",
        ),
        (
            "risk_ratio",
            primary["risk_ratio"],
            primary["rr_lower"],
            primary["rr_upper"],
            "",
            "95% constrained two-binomial score interval",
        ),
        (
            "odds_ratio",
            primary["odds_ratio"],
            primary["or_lower"],
            primary["or_upper"],
            "",
            "Cross-product point estimate; 95% conditional exact interval",
        ),
        (
            "fisher_exact_two_sided",
            "",
            "",
            "",
            primary["fisher_p"],
            "Central-hypergeometric probability ordering",
        ),
    ]
    for metric, estimate, lower, upper, p_value, notes in measures:
        rows.append(
            {
                "section": "PRIMARY_CONTRAST",
                "analysis": "UNRESTRICTED_AGE_80_PLUS",
                "group_a": "APOLLO_FLEW",
                "group_b": "OTHER_ALL",
                "metric": metric,
                "estimate": estimate,
                "ci_lower": lower,
                "ci_upper": upper,
                "p_value": p_value,
                "numerator_a": primary["first"]["numerator"],
                "denominator_a": primary["first"]["denominator"],
                "numerator_b": primary["second"]["numerator"],
                "denominator_b": primary["second"]["denominator"],
                "notes": notes,
            }
        )
    for analysis_name, group_b, summary, notes in (
        (
            "COMPOSITION_CORE_NASA_NON_APOLLO",
            "CORE_NASA_NON_APOLLO",
            result["composition_core"],
            "Nested within OTHER_ALL; not independent",
        ),
        (
            "COMPOSITION_MILITARY_ONLY",
            "MILITARY_ONLY",
            result["composition_military"],
            "Nested within OTHER_ALL; overlaps CORE_NASA_NON_APOLLO; not independent",
        ),
        (
            "TECHNICAL_DEVIATION_EXCLUDE_R001",
            "OTHER_ALL",
            result["without_r001"],
            "Technical-deviation sensitivity; R001 excluded",
        ),
    ):
        rows.append(
            {
                "section": "SENSITIVITY",
                "analysis": analysis_name,
                "group_a": "APOLLO_FLEW",
                "group_b": group_b,
                "metric": "risk_difference",
                "estimate": summary["risk_difference"],
                "ci_lower": summary["rd_lower"],
                "ci_upper": summary["rd_upper"],
                "p_value": "",
                "numerator_a": summary["first"]["numerator"],
                "denominator_a": summary["first"]["denominator"],
                "numerator_b": summary["second"]["numerator"],
                "denominator_b": summary["second"]["denominator"],
                "notes": notes,
            }
        )
    rows.extend(
        [
            {
                "section": "LATENT_EVENT_BOUND_DIFFERENT_QUESTION",
                "analysis": "NEITHER_FOUND_WORST_CASE",
                "group_a": "APOLLO_FLEW",
                "group_b": "OTHER_ALL",
                "metric": "latent_event_risk_difference_bound",
                "estimate": result["latent_lower"],
                "ci_lower": "",
                "ci_upper": "",
                "p_value": "",
                "numerator_a": primary["first"]["numerator"],
                "denominator_a": primary["first"]["denominator"],
                "numerator_b": primary["second"]["numerator"]
                + result["latent_other_neither"],
                "denominator_b": primary["second"]["denominator"],
                "notes": "Assign no latent event to Apollo NEITHER_FOUND and an event to Other NEITHER_FOUND",
            },
            {
                "section": "LATENT_EVENT_BOUND_DIFFERENT_QUESTION",
                "analysis": "NEITHER_FOUND_BEST_CASE",
                "group_a": "APOLLO_FLEW",
                "group_b": "OTHER_ALL",
                "metric": "latent_event_risk_difference_bound",
                "estimate": result["latent_upper"],
                "ci_lower": "",
                "ci_upper": "",
                "p_value": "",
                "numerator_a": primary["first"]["numerator"]
                + result["latent_apollo_neither"],
                "denominator_a": primary["first"]["denominator"],
                "numerator_b": primary["second"]["numerator"],
                "denominator_b": primary["second"]["denominator"],
                "notes": "Assign an event to Apollo NEITHER_FOUND and no latent event to Other NEITHER_FOUND",
            },
            {
                "section": "CLASSIFICATION",
                "analysis": "CORRECTED_PUBLIC_FUNCTION",
                "group_a": "APOLLO_FLEW",
                "group_b": "OTHER_ALL",
                "metric": "strength_and_direction",
                "estimate": f'{result["strength"]}|{result["direction"]}',
                "ci_lower": "",
                "ci_upper": "",
                "p_value": "",
                "numerator_a": "",
                "denominator_a": "",
                "numerator_b": "",
                "denominator_b": "",
                "notes": "Fixed classification rule and unrestricted primary sign",
            },
        ]
    )
    return rows


def report_markdown(result: dict[str, Any]) -> str:
    p = result["primary"]
    ap = p["first"]
    ot = p["second"]
    latest = result["latest_rows"]
    event_ages = [row["first_event_age"] for row in latest]
    latest_ages = [row["latest_event_age"] for row in latest]
    first_summary = (
        f"range {min(event_ages):.2f}–{max(event_ages):.2f}, median {median(event_ages):.2f}"
        if event_ages
        else "no detected people"
    )
    latest_summary = (
        f"range {min(latest_ages):.2f}–{max(latest_ages):.2f}, median {median(latest_ages):.2f}"
        if latest_ages
        else "no detected people"
    )
    lines = [
        "# Corrected Stage 2R Public-Function Analysis",
        "",
        "## Corrected question and status",
        "",
        "Among locked cohort members who reached age 80, this analysis compares `APOLLO_FLEW` with `OTHER_ALL` on public detection of at least one locked `QUALIFYING_FUNCTION_EVENT` at any age 80 or older through death or administrative censoring on 2026-06-01. This is public-evidence detection, not a clinical measure.",
        "",
        "This is a transparently labeled post-lock endpoint correction. It retains the locked evidence, dates, adjudication, source rules, and person-level states, but supersedes the stale age-80-to-85 primary restriction. No event is discarded merely for occurring at age 85 or older.",
        "",
        "## Unrestricted corrected primary",
        "",
        "| Group | Detected / eligible | Risk (95% Clopper–Pearson CI) |",
        "|---|---:|---:|",
        f"| APOLLO_FLEW | {ap['numerator']} / {ap['denominator']} | {fmt_pct(ap['risk'])} ({fmt_pct(ap['ci_lower'])}, {fmt_pct(ap['ci_upper'])}) |",
        f"| OTHER_ALL | {ot['numerator']} / {ot['denominator']} | {fmt_pct(ot['risk'])} ({fmt_pct(ot['ci_lower'])}, {fmt_pct(ot['ci_upper'])}) |",
        "",
        f"The unrestricted Apollo-minus-Other risk difference is **{fmt_pct(p['risk_difference'])}** (95% Newcombe CI {fmt_pct(p['rd_lower'])} to {fmt_pct(p['rd_upper'])}). The group-stratified 50,000-replicate person-level bootstrap interval (seed 20260721) is {fmt_pct(p['bootstrap_lower'])} to {fmt_pct(p['bootstrap_upper'])}.",
        "",
        f"The risk ratio is {fmt_num(p['risk_ratio'])} (95% score CI {fmt_num(p['rr_lower'])} to {fmt_num(p['rr_upper'])}); the odds ratio is {fmt_num(p['odds_ratio'])} (95% conditional exact CI {fmt_num(p['or_lower'])} to {fmt_num(p['or_upper'])}). The two-sided Fisher exact p-value is {fmt_num(p['fisher_p'], 4)}.",
        "",
        f"The prespecified practical threshold remains 10 absolute percentage points. Corrected `PUBLIC FUNCTION` classification: **{result['strength']}**, direction **{result['direction']}**.",
        "",
        "## Unequal observable time",
        "",
        "The Aalen–Johansen curves start at age 80, treat first qualifying function as the event of interest, death first as competing, and 2026-06-01 as right censoring. They retain all age-80-plus events and never censor at age 85. These are subordinate descriptions, not eligibility restrictions or primary endpoints.",
        "",
        "| Group | Years after 80 | Cumulative incidence | Under observation | Tail support |",
        "|---|---:|---:|---:|---|",
    ]
    for row in result["readouts"]:
        lines.append(
            f"| {row['group']} | {row['years_after_80']} | {fmt_pct(row['cumulative_incidence'])} | {row['n_under_observation']} / {row['starting_n']} | {row['support_status']} |"
        )
    lines.extend(
        [
            "",
            "A zero-support readout is marked non-estimable rather than extending a plateau beyond observed support. Low-count or low-fraction tails are explicitly warned.",
            "",
            "Potential follow-up runs from age 80 to death or administrative end; observed follow-up runs to first detected function, death first, or administrative end. Documentation depth, substantive sources, and independent publishers are descriptive ascertainment features only and were not used to condition, weight, or exclude endpoint observations.",
            "",
            "| Group | Potential follow-up, median [Q1, Q3] y | Observed follow-up, median [Q1, Q3] y | Function / death / admin stops | Sources, median [Q1, Q3] | Publishers, median [Q1, Q3] |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for group in ("APOLLO_FLEW", "OTHER_ALL"):
        rows = {row["metric"]: row for row in result["followup"] if row["group"] == group}
        pot = rows["potential_followup_years"]
        obs = rows["observed_followup_years"]
        src = rows["substantive_sources_opened"]
        pub = rows["independent_publishers"]
        stops = "/".join(
            str(rows[key]["count"])
            for key in (
                "function_event_first",
                "death_before_function",
                "administrative_censor_without_function",
            )
        )
        lines.append(
            f"| {group} | {pot['median']:.2f} [{pot['q1']:.2f}, {pot['q3']:.2f}] | "
            f"{obs['median']:.2f} [{obs['q1']:.2f}, {obs['q3']:.2f}] | {stops} | "
            f"{src['median']:.1f} [{src['q1']:.1f}, {src['q3']:.1f}] | "
            f"{pub['median']:.1f} [{pub['q1']:.1f}, {pub['q3']:.1f}] |"
        )
    lines.extend(
        [
            "",
            "Full time-step curves, risk sets, readouts, descriptive distributions, and the SVG curve figure are retained as separate artifacts.",
            "",
            "## Later achievement and locked sequences",
            "",
            f"Among detected people, first-event ages have {first_summary}; latest-event ages have {latest_summary}. The complete person-level latest-age distribution is retained rather than reduced to this summary.",
            "",
            "| Group | [80,85) | [85,90) | [90,95) | 95+ |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for group in ("APOLLO_FLEW", "OTHER_ALL", "ALL_ELIGIBLE"):
        counts = {
            row["age_band"]: row["qualifying_detected_event_count"]
            for row in result["age_band_rows"]
            if row["group"] == group
        }
        lines.append(
            f"| {group} | {counts['[80,85)']} | {counts['[85,90)']} | {counts['[90,95)']} | {counts['95+']} |"
        )
    lines.extend(
        [
            "",
            "The age-band entries count detected qualifying events, not people. The person-level table retains all event dates and ages plus first/latest ages.",
            "",
            "| Group | Locked state | People |",
            "|---|---|---:|",
        ]
    )
    for row in result["sequence_rows"]:
        if row["person_count"]:
            lines.append(
                f"| {row['group']} | {row['locked_person_level_state']} | {row['person_count']} |"
            )
    lines.extend(
        [
            "",
            "`NEITHER_FOUND` is left as a searched-public-record state. No health ordering is assigned to it.",
            "",
            "## Sensitivities",
            "",
            "| Analysis | Apollo detected / n | Comparator detected / n | Risk difference | 95% Newcombe CI |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for label, summary in (
        ("Unrestricted OTHER_ALL", p),
        ("CORE_NASA_NON_APOLLO", result["composition_core"]),
        ("MILITARY_ONLY", result["composition_military"]),
        ("Exclude R001 technical deviation", result["without_r001"]),
    ):
        lines.append(
            f"| {label} | {summary['first']['numerator']} / {summary['first']['denominator']} | "
            f"{summary['second']['numerator']} / {summary['second']['denominator']} | "
            f"{fmt_pct(summary['risk_difference'])} | {fmt_pct(summary['rd_lower'])} to {fmt_pct(summary['rd_upper'])} |"
        )
    equality_text = (
        "identical"
        if result["other_set_equal"]
        else "not identical (validation failure)"
    )
    lines.extend(
        [
            "",
            f"`OTHER_AVAILABLE` and `OTHER_ALL` full-window eligible person-ID sets were verified as **{equality_text}**, so no duplicate numerical result is reported. `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY` are both nested within `OTHER_ALL`; they overlap by {result['overlap_core_military']} eligible people and are not independent.",
            "",
            f"The separately labeled `NEITHER_FOUND` latent-event extremes answer a different, unobserved-event question: the Apollo-minus-Other bound is {fmt_pct(result['latent_lower'])} under the worst assignment and {fmt_pct(result['latent_upper'])} under the best assignment. These are not clinical estimates and do not change the public-detection primary.",
            "",
            "| Plausible-date scenario | Apollo detected / n | Other detected / n | Risk difference | Eligibility changes | Detection/sequence changes | Date-only changes |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["date_rows"]:
        lines.append(
            f"| {row['scenario']} | {row['apollo_numerator']} / {row['apollo_denominator']} | "
            f"{row['other_numerator']} / {row['other_denominator']} | "
            f"{fmt_pct(row['apollo_minus_other_risk_difference'])} | "
            f"{row['age80_eligibility_changes']} | {row['detection_or_sequence_changes']} | "
            f"{row['date_only_changes']} |"
        )
    lines.extend(
        [
            "",
            "The plausible-date sensitivity uses locked earliest/latest bounds for age-80 eligibility and event timing/order. Age 85 is not a boundary.",
            "",
            "## Interpretation",
            "",
            f"The unrestricted sign determines direction ({result['direction']}). The fixed strength rule yields {result['strength']}: the judgment follows the absolute 10-point threshold, the primary Newcombe interval, and direction checks in both nested composition sensitivities. The result concerns public detection under the locked search and source rules, not health, clinical function, survival, or absence of unpublished activity.",
            "",
            "No original Stage 2 result was inspected, reconstructed, or compared.",
        ]
    )
    return "\n".join(lines) + "\n"


def corrected_conclusion(result: dict[str, Any]) -> str:
    p = result["primary"]
    return (
        "# Corrected Stage 2R Conclusion\n\n"
        f"Corrected `PUBLIC FUNCTION` strength: **{result['strength']}**. "
        f"Direction: **{result['direction']}**.\n\n"
        f"Using every locked qualifying event at age 80 or older through death or "
        f"2026-06-01, APOLLO_FLEW had {p['first']['numerator']} detections among "
        f"{p['first']['denominator']} eligible people ({fmt_pct(p['first']['risk'])}), "
        f"and OTHER_ALL had {p['second']['numerator']} among "
        f"{p['second']['denominator']} ({fmt_pct(p['second']['risk'])}). The unrestricted "
        f"Apollo-minus-Other risk difference was {fmt_pct(p['risk_difference'])} "
        f"(95% Newcombe CI {fmt_pct(p['rd_lower'])} to {fmt_pct(p['rd_upper'])}).\n\n"
        f"The classification applies the fixed 10-absolute-percentage-point threshold, "
        f"primary interval rule, and the two explicitly nested composition checks. "
        f"It describes public-evidence detection, not a clinical measure, latent health "
        f"state, or survival. `NEITHER_FOUND` is not assigned a health ordering. No "
        f"event was excluded at age 85, and no original Stage 2 estimate was consulted "
        f"or used for comparison.\n"
    )


def validation_markdown(
    result: dict[str, Any],
    before_hashes: dict[str, str],
    after_hashes: dict[str, str],
    deterministic: bool,
) -> str:
    immutable = before_hashes == after_hashes
    checks = [
        ("Locked input hashes unchanged before versus after analysis", immutable),
        ("Independent in-memory regeneration byte-identical", deterministic),
        ("No person-level structural or adjudication validation errors", not result["errors"]),
        (
            "OTHER_AVAILABLE and OTHER_ALL full-window eligible sets identical",
            result["other_set_equal"],
        ),
        (
            "CORE_NASA_NON_APOLLO nested within OTHER_ALL",
            {record["person_id"] for record in result["core"]}
            <= {record["person_id"] for record in result["other"]},
        ),
        (
            "MILITARY_ONLY nested within OTHER_ALL",
            {record["person_id"] for record in result["military"]}
            <= {record["person_id"] for record in result["other"]},
        ),
        (
            "Corrected endpoint includes every qualifying function event in the locked age-80-plus evidence window",
            all(
                record["detected"] == int(bool(record["functions"]))
                for record in result["eligible"]
            ),
        ),
        (
            "No age-85 censor used in corrected competing-risk records",
            all(
                record["stop"]
                == min(
                    candidate
                    for candidate in (
                        record["first_function"],
                        record["death"],
                        ADMIN_END,
                    )
                    if candidate is not None
                )
                for record in result["eligible"]
            ),
        ),
        (
            "Bootstrap specification fixed at 50,000 replicates and seed 20260721",
            BOOTSTRAP_REPLICATES == 50_000 and BOOTSTRAP_SEED == 20260721,
        ),
        (
            "Earliest/latest plausible-date scenarios do not use age 85",
            all(row["age85_used_as_boundary"] == 0 for row in result["date_rows"]),
        ),
    ]
    overall = all(passed for _, passed in checks)
    lines = [
        "# Stage 2R Validation",
        "",
        f"Overall validation: **{'PASS' if overall else 'FAIL'}**.",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(
        f"| {description} | {'PASS' if passed else 'FAIL'} |"
        for description, passed in checks
    )
    lines.extend(
        [
            "",
            f"Locked input manifest contains {len(before_hashes)} files. SHA-256 values are retained in `LOCKED_INPUT_HASHES.csv`; generated artifact hashes are retained in `OUTPUT_HASHES.csv`.",
            "",
            f"Eligible analytic population: {len(result['eligible'])}; APOLLO_FLEW: {len(result['apollo'])}; OTHER_ALL: {len(result['other'])}.",
            "",
            "Deterministic regeneration compares two complete independent analytical/rendering passes from the same locked inputs. Each pass resets the bootstrap generator to the fixed seed. The append-only action log and hand-authored prospective documents are outside that byte comparison.",
            "",
            "Validation errors:",
        ]
    )
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def contamination_markdown() -> str:
    return (
        "# Stage 2R Contamination Assessment\n\n"
        "Status: **NO DETECTED RESULT CONTAMINATION**.\n\n"
        "- The pre-data context attestation records that no project-specific person, "
        "outcome, estimate, direction, conclusion, method result, article, or hypothesis "
        "was disclosed before the Stage 2R instruction.\n"
        "- The endpoint correction and fixed analysis requirements came from the Stage "
        "2R instruction and were prospectively written to `ANALYSIS_DECISIONS.md` before "
        "a group outcome was computed or revealed.\n"
        "- Only locked files under `stage1/`, `stage1b/`, and `stage1c/` were used. No "
        "parent or sibling directory was read, and no web search or external source was used.\n"
        "- No original Stage 2 artifact, estimate, direction, conclusion, or reference "
        "result was inspected, reconstructed, or compared.\n"
        "- The correction did not change evidence definitions, event qualification, dates, "
        "source rules, adjudication, or locked person-level states.\n"
    )


def stage_complete_markdown(result: dict[str, Any], validation_pass: bool) -> str:
    required = [
        "CONTEXT_ATTESTATION.md",
        "ANALYSIS_DECISIONS.md",
        "analysis.py",
        "ANALYSIS_REPORT.md",
        "RESULTS_SUMMARY.csv",
        "EVENT_AGE_TABLE.csv",
        "VALIDATION.md",
        "CONTAMINATION.md",
        "CORRECTED_CONCLUSION.md",
        "STAGE_COMPLETE.md",
        "../STAGE2R_ACTION_LOG.md",
    ]
    lines = [
        "# Stage 2R Complete",
        "",
        f"Stage status: **{'COMPLETE' if validation_pass else 'BLOCKED'}**.",
        "",
        f"Corrected PUBLIC FUNCTION classification: **{result['strength']} / {result['direction']}**.",
        "",
        "Required artifacts:",
        "",
    ]
    lines.extend(f"- `{path}`" for path in required)
    lines.extend(
        [
            "",
            "All analytical tables and the generated Aalen–Johansen figure are retained under `stage2r/`. Locked inputs were unchanged, regeneration was deterministic, and analysis stops at Stage 2R.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_artifacts(
    result: dict[str, Any],
    before_hashes: dict[str, str],
    after_hashes: dict[str, str],
    deterministic_assumed: bool,
) -> dict[str, bytes]:
    result_fields = [
        "section",
        "analysis",
        "group_a",
        "group_b",
        "metric",
        "estimate",
        "ci_lower",
        "ci_upper",
        "p_value",
        "numerator_a",
        "denominator_a",
        "numerator_b",
        "denominator_b",
        "notes",
    ]
    event_fields = [
        "research_id",
        "person_id",
        "full_name",
        "primary_group",
        "set_memberships",
        "detected_any_age_80_plus",
        "qualifying_function_event_count",
        "all_event_dates",
        "all_event_ages",
        "first_event_date",
        "first_event_age",
        "latest_event_date",
        "latest_event_age",
        "outcome_state",
    ]
    curve_fields = [
        "group",
        "time_days",
        "time_years",
        "n_risk_before",
        "function_events",
        "death_competing_events",
        "administrative_censors",
        "event_free_probability",
        "function_cumulative_incidence",
        "death_cumulative_incidence",
        "n_risk_after",
    ]
    readout_fields = [
        "group",
        "years_after_80",
        "cumulative_incidence",
        "n_under_observation",
        "starting_n",
        "support_fraction",
        "support_status",
        "note",
    ]
    followup_fields = [
        "group",
        "metric",
        "n",
        "count",
        "mean",
        "minimum",
        "q1",
        "median",
        "q3",
        "maximum",
    ]
    date_change_fields = [
        "scenario",
        "research_id",
        "person_id",
        "primary_detected",
        "scenario_detected",
        "primary_state",
        "scenario_state",
        "primary_first_function_date",
        "scenario_first_function_date",
        "primary_latest_function_date",
        "scenario_latest_function_date",
        "age85_used_as_boundary",
    ]
    immutable = before_hashes == after_hashes
    validation_pass = (
        immutable
        and deterministic_assumed
        and not result["errors"]
        and result["other_set_equal"]
    )
    artifacts = {
        "RESULTS_SUMMARY.csv": csv_bytes(result_fields, results_rows(result)),
        "EVENT_AGE_TABLE.csv": csv_bytes(event_fields, result["event_age_rows"]),
        "AALEN_JOHANSEN_CURVES.csv": csv_bytes(curve_fields, result["curves"]),
        "AALEN_JOHANSEN_READOUTS.csv": csv_bytes(
            readout_fields, result["readouts"]
        ),
        "FOLLOWUP_DOCUMENTATION.csv": csv_bytes(
            followup_fields, result["followup"]
        ),
        "LATEST_EVENT_AGE_DISTRIBUTION.csv": csv_bytes(
            [
                "research_id",
                "person_id",
                "full_name",
                "primary_group",
                "first_event_age",
                "latest_event_age",
                "event_count",
            ],
            result["latest_rows"],
        ),
        "EVENT_AGE_BANDS.csv": csv_bytes(
            ["group", "age_band", "qualifying_detected_event_count"],
            result["age_band_rows"],
        ),
        "FUNCTION_IMPAIRMENT_SEQUENCES.csv": csv_bytes(
            ["group", "locked_person_level_state", "person_count", "interpretation"],
            result["sequence_rows"],
        ),
        "DATE_SENSITIVITY.csv": csv_bytes(
            [
                "scenario",
                "apollo_numerator",
                "apollo_denominator",
                "other_numerator",
                "other_denominator",
                "apollo_minus_other_risk_difference",
                "age80_eligibility_changes",
                "detection_or_sequence_changes",
                "date_only_changes",
                "age85_used_as_boundary",
                "note",
            ],
            result["date_rows"],
        ),
        "DATE_CLASSIFICATION_CHANGES.csv": csv_bytes(
            date_change_fields, result["date_changes"]
        ),
        "SET_MEMBERSHIP.csv": csv_bytes(
            ["set_name", "eligible_n", "person_ids", "nested_within"],
            result["set_rows"],
        ),
        "LOCKED_INPUT_HASHES.csv": csv_bytes(
            ["path", "sha256_before", "sha256_after", "unchanged"],
            [
                {
                    "path": path,
                    "sha256_before": before_hashes[path],
                    "sha256_after": after_hashes.get(path, ""),
                    "unchanged": int(before_hashes[path] == after_hashes.get(path)),
                }
                for path in sorted(before_hashes)
            ],
        ),
        "AALEN_JOHANSEN_CURVES.svg": make_svg(
            result["curves"], result["readouts"]
        ),
        "ANALYSIS_REPORT.md": report_markdown(result).encode("utf-8"),
        "CORRECTED_CONCLUSION.md": corrected_conclusion(result).encode("utf-8"),
        "CONTAMINATION.md": contamination_markdown().encode("utf-8"),
        "VALIDATION.md": validation_markdown(
            result, before_hashes, after_hashes, deterministic_assumed
        ).encode("utf-8"),
        "STAGE_COMPLETE.md": stage_complete_markdown(
            result, validation_pass
        ).encode("utf-8"),
    }
    return artifacts


def main() -> int:
    OUT.mkdir(exist_ok=True)
    before_hashes = locked_hashes()
    cohort_rows = read_csv(ROOT / "stage1" / "cohort.csv")
    outcome_rows = read_csv(ROOT / "stage1c" / "PERSON_OUTCOMES.csv")
    event_rows = read_csv(ROOT / "stage1c" / "EVIDENCE_EVENTS.csv")

    first_result = analyze(cohort_rows, outcome_rows, event_rows)
    second_result = analyze(cohort_rows, outcome_rows, event_rows)
    after_hashes = locked_hashes()

    first_artifacts = render_artifacts(
        first_result, before_hashes, after_hashes, True
    )
    second_artifacts = render_artifacts(
        second_result, before_hashes, after_hashes, True
    )
    deterministic = first_artifacts == second_artifacts
    if not deterministic:
        first_artifacts = render_artifacts(
            first_result, before_hashes, after_hashes, False
        )

    for name, content in first_artifacts.items():
        (OUT / name).write_bytes(content)

    output_hash_rows = []
    for name in sorted(first_artifacts):
        path = OUT / name
        output_hash_rows.append(
            {
                "path": f"stage2r/{name}",
                "sha256": file_sha256(path),
                "generated_by_analysis": 1,
            }
        )
    for name in ("analysis.py", "CONTEXT_ATTESTATION.md", "ANALYSIS_DECISIONS.md"):
        path = OUT / name
        output_hash_rows.append(
            {
                "path": f"stage2r/{name}",
                "sha256": file_sha256(path),
                "generated_by_analysis": 0,
            }
        )
    (OUT / "OUTPUT_HASHES.csv").write_bytes(
        csv_bytes(
            ["path", "sha256", "generated_by_analysis"],
            sorted(output_hash_rows, key=lambda row: row["path"]),
        )
    )

    immutable = before_hashes == after_hashes
    valid = (
        immutable
        and deterministic
        and not first_result["errors"]
        and first_result["other_set_equal"]
    )
    print(
        json.dumps(
            {
                "status": "PASS" if valid else "FAIL",
                "classification": first_result["strength"],
                "direction": first_result["direction"],
                "locked_inputs_immutable": immutable,
                "deterministic_regeneration": deterministic,
                "validation_errors": first_result["errors"],
            },
            sort_keys=True,
        )
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
