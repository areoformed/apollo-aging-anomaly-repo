#!/usr/bin/env python3
"""Read-only independent checks for generated Stage 1 CSV artifacts."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COHORT_PATH = ROOT / "cohort.csv"
SOURCE_PATH = ROOT / "SOURCE_LOG.csv"

EXPECTED_COHORT_COLUMNS = [
    "person_id", "full_name", "search_disambiguator", "birth_date",
    "death_date", "vital_status_20260601", "first_selection_date",
    "first_spaceflight_date", "apollo_flew", "apollo_missions",
    "apollo1_crew", "core_nasa_non_apollo", "military_x15",
    "military_dyna_soar", "military_mol", "other_all",
    "pre1970_accidental_death", "backup_crew_roles",
    "membership_source_urls", "birth_source_url", "death_source_url",
    "confidence", "notes",
]
EXPECTED_SOURCE_COLUMNS = [
    "timestamp", "person_id", "query_or_direct_navigation", "result_rank",
    "url", "opened", "access_result", "fact_supported", "source_tier",
    "notes",
]
BOOLEAN_COLUMNS = [
    "apollo_flew", "apollo1_crew", "core_nasa_non_apollo",
    "military_x15", "military_dyna_soar", "military_mol", "other_all",
    "pre1970_accidental_death",
]
DATE_COLUMNS = [
    "birth_date", "death_date", "first_selection_date",
    "first_spaceflight_date",
]


with COHORT_PATH.open(newline="", encoding="utf-8") as handle:
    cohort_reader = csv.DictReader(handle)
    cohort = list(cohort_reader)
with SOURCE_PATH.open(newline="", encoding="utf-8") as handle:
    source_reader = csv.DictReader(handle)
    sources = list(source_reader)

assert cohort_reader.fieldnames == EXPECTED_COHORT_COLUMNS
assert source_reader.fieldnames == EXPECTED_SOURCE_COLUMNS
assert len(cohort) == 95
assert len(sources) == 489
assert len({row["person_id"] for row in cohort}) == 95
assert len({row["full_name"].casefold() for row in cohort}) == 95
assert all(row[column] in {"0", "1"} for row in cohort for column in BOOLEAN_COLUMNS)
assert sum(row["apollo_flew"] == "1" for row in cohort) == 29
assert sum(row["core_nasa_non_apollo"] == "1" for row in cohort) == 44
assert sum(row["military_x15"] == "1" for row in cohort) == 12
assert sum(row["military_dyna_soar"] == "1" for row in cohort) == 6
assert sum(row["military_mol"] == "1" for row in cohort) == 17
assert sum(row["other_all"] == "1" for row in cohort) == 66
assert sum(row["vital_status_20260601"] == "alive" for row in cohort) == 19

for row in cohort:
    for column in DATE_COLUMNS:
        if row[column]:
            date.fromisoformat(row[column])
    expected_other = (
        row["apollo_flew"] == "0"
        and any(
            row[column] == "1"
            for column in (
                "core_nasa_non_apollo", "military_x15",
                "military_dyna_soar", "military_mol",
            )
        )
    )
    assert (row["other_all"] == "1") == expected_other
    if row["vital_status_20260601"] == "alive":
        assert not row["death_date"]
        assert not row["death_source_url"]
    else:
        assert row["death_date"]
        assert date.fromisoformat(row["death_date"]) <= date(2026, 6, 1)
        assert row["death_source_url"]
    assert row["membership_source_urls"]
    assert row["birth_source_url"]

cohort_urls = {
    url
    for row in cohort
    for column in (
        "membership_source_urls", "birth_source_url", "death_source_url",
    )
    for url in row[column].split("|")
    if url
}
opened_urls = {
    row["url"]
    for row in sources
    if row["opened"] == "1" and row["access_result"] == "fetched"
}
assert cohort_urls <= opened_urls

living_ids = {
    row["person_id"]
    for row in cohort
    if row["vital_status_20260601"] == "alive"
}
searched_ids = {
    row["person_id"]
    for row in sources
    if row["fact_supported"] == "living-status check through censor"
}
assert living_ids == searched_ids

raw_cohort = COHORT_PATH.read_bytes()
raw_source = SOURCE_PATH.read_bytes()
assert raw_cohort.count(b"\r\n") == 96
assert raw_cohort.count(b"\n") == 96
assert raw_source.count(b"\r\n") == 490
assert raw_source.count(b"\n") == 490

print({
    "cohort_rows": len(cohort),
    "source_rows": len(sources),
    "cohort_source_urls": len(cohort_urls),
    "fetched_source_urls": len(opened_urls),
    "living_searches": len(searched_ids),
    "cohort_crlf_records": raw_cohort.count(b"\r\n"),
    "source_crlf_records": raw_source.count(b"\r\n"),
})
