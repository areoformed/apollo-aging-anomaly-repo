#!/usr/bin/env python3
"""Independent mechanical gate for the locked sol_002 Stage 1 artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "[TMPDIR]/historical-cohort-replication-002")
STAGE = ROOT / "stage1"
CENSOR = date(2026, 6, 1)
COMPLETION_CEILING = datetime(2026, 7, 23, 4, 16, 17, tzinfo=timezone.utc)

COHORT_FIELDS = [
    "person_id",
    "full_name",
    "search_disambiguator",
    "birth_date",
    "death_date",
    "vital_status_20260601",
    "first_selection_date",
    "first_spaceflight_date",
    "apollo_flew",
    "apollo_missions",
    "apollo1_crew",
    "core_nasa_non_apollo",
    "military_x15",
    "military_dyna_soar",
    "military_mol",
    "other_all",
    "pre1970_accidental_death",
    "backup_crew_roles",
    "membership_source_urls",
    "birth_source_url",
    "death_source_url",
    "confidence",
    "notes",
]
SOURCE_FIELDS = [
    "timestamp",
    "person_id",
    "query_or_direct_navigation",
    "result_rank",
    "url",
    "opened",
    "access_result",
    "fact_supported",
    "source_tier",
    "notes",
]
BOOLEAN_FIELDS = [
    "apollo_flew",
    "apollo1_crew",
    "core_nasa_non_apollo",
    "military_x15",
    "military_dyna_soar",
    "military_mol",
    "other_all",
    "pre1970_accidental_death",
]
DATE_FIELDS = [
    "birth_date",
    "death_date",
    "first_selection_date",
    "first_spaceflight_date",
]
EXPECTED_FILES = {
    "ACTION_LOG.md",
    "CONTEXT_ATTESTATION.md",
    "CONTROLLER_LAST_MESSAGE.txt",
    "stage1/CONTAMINATION.md",
    "stage1/DECISIONS.md",
    "stage1/SOURCE_LOG.csv",
    "stage1/STAGE_COMPLETE.md",
    "stage1/VALIDATION.md",
    "stage1/build_stage1.py",
    "stage1/cohort.csv",
    "stage1/validate_stage1.py",
}


def parse_date(value: str, label: str, problems: list[str]) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        problems.append(f"invalid ISO date {label}={value!r}")
        return None


def parse_timestamp(value: str, label: str, problems: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        problems.append(f"invalid timestamp {label}={value!r}")
        return None
    if parsed.tzinfo is None:
        problems.append(f"naive timestamp {label}={value!r}")
        return None
    return parsed.astimezone(timezone.utc)


problems: list[str] = []
inventory = {
    str(path.relative_to(ROOT))
    for path in ROOT.rglob("*")
    if path.is_file()
}
if inventory != EXPECTED_FILES:
    problems.append(
        "unexpected inventory: "
        f"missing={sorted(EXPECTED_FILES - inventory)} "
        f"extra={sorted(inventory - EXPECTED_FILES)}"
    )

with (STAGE / "cohort.csv").open(newline="", encoding="utf-8") as handle:
    cohort_reader = csv.DictReader(handle)
    cohort = list(cohort_reader)
if cohort_reader.fieldnames != COHORT_FIELDS:
    problems.append(f"cohort header mismatch: {cohort_reader.fieldnames}")

with (STAGE / "SOURCE_LOG.csv").open(newline="", encoding="utf-8") as handle:
    source_reader = csv.DictReader(handle)
    sources = list(source_reader)
if source_reader.fieldnames != SOURCE_FIELDS:
    problems.append(f"source header mismatch: {source_reader.fieldnames}")

if len(cohort) != 95:
    problems.append(f"cohort row count={len(cohort)}, expected 95")
if len(sources) != 489:
    problems.append(f"source row count={len(sources)}, expected locked 489")

for key in ("person_id", "full_name"):
    duplicates = [value for value, count in Counter(row[key].casefold() for row in cohort).items() if count > 1]
    if duplicates:
        problems.append(f"duplicate {key}: {duplicates}")

cohort_ids = {row["person_id"] for row in cohort}
source_ids = {row["person_id"] for row in sources if row["person_id"]}
unknown_source_ids = source_ids - cohort_ids
if unknown_source_ids:
    problems.append(f"unknown person IDs in source log: {sorted(unknown_source_ids)}")

parsed_rows: dict[str, dict[str, date | None]] = {}
for row in cohort:
    pid = row["person_id"]
    if any(row[field] not in {"0", "1"} for field in BOOLEAN_FIELDS):
        problems.append(f"{pid}: non-Boolean flag")
    parsed = {
        field: parse_date(row[field], f"{pid}.{field}", problems)
        for field in DATE_FIELDS
    }
    parsed_rows[pid] = parsed
    birth = parsed["birth_date"]
    death = parsed["death_date"]
    selection = parsed["first_selection_date"]
    flight = parsed["first_spaceflight_date"]
    if birth is None:
        problems.append(f"{pid}: missing birth date")
    if birth and death and not birth < death <= CENSOR:
        problems.append(f"{pid}: implausible/out-of-window death chronology")
    if birth and selection and selection <= birth:
        problems.append(f"{pid}: selection not after birth")
    if birth and flight and flight <= birth:
        problems.append(f"{pid}: first spaceflight not after birth")
    if death and flight and flight > death:
        problems.append(f"{pid}: first spaceflight after death")
    status = row["vital_status_20260601"]
    if status not in {"alive", "deceased"}:
        problems.append(f"{pid}: invalid vital status {status!r}")
    if status == "alive" and (row["death_date"] or row["death_source_url"]):
        problems.append(f"{pid}: alive row has death fact/source")
    if status == "deceased" and (not row["death_date"] or not row["death_source_url"]):
        problems.append(f"{pid}: deceased row lacks death fact/source")
    if not row["membership_source_urls"] or not row["birth_source_url"]:
        problems.append(f"{pid}: missing membership or birth source URL")
    expected_other = (
        row["apollo_flew"] == "0"
        and any(row[field] == "1" for field in (
            "core_nasa_non_apollo",
            "military_x15",
            "military_dyna_soar",
            "military_mol",
        ))
    )
    if (row["other_all"] == "1") != expected_other:
        problems.append(f"{pid}: other_all union mismatch")
    if row["apollo_flew"] == "1" and row["core_nasa_non_apollo"] == "1":
        problems.append(f"{pid}: Apollo and core NASA comparator overlap")
    if row["pre1970_accidental_death"] == "1" and (death is None or death >= date(1970, 1, 1)):
        problems.append(f"{pid}: pre-1970 accident flag/date mismatch")
    missions = [item for item in row["apollo_missions"].split("|") if item]
    if (row["apollo_flew"] == "1") != bool(missions):
        problems.append(f"{pid}: Apollo flag/mission mismatch")
    for mission in missions:
        match = re.fullmatch(r"Apollo (\d+)", mission)
        if not match or not 7 <= int(match.group(1)) <= 17:
            problems.append(f"{pid}: invalid Apollo mission value {mission!r}")
    if row["confidence"] not in {"high", "medium", "low"}:
        problems.append(f"{pid}: invalid confidence {row['confidence']!r}")

source_rows_by_person: dict[str, list[dict[str, str]]] = defaultdict(list)
fetched_urls: set[str] = set()
source_timestamps: list[datetime] = []
for index, row in enumerate(sources, start=2):
    pid = row["person_id"]
    if pid:
        source_rows_by_person[pid].append(row)
    if row["opened"] not in {"0", "1"}:
        problems.append(f"source row {index}: invalid opened flag")
    if row["result_rank"] and row["result_rank"] != "direct" and not row["result_rank"].isdigit():
        problems.append(f"source row {index}: invalid result rank")
    parsed_timestamp = parse_timestamp(row["timestamp"], f"source row {index}", problems)
    if parsed_timestamp:
        source_timestamps.append(parsed_timestamp)
        if parsed_timestamp > COMPLETION_CEILING:
            problems.append(f"source row {index}: timestamp after lock ceiling")
    if row["opened"] == "1" and row["access_result"] == "fetched" and row["url"]:
        fetched_urls.add(row["url"])

# SOURCE_LOG is organized by person/fact rather than chronology. Exact event
# times are still checked individually against the lock ceiling; chronology is
# established by the append-only ACTION_LOG.

cohort_urls: set[str] = set()
for row in cohort:
    for field in ("membership_source_urls", "birth_source_url", "death_source_url"):
        cohort_urls.update(url for url in row[field].split("|") if url)
missing_fetched_urls = cohort_urls - fetched_urls
if missing_fetched_urls:
    problems.append(f"cohort source URLs not logged fetched: {sorted(missing_fetched_urls)}")

living_ids = {row["person_id"] for row in cohort if row["vital_status_20260601"] == "alive"}
living_audited = {
    pid
    for pid, rows in source_rows_by_person.items()
    if any(row["fact_supported"] == "living-status check through censor" for row in rows)
}
if living_ids != living_audited:
    problems.append(
        f"living audit mismatch: missing={sorted(living_ids - living_audited)} "
        f"extra={sorted(living_audited - living_ids)}"
    )

for row in cohort:
    pid = row["person_id"]
    facts = {item["fact_supported"] for item in source_rows_by_person[pid]}
    if not any("membership" in fact for fact in facts):
        problems.append(f"{pid}: no membership-support source-log row")
    if not any("birth" in fact for fact in facts):
        problems.append(f"{pid}: no birth-support source-log row")
    if row["vital_status_20260601"] == "deceased" and not any("death" in fact for fact in facts):
        problems.append(f"{pid}: no death-support source-log row")

raw_cohort = (STAGE / "cohort.csv").read_bytes()
raw_sources = (STAGE / "SOURCE_LOG.csv").read_bytes()
if raw_cohort.count(b"\r\n") != 96 or raw_cohort.count(b"\n") != 96:
    problems.append("cohort.csv is not 96 RFC-4180 CRLF records")
if raw_sources.count(b"\r\n") != 490 or raw_sources.count(b"\n") != 490:
    problems.append("SOURCE_LOG.csv is not 490 RFC-4180 CRLF records")

action_text = (ROOT / "ACTION_LOG.md").read_text(encoding="utf-8")
action_timestamps = [
    datetime.fromisoformat(item.replace("Z", "+00:00")).astimezone(timezone.utc)
    for item in re.findall(r"(?m)^(?:\| )?(2026-\d\d-\d\dT\d\d:\d\d:\d\dZ)", action_text)
]
if action_timestamps != sorted(action_timestamps):
    problems.append("ACTION_LOG durable timestamps are not nondecreasing")
if action_timestamps and action_timestamps[-1] > COMPLETION_CEILING:
    problems.append("ACTION_LOG contains a post-lock future timestamp")

counts = {
    "cohort_rows": len(cohort),
    "source_rows": len(sources),
    "apollo_flew": sum(row["apollo_flew"] == "1" for row in cohort),
    "core_nasa_non_apollo": sum(row["core_nasa_non_apollo"] == "1" for row in cohort),
    "x15": sum(row["military_x15"] == "1" for row in cohort),
    "dyna_soar": sum(row["military_dyna_soar"] == "1" for row in cohort),
    "mol": sum(row["military_mol"] == "1" for row in cohort),
    "other_all": sum(row["other_all"] == "1" for row in cohort),
    "alive": len(living_ids),
    "deceased": sum(row["vital_status_20260601"] == "deceased" for row in cohort),
    "cohort_source_urls": len(cohort_urls),
    "fetched_source_urls": len(fetched_urls),
    "action_timestamp_entries": len(action_timestamps),
    "source_timestamp_entries": len(source_timestamps),
    "problems": problems,
}
print(json.dumps(counts, indent=2, sort_keys=True))
raise SystemExit(1 if problems else 0)
