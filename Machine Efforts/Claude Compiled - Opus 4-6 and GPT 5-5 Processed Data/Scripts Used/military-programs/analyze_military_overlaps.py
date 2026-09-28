#!/usr/bin/env python3
"""
Identify unique non-core-73 military pilots who reached 80+, and count overlaps.

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-20T06:37:25Z (line 3531) and 2026-05-20T06:47:55Z (line 3549)
What it does: Two analysis scripts combined:
  1. Reads all 3 military files + core 73, identifies every person, flags core membership,
     cross-program membership, age, SG status, and whether they reached 80+.
  2. Counts exact overlaps per file and cross-program overlaps (Dyna-Soar & MOL).

This was the analysis that informed the dedup strategy in dedup_military_files.py.

Run from the Claude Compiled Data directory.
"""

import csv
from datetime import date

today = date(2026, 5, 19)

# --- Part 1: Detailed overlap analysis ---

# Core 73 names for dedup
core_names = set()
for f in ['07E-lunar-enriched.tsv', '08E-non-lunar-apollo-enriched.tsv', '03E-non-apollo-enriched.tsv']:
    with open(f) as fh:
        reader = csv.reader(fh, delimiter='\t')
        next(reader)
        for row in reader:
            if row:
                core_names.add(row[0].strip())

print(f'Core 73 names: {len(core_names)}')
print()

# Read military files, track all people
all_military = {}  # name -> {file, group, dob, dod, age, status, sg, ...}
files = {
    '09-x15-pilots-enriched.tsv': 'X-15',
    '10-dyna-soar-pilots-enriched.tsv': 'Dyna-Soar',
    '11-mol-full-enriched.tsv': 'MOL'
}

for fname, program in files.items():
    with open(fname) as fh:
        reader = csv.reader(fh, delimiter='\t')
        header = next(reader)
        for row in reader:
            if len(row) < 23:
                continue
            name = row[0].strip()
            dob_str = row[2].strip()
            dod_str = row[10].strip()
            status = row[12].strip()
            sg = row[15].strip()
            birth_year = row[21].strip()

            in_core = name in core_names

            # Check if already seen in another military file
            if name in all_military:
                all_military[name]['also_in'].append(program)
                continue

            # Parse age
            age = None
            if dob_str:
                try:
                    parts = dob_str.split('-')
                    born = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    if dod_str:
                        parts2 = dod_str.split('-')
                        died = date(int(parts2[0]), int(parts2[1]), int(parts2[2]))
                        age = (died - born).days / 365.25
                    else:
                        age = (today - born).days / 365.25
                except:
                    pass

            all_military[name] = {
                'program': program,
                'also_in': [],
                'in_core': in_core,
                'dob': dob_str,
                'dod': dod_str or 'Living',
                'age': age,
                'status': status,
                'sg': sg,
                'reached_80': age is not None and age >= 80
            }

# Report
print('=== ALL MILITARY PILOTS (deduplicated across programs) ===')
unique_non_core = []
for name, info in sorted(all_military.items(), key=lambda x: x[1]['program']):
    also = f' + {" + ".join(info["also_in"])}' if info['also_in'] else ''
    core_flag = ' [CORE 73]' if info['in_core'] else ''
    age_str = f'{info["age"]:.0f}' if info['age'] else '?'
    r80 = ' [80+]' if info['reached_80'] else ''
    print(f'  {info["program"]}{also}{core_flag} | {name} | {info["dod"]} | age {age_str} | SG={info["sg"]}{r80}')
    if not info['in_core']:
        unique_non_core.append((name, info))

print(f'\nTotal unique military pilots: {len(all_military)}')
print(f'In core 73: {sum(1 for v in all_military.values() if v["in_core"])}')
print(f'Unique (not in core 73): {len(unique_non_core)}')
print(f'Unique who reached 80+: {sum(1 for _, v in unique_non_core if v["reached_80"])}')

print('\n=== UNIQUE NON-CORE WHO REACHED 80+ (need standardized SG search) ===')
for name, info in unique_non_core:
    if info['reached_80']:
        also = f' + {" + ".join(info["also_in"])}' if info['also_in'] else ''
        print(f'  {name} | {info["program"]}{also} | {info["dod"]} | age {info["age"]:.0f} | current SG={info["sg"]}')

# --- Part 2: Per-file overlap counts ---

print('\n\n=== PER-FILE OVERLAP COUNTS ===')
for fname in ['09-x15-pilots-enriched.tsv', '10-dyna-soar-pilots-enriched.tsv', '11-mol-full-enriched.tsv']:
    with open(fname) as fh:
        reader = csv.reader(fh, delimiter='\t')
        header = next(reader)
        rows = list(reader)

    overlaps = [r[0].strip() for r in rows if r[0].strip() in core_names]
    unique = [r for r in rows if r[0].strip() not in core_names]
    print(f'{fname}: {len(rows)} total, {len(overlaps)} core-73 overlaps ({overlaps}), {len(unique)} unique')

# Check Crews cross-overlap (Dyna-Soar + MOL)
ds_names = set()
with open('10-dyna-soar-pilots-enriched.tsv') as fh:
    reader = csv.reader(fh, delimiter='\t')
    next(reader)
    for row in reader:
        if row[0].strip() not in core_names:
            ds_names.add(row[0].strip())

mol_names = set()
with open('11-mol-full-enriched.tsv') as fh:
    reader = csv.reader(fh, delimiter='\t')
    next(reader)
    for row in reader:
        if row[0].strip() not in core_names:
            mol_names.add(row[0].strip())

cross = ds_names & mol_names
print(f'Cross-overlap (Dyna-Soar & MOL after core removal): {cross}')
