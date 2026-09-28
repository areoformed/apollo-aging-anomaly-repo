#!/usr/bin/env python3
"""Independent controller-side validation for the locked sol_002 Stage 1C."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse


CENSOR = date(2026, 6, 1)
BASE_FAMILIES = {
    "INTERVIEW",
    "LECTURE_TALK_QA",
    "AUTHOR_WORK",
    "IMPAIRMENT",
    "MILESTONE_BIRTHDAY",
    "OBITUARY_DEATH",
}
ALLOWED_TRIGGERS = {
    "inaccessible base result",
    "same-name identity ambiguity",
    "event-date ambiguity",
    "conflicting evidence",
    "base source that identifies a more-primary source",
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
FORBIDDEN_FIELDS = {
    "apollo_flew",
    "apollo_missions",
    "apollo1_crew",
    "core_nasa_non_apollo",
    "military_x15",
    "military_dyna_soar",
    "military_mol",
    "other_all",
}
WORKLIST_COLUMNS = [
    "research_id",
    "person_id",
    "full_name",
    "search_disambiguator",
    "birth_date",
    "end_date",
    "eligible_age80",
]
SEARCH_COLUMNS = [
    "timestamp",
    "research_id",
    "person_id",
    "query_family",
    "query",
    "result_rank",
    "url",
    "opened",
    "access_result",
    "source_tier",
    "substantive_late_life_source",
    "evidence_candidate",
    "extra_search_trigger",
    "notes",
]
EVENT_COLUMNS = [
    "research_id",
    "person_id",
    "event_date",
    "event_date_precision",
    "event_date_earliest",
    "event_date_latest",
    "analysis_event_date",
    "age_at_analysis_event",
    "evidence_type",
    "event_family",
    "source_url",
    "source_publisher",
    "source_tier",
    "direct_or_indirect",
    "qualifies",
    "boundary_sensitive",
    "adjudication_confidence",
    "supporting_paraphrase",
    "notes",
]
OUTCOME_COLUMNS = [
    "research_id",
    "person_id",
    "eligible_age80",
    "potential_followup_days",
    "observed_followup_days",
    "death_competing_event_within_five_years",
    "administratively_censored_before_five_years",
    "base_search_complete",
    "base_results_logged",
    "base_pages_opened",
    "extra_queries",
    "extra_pages_opened",
    "substantive_sources_opened",
    "independent_publishers",
    "documentation_depth",
    "first_qualifying_function_date",
    "first_function_date_precision",
    "first_function_days_after_80",
    "first_function_within_five_years",
    "latest_qualifying_function_date",
    "latest_qualifying_function_age",
    "first_qualifying_impairment_date",
    "outcome_state",
    "boundary_sensitive",
    "adjudication_confidence",
    "notes",
]


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def midpoint(first: date, last: date) -> date:
    return first + timedelta(days=(last - first).days // 2)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    data = path.read_bytes()
    if b"\n" in data.replace(b"\r\n", b""):
        raise ValueError(f"{path.name}: non-CRLF record ending")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def publisher_family(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for suffix in (
        "nasa.gov",
        "si.edu",
        "wikipedia.org",
        "wikidata.org",
        "google.com",
        "gettyimages.com",
        "gettyimages.co.uk",
        "gettyimages.at",
        "gettyimages.dk",
        "gettyimages.pt",
        "gettyimages.co.nz",
        "gettyimages.be",
    ):
        if host.endswith(suffix):
            return suffix
    return host


def all_keys(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key))
            found.update(all_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(all_keys(child))
    return found


def split_triggers(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def validate(root: Path, cohort_path: Path) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    stage = root / "stage1c"
    required = {
        "research_worklist.csv",
        "SEARCH_LOG.csv",
        "EVIDENCE_EVENTS.csv",
        "PERSON_OUTCOMES.csv",
        "DECISIONS_AND_DEVIATIONS.md",
        "VALIDATION.md",
        "CONTAMINATION.md",
        "STAGE_COMPLETE.md",
    }
    missing = sorted(name for name in required if not (stage / name).is_file())
    if missing:
        return [f"missing required artifacts: {missing}"], {}

    try:
        work_header, work = read_csv(stage / "research_worklist.csv")
        search_header, search = read_csv(stage / "SEARCH_LOG.csv")
        event_header, events = read_csv(stage / "EVIDENCE_EVENTS.csv")
        outcome_header, outcomes = read_csv(stage / "PERSON_OUTCOMES.csv")
    except Exception as exc:
        return [str(exc)], {}

    for actual, expected, label in (
        (work_header, WORKLIST_COLUMNS, "worklist"),
        (search_header, SEARCH_COLUMNS, "search log"),
        (event_header, EVENT_COLUMNS, "evidence events"),
        (outcome_header, OUTCOME_COLUMNS, "person outcomes"),
    ):
        if actual != expected:
            failures.append(f"{label}: header mismatch")
        if FORBIDDEN_FIELDS.intersection(actual):
            failures.append(f"{label}: cohort flag leaked into header")

    if len(work) != 95:
        failures.append(f"worklist: expected 95 rows, got {len(work)}")
    if len(outcomes) != 95:
        failures.append(f"outcomes: expected 95 rows, got {len(outcomes)}")
    work_ids = [row["research_id"] for row in work]
    outcome_ids = [row["research_id"] for row in outcomes]
    if len(set(work_ids)) != len(work_ids):
        failures.append("worklist: duplicate research_id")
    if len(set(outcome_ids)) != len(outcome_ids):
        failures.append("outcomes: duplicate research_id")
    if set(work_ids) != set(outcome_ids):
        failures.append("worklist/outcomes: research_id coverage mismatch")

    salted = [
        hashlib.sha256(
            f'SOL-20260721-EVIDENCE|{row["person_id"]}'.encode("utf-8")
        ).hexdigest()
        for row in work
    ]
    if salted != sorted(salted):
        failures.append("worklist: salted SHA-256 order mismatch")

    with cohort_path.open(encoding="utf-8", newline="") as handle:
        cohort = list(csv.DictReader(handle))
    cohort_by_id = {row["person_id"]: row for row in cohort}
    if set(cohort_by_id) != {row["person_id"] for row in work}:
        failures.append("worklist: Stage 1 cohort coverage mismatch")

    people = {row["research_id"]: row for row in work}
    eligible = {row["research_id"] for row in work if row["eligible_age80"] == "1"}
    if len(eligible) != 57:
        failures.append(f"worklist: expected 57 age-80 eligible rows, got {len(eligible)}")
    for row in work:
        try:
            birth = date.fromisoformat(row["birth_date"])
            end = date.fromisoformat(row["end_date"])
        except ValueError:
            failures.append(f'worklist: invalid date for {row["research_id"]}')
            continue
        expected_eligible = int(add_years(birth, 80) <= end)
        if int(row["eligible_age80"]) != expected_eligible:
            failures.append(f'worklist: age-80 eligibility mismatch {row["research_id"]}')
        cohort_row = cohort_by_id.get(row["person_id"])
        if cohort_row:
            expected_end = cohort_row["death_date"] or CENSOR.isoformat()
            if row["full_name"] != cohort_row["full_name"]:
                failures.append(f'worklist: name mismatch {row["research_id"]}')
            if row["search_disambiguator"] != cohort_row["search_disambiguator"]:
                failures.append(f'worklist: disambiguator mismatch {row["research_id"]}')
            if row["birth_date"] != cohort_row["birth_date"] or row["end_date"] != expected_end:
                failures.append(f'worklist: Stage 1 date mismatch {row["research_id"]}')

    raw_files = sorted((stage / "raw").glob("*.json"))
    if len(raw_files) != len(eligible):
        failures.append(f"raw: expected {len(eligible)} JSON files, got {len(raw_files)}")
    raw_by_id: dict[str, dict] = {}
    base_expected: dict[tuple[str, str, str], tuple[list[dict], list[dict]]] = {}
    base_attempt_count: dict[str, int] = defaultdict(int)
    base_result_count: dict[str, int] = defaultdict(int)
    for path in raw_files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"raw: unreadable {path.name}: {exc}")
            continue
        person = payload.get("person", {})
        rid = person.get("research_id", "")
        raw_by_id[rid] = payload
        if rid not in eligible:
            failures.append(f"raw: unexpected or ineligible research ID {rid or path.name}")
            continue
        if path.stem != rid:
            failures.append(f"raw: filename/research_id mismatch {path.name}")
        if person.get("person_id") != people[rid]["person_id"]:
            failures.append(f"raw: person_id mismatch {rid}")
        if FORBIDDEN_FIELDS.intersection(all_keys(payload)):
            failures.append(f"raw: cohort flag key leaked for {rid}")
        queries = payload.get("queries", [])
        if len(queries) != 6 or {q.get("family") for q in queries} != BASE_FAMILIES:
            failures.append(f"raw: six-family coverage mismatch {rid}")
        for query in queries:
            family = query.get("family", "")
            text = query.get("query", "")
            key = (rid, family, text)
            if key in base_expected:
                failures.append(f"raw: duplicate base query {rid} {family}")
            results = query.get("results", [])
            ranks = [item.get("rank") for item in results]
            if ranks != list(range(1, len(results) + 1)) or len(results) > 10:
                failures.append(f"raw: rank sequence/cap mismatch {rid} {family}")
            attempts = query.get("open_attempts", [])
            result_pairs = {(item.get("rank"), item.get("url")) for item in results}
            for attempt in attempts:
                if (attempt.get("rank"), attempt.get("url")) not in result_pairs:
                    failures.append(f"raw: open attempt absent from ranks {rid} {family}")
            success = sum(item.get("access_result") == "opened" for item in attempts)
            if success != int(query.get("success_count", 0)) or success > 2:
                failures.append(f"raw: successful-open count mismatch {rid} {family}")
            base_expected[key] = (results, attempts)
            base_attempt_count[rid] += len(attempts)
            base_result_count[rid] += len(results)

    by_rid_search: dict[str, list[dict[str, str]]] = defaultdict(list)
    base_log: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in search:
        rid = row["research_id"]
        by_rid_search[rid].append(row)
        if row["person_id"] != people.get(rid, {}).get("person_id"):
            failures.append(f"search log: person mismatch {rid}")
        if row["opened"] not in {"0", "1"}:
            failures.append(f"search log: invalid opened flag {rid}")
        if row["substantive_late_life_source"] not in {"0", "1"}:
            failures.append(f"search log: invalid substantive flag {rid}")
        if row["evidence_candidate"] not in {"0", "1"}:
            failures.append(f"search log: invalid candidate flag {rid}")
        if row["result_rank"]:
            try:
                rank = int(row["result_rank"])
            except ValueError:
                failures.append(f"search log: nonnumeric rank {rid}")
            else:
                if not 1 <= rank <= 10:
                    failures.append(f"search log: rank outside 1..10 {rid}")
        if row["query_family"] in BASE_FAMILIES:
            base_log[(rid, row["query_family"], row["query"])].append(row)
        elif row["query_family"].startswith("EXTRA"):
            triggers = split_triggers(row["extra_search_trigger"])
            if not triggers or not triggers.issubset(ALLOWED_TRIGGERS):
                failures.append(f"search log: invalid/unlogged extra trigger {rid}")
        else:
            failures.append(f'search log: unknown query family {row["query_family"]}')

    if set(base_log) != set(base_expected):
        failures.append("search log: raw/base query-key coverage mismatch")
    for key, expected in base_expected.items():
        results, attempts = expected
        rows = base_log.get(key, [])
        ranked = [row for row in rows if row["result_rank"]]
        if results:
            if len(ranked) != len(results):
                failures.append(f"search log: raw rank count mismatch {key[0]} {key[1]}")
                continue
            attempt_by_pair = {
                (int(item["rank"]), item["url"]): item for item in attempts
            }
            for raw_item, log_item in zip(results, ranked):
                if (
                    int(log_item["result_rank"]) != int(raw_item["rank"])
                    or log_item["url"] != raw_item["url"]
                ):
                    failures.append(f"search log: raw rank/URL mismatch {key[0]} {key[1]}")
                    continue
                attempt = attempt_by_pair.get((int(raw_item["rank"]), raw_item["url"]))
                expected_opened = "1" if attempt else "0"
                expected_access = (
                    attempt.get("access_result", "")
                    if attempt
                    else raw_item.get("disposition", "not_opened")
                )
                if (
                    log_item["opened"] != expected_opened
                    or log_item["access_result"] != expected_access
                ):
                    failures.append(
                        f"search log: raw opened/access mismatch {key[0]} {key[1]}"
                    )
        elif not any(row["access_result"] == "no_results" for row in rows):
            failures.append(f"search log: missing explicit no-results row {key[0]} {key[1]}")

    outcome_by_id = {row["research_id"]: row for row in outcomes}
    for rid in eligible:
        rows = by_rid_search[rid]
        extras = [row for row in rows if row["query_family"].startswith("EXTRA")]
        extra_queries = {row["query"] for row in extras if row["query"]}
        extra_pages = sum(int(row["opened"]) for row in extras)
        if len(extra_queries) > 2 or extra_pages > 3:
            failures.append(f"search log: extra budget exceeded {rid}")
        outcome = outcome_by_id[rid]
        if int(outcome["base_results_logged"]) != base_result_count[rid]:
            failures.append(f"outcomes: base result count mismatch {rid}")
        if int(outcome["base_pages_opened"]) != base_attempt_count[rid]:
            failures.append(f"outcomes: base page-attempt count mismatch {rid}")
        if int(outcome["extra_queries"]) != len(extra_queries):
            failures.append(f"outcomes: extra query count mismatch {rid}")
        if int(outcome["extra_pages_opened"]) != extra_pages:
            failures.append(f"outcomes: extra page count mismatch {rid}")
        if outcome["base_search_complete"] != "1":
            failures.append(f"outcomes: base search incomplete {rid}")

    opened_by_id = {
        rid: {
            row["url"]
            for row in rows
            if row["opened"] == "1" and row["access_result"] == "opened"
        }
        for rid, rows in by_rid_search.items()
    }
    function_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    impairment_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        rid = row["research_id"]
        if rid not in eligible or row["person_id"] != people.get(rid, {}).get("person_id"):
            failures.append(f"events: person coverage mismatch {rid}")
            continue
        if row["qualifies"] != "1":
            failures.append(f"events: nonqualifying row retained as event {rid}")
        if row["source_url"] not in opened_by_id.get(rid, set()):
            failures.append(f"events: source was not successfully opened {rid}")
        if row["source_tier"] not in {"TIER_1", "TIER_2", "TIER_3", "TIER_4"}:
            failures.append(f"events: invalid source tier {rid}")
        if row["direct_or_indirect"] not in {"DIRECT", "INDIRECT"}:
            failures.append(f"events: invalid directness {rid}")
        if row["adjudication_confidence"] not in {"LOW", "MEDIUM", "HIGH"}:
            failures.append(f"events: invalid confidence {rid}")
        try:
            first = date.fromisoformat(row["event_date_earliest"])
            last = date.fromisoformat(row["event_date_latest"])
            analysis = date.fromisoformat(row["analysis_event_date"])
        except ValueError:
            failures.append(f"events: invalid date {rid}")
            continue
        birth = date.fromisoformat(people[rid]["birth_date"])
        end = date.fromisoformat(people[rid]["end_date"])
        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        if not (b80 <= first <= analysis <= last <= end):
            failures.append(f"events: date outside bounds/window {rid}")
        precision = row["event_date_precision"]
        if precision == "DAY":
            if not (first == analysis == last):
                failures.append(f"events: DAY rule mismatch {rid}")
        elif precision in {"MONTH", "YEAR", "BOUNDED_INTERVAL"}:
            if analysis != midpoint(first, last):
                failures.append(f"events: midpoint rule mismatch {rid}")
        else:
            failures.append(f"events: invalid precision {rid}")
        expected_boundary = int(
            (first < b80 <= last)
            or (first < b85 <= last)
            or (first < end <= last)
        )
        if int(row["boundary_sensitive"]) != expected_boundary:
            failures.append(f"events: boundary flag mismatch {rid}")
        expected_age = (analysis - birth).days / 365.2425
        if abs(float(row["age_at_analysis_event"]) - expected_age) > 0.000001:
            failures.append(f"events: age mismatch {rid}")
        if row["evidence_type"] == "QUALIFYING_FUNCTION_EVENT":
            function_by_id[rid].append(row)
        elif row["evidence_type"] == "QUALIFYING_IMPAIRMENT_EVIDENCE":
            impairment_by_id[rid].append(row)
        else:
            failures.append(f'events: invalid qualifying evidence type {rid}')

    for rid, outcome in outcome_by_id.items():
        if outcome["outcome_state"] not in STATES:
            failures.append(f"outcomes: invalid state {rid}")
            continue
        if rid not in eligible:
            if outcome["outcome_state"] != "NOT_ELIGIBLE_UNDER_80":
                failures.append(f"outcomes: ineligible state mismatch {rid}")
            continue
        funcs = sorted(function_by_id[rid], key=lambda row: row["analysis_event_date"])
        imps = sorted(impairment_by_id[rid], key=lambda row: row["analysis_event_date"])
        if funcs and not imps:
            expected_state = "FUNCTION_ONLY"
        elif imps and not funcs:
            expected_state = "IMPAIRMENT_ONLY"
        elif funcs and imps:
            func_first = funcs[0]
            imp_first = imps[0]
            if date.fromisoformat(func_first["event_date_latest"]) < date.fromisoformat(
                imp_first["event_date_earliest"]
            ):
                expected_state = "FUNCTION_THEN_IMPAIRMENT"
            elif date.fromisoformat(imp_first["event_date_latest"]) < date.fromisoformat(
                func_first["event_date_earliest"]
            ):
                expected_state = "IMPAIRMENT_THEN_FUNCTION"
            else:
                expected_state = "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE"
        else:
            expected_state = "NEITHER_FOUND"
        if outcome["outcome_state"] != expected_state:
            failures.append(f"outcomes: state/event linkage mismatch {rid}")

        birth = date.fromisoformat(people[rid]["birth_date"])
        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        cohort_row = cohort_by_id[people[rid]["person_id"]]
        death = date.fromisoformat(cohort_row["death_date"]) if cohort_row["death_date"] else None
        primary = None
        if funcs:
            candidate = date.fromisoformat(funcs[0]["analysis_event_date"])
            if b80 <= candidate < b85 and candidate <= CENSOR:
                primary = candidate
            expected_first = funcs[0]["analysis_event_date"]
            expected_latest = funcs[-1]["analysis_event_date"]
            if outcome["first_qualifying_function_date"] != expected_first:
                failures.append(f"outcomes: first function mismatch {rid}")
            if outcome["latest_qualifying_function_date"] != expected_latest:
                failures.append(f"outcomes: latest function mismatch {rid}")
            if int(outcome["first_function_days_after_80"]) != (
                date.fromisoformat(expected_first) - b80
            ).days:
                failures.append(f"outcomes: function day offset mismatch {rid}")
        elif any(
            outcome[field]
            for field in (
                "first_qualifying_function_date",
                "first_function_date_precision",
                "first_function_days_after_80",
                "latest_qualifying_function_date",
                "latest_qualifying_function_age",
            )
        ):
            failures.append(f"outcomes: function fields populated without event {rid}")
        expected_impairment = imps[0]["analysis_event_date"] if imps else ""
        if outcome["first_qualifying_impairment_date"] != expected_impairment:
            failures.append(f"outcomes: first impairment mismatch {rid}")
        if int(outcome["first_function_within_five_years"]) != int(primary is not None):
            failures.append(f"outcomes: primary function indicator mismatch {rid}")
        expected_potential = (min(b85, CENSOR) - b80).days
        candidates = [b85, CENSOR]
        if death is not None:
            candidates.append(death)
        if primary is not None:
            candidates.append(primary)
        expected_observed = (min(candidates) - b80).days
        if int(outcome["potential_followup_days"]) != expected_potential:
            failures.append(f"outcomes: potential follow-up mismatch {rid}")
        if int(outcome["observed_followup_days"]) != expected_observed:
            failures.append(f"outcomes: observed follow-up mismatch {rid}")
        expected_competing = int(
            death is not None
            and b80 <= death < b85
            and death <= CENSOR
            and (primary is None or death < primary)
        )
        expected_admin = int(
            CENSOR < b85
            and (death is None or death > CENSOR)
            and (primary is None or primary > CENSOR)
        )
        if int(outcome["death_competing_event_within_five_years"]) != expected_competing:
            failures.append(f"outcomes: competing-death mismatch {rid}")
        if int(outcome["administratively_censored_before_five_years"]) != expected_admin:
            failures.append(f"outcomes: administrative-censor mismatch {rid}")
        substantive_urls = {
            row["url"]
            for row in by_rid_search[rid]
            if row["substantive_late_life_source"] == "1"
            and row["access_result"] == "opened"
        }
        publishers = {publisher_family(url) for url in substantive_urls}
        if int(outcome["substantive_sources_opened"]) != len(substantive_urls):
            failures.append(f"outcomes: substantive-source count mismatch {rid}")
        if int(outcome["independent_publishers"]) != len(publishers):
            failures.append(f"outcomes: publisher count mismatch {rid}")
        if len(substantive_urls) <= 1:
            expected_depth = "LOW"
        elif len(substantive_urls) <= 4:
            expected_depth = "MEDIUM"
        elif len(publishers) >= 2:
            expected_depth = "HIGH"
        else:
            expected_depth = "MEDIUM"
        if outcome["documentation_depth"] != expected_depth:
            failures.append(f"outcomes: documentation depth mismatch {rid}")

    action_log = root / "ACTION_LOG.md"
    timestamps: list[datetime] = []
    repair_start = datetime(2026, 7, 23, 5, 35, 0, tzinfo=timezone.utc)
    if not action_log.is_file():
        failures.append("action log: missing")
    else:
        for line in action_log.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", line)
            if match:
                stamp = datetime.fromisoformat(match.group(1).replace("Z", "+00:00"))
                timestamps.append(stamp)
                if stamp >= repair_start and "WEB QUERY" in line:
                    failures.append("action log: web query recorded during no-browsing repair")
        inversions = [
            (timestamps[index - 1], timestamps[index])
            for index in range(1, len(timestamps))
            if timestamps[index] < timestamps[index - 1]
        ]
        allowed_inversion = [
            (
                datetime(2026, 7, 23, 4, 43, 33, tzinfo=timezone.utc),
                datetime(2026, 7, 23, 4, 43, 32, tzinfo=timezone.utc),
            )
        ]
        if inversions != allowed_inversion:
            failures.append(f"action log: unexpected timestamp inversions {inversions}")
        if timestamps and timestamps[-1] > datetime.now(timezone.utc) + timedelta(minutes=5):
            failures.append("action log: future timestamp")

    summary = {
        "worklist_rows": len(work),
        "eligible_rows": len(eligible),
        "search_rows": len(search),
        "event_rows": len(events),
        "qualifying_function_rows": sum(
            row["evidence_type"] == "QUALIFYING_FUNCTION_EVENT" for row in events
        ),
        "qualifying_impairment_rows": sum(
            row["evidence_type"] == "QUALIFYING_IMPAIRMENT_EVIDENCE" for row in events
        ),
        "primary_function_rows": sum(
            row["eligible_age80"] == "1" and row["first_function_within_five_years"] == "1"
            for row in outcomes
        ),
        "raw_json_files": len(raw_files),
        "action_timestamps": len(timestamps),
        "declared_one_second_log_inversions": len(inversions),
    }
    return sorted(set(failures)), summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("cohort_csv", type=Path)
    args = parser.parse_args()
    failures, summary = validate(args.root.resolve(), args.cohort_csv.resolve())
    print(json.dumps({"problems": failures, "summary": summary}, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
