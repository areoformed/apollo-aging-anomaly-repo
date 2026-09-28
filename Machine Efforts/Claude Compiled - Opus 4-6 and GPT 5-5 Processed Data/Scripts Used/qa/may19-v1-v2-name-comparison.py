#!/usr/bin/env python3
"""Compare V1 (projects/apollo-aging-anomaly) and V2 (Claude Compiled Data) name lists.
Source: Session 8ed732b6 (May 19, 2026), line 3617.
Uses surname matching to find people in V1 who are missing from V2,
accounting for short-name vs full-name differences between the two datasets.
"""

import csv

# Extract V1 names (deduplicated, normalized)
v1_names = set()
with open("<workspace>/projects/apollo-aging-anomaly/astronaut-dataset.tsv") as f:
    next(f)
    for line in f:
        name = line.split('\t')[0].strip()
        if name:
            v1_names.add(name)

# Extract V2 names from all 6 enriched files
v2_names = set()
v2_name_list = {}
data_dir = "./Claude Compiled Data/"
for fname in ['07E-lunar-enriched.tsv', '08E-non-lunar-apollo-enriched.tsv', '03E-non-apollo-enriched.tsv',
              '09-x15-pilots-enriched.tsv', '10-dyna-soar-pilots-enriched.tsv', '11-mol-full-enriched.tsv']:
    with open(data_dir + fname) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            name = row[0].strip()
            v2_names.add(name)
            v2_name_list[name] = fname

print(f"V1: {len(v1_names)} unique names")
print(f"V2: {len(v2_names)} unique names")

# Build surname mapping for V2
v2_by_surname = {}
for name in v2_names:
    parts = name.replace('"', '').split()
    surname = parts[-1]
    if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
        surname = parts[-2] if len(parts) > 1 else surname
    v2_by_surname.setdefault(surname.lower(), []).append(name)

# Find V1 names not in V2
print("\n=== In V1 but NOT in V2 ===")
unmatched_v1 = []
for v1_name in sorted(v1_names):
    parts = v1_name.replace('"', '').split()
    surname = parts[-1]
    if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
        surname = parts[-2] if len(parts) > 1 else surname

    matches = v2_by_surname.get(surname.lower(), [])
    if not matches:
        unmatched_v1.append(v1_name)
        print(f"  {v1_name} -- NO surname match in V2")
    elif len(matches) == 1:
        pass
    else:
        first = parts[0].lower()
        found = False
        for m in matches:
            if first in m.lower():
                found = True
                break
        if not found:
            unmatched_v1.append(v1_name)
            print(f"  {v1_name} -- surname matched [{', '.join(matches)}] but first name didn't match")

print(f"\nTotal unmatched: {len(unmatched_v1)}")
