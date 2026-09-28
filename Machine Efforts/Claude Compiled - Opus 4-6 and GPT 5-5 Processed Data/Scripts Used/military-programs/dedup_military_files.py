#!/usr/bin/env python3
"""
Deduplicate military files (X-15, Dyna-Soar, MOL), removing core-73 and cross-program overlaps.

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-20T06:49:41Z (line 3563)
What it does: Builds the core 73 name set from 07E/08E/03E, then removes overlapping
              names from the three military program files:
  - 09 (X-15): removes core-73 overlaps (Armstrong, Engle)
  - 10 (Dyna-Soar): removes core-73 overlaps (Armstrong)
  - 11 (MOL): removes core-73 overlaps (7 Group 7 transfers) + Adams (in X-15) + Crews (in Dyna-Soar)

Uses both exact name matching and fuzzy surname matching to catch format differences
(e.g., "Karol Joseph Bobko" in core vs "Karol J. Bobko" in MOL).

Run from the Claude Compiled Data directory.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "Final - Analysis - Enriched Datasets"

# Build core 73 surname set for fuzzy matching
core_names_exact = set()
core_surnames = {}  # surname -> full name
for fn in [
    DATASET_DIR / '07E-lunar-enriched.tsv',
    DATASET_DIR / '08E-non-lunar-apollo-enriched.tsv',
    DATASET_DIR / '03E-non-apollo-enriched.tsv',
]:
    with open(fn) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            name = row[0].strip()
            core_names_exact.add(name)
            # Extract surname (last word, ignoring Jr./Sr./III etc)
            parts = name.replace('"', '').split()
            surname = parts[-1]
            if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
                surname = parts[-2]
            core_surnames[surname.lower()] = name

def is_core_73(name):
    if name in core_names_exact:
        return True
    # Fuzzy: check surname
    parts = name.replace('"', '').split()
    surname = parts[-1]
    if surname in ('Jr.', 'Sr.', 'II', 'III', 'IV'):
        surname = parts[-2]
    if surname.lower() in core_surnames:
        return True
    return False

# Dedup plan:
# - 09 (X-15): remove core-73 overlaps (Armstrong, Engle)
# - 10 (Dyna-Soar): remove core-73 overlaps (Armstrong). Keep Crews here.
# - 11 (MOL): remove core-73 overlaps (7 transfers) + Adams (in X-15) + Crews (in Dyna-Soar)

# Names to remove from MOL beyond core-73
mol_cross_remove = {'Michael James Adams', 'Albert Hanlin Crews Jr.'}

for fname, extra_remove in [
    (DATASET_DIR / '09-x15-pilots-enriched.tsv', set()),
    (DATASET_DIR / '10-dyna-soar-pilots-enriched.tsv', set()),
    (DATASET_DIR / '11-mol-full-enriched.tsv', mol_cross_remove)
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

    # Write deduplicated file
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
for fname in [
    DATASET_DIR / '09-x15-pilots-enriched.tsv',
    DATASET_DIR / '10-dyna-soar-pilots-enriched.tsv',
    DATASET_DIR / '11-mol-full-enriched.tsv',
]:
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        rows = list(reader)
        total_unique += len(rows)
        print(f'{fname}: {len(rows)} rows')

print(f'\nTotal unique military pilots (not in core 73): {total_unique}')
print(f'Core 73: 73')
print(f'Grand total unique people: {73 + total_unique}')
