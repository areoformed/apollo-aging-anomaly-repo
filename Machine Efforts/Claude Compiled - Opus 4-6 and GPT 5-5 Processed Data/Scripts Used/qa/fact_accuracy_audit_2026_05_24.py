#!/usr/bin/env python3
"""Compare current enriched astronaut facts against the prior project yardstick.

This script intentionally treats the older project dataset as a comparison
yardstick only. It does not declare either side canonical.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
YARDSTICK = Path("<workspace>/projects/apollo-aging-anomaly/astronaut-dataset.tsv")
CURRENT_DIR = ROOT / "Final - Analysis - Enriched Datasets"
OUT_DIR = ROOT / "data"

CURRENT_FILES = [
    "07E-lunar-enriched.tsv",
    "08E-non-lunar-apollo-enriched.tsv",
    "03E-non-apollo-enriched.tsv",
    "09-x15-pilots-enriched.tsv",
    "10-dyna-soar-pilots-enriched.tsv",
    "11-mol-full-enriched.tsv",
]

FIELD_MAP = [
    ("name", "Name", "Name"),
    ("group", "Astronaut Group", "Primary Group"),
    ("birth_date", "Date of Birth", "Date of Birth"),
    ("selection_date", "Date of Selection", "Date of Selection"),
    ("death_date", "Date of Death", "Date of Death"),
    ("status", "Status", "Status"),
    ("accidental_death", "Accidental Death", "Accidental Death"),
    ("space_grandpa", "Space Grandpa", "Space Grandpa"),
    ("time_in_space", "Time in Space", "Time in Space"),
    ("number_of_flights", "Number of Flights", "Number of Flights"),
    ("missions", "Missions Flown", "Missions"),
    ("moonwalker", "Moonwalker", "Moonwalker"),
    ("military_branch", "Military Branch", "Military Branch"),
]

ALIASES = {
    "Walter Marty Schirra Jr.": "Wally Schirra",
    "James Alton McDivitt Jr.": "James McDivitt",
    "Thomas Patten Stafford": "Thomas P. Stafford",
    "Ronnie Walter Cunningham": "Walter Cunningham",
    'Karol Joseph "Bo" Bobko': "Karol J. Bobko",
    "Charles Arthur Bassett II": "Charles Bassett",
    "Joseph Percival Allen IV": "Joseph P. Allen",
    "Vance DeVoe Brand": "Vance Brand",
    "Bruce McCandless II": "Bruce McCandless II",
    "Duane Edgar \"Doc\" Graveline": "Duane Graveline",
    "Edward Galen Givens Jr.": "Edward Givens",
    "Jack Robert Lousma": "Jack Lousma",
    "John Anthony Llewellyn": "Anthony Llewellyn",
    "William Alison Anders": "William Anders",
    "Richard Francis Gordon Jr.": "Richard F. Gordon Jr.",
    "Edwin Eugene Aldrin Jr.": "Buzz Aldrin",
    "Clifton Curtis Williams Jr.": "Clifton Williams",
    "Franklin Story Musgrave": "Story Musgrave",
    "Frank Curtis Michel": "Curt Michel",
    "Paul Joseph Weitz": "Paul Weitz",
    "Donald Herod Peterson": "Donald Peterson",
    "Albert Scott Crossfield": "Scott Crossfield",
    "Forrest Silas Petersen": "Forrest S. Petersen",
    "Michael James Adams": "Michael J. Adams",
    "John Barron McKay": "John B. McKay",
    "Joseph Albert Walker": "Joseph A. Walker",
    "Robert Aitken Rushworth": "Robert A. Rushworth",
    "Milton Orville Thompson": "Milton Thompson",
    "William Harvey Dana": "William H. Dana",
    "William John Knight": "William J. Knight",
    "William Barton Bridgeman": "William B. Bridgeman",
    "Albert Hanlin Crews Jr.": "Albert H. Crews Jr.",
    "Henry Charles Gordon": "Henry C. Gordon",
    "James Wayne Wood": "James W. Wood",
    "Francis Gregory Neubeck": "Francis G. Neubeck",
    "James Alan Abrahamson": "James A. Abrahamson",
    "James Martin Taylor": "James M. Taylor",
    "Robert Tralles Herres": "Robert Herres",
    "John Sumter Bull": "John S. Bull",
    "Joseph Peter Kerwin": "Joseph Kerwin",
    "Philip Kenyon Chapman": "Philip Chapman",
    "William Benjamin Lenoir": "William B. Lenoir",
    "William Edgar Thornton": "William Thornton",
    "Edward George Gibson": "Edward Gibson",
}


@dataclass
class RowRef:
    source_file: str
    line_number: int
    row: dict[str, str]
    key: str


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def iter_tsv(path: Path) -> Iterable[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for offset, row in enumerate(reader, start=2):
            yield offset, row


def slug_from_url(value: str) -> str:
    if not value:
        return ""
    match = re.search(r"https?://en\.wikipedia\.org/wiki/([^;\s]+)", value.strip())
    if not match:
        return ""
    return match.group(1).split("#", 1)[0].strip().lower()


def normalize_name(value: str) -> str:
    value = ALIASES.get(value.strip(), value.strip())
    value = value.lower()
    value = value.replace('"', "")
    value = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def person_key(row: dict[str, str], url_fields: list[str]) -> str:
    for field in url_fields:
        slug = slug_from_url(row.get(field, ""))
        if slug:
            return f"wiki:{slug}"
    return f"name:{normalize_name(row.get('Name', ''))}"


def surname_birth_key(row: dict[str, str]) -> str:
    name = normalize_name(row.get("Name", ""))
    tokens = name.split()
    if not tokens:
        return ""
    dob = row.get("Date of Birth", "").strip()
    return f"{tokens[-1]}|{dob}"


def norm_field(field_id: str, value: str) -> str:
    value = (value or "").strip()
    if field_id in {"space_grandpa", "accidental_death", "moonwalker"}:
        lowered = value.lower()
        if lowered in {"y", "yes", "true"}:
            return "Y"
        if lowered in {"n", "no", "false"}:
            return "N"
        return value
    if field_id == "status":
        return value.lower()
    if field_id == "death_date" and value.lower() in {"living", "alive"}:
        return ""
    if field_id in {"missions", "group", "military_branch"}:
        return re.sub(r"\s+", " ", value.replace(",", ";")).strip().lower()
    return value


def load_current() -> dict[str, list[RowRef]]:
    out: dict[str, list[RowRef]] = {}
    for filename in CURRENT_FILES:
        path = CURRENT_DIR / filename
        for line_number, row in iter_tsv(path):
            key = person_key(row, ["Citations"])
            out.setdefault(key, []).append(RowRef(filename, line_number, row, key))
    return out


def load_yardstick() -> tuple[dict[str, RowRef], dict[str, list[RowRef]]]:
    by_key: dict[str, list[RowRef]] = {}
    for line_number, row in iter_tsv(YARDSTICK):
        key = person_key(row, ["Wikipedia"])
        by_key.setdefault(key, []).append(RowRef(YARDSTICK.name, line_number, row, key))
    primary = {key: refs[-1] for key, refs in by_key.items()}
    duplicates = {key: refs for key, refs in by_key.items() if len(refs) > 1}
    return primary, duplicates


def unique_index(refs: Iterable[RowRef], key_fn) -> dict[str, RowRef]:
    tmp: dict[str, list[RowRef]] = {}
    for ref in refs:
        key = key_fn(ref.row)
        if key:
            tmp.setdefault(key, []).append(ref)
    return {key: values[0] for key, values in tmp.items() if len(values) == 1}


def match_rows(current: dict[str, list[RowRef]], yardstick: dict[str, RowRef]) -> tuple[list[tuple[RowRef, RowRef, str]], list[RowRef], list[RowRef]]:
    current_refs = [ref for refs in current.values() for ref in refs]
    yard_refs = list(yardstick.values())
    unmatched_current = set(id(ref) for ref in current_refs)
    unmatched_yard = set(id(ref) for ref in yard_refs)
    current_by_id = {id(ref): ref for ref in current_refs}
    yard_by_id = {id(ref): ref for ref in yard_refs}
    matches: list[tuple[RowRef, RowRef, str]] = []

    def add_match(current_ref: RowRef, yard_ref: RowRef, method: str) -> None:
        if id(current_ref) in unmatched_current and id(yard_ref) in unmatched_yard:
            unmatched_current.remove(id(current_ref))
            unmatched_yard.remove(id(yard_ref))
            matches.append((current_ref, yard_ref, method))

    for key, refs in current.items():
        if len(refs) == 1 and key in yardstick:
            add_match(refs[0], yardstick[key], "wiki_slug")

    current_remaining = [current_by_id[i] for i in unmatched_current]
    yard_remaining = [yard_by_id[i] for i in unmatched_yard]

    current_name = unique_index(current_remaining, lambda row: normalize_name(row.get("Name", "")))
    yard_name = unique_index(yard_remaining, lambda row: normalize_name(row.get("Name", "")))
    for key in sorted(set(current_name) & set(yard_name)):
        add_match(current_name[key], yard_name[key], "normalized_name")

    current_remaining = [current_by_id[i] for i in unmatched_current]
    yard_remaining = [yard_by_id[i] for i in unmatched_yard]
    current_sb = unique_index(current_remaining, surname_birth_key)
    yard_sb = unique_index(yard_remaining, surname_birth_key)
    for key in sorted(set(current_sb) & set(yard_sb)):
        add_match(current_sb[key], yard_sb[key], "surname_birthdate")

    return (
        matches,
        [current_by_id[i] for i in unmatched_current],
        [yard_by_id[i] for i in unmatched_yard],
    )


def main() -> None:
    current = load_current()
    yardstick, yardstick_duplicates = load_yardstick()
    matches, current_only, yardstick_only = match_rows(current, yardstick)

    coverage_path = OUT_DIR / "fact-audit-name-coverage-2026-05-24.tsv"
    diff_path = OUT_DIR / "fact-audit-yardstick-diffs-2026-05-24.tsv"
    duplicate_path = OUT_DIR / "fact-audit-yardstick-duplicates-2026-05-24.tsv"

    coverage_fields = [
        "key",
        "coverage",
        "current_name",
        "yardstick_name",
        "current_sources",
        "yardstick_source",
        "notes",
    ]
    with coverage_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=coverage_fields)
        writer.writeheader()
        for current_ref, yard_ref, method in sorted(matches, key=lambda pair: pair[1].row.get("Name", "")):
            writer.writerow(
                {
                    "key": current_ref.key,
                    "coverage": "both",
                    "current_name": current_ref.row.get("Name", ""),
                    "yardstick_name": yard_ref.row.get("Name", ""),
                    "current_sources": f"{current_ref.source_file}:{current_ref.line_number}",
                    "yardstick_source": f"{yard_ref.source_file}:{yard_ref.line_number}",
                    "notes": f"matched_by={method}",
                }
            )
        for current_ref in sorted(current_only, key=lambda ref: ref.row.get("Name", "")):
            writer.writerow(
                {
                    "key": current_ref.key,
                    "coverage": "current_only",
                    "current_name": current_ref.row.get("Name", ""),
                    "yardstick_name": "",
                    "current_sources": f"{current_ref.source_file}:{current_ref.line_number}",
                    "yardstick_source": "",
                    "notes": "",
                }
            )
        for yard_ref in sorted(yardstick_only, key=lambda ref: ref.row.get("Name", "")):
            writer.writerow(
                {
                    "key": yard_ref.key,
                    "coverage": "yardstick_only",
                    "current_name": "",
                    "yardstick_name": yard_ref.row.get("Name", ""),
                    "current_sources": "",
                    "yardstick_source": f"{yard_ref.source_file}:{yard_ref.line_number}",
                    "notes": "",
                }
            )

    diff_fields = [
        "key",
        "name_current",
        "name_yardstick",
        "field_id",
        "current_field",
        "yardstick_field",
        "current_value",
        "yardstick_value",
        "current_source",
        "yardstick_source",
        "comparison_status",
    ]
    with diff_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=diff_fields)
        writer.writeheader()
        for current_ref, yard_ref, method in sorted(matches, key=lambda pair: pair[1].row.get("Name", "")):
            for field_id, current_field, yard_field in FIELD_MAP:
                current_value = current_ref.row.get(current_field, "")
                yard_value = yard_ref.row.get(yard_field, "")
                if norm_field(field_id, current_value) == norm_field(field_id, yard_value):
                    status = "matches_after_normalization"
                else:
                    status = "diff_needs_source_check"
                writer.writerow(
                    {
                        "key": current_ref.key,
                        "name_current": current_ref.row.get("Name", ""),
                        "name_yardstick": yard_ref.row.get("Name", ""),
                        "field_id": field_id,
                        "current_field": current_field,
                        "yardstick_field": yard_field,
                        "current_value": current_value,
                        "yardstick_value": yard_value,
                        "current_source": f"{current_ref.source_file}:{current_ref.line_number}",
                        "yardstick_source": f"{yard_ref.source_file}:{yard_ref.line_number}",
                        "comparison_status": f"{status}; matched_by={method}",
                    }
                )

    duplicate_fields = [
        "key",
        "yardstick_name",
        "yardstick_source",
        "date_of_birth",
        "date_of_death",
        "wikipedia",
    ]
    with duplicate_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=duplicate_fields)
        writer.writeheader()
        for key, refs in sorted(yardstick_duplicates.items()):
            for ref in refs:
                writer.writerow(
                    {
                        "key": key,
                        "yardstick_name": ref.row.get("Name", ""),
                        "yardstick_source": f"{ref.source_file}:{ref.line_number}",
                        "date_of_birth": ref.row.get("Date of Birth", ""),
                        "date_of_death": ref.row.get("Date of Death", ""),
                        "wikipedia": ref.row.get("Wikipedia", ""),
                    }
                )

    print(f"Wrote {coverage_path}")
    print(f"Wrote {diff_path}")
    print(f"Wrote {duplicate_path}")
    print(f"Current unique keys: {len(current)}")
    print(f"Yardstick unique keys: {len(yardstick)}")
    print(f"Yardstick duplicate keys: {len(yardstick_duplicates)}")
    print(f"Both after alias/date matching: {len(matches)}")
    print(f"Current only after alias/date matching: {len(current_only)}")
    print(f"Yardstick only after alias/date matching: {len(yardstick_only)}")


if __name__ == "__main__":
    main()
