#!/usr/bin/env python3
"""Emit selected blinded worklist/query-schedule records as JSON."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
requested = set(sys.argv[1:])
if not requested:
    raise SystemExit("supply one or more research_id values")

with (ROOT / "stage1c" / "research_worklist.csv").open(
    newline="", encoding="utf-8"
) as handle:
    people = {
        row["research_id"]: row
        for row in csv.DictReader(handle)
        if row["research_id"] in requested
    }

queries: dict[str, list[dict[str, str]]] = {key: [] for key in requested}
with (ROOT / "stage1c" / "query_schedule.csv").open(
    newline="", encoding="utf-8"
) as handle:
    for row in csv.DictReader(handle):
        if row["research_id"] in requested:
            queries[row["research_id"]].append({
                "query_family": row["query_family"],
                "query": row["query"],
            })

result = []
for research_id in sys.argv[1:]:
    person = people[research_id]
    result.append({
        "research_id": research_id,
        "person_id": person["person_id"],
        "full_name": person["full_name"],
        "search_disambiguator": person["search_disambiguator"],
        "birth_date": person["birth_date"],
        "end_date": person["end_date"],
        "queries": queries[research_id],
    })
assert all(len(item["queries"]) == 6 for item in result)
print(json.dumps(result, ensure_ascii=False))
