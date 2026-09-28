#!/usr/bin/env python3
"""Create the fixed six-family Stage 1C query schedule."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLIST = ROOT / "stage1c" / "research_worklist.csv"
OUTPUT = ROOT / "stage1c" / "query_schedule.csv"

families = [
    ("INTERVIEW", '"{name}" {role} interview'),
    ("LECTURE_TALK_QA", '"{name}" {role} lecture OR talk OR Q&A'),
    ("AUTHOR_WORK", '"{name}" {role} author OR book OR memoir'),
    ("IMPAIRMENT", '"{name}" {role} dementia OR Alzheimer OR "cognitive decline" OR stroke'),
    ("MILESTONE_BIRTHDAY", '"{name}" {role} 80th OR 85th OR 90th birthday'),
    ("OBITUARY_DEATH", '"{name}" {role} obituary OR died'),
]

scheduled: list[dict[str, str]] = []
with WORKLIST.open(newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        if row["eligible_age80"] != "1":
            continue
        birth = date.fromisoformat(row["birth_date"])
        end = date.fromisoformat(row["end_date"])
        lower_year = birth.year + 79
        upper_year = end.year + 1
        bounds = f"after:{lower_year}-12-31 before:{upper_year}-01-01"
        for family, template in families:
            core = template.format(
                name=row["full_name"],
                role=row["search_disambiguator"],
            )
            scheduled.append({
                "research_id": row["research_id"],
                "person_id": row["person_id"],
                "query_family": family,
                "query": f"{core} {bounds}",
            })

with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=["research_id", "person_id", "query_family", "query"],
        dialect="excel",
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(scheduled)

assert all(
    sum(item["research_id"] == research_id for item in scheduled) == 6
    for research_id in {item["research_id"] for item in scheduled}
)
print(f"wrote {len(scheduled)} fixed base queries")
