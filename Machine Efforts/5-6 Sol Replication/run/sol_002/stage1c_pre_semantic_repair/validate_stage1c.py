#!/usr/bin/env python3
"""Read-only mechanical validation for Stage 1C artifacts."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

import compile_stage1c as compiler


STAGE = Path(__file__).resolve().parent
CENSOR = date(2026, 6, 1)
BASE = {
    "INTERVIEW",
    "LECTURE_TALK_QA",
    "AUTHOR_WORK",
    "IMPAIRMENT",
    "MILESTONE_BIRTHDAY",
    "OBITUARY_DEATH",
}
STATES = {
    "FUNCTION_ONLY",
    "IMPAIRMENT_ONLY",
    "FUNCTION_THEN_IMPAIRMENT",
    "IMPAIRMENT_THEN_FUNCTION",
    "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE",
    "NEITHER_FOUND",
    "NOT_ELIGIBLE_UNDER_80",
}


def load_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (STAGE / name).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parse(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def midpoint(first: date, last: date) -> date:
    return first + timedelta(days=(last - first).days // 2)


def check() -> list[str]:
    failures: list[str] = []
    work_header, work = load_csv("research_worklist.csv")
    search_header, search = load_csv("SEARCH_LOG.csv")
    event_header, events = load_csv("EVIDENCE_EVENTS.csv")
    outcome_header, outcomes = load_csv("PERSON_OUTCOMES.csv")

    expected_work = [
        "research_id",
        "person_id",
        "full_name",
        "search_disambiguator",
        "birth_date",
        "end_date",
        "eligible_age80",
    ]
    if work_header != expected_work:
        failures.append("worklist header")
    if search_header != compiler.SEARCH_COLUMNS:
        failures.append("search header")
    if event_header != compiler.EVENT_COLUMNS:
        failures.append("event header")
    if outcome_header != compiler.OUTCOME_COLUMNS:
        failures.append("outcome header")

    if len(work) != len({row["research_id"] for row in work}):
        failures.append("duplicate worklist research_id")
    if len(outcomes) != len({row["research_id"] for row in outcomes}):
        failures.append("duplicate outcome research_id")
    if {row["research_id"] for row in work} != {row["research_id"] for row in outcomes}:
        failures.append("worklist/outcome coverage")

    hashes = [
        hashlib.sha256(
            f'SOL-20260721-EVIDENCE|{row["person_id"]}'.encode("utf-8")
        ).hexdigest()
        for row in work
    ]
    if hashes != sorted(hashes):
        failures.append("salted SHA-256 worklist order")

    people = {row["research_id"]: row for row in work}
    eligible = {row["research_id"] for row in work if row["eligible_age80"] == "1"}
    by_rid_search: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in search:
        by_rid_search[row["research_id"]].append(row)
        if row["opened"] not in {"0", "1"}:
            failures.append(f'invalid opened boolean {row["research_id"]}')
        if row["result_rank"] and not 1 <= int(row["result_rank"]) <= 10:
            failures.append(f'rank outside 1..10 {row["research_id"]}')
        if row["query_family"].startswith("EXTRA") and not row["extra_search_trigger"]:
            failures.append(f'untriggered extra {row["research_id"]}')

    for rid in eligible:
        base_queries = {
            (row["query_family"], row["query"])
            for row in by_rid_search[rid]
            if row["query_family"] in BASE
        }
        if {family for family, _ in base_queries} != BASE:
            failures.append(f"six-family coverage {rid}")
        for family in BASE:
            queries = {query for fam, query in base_queries if fam == family}
            if len(queries) != 1:
                failures.append(f"exactly one base query {rid} {family}")
            family_rows = [
                row
                for row in by_rid_search[rid]
                if row["query_family"] == family
            ]
            ranks = [int(row["result_rank"]) for row in family_rows if row["result_rank"]]
            if ranks:
                if ranks != list(range(1, len(ranks) + 1)):
                    failures.append(f"rank sequence {rid} {family}")
            elif not any(row["access_result"] == "no_results" for row in family_rows):
                failures.append(f"explicit no-result {rid} {family}")

    outcome_by_rid = {row["research_id"]: row for row in outcomes}
    for rid, row in outcome_by_rid.items():
        if rid in eligible:
            if row["base_search_complete"] != "1":
                failures.append(f"base search complete {rid}")
            base_rows = [item for item in by_rid_search[rid] if item["query_family"] in BASE]
            if int(row["base_results_logged"]) != sum(bool(item["result_rank"]) for item in base_rows):
                failures.append(f"base result count {rid}")
            if int(row["base_pages_opened"]) != sum(int(item["opened"]) for item in base_rows):
                failures.append(f"base page count {rid}")
            extra_rows = [
                item
                for item in by_rid_search[rid]
                if item["query_family"].startswith("EXTRA")
            ]
            extra_query_texts = {
                item["query"] for item in extra_rows if item["query"]
            }
            if int(row["extra_queries"]) != len(extra_query_texts):
                failures.append(f"extra query count {rid}")
            if int(row["extra_pages_opened"]) != sum(int(item["opened"]) for item in extra_rows):
                failures.append(f"extra page count {rid}")
            if int(row["extra_queries"]) > 2 or int(row["extra_pages_opened"]) > 3:
                failures.append(f"extra budget cap {rid}")
        else:
            if row["outcome_state"] != "NOT_ELIGIBLE_UNDER_80":
                failures.append(f"ineligible state {rid}")

    qualifying = [
        row
        for row in events
        if row["qualifies"] == "1"
        and row["evidence_type"] == "QUALIFYING_FUNCTION_EVENT"
    ]
    opened_urls_by_rid = {
        rid: {
            item["url"]
            for item in rows
            if item["opened"] == "1" and item["access_result"] == "opened"
        }
        for rid, rows in by_rid_search.items()
    }
    for row in events:
        if row["source_url"] not in opened_urls_by_rid.get(row["research_id"], set()):
            failures.append(f"evidence source not opened {row['research_id']}")
    qual_by_rid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in qualifying:
        qual_by_rid[row["research_id"]].append(row)
        person = people[row["research_id"]]
        birth = parse(person["birth_date"])
        end = parse(person["end_date"])
        earliest = parse(row["event_date_earliest"])
        latest = parse(row["event_date_latest"])
        analysis = parse(row["analysis_event_date"])
        if not all((birth, end, earliest, latest, analysis)):
            failures.append(f"missing event dates {row['research_id']}")
            continue
        assert birth and end and earliest and latest and analysis
        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        if not (b80 <= analysis <= end):
            failures.append(f"event outside collection window {row['research_id']}")
        if not (earliest <= analysis <= latest):
            failures.append(f"analysis outside date bounds {row['research_id']}")
        precision = row["event_date_precision"]
        if precision == "DAY" and not (earliest == analysis == latest):
            failures.append(f"DAY precision rule {row['research_id']}")
        if precision in {"MONTH", "YEAR", "BOUNDED_INTERVAL"} and analysis != midpoint(earliest, latest):
            failures.append(f"midpoint precision rule {row['research_id']}")
        boundary = int(
            (earliest < b80 <= latest)
            or (earliest < b85 <= latest)
        )
        if int(row["boundary_sensitive"]) != boundary:
            failures.append(f"event boundary flag {row['research_id']}")
        if not row["source_url"].startswith(("http://", "https://")):
            failures.append(f"event source URL {row['research_id']}")

    for rid, row in outcome_by_rid.items():
        if row["outcome_state"] not in STATES:
            failures.append(f"state label {rid}")
        if rid not in eligible:
            continue
        person = people[rid]
        birth = parse(person["birth_date"])
        end = parse(person["end_date"])
        assert birth and end
        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        death = end if end < CENSOR else None
        qevents = sorted(qual_by_rid.get(rid, []), key=lambda item: item["analysis_event_date"])
        expected_state = "FUNCTION_ONLY" if qevents else "NEITHER_FOUND"
        if row["outcome_state"] != expected_state:
            failures.append(f"outcome/event state linkage {rid}")
        primary = None
        if qevents:
            first = parse(qevents[0]["analysis_event_date"])
            if first and b80 <= first < b85 and first <= CENSOR:
                primary = first
        expected_potential = (min(b85, CENSOR) - b80).days
        candidates = [b85, CENSOR]
        if death:
            candidates.append(death)
        if primary:
            candidates.append(primary)
        expected_observed = (min(candidates) - b80).days
        if int(row["potential_followup_days"]) != expected_potential:
            failures.append(f"potential follow-up {rid}")
        if int(row["observed_followup_days"]) != expected_observed:
            failures.append(f"observed follow-up {rid}")
        expected_competing = int(
            bool(
                death
                and b80 <= death < b85
                and death <= CENSOR
                and (primary is None or death < primary)
            )
        )
        expected_admin = int(
            CENSOR < b85
            and (death is None or death > CENSOR)
            and (primary is None or primary > CENSOR)
        )
        if int(row["death_competing_event_within_five_years"]) != expected_competing:
            failures.append(f"competing death {rid}")
        if int(row["administratively_censored_before_five_years"]) != expected_admin:
            failures.append(f"administrative censor {rid}")
        substantive_urls = {
            item["url"]
            for item in by_rid_search[rid]
            if item["substantive_late_life_source"] == "1"
            and item["access_result"] == "opened"
        }
        publishers = {
            compiler.publisher_key(url) for url in substantive_urls if url
        }
        if int(row["substantive_sources_opened"]) != len(substantive_urls):
            failures.append(f"substantive source count {rid}")
        if int(row["independent_publishers"]) != len(publishers):
            failures.append(f"publisher count {rid}")
        count = len(substantive_urls)
        if count <= 1:
            expected_depth = "LOW"
        elif count <= 4:
            expected_depth = "MEDIUM"
        elif len(publishers) >= 2:
            expected_depth = "HIGH"
        else:
            expected_depth = "MEDIUM"
        if row["documentation_depth"] != expected_depth:
            failures.append(f"documentation depth {rid}")

    forbidden_columns = {
        "apollo_flew",
        "apollo_missions",
        "apollo1_crew",
        "core_nasa_non_apollo",
        "military_x15",
        "military_dyna_soar",
        "military_mol",
        "other_all",
    }
    if forbidden_columns.intersection(work_header + search_header + event_header + outcome_header):
        failures.append("cohort flag column leakage")
    for name in (
        "DECISIONS_AND_DEVIATIONS.md",
        "VALIDATION.md",
        "CONTAMINATION.md",
        "STAGE_COMPLETE.md",
    ):
        if not (STAGE / name).exists():
            failures.append(f"missing {name}")
    return failures


if __name__ == "__main__":
    problems = check()
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        raise SystemExit(1)
    print("PASS: all Stage 1C mechanical validation checks passed")
