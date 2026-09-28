#!/usr/bin/env python3
"""Deduplicate military program files (X-15, Dyna-Soar, MOL) against core 73 and each other.
Source: Session 8ed732b6 (May 19, 2026), line 3564.
Removes core-73 overlaps (Armstrong/Engle from X-15, Armstrong from Dyna-Soar,
7 NASA transfers from MOL) and cross-program overlaps (Adams and Crews from MOL
since they appear in X-15 and Dyna-Soar respectively).
"""

import csv, os

os.chdir("./Claude Compiled Data")

# Build core 73 surname set for fuzzy matching
core_names_exact = set()
core_surnames = {}
for fn in ['07E-lunar-enriched.tsv', '08E-non-lunar-apollo-enriched.tsv', '03E-non-apollo-enriched.tsv']:
    with open(fn) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            name = row[0].strip()
            core_names_exact.add(name)
            parts = name.replace('"', '').split()
            surname = parts[-1]
            if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
                surname = parts[-2]
            core_surnames[surname.lower()] = name

def is_core_73(name):
    if name in core_names_exact:
        return True
    parts = name.replace('"', '').split()
    surname = parts[-1]
    if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
        surname = parts[-2]
    if surname.lower() in core_surnames:
        return True
    return False

# Names to remove from MOL beyond core-73
mol_cross_remove = {'Michael James Adams', 'Albert Hanlin Crews Jr.'}

for fname, extra_remove in [
    ('09-x15-pilots-enriched.tsv', set()),
    ('10-dyna-soar-pilots-enriched.tsv', set()),
    ('11-mol-full-enriched.tsv', mol_cross_remove)
]:
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        rows = list(reader)

    kept = []
    removed = []
    for row in rows:
        name = row[0].strip()
        if is_core_73(name):
            removed.append(f'{name} [core-73]')
        elif name in extra_remove:
            removed.append(f'{name} [cross-program]')
        else:
            kept.append(row)

    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        for row in kept:
            writer.writerow(row)

    print(f'{fname}: {len(rows)} -> {len(kept)} rows')
    print(f'  Removed: {removed}')
    print()

# Final verification
total_unique = 0
for fname in ['09-x15-pilots-enriched.tsv', '10-dyna-soar-pilots-enriched.tsv', '11-mol-full-enriched.tsv']:
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        rows = list(reader)
        total_unique += len(rows)
        print(f'{fname}: {len(rows)} rows')

print(f'\nTotal unique military pilots (not in core 73): {total_unique}')
print(f'Core 73: 73')
print(f'Grand total unique people: {73 + total_unique}')
