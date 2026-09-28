#!/usr/bin/env python3
"""Print compact opened-page digests for blinded Stage 1C adjudication."""

from __future__ import annotations

import json
import re
import sys
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "stage1c" / "raw"
requested = sys.argv[1:]
if not requested:
    raise SystemExit("supply one or more research_id values")

with (ROOT / "stage1c" / "research_worklist.csv").open(
    newline="", encoding="utf-8"
) as handle:
    worklist = {
        row["research_id"]: row
        for row in csv.DictReader(handle)
        if row["research_id"] in requested
    }

keywords = re.compile(
    r"\b(interview|conversation|q&a|question|answer|said|says|told|"
    r"lecture|talk|present|teach|professor|book|memoir|author|wrote|"
    r"publish|chair|board|advis|director|founder|president|work|"
    r"pilot|fly|flew|flying|aircraft|museum|fieldwork|"
    r"dementia|alzheimer|cognit|memory|stroke|impair)\b",
    re.IGNORECASE,
)
dateish = re.compile(
    r"\b(?:19|20)\d{2}\b|"
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b",
    re.IGNORECASE,
)

for research_id in requested:
    path = RAW / f"{research_id}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    person = record["person"]
    birth_date = person.get(
        "birth_date", worklist[research_id]["birth_date"]
    )
    end_date = person.get("end_date", worklist[research_id]["end_date"])
    print(
        f"===== {research_id} | {person['full_name']} | "
        f"{birth_date} to {end_date} ====="
    )
    groups = list(record.get("queries", [])) + list(
        record.get("extra_queries", [])
    )
    for query in groups:
        for opened in query.get("open_attempts", []):
            print(
                f"-- {query['family']} rank={opened['rank']} "
                f"access={opened.get('access_result','')} "
                f"title={opened.get('title','')}"
            )
            print(f"URL {opened['url']}")
            if opened.get("access_result") != "opened":
                continue
            content = opened.get("content", "")
            lines = [
                re.sub(r"\s+", " ", line).strip()
                for line in content.splitlines()
                if line.strip()
            ]
            selected: list[str] = lines[:8]
            for line in lines:
                if (
                    ("Published:" in line or "Updated:" in line)
                    or dateish.search(line)
                    or (
                        keywords.search(line)
                        and any(
                            token in line.lower()
                            for token in ("years old", "age ", "aged ")
                        )
                    )
                ):
                    if line not in selected:
                        selected.append(line)
                if len(selected) == 16:
                    break
            for line in selected:
                print(f"EXCERPT {line[:900]}")
