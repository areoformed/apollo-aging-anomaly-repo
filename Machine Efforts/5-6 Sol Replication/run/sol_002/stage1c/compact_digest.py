#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

KEYWORDS = re.compile(
    r"interview|q&a|question|answer|lecture|talk|discussion|present|teach|taught|"
    r"author|wrote|book|memoir|publish|active|current|advisor|advisory|chair|board|"
    r"pilot|flew|flying|operat|artist|paint|dementia|alzheimer|cognitive|stroke|"
    r"obituar|died|death|birthday|turn(?:ed|s)\s+8[0-9]|turn(?:ed|s)\s+9[0-9]",
    re.I,
)

def main(ids):
    for rid in ids:
        data = json.loads((ROOT / "raw" / f"{rid}.json").read_text())
        person = data.get("person", {})
        surname = person.get("full_name", "").split()[-1].replace("Jr.", "")
        print(f"===== {rid} | {person.get('full_name')} | {person.get('birth_date')} to {person.get('end_date')} =====")
        for q in data.get("queries", []):
            for op in q.get("open_attempts", []):
                if op.get("access_result") != "opened":
                    continue
                print(f"-- {q.get('family')} rank={op.get('rank')} | {op.get('title')}\nURL {op.get('url')}")
                lines = [re.sub(r"^EXCERPT\s*", "", x).strip() for x in (op.get("content") or "").splitlines()]
                selected = []
                for i, line in enumerate(lines):
                    if not line:
                        continue
                    if i < 4 or (surname and surname.lower() in line.lower()) or KEYWORDS.search(line):
                        selected.append(line)
                seen = set()
                for line in selected:
                    if line in seen:
                        continue
                    seen.add(line)
                    print(line[:900])
                    if len(seen) >= 14:
                        break

if __name__ == "__main__":
    main(sys.argv[1:])
