#!/usr/bin/env python3
"""Independent read-only validator for generated Stage 3 artifacts."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TREES = {
    "stage1": "3c23c3cebb6e37f0a8ab443cb1a7bdda6235d9e5cdb341a6d55c0a6f763fd8e1",
    "stage1b": "65b5a1128844641577c96cb4fe396a8422bc75582d2d77035c91e873ac73e5d3",
    "stage1c": "c7b3555a8a569cab5429fb07e76e5b502bbdc466494548409ad17cdfa1c7901c",
    "stage2": "95b6c76f30a507bba1c363507dc04d2232488475eda34085d216e2937161799a",
    "stage3/reference": "d4bc2493af7604615b5c9f6efd417d8ae4fe4799f5e27436c7d18bc23bd0e363",
    "stage3/locked_supplement": "4cf652dc741ee102c8d378352d8864f77a5c7b051dc41a71e2eea78b628726cd",
}
BLIND_HASH = "727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df"
CORRECTED_HASH = "bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def aggregate(relative: str) -> str:
    lines = []
    for path in sorted(p for p in (ROOT / relative).rglob("*") if p.is_file()):
        lines.append(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n")
    return hashlib.sha256("".join(lines).encode()).hexdigest()


def rows(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(value: str, expected: float, tolerance: float = 5e-9) -> bool:
    return abs(float(value) - expected) <= tolerance


def main() -> None:
    required = [
        "stage3/RECONCILIATION.md",
        "stage3/ROW_DIFFERENCES.csv",
        "stage3/HARMONIZED_RESULTS.csv",
        "stage3/CONTAMINATION.md",
        "stage3/STAGE_COMPLETE.md",
        "stage3/SOURCE_LOG.csv",
        "stage3/VALIDATION.md",
        "stage3/IDENTITY_MAPPING.csv",
        "stage3/PUBLIC_FUNCTION_CROSSTAB.csv",
        "stage3/LOCKED_INPUT_HASHES.csv",
        "stage3/REFERENCE_MANIFEST_VALIDATION.csv",
        "stage3/analysis.py",
        "stage3/validate.py",
    ]
    assert all((ROOT / path).is_file() for path in required)
    assert {key: aggregate(key) for key in EXPECTED_TREES} == EXPECTED_TREES
    blind = ROOT / "stage2/BLIND_CONCLUSION.md"
    corrected = ROOT / "stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md"
    assert sha(blind) == BLIND_HASH
    assert sha(corrected) == CORRECTED_HASH

    mapping = rows("stage3/IDENTITY_MAPPING.csv")
    assert Counter(row["scope_status"] for row in mapping) == Counter(
        {"SHARED": 95, "ONLY_IN_REFERENCE": 3}
    )
    assert len({row["ours_person_id"] for row in mapping if row["ours_person_id"]}) == 95
    assert len({row["reference_person_id"] for row in mapping}) == 98

    differences = rows("stage3/ROW_DIFFERENCES.csv")
    categories = Counter(row["difference_category"] for row in differences)
    assert categories == Counter(
        {
            "exact_agreement": 42,
            "public_evidence_endpoint_disagreement": 40,
            "program_flag_disagreement": 13,
            "definition_only_membership_difference": 4,
            "birth_death_status_disagreement": 3,
            "factual_membership_disagreement": 1,
        }
    )
    assert sum(row["scope_status"] == "ONLY_IN_REFERENCE" for row in differences) == 3
    assert sum(row["scope_status"] == "ONLY_IN_YOURS_NONE" for row in differences) == 1
    assert not any(
        row["difference_category"] == "factual_membership_disagreement"
        and row["scope_status"] != "SUMMARY_NONE"
        for row in differences
    )

    results = rows("stage3/HARMONIZED_RESULTS.csv")
    primary = next(
        row
        for row in results
        if row["analysis"] == "HARMONIZED_SHARED_SCOPE_1973_LANDMARK"
        and row["metric"] == "rmst_difference"
    )
    assert close(primary["estimate"], 0.670028147)
    assert close(primary["ci_lower"], -5.088314852)
    assert close(primary["ci_upper"], 6.098816053)
    sol = next(
        row
        for row in results
        if row["analysis"] == "HARMONIZED_SHARED_AGE80_RISK_SET"
        and row["endpoint_rule"] == "SOL_CORRECTED_UNRESTRICTED_AGE80_PLUS"
        and row["metric"] == "risk_difference"
    )
    sg = next(
        row
        for row in results
        if row["analysis"] == "HARMONIZED_SHARED_AGE80_RISK_SET"
        and row["endpoint_rule"] == "REFERENCE_SPACE_GRANDPA"
        and row["metric"] == "risk_difference"
    )
    assert (sol["numerator_a"], sol["denominator_a"], sol["numerator_b"], sol["denominator_b"]) == (
        "3",
        "22",
        "2",
        "35",
    )
    assert (sg["numerator_a"], sg["denominator_a"], sg["numerator_b"], sg["denominator_b"]) == (
        "21",
        "22",
        "24",
        "35",
    )
    assert not any("FIVE_YEAR" in "|".join(row.values()).upper() for row in results)

    crosstab = rows("stage3/PUBLIC_FUNCTION_CROSSTAB.csv")
    all_cells = {
        (row["sol_qualifying_function"], row["reference_space_grandpa"]): int(
            row["count"]
        )
        for row in crosstab
        if row["group"] == "ALL_SHARED"
    }
    assert all_cells == {("0", "0"): 12, ("0", "1"): 40, ("1", "0"): 0, ("1", "1"): 5}

    manifest = rows("stage3/REFERENCE_MANIFEST_VALIDATION.csv")
    assert len(manifest) == 63 and all(row["match"] == "1" for row in manifest)
    locked = rows("stage3/LOCKED_INPUT_HASHES.csv")
    assert len(locked) == 8 and all(row["unchanged"] == "1" for row in locked)

    report = (ROOT / "stage3/RECONCILIATION.md").read_text(encoding="utf-8")
    assert blind.read_text(encoding="utf-8").rstrip() in report
    assert corrected.read_text(encoding="utf-8").rstrip() in report
    assert "weakens the broad" in report
    assert "does not overturn" in report
    print("STAGE3_VALIDATION_PASS")


if __name__ == "__main__":
    main()
