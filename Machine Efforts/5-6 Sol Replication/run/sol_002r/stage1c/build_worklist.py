#!/usr/bin/env python3
"""Build the blinded Stage 1C research worklist from identity/vital fields only."""

from __future__ import annotations

import csv
import hashlib
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "stage1" / "cohort.csv"
OUTPUT = ROOT / "stage1c" / "research_worklist.csv"
CENSOR = date(2026, 6, 1)
SALT = "SOL-20260721-EVIDENCE|"


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


records: list[dict[str, str]] = []
with INPUT.open(newline="", encoding="utf-8") as handle:
    for source in csv.DictReader(handle):
        # Deliberately access only these locked identity/vital fields.
        person_id = source["person_id"]
        birth_date = parse_date(source["birth_date"])
        end_date = parse_date(source["death_date"]) if source["death_date"] else CENSOR
        birthday_80 = birth_date.replace(year=birth_date.year + 80)
        records.append({
            "_sort_hash": hashlib.sha256(
                f"{SALT}{person_id}".encode("utf-8")
            ).hexdigest(),
            "person_id": person_id,
            "full_name": source["full_name"],
            "search_disambiguator": source["search_disambiguator"],
            "birth_date": birth_date.isoformat(),
            "end_date": end_date.isoformat(),
            "eligible_age80": "1" if birthday_80 <= end_date else "0",
        })

records.sort(key=lambda row: row["_sort_hash"])
for index, row in enumerate(records, start=1):
    row["research_id"] = f"R{index:03d}"

columns = [
    "research_id", "person_id", "full_name", "search_disambiguator",
    "birth_date", "end_date", "eligible_age80",
]
with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle, fieldnames=columns, extrasaction="ignore",
        dialect="excel", lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(records)

assert len(records) == len({row["person_id"] for row in records})
assert records == sorted(records, key=lambda row: row["_sort_hash"])
assert all(row["eligible_age80"] in {"0", "1"} for row in records)
print(f"wrote {len(records)} blinded worklist rows")
