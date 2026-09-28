#!/usr/bin/env python3
"""Print matching stored page lines with local context; never accesses the web."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


RAW = Path(__file__).resolve().parent / "raw"


def main(research_id: str, url_fragment: str, pattern: str) -> None:
    data = json.loads((RAW / f"{research_id}.json").read_text(encoding="utf-8"))
    matcher = re.compile(pattern, re.IGNORECASE)
    for query in data.get("queries", []) + data.get("extra_queries", []):
        for attempt in query.get("open_attempts", []):
            if url_fragment not in attempt.get("url", ""):
                continue
            print(
                research_id,
                query.get("family", ""),
                attempt.get("url", ""),
                attempt.get("title", ""),
                attempt.get("access_result", ""),
                sep=" | ",
            )
            lines = attempt.get("content", "").splitlines()
            selected: set[int] = set()
            for index, line in enumerate(lines):
                if matcher.search(line):
                    selected.update(range(max(0, index - 2), min(len(lines), index + 3)))
            for index in sorted(selected):
                print(lines[index])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
