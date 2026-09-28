#!/usr/bin/env python3
"""Read-only extraction of locally stored lines for controller-gate re-audit."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


STAGE = Path(__file__).resolve().parent
RAW = STAGE / "raw"
KEYWORDS = re.compile(
    r"\b(interview|recorded|recording|release|published|publication|"
    r"speaks?|lecture|talk|q&a|question|answer|author|book|memoir|"
    r"will|event|piloti(?:ng|ed)|flew|crash|died|donat|letter|"
    r"respons|discussion|presentation|caption|date|foreword)\b",
    re.IGNORECASE,
)


def attempts(data: dict) -> list[tuple[str, dict]]:
    found: list[tuple[str, dict]] = []
    for query in data.get("queries", []) + data.get("extra_queries", []):
        for attempt in query.get("open_attempts", []):
            found.append((query.get("family", ""), attempt))
    return found


def relevant_lines(content: str) -> list[str]:
    lines = content.splitlines()
    selected: set[int] = set()
    for index, line in enumerate(lines):
        if KEYWORDS.search(line):
            selected.update(range(max(0, index - 1), min(len(lines), index + 2)))
    if not selected:
        selected.update(range(min(len(lines), 20)))
    return [lines[index] for index in sorted(selected)]


def main(ids: list[str]) -> None:
    with (STAGE / "EVIDENCE_EVENTS.csv").open(encoding="utf-8", newline="") as handle:
        event_rows = list(csv.DictReader(handle))
    by_id: dict[str, list[dict[str, str]]] = {}
    for row in event_rows:
        by_id.setdefault(row["research_id"], []).append(row)
    for rid in ids:
        print(f"===== {rid} =====")
        data = json.loads((RAW / f"{rid}.json").read_text(encoding="utf-8"))
        local_attempts = attempts(data)
        for event in by_id.get(rid, []):
            print(
                "EVENT",
                event["evidence_type"],
                event["event_date"],
                event["source_url"],
                sep=" | ",
            )
            matches = [
                (family, attempt)
                for family, attempt in local_attempts
                if attempt.get("url") == event["source_url"]
            ]
            if not matches:
                print("RAW_MATCH | NONE")
                continue
            for family, attempt in matches:
                print(
                    "RAW_MATCH",
                    family,
                    attempt.get("title", ""),
                    attempt.get("access_result", ""),
                    sep=" | ",
                )
                for line in relevant_lines(attempt.get("content", "")):
                    print(line)
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
