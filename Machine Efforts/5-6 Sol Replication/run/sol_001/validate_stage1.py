#!/usr/bin/env python3
"""Mechanical integrity checks for Stage 1; performs no outcome analysis."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "stage1"
EXPECTED_COHORT_COLUMNS = [
    "person_id", "full_name", "search_disambiguator", "birth_date", "death_date",
    "vital_status_20260601", "first_selection_date", "first_spaceflight_date",
    "apollo_flew", "apollo_missions", "apollo1_crew", "core_nasa_non_apollo",
    "military_x15", "military_dyna_soar", "military_mol", "other_all",
    "pre1970_accidental_death", "backup_crew_roles", "membership_source_urls",
    "birth_source_url", "death_source_url", "confidence", "notes",
]
EXPECTED_SOURCE_COLUMNS = [
    "timestamp", "person_id", "query_or_direct_navigation", "result_rank", "url",
    "opened", "access_result", "fact_supported", "source_tier", "notes",
]
BOOL_FIELDS = [
    "apollo_flew", "apollo1_crew", "core_nasa_non_apollo", "military_x15",
    "military_dyna_soar", "military_mol", "other_all",
    "pre1970_accidental_death",
]
DATE_FIELDS = ["birth_date", "death_date", "first_selection_date", "first_spaceflight_date"]


check_count = 0


def require(condition: bool, label: str) -> None:
    global check_count
    if not condition:
        raise AssertionError(label)
    check_count += 1


with (STAGE / "cohort.csv").open(newline="", encoding="utf-8") as handle:
    cohort_reader = csv.DictReader(handle)
    require(cohort_reader.fieldnames == EXPECTED_COHORT_COLUMNS, "cohort header matches the required exact column order")
    cohort = list(cohort_reader)

with (STAGE / "SOURCE_LOG.csv").open(newline="", encoding="utf-8") as handle:
    source_reader = csv.DictReader(handle)
    require(source_reader.fieldnames == EXPECTED_SOURCE_COLUMNS, "source-log header matches the required exact column order")
    sources = list(source_reader)

require(len(cohort) == 95, "cohort contains the 95 unique frozen-roster people")
require(len({r["person_id"] for r in cohort}) == 95, "person_id is unique")
require(len({r["full_name"] for r in cohort}) == 95, "full_name is unique")
require(all(r["person_id"] and r["full_name"] and r["search_disambiguator"] for r in cohort), "identity fields are nonblank")
require(all(r["birth_source_url"] and r["membership_source_urls"] for r in cohort), "every person has birth and membership source URLs")

for row in cohort:
    for field in BOOL_FIELDS:
        require(row[field] in {"0", "1"}, f"{row['person_id']} {field} is binary")
    for field in DATE_FIELDS:
        if row[field]:
            parsed = dt.date.fromisoformat(row[field])
            require(parsed.isoformat() == row[field], f"{row['person_id']} {field} is a valid ISO date")
    require(row["vital_status_20260601"] in {"alive", "dead"}, f"{row['person_id']} censor status is valid")
    expected_status = "dead" if row["death_date"] and row["death_date"] <= "2026-06-01" else "alive"
    require(row["vital_status_20260601"] == expected_status, f"{row['person_id']} censor status agrees with death date")
    require((row["apollo_flew"] == "1") == bool(row["apollo_missions"]), f"{row['person_id']} Apollo flag agrees with missions")
    is_group_1_7 = row["search_disambiguator"].startswith("NASA astronaut group ")
    expected_core = "1" if is_group_1_7 and row["apollo_flew"] == "0" else "0"
    require(row["core_nasa_non_apollo"] == expected_core, f"{row['person_id']} core NASA non-Apollo flag follows frozen rule")
    expected_other = "1" if row["apollo_flew"] == "0" and any(row[f] == "1" for f in ["core_nasa_non_apollo", "military_x15", "military_dyna_soar", "military_mol"]) else "0"
    require(row["other_all"] == expected_other, f"{row['person_id']} other_all is the frozen non-Apollo union")
    if row["pre1970_accidental_death"] == "1":
        require(bool(row["death_date"]) and row["death_date"] < "1970-01-01", f"{row['person_id']} positive pre-1970 accident flag respects date cutoff")
    if not row["first_selection_date"]:
        require("exact" in row["notes"].lower(), f"{row['person_id']} blank exact selection date is explained")

technical_counts = {
    "apollo_flew": sum(r["apollo_flew"] == "1" for r in cohort),
    "apollo1_crew": sum(r["apollo1_crew"] == "1" for r in cohort),
    "core_nasa_non_apollo": sum(r["core_nasa_non_apollo"] == "1" for r in cohort),
    "military_x15": sum(r["military_x15"] == "1" for r in cohort),
    "military_dyna_soar": sum(r["military_dyna_soar"] == "1" for r in cohort),
    "military_mol": sum(r["military_mol"] == "1" for r in cohort),
    "other_all": sum(r["other_all"] == "1" for r in cohort),
    "pre1970_accidental_death": sum(r["pre1970_accidental_death"] == "1" for r in cohort),
}
require(technical_counts == {
    "apollo_flew": 29,
    "apollo1_crew": 3,
    "core_nasa_non_apollo": 44,
    "military_x15": 12,
    "military_dyna_soar": 8,
    "military_mol": 17,
    "other_all": 66,
    "pre1970_accidental_death": 12,
}, "technical roster/flag counts match the frozen inclusion rules")
require(sum(r["vital_status_20260601"] == "alive" for r in cohort) == 19, "all 19 apparently living records received a censor-status classification")

source_by_person: dict[str, list[dict[str, str]]] = {}
for source in sources:
    source_by_person.setdefault(source["person_id"], []).append(source)
require(set(source_by_person) == {r["person_id"] for r in cohort}, "source log covers every cohort person and no unknown person")

for row in cohort:
    person_sources = source_by_person[row["person_id"]]
    fetched_urls = {s["url"] for s in person_sources}
    require(row["birth_source_url"] in fetched_urls, f"{row['person_id']} birth URL is in source log")
    if row["death_date"]:
        require(bool(row["death_source_url"]), f"{row['person_id']} death source URL is nonblank")
        require(row["death_source_url"] in fetched_urls, f"{row['person_id']} death URL is in source log")
    else:
        require(not row["death_source_url"], f"{row['person_id']} living record has no fabricated death URL")
        require(any("targeted living-person search" in s["fact_supported"] for s in person_sources), f"{row['person_id']} living status has a targeted search ledger row")
    for membership_url in row["membership_source_urls"].split("|"):
        require(membership_url in fetched_urls, f"{row['person_id']} membership URL is in source log")
    if row["first_selection_date"]:
        require(any(f"first_selection_date={row['first_selection_date']}" == s["fact_supported"] for s in person_sources), f"{row['person_id']} selection date has an explicit ledger row")
    if row["first_spaceflight_date"]:
        require(any(f"first_spaceflight_date={row['first_spaceflight_date']}" == s["fact_supported"] for s in person_sources), f"{row['person_id']} first spaceflight has an explicit ledger row")
    if row["pre1970_accidental_death"] == "1":
        require(any(s["fact_supported"] == "pre1970_accidental_death=1" for s in person_sources), f"{row['person_id']} accident flag has an explicit ledger row")

print(f"SUMMARY | cohort_rows={len(cohort)} source_rows={len(sources)} checks={check_count} all_checks_passed=1")
