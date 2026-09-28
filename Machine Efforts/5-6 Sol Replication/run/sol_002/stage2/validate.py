#!/usr/bin/env python3
"""Independent read-only mechanical validation for Stage 2."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import analysis


ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "stage2"


def rows(name: str) -> list[dict[str, str]]:
    with (STAGE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    manifest, aggregate = analysis.locked_input_manifest()
    require(aggregate == analysis.LOCKED_AGGREGATE_SHA256, "locked input hash")
    retained_manifest = rows("locked_input_hashes.csv")
    require(manifest == retained_manifest, "locked manifest content")

    required = [
        "ANALYSIS_DECISIONS.md", "analysis.py", "ANALYSIS_REPORT.md",
        "RESULTS_SUMMARY.csv", "VALIDATION.md", "CONTAMINATION.md",
        "BLIND_CONCLUSION.md", "STAGE_COMPLETE.md",
        "EXTERNAL_SOURCE_LOG.csv", "ssa_male_cohort_expectations.csv",
        "locked_input_hashes.csv", "survival_group_summary.csv",
        "population_expectation.csv", "survival_landmark_rmst.csv",
        "cox_model.csv", "ph_diagnostic.csv", "km_birth_selected_ages.csv",
        "public_function_primary.csv", "public_function_crude.csv",
        "documentation_depth.csv", "documentation_counts.csv",
        "latent_event_bounds.csv", "boundary_date_sensitivity.csv",
        "latest_function_age.csv", "temporal_sequences.csv",
        "survival_landmark_km.svg", "survival_birth_km.svg",
        "public_function_cif.svg", "documentation_depth.svg",
    ]
    for name in required:
        path = STAGE / name
        require(path.is_file() and path.stat().st_size > 0, f"required artifact {name}")

    for path in STAGE.glob("*.csv"):
        data = path.read_bytes()
        require(b"\n" not in data.replace(b"\r\n", b""), f"RFC4180 CRLF {path.name}")

    cohort = rows("../stage1/cohort.csv")
    outcomes = rows("../stage1c/PERSON_OUTCOMES.csv")
    outcome_by_person = {row["person_id"]: row for row in outcomes}
    require(len(cohort) == len(outcomes) == len(outcome_by_person), "one-to-one outcome join")

    def group(row: dict[str, str], name: str) -> bool:
        return analysis.group_membership(row)[name]

    require(
        not any(group(row, "APOLLO_FLEW") and group(row, "OTHER_ALL") for row in cohort),
        "Apollo/other disjointness",
    )
    landmark_other = {
        row["person_id"] for row in cohort
        if group(row, "OTHER_ALL") and (not row["death_date"] or row["death_date"] >= "1973-01-01")
    }
    landmark_available = {
        row["person_id"] for row in cohort
        if group(row, "OTHER_AVAILABLE") and (not row["death_date"] or row["death_date"] >= "1973-01-01")
    }
    age80_other = {
        row["person_id"] for row in cohort
        if group(row, "OTHER_ALL") and outcome_by_person[row["person_id"]]["eligible_age80"] == "1"
    }
    age80_available = {
        row["person_id"] for row in cohort
        if group(row, "OTHER_AVAILABLE") and outcome_by_person[row["person_id"]]["eligible_age80"] == "1"
    }
    require(landmark_other == landmark_available, "landmark set identity")
    require(age80_other == age80_available, "age80 set identity")

    rmst = rows("survival_landmark_rmst.csv")
    require(len(rmst) == 3, "three RMST contrasts")
    require(rmst[0]["analysis_role"] == "PRIMARY", "RMST primary row")
    require(all(row["bootstrap_replicates"] == "50000" for row in rmst), "RMST replicates")
    require(all(row["bootstrap_seed"] == "20260721" for row in rmst), "RMST seed")
    require(all("OTHER_AVAILABLE" not in row["contrast"] for row in rmst), "no duplicate available RMST")

    cox = rows("cox_model.csv")
    require({row["term"] for row in cox} == {"APOLLO_FLEW", "AGE_AT_LANDMARK_PER_YEAR"}, "Cox terms")
    require(all(row["ties"] == "Efron" and row["converged"] == "1" for row in cox), "Cox fit")
    ph = rows("ph_diagnostic.csv")
    require({row["term"] for row in ph} == {"APOLLO_FLEW", "AGE_AT_LANDMARK", "GLOBAL_APPROXIMATION"}, "PH rows")

    public = rows("public_function_primary.csv")
    require(len(public) == 4, "three public contrasts plus R001")
    require(public[0]["analysis_role"] == "PRIMARY", "public primary row")
    require(all(row["bootstrap_replicates"] == "50000" for row in public), "public replicates")
    require(all(row["bootstrap_seed"] == "20260721" for row in public), "public seed")
    require(sum("R001 excluded" in row["contrast"] for row in public) == 1, "R001 AJ sensitivity")
    crude = rows("public_function_crude.csv")
    require(len(crude) == 4, "crude contrasts")
    require(sum("R001 excluded" in row["contrast"] for row in crude) == 1, "R001 crude sensitivity")
    for row in crude:
        for field in (
            "apollo_exact95_lower", "apollo_exact95_upper",
            "comparator_exact95_lower", "comparator_exact95_upper",
            "risk_difference95_lower", "risk_difference95_upper",
            "risk_ratio95_lower", "risk_ratio95_upper",
            "odds_ratio_conditional_exact95_lower",
            "odds_ratio_conditional_exact95_upper",
            "fisher_exact_two_sided_p",
        ):
            require(row[field] != "", f"crude uncertainty {field}")

    evidence = rows("../stage1c/EVIDENCE_EVENTS.csv")
    boundary = [
        row for row in evidence
        if row["qualifies"] == "1" and row["boundary_sensitive"] == "1"
    ]
    boundary_table = rows("boundary_date_sensitivity.csv")
    require(not boundary and boundary_table[0]["research_id"] == "NONE", "boundary sensitivity")

    source_log = rows("EXTERNAL_SOURCE_LOG.csv")
    require(all(row["url"].startswith("https://www.ssa.gov/") for row in source_log), "SSA-only external URLs")
    expected = rows("ssa_male_cohort_expectations.csv")
    represented_years = {int(row["birth_date"][:4]) for row in cohort}
    require(represented_years.issubset({int(row["birth_year"]) for row in expected}), "life-table year coverage")

    summary = rows("RESULTS_SUMMARY.csv")
    require(any(row["primary"] == "YES" and row["analysis"] == "LANDMARK_RMST" for row in summary), "primary RMST summary")
    require(any(row["primary"] == "YES" and row["analysis"] == "FIVE_YEAR_AALEN_JOHANSEN" for row in summary), "primary public summary")
    require(any(row["sensitivity_type"] == "TECHNICAL_DEVIATION_SENSITIVITY" for row in summary), "technical sensitivity summary")
    require(any(row["sensitivity_type"] == "LATENT_EVENT_DIFFERENT_QUESTION" for row in summary), "latent summary")

    blind = (STAGE / "BLIND_CONCLUSION.md").read_text(encoding="utf-8")
    primary_rmst = float(rmst[0]["apollo_minus_comparator_rmst_years"])
    primary_public = float(public[0]["apollo_minus_comparator_risk_difference"])
    require(("HIGHER" if primary_rmst > 0 else "LOWER") in blind, "survival direction")
    require(("HIGHER" if primary_public > 0 else "LOWER") in blind, "public direction")
    require("SURVIVAL: **NOT_DETECTED" in blind, "survival classification")
    require("PUBLIC FUNCTION: **NOT_DETECTED" in blind, "public classification")

    for name in (
        "survival_landmark_km.svg", "survival_birth_km.svg",
        "public_function_cif.svg", "documentation_depth.svg",
    ):
        text = (STAGE / name).read_text(encoding="utf-8")
        require(text.lstrip().startswith("<svg") and text.rstrip().endswith("</svg>"), f"SVG structure {name}")

    report = (STAGE / "ANALYSIS_REPORT.md").read_text(encoding="utf-8")
    require("future-flight-selected" in report, "future-flight selection limitation")
    require("healthy-selectee" in report, "healthy-selectee limitation")
    require("noncausal" in report, "noncausal interpretation")
    require("not a clinical" in report, "clinical-cognition restriction")
    require("No prespecified descriptive anomaly is detected." in blind, "narrow anomaly answer")

    print("PASS: independent Stage 2 mechanical validation")


if __name__ == "__main__":
    main()
