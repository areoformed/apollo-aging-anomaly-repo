#!/usr/bin/env python3
"""Independent controller validation of repaired sol_002 Stage 3.

This validator does not import either experimenter analysis module. It checks
the permanent archive, rebuilds the harmonized cohorts and key estimands from
the locked person-level files, and explicitly validates DEV-20260723-13.
"""

from __future__ import annotations

import csv
import hashlib
import math
import random
from collections import Counter
from datetime import date
from pathlib import Path

MACHINE_ROOT = Path(
    "./Machine Efforts"
)
RUN = MACHINE_ROOT / "5-6 Sol Replication" / "run" / "sol_002"
STAGE3 = RUN / "stage3"
REFERENCE_SOURCE_MANIFEST = (
    MACHINE_ROOT
    / "5-6 Sol Replication"
    / "controller"
    / "sol_002"
    / "STAGE3_REFERENCE_MANIFEST.csv"
)
CENSOR = date(2026, 6, 1)
LANDMARK = date(1973, 1, 1)
DAYS_PER_YEAR = 365.2425
SEED = 20260721
REPS = 50_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_rows(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def verify_hash_manifest(
    path: Path,
    root: Path,
    substitutions: dict[str, Path] | None = None,
) -> None:
    substitutions = substitutions or {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split("  ", 1)
        target = substitutions.get(relative, root / relative)
        assert target.is_file(), target
        assert sha256(target) == expected, target


def verify_initial_stage3_manifest() -> None:
    for raw in (RUN / "STAGE3_INITIAL_SHA256.txt").read_text(
        encoding="utf-8"
    ).splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split("  ", 1)
        if relative.startswith("stage3/"):
            target = RUN / "stage3_pre_controller_repair" / relative.removeprefix(
                "stage3/"
            )
        elif relative == "ACTION_LOG.md":
            target = RUN / "snapshots" / "ACTION_LOG_STAGE3_INITIAL.md"
        else:
            target = RUN / relative
        assert target.is_file(), target
        assert sha256(target) == expected, target


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def birthday_80(birth: date) -> date:
    return birth.replace(year=birth.year + 80)


def age_years(birth: date, endpoint: date) -> float:
    return (endpoint - birth).days / DAYS_PER_YEAR


def km_rmst(records: list[tuple[float, int]], horizon: float) -> float:
    by_time: dict[float, list[int]] = {}
    for time, event in records:
        by_time.setdefault(time, []).append(event)
    at_risk = len(records)
    survival = 1.0
    previous = 0.0
    area = 0.0
    for time in sorted(by_time):
        bounded = min(time, horizon)
        if bounded > previous:
            area += survival * (bounded - previous)
            previous = bounded
        if time >= horizon:
            break
        events = sum(by_time[time])
        censored = len(by_time[time]) - events
        if events:
            survival *= 1.0 - events / at_risk
        at_risk -= events + censored
    if previous < horizon:
        area += survival * (horizon - previous)
    return area


def km_at_age(records: list[tuple[float, int]], target: float) -> float:
    by_time: dict[float, list[int]] = {}
    for time, event in records:
        by_time.setdefault(time, []).append(event)
    at_risk = len(records)
    survival = 1.0
    for time in sorted(by_time):
        if time > target:
            break
        events = sum(by_time[time])
        censored = len(by_time[time]) - events
        if events:
            survival *= 1.0 - events / at_risk
        at_risk -= events + censored
    return survival


def bootstrap_rmst(
    apollo: list[tuple[float, int]],
    other: list[tuple[float, int]],
) -> tuple[float, float]:
    generator = random.Random(SEED)
    values = []
    for _ in range(REPS):
        a_sample = [apollo[generator.randrange(len(apollo))] for _ in apollo]
        o_sample = [other[generator.randrange(len(other))] for _ in other]
        values.append(km_rmst(a_sample, 50.0) - km_rmst(o_sample, 50.0))
    return percentile(values, 0.025), percentile(values, 0.975)


def wilson(successes: int, total: int) -> tuple[float, float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    return center - half, center + half


def newcombe(
    successes_a: int, total_a: int, successes_b: int, total_b: int
) -> tuple[float, float]:
    p_a = successes_a / total_a
    p_b = successes_b / total_b
    low_a, high_a = wilson(successes_a, total_a)
    low_b, high_b = wilson(successes_b, total_b)
    difference = p_a - p_b
    low = difference - math.sqrt((p_a - low_a) ** 2 + (high_b - p_b) ** 2)
    high = difference + math.sqrt((high_a - p_a) ** 2 + (p_b - low_b) ** 2)
    return low, high


def bootstrap_binary(
    outcomes_a: list[int], outcomes_b: list[int]
) -> tuple[float, float]:
    generator = random.Random(SEED)
    values = []
    for _ in range(REPS):
        a_mean = (
            sum(
                outcomes_a[generator.randrange(len(outcomes_a))]
                for _ in outcomes_a
            )
            / len(outcomes_a)
        )
        b_mean = (
            sum(
                outcomes_b[generator.randrange(len(outcomes_b))]
                for _ in outcomes_b
            )
            / len(outcomes_b)
        )
        values.append(a_mean - b_mean)
    return percentile(values, 0.025), percentile(values, 0.975)


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row_1 = a + b
    row_2 = c + d
    col_1 = a + c
    total = row_1 + row_2

    def probability(x: int) -> float:
        return (
            math.comb(col_1, x)
            * math.comb(total - col_1, row_1 - x)
            / math.comb(total, row_1)
        )

    lower = max(0, row_1 - (total - col_1))
    upper = min(row_1, col_1)
    observed = probability(a)
    return sum(
        probability(x)
        for x in range(lower, upper + 1)
        if probability(x) <= observed + 1e-15
    )


def result(
    rows: list[dict[str, str]],
    *,
    analysis: str,
    endpoint_rule: str,
    metric: str,
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["analysis"] == analysis
        and row["endpoint_rule"] == endpoint_rule
        and row["metric"] == metric
    ]
    assert len(matches) == 1, (analysis, endpoint_rule, metric, len(matches))
    return matches[0]


def main() -> None:
    # Permanent archive integrity.
    verify_hash_manifest(RUN / "STAGE3_SHA256.txt", RUN)
    verify_initial_stage3_manifest()
    verify_hash_manifest(RUN / "STAGE1_SHA256.txt", RUN)
    verify_hash_manifest(RUN / "STAGE1B_SHA256.txt", RUN)
    verify_hash_manifest(RUN / "STAGE1C_SHA256.txt", RUN)
    verify_hash_manifest(
        RUN / "STAGE2_SHA256.txt",
        RUN,
        {"ACTION_LOG.md": RUN / "snapshots" / "ACTION_LOG_STAGE2.md"},
    )
    assert sha256(RUN / "stage2" / "BLIND_CONCLUSION.md") == (
        "727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df"
    )
    assert sha256(
        STAGE3 / "locked_supplement" / "stage2r" / "CORRECTED_CONCLUSION.md"
    ) == "bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600"

    reference_manifest = csv_rows(REFERENCE_SOURCE_MANIFEST)
    assert len(reference_manifest) == 63
    for row in reference_manifest:
        source = Path(row["source_path"])
        archived = RUN / row["runtime_path"]
        assert source.is_file() and archived.is_file()
        assert sha256(source) == row["source_sha256"]
        assert sha256(archived) == row["runtime_sha256"]

    # Identity and row-scope reconstruction.
    cohort = csv_rows(RUN / "stage1" / "cohort.csv")
    by_id = {row["person_id"]: row for row in cohort}
    assert len(cohort) == len(by_id) == 95
    reference = csv_rows(
        STAGE3 / "reference" / "derived_cohorts" / "cohorts" / "all_astronauts.tsv",
        delimiter="\t",
    )
    mapping = csv_rows(STAGE3 / "IDENTITY_MAPPING.csv")
    assert Counter(row["scope_status"] for row in mapping) == Counter(
        {"SHARED": 95, "ONLY_IN_REFERENCE": 3}
    )
    assert {
        row["reference_name"]
        for row in mapping
        if row["scope_status"] == "ONLY_IN_REFERENCE"
    } == {"Alvin Swauger White", "Iven Carl Kincheloe Jr.", "William Barton Bridgeman"}
    shared = {row["ours_person_id"]: row for row in mapping if row["ours_person_id"]}
    assert set(shared) == set(by_id)
    reference_by_birth_name = {(row["Date of Birth"], row["Name"]): row for row in reference}
    for person_id, map_row in shared.items():
        ours = by_id[person_id]
        assert ours["birth_date"] == map_row["birth_date"]
        ref = reference_by_birth_name[(map_row["birth_date"], map_row["reference_name"])]
        assert (ours["apollo_flew"] == "1") == (ref["analysis_primary"] == "apollo")
    assert sum(row["apollo_flew"] == "1" for row in cohort) == 29

    # DEV-20260723-13 reconstruction.
    other_all = [row for row in cohort if row["other_all"] == "1"]
    corrected_available = [
        row for row in other_all if row["pre1970_accidental_death"] == "0"
    ]
    excluded = [row for row in other_all if row["pre1970_accidental_death"] == "1"]
    assert (len(other_all), len(corrected_available), len(excluded)) == (66, 54, 12)

    def endpoint(row: dict[str, str]) -> date:
        return parse_date(row["death_date"]) or CENSOR  # type: ignore[return-value]

    post1973_all = {
        row["person_id"] for row in other_all if endpoint(row) >= LANDMARK
    }
    post1973_available = {
        row["person_id"] for row in corrected_available if endpoint(row) >= LANDMARK
    }
    age80_all = {
        row["person_id"]
        for row in other_all
        if birthday_80(parse_date(row["birth_date"])) <= endpoint(row)  # type: ignore[arg-type]
    }
    age80_available = {
        row["person_id"]
        for row in corrected_available
        if birthday_80(parse_date(row["birth_date"])) <= endpoint(row)  # type: ignore[arg-type]
    }
    assert post1973_all == post1973_available and len(post1973_all) == 53
    assert age80_all == age80_available and len(age80_all) == 35

    correction_rows = csv_rows(STAGE3 / "OTHER_AVAILABLE_CORRECTION.csv")
    assert len(correction_rows) == 66
    assert sum(row["corrected_other_available"] == "1" for row in correction_rows) == 54
    assert sum(row["pre1970_accidental_death"] == "1" for row in correction_rows) == 12

    corrected_birth_records = []
    for row in corrected_available:
        birth = parse_date(row["birth_date"])
        end = endpoint(row)
        corrected_birth_records.append(
            (age_years(birth, end), int(bool(row["death_date"])))  # type: ignore[arg-type]
        )

    results = csv_rows(STAGE3 / "HARMONIZED_RESULTS.csv")
    expected_km = {
        60: 0.944444444,
        70: 0.833333333,
        80: 0.648148148,
        85: 0.498084291,
        90: 0.322645695,
        95: 0.225851986,
    }
    for target, expected in expected_km.items():
        calculated = km_at_age(corrected_birth_records, float(target))
        assert abs(calculated - expected) < 5e-10
        reported = result(
            results,
            analysis="DEV-20260723-13_POST_LOCK_CORRECTION",
            endpoint_rule="FROZEN_OTHER_AVAILABLE_SECONDARY_BIRTH_ORIGIN",
            metric=f"km_survival_to_age_{target}",
        )
        assert abs(float(reported["estimate"]) - calculated) < 5e-10

    # Harmonized RMST reconstruction with the adjudicated Rushworth one-day date.
    stage3_dates = {
        row["person_id"]: parse_date(row["death_date_stage3_adjudicated"])
        for row in correction_rows
    }

    def landmark_records(rows: list[dict[str, str]]) -> list[tuple[float, int]]:
        records = []
        for row in rows:
            end = stage3_dates.get(row["person_id"]) or parse_date(row["death_date"]) or CENSOR
            if end < LANDMARK:
                continue
            records.append(((end - LANDMARK).days / DAYS_PER_YEAR, int(bool(row["death_date"]))))
        return records

    apollo_records = landmark_records([row for row in cohort if row["apollo_flew"] == "1"])
    other_records = landmark_records(other_all)
    assert (len(apollo_records), len(other_records)) == (29, 53)
    rmst_difference = km_rmst(apollo_records, 50.0) - km_rmst(other_records, 50.0)
    assert abs(rmst_difference - 0.670028147) < 5e-9
    rmst_row = result(
        results,
        analysis="HARMONIZED_SHARED_SCOPE_1973_LANDMARK",
        endpoint_rule="all_cause_survival",
        metric="rmst_difference",
    )
    assert abs(float(rmst_row["estimate"]) - rmst_difference) < 5e-9
    rmst_low, rmst_high = bootstrap_rmst(apollo_records, other_records)
    assert abs(rmst_low - float(rmst_row["ci_lower"])) < 5e-9
    assert abs(rmst_high - float(rmst_row["ci_upper"])) < 5e-9

    # Both public-evidence rules on the same shared age-80 people.
    event_rows = csv_rows(
        STAGE3
        / "locked_supplement"
        / "stage2r"
        / "EVENT_AGE_TABLE.csv"
    )
    sol_detection = {
        row["person_id"]: int(row["detected_any_age_80_plus"]) for row in event_rows
    }
    reference_lookup = {
        (row["Date of Birth"], row["Name"]): row for row in reference
    }
    ref_detection: dict[str, int] = {}
    for person_id in sol_detection:
        map_row = shared[person_id]
        ref = reference_lookup[(map_row["birth_date"], map_row["reference_name"])]
        ref_detection[person_id] = int(ref["Space Grandpa"] == "Y")

    apollo_age80 = [
        row["person_id"]
        for row in cohort
        if row["apollo_flew"] == "1" and row["person_id"] in sol_detection
    ]
    other_age80 = [
        row["person_id"]
        for row in cohort
        if row["other_all"] == "1" and row["person_id"] in sol_detection
    ]
    sol_a = [sol_detection[person_id] for person_id in apollo_age80]
    sol_o = [sol_detection[person_id] for person_id in other_age80]
    ref_a = [ref_detection[person_id] for person_id in apollo_age80]
    ref_o = [ref_detection[person_id] for person_id in other_age80]
    assert (len(sol_a), sum(sol_a), len(sol_o), sum(sol_o)) == (22, 3, 35, 2)
    assert (len(ref_a), sum(ref_a), len(ref_o), sum(ref_o)) == (22, 21, 35, 24)
    assert Counter(zip(sol_a + sol_o, ref_a + ref_o)) == Counter(
        {(0, 0): 12, (0, 1): 40, (1, 1): 5}
    )

    for outcomes_a, outcomes_b, endpoint_rule, expected_p in (
        (
            sol_a,
            sol_o,
            "SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS",
            0.363805215,
        ),
        (ref_a, ref_o, "REFERENCE_SPACE_GRANDPA", 0.019340318),
    ):
        successes_a, successes_b = sum(outcomes_a), sum(outcomes_b)
        row = result(
            results,
            analysis="HARMONIZED_SHARED_AGE80_RISK_SET",
            endpoint_rule=endpoint_rule,
            metric="risk_difference",
        )
        difference = successes_a / len(outcomes_a) - successes_b / len(outcomes_b)
        low, high = newcombe(
            successes_a, len(outcomes_a), successes_b, len(outcomes_b)
        )
        p_value = fisher_two_sided(
            successes_a,
            len(outcomes_a) - successes_a,
            successes_b,
            len(outcomes_b) - successes_b,
        )
        assert abs(float(row["estimate"]) - difference) < 5e-10
        assert abs(float(row["ci_lower"]) - low) < 5e-9
        assert abs(float(row["ci_upper"]) - high) < 5e-9
        assert abs(p_value - expected_p) < 5e-9
        assert abs(float(row["p_value"]) - p_value) < 5e-9
        bootstrap_row = result(
            results,
            analysis="HARMONIZED_SHARED_AGE80_RISK_SET",
            endpoint_rule=endpoint_rule,
            metric="risk_difference_bootstrap",
        )
        boot_low, boot_high = bootstrap_binary(outcomes_a, outcomes_b)
        assert abs(float(bootstrap_row["ci_lower"]) - boot_low) < 5e-9
        assert abs(float(bootstrap_row["ci_upper"]) - boot_high) < 5e-9

    # Required reporting boundaries and repaired classification.
    differences = csv_rows(STAGE3 / "ROW_DIFFERENCES.csv")
    categories = Counter(row["difference_category"] for row in differences)
    assert categories["implementation_analysis_difference"] == 1
    assert categories["public_evidence_endpoint_disagreement"] == 40
    assert categories["definition_only_membership_difference"] == 4
    assert categories["birth_death_status_disagreement"] == 3
    assert not any(
        "FIVE_YEAR" in "|".join(row.values()).upper() for row in results
    )
    for name in ("RECONCILIATION.md", "VALIDATION.md", "STAGE_COMPLETE.md"):
        text = (STAGE3 / name).read_text(encoding="utf-8")
        assert "DEV-20260723-13" in text
        assert "54" in text and "12" in text and "unchanged" in text
    assert (RUN / "stage3_pre_controller_repair" / "STAGE_COMPLETE.md").is_file()

    print(
        "STAGE3_CONTROLLER_VALIDATION_PASS "
        f"rmst={rmst_difference:.9f} "
        f"other_available={len(corrected_available)} "
        f"sol_rd={sum(sol_a)/len(sol_a)-sum(sol_o)/len(sol_o):.9f} "
        f"reference_rd={sum(ref_a)/len(ref_a)-sum(ref_o)/len(ref_o):.9f}"
    )


if __name__ == "__main__":
    main()
