#!/usr/bin/env python3
"""
Reconstruct accidentally-removed White and Gordon rows, fix cross-overlaps, verify no duplicates.

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-20T06:51:14Z (line 3590)
What it does: After dedup_military_files.py ran, Robert Michael White (X-15) and
              Henry Charles Gordon (Dyna-Soar) were incorrectly removed because their surnames
              matched core-73 members (Ed White, Richard Gordon). This script:
  1. Reconstructs their rows from cached Wikipedia data
  2. Adds White back to 09 (X-15)
  3. Adds Gordon back to 10 (Dyna-Soar), removing Dana/Knight/Thompson (already in X-15)
  4. Verifies no duplicates across all 6 files

Run from the Claude Compiled Data directory.
"""

import csv

# Read current files
def read_tsv(fname):
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        rows = list(reader)
    return header, rows

# Robert White row (from cached wiki page)
white_row = [
    "Robert Michael White",           # Name
    "X-15 Research Pilot",            # Astronaut Group
    "1924-07-06",                     # DOB
    "1958-01-01",                     # Date of Selection (approximate)
    "33.5",                           # Age at Selection
    "Y",                              # Went to Space (59.6 mi = above 50mi USAF threshold)
    "N",                              # Moonwalker
    "X-15 (16 flights)",              # Missions Flown
    "16",                             # Number of Flights
    "unknown",                        # Time in Space
    "2010-03-17",                     # Date of Death
    "85.7",                           # Age at Death
    "Deceased",                       # Status
    "N",                              # Accidental Death
    "Age-related causes",             # Mort
    "Y",                              # Space Grandpa
    "National Aviation Hall of Fame induction at 82 (2006)", # SG Citation
    "USAF, Major General",            # Military Branch
    "Test pilot, WWII/Korea fighter pilot", # Pre-NASA Career
    "BS Electrical Engineering NYU; MBA George Washington", # Education
    "Vietnam combat (Air Force Cross), F-15 program manager, AFFTC Commander, retired 1981", # Post-NASA Career
    "1924",                           # Birth Year
    "https://en.wikipedia.org/wiki/Robert_Michael_White" # Citations
]

# Henry Gordon row (from cached wiki page)
gordon_row = [
    "Henry Charles Gordon",           # Name
    "X-20 Dyna-Soar Pilot",          # Astronaut Group
    "1925-12-23",                     # DOB
    "1960-04-01",                     # Date of Selection (approximate)
    "34.3",                           # Age at Selection
    "N",                              # Went to Space
    "N",                              # Moonwalker
    "None (Dyna-Soar cancelled before flight)", # Missions Flown
    "0",                              # Number of Flights
    "",                               # Time in Space
    "1996-09-24",                     # Date of Death
    "70.8",                           # Age at Death
    "Deceased",                       # Status
    "N",                              # Accidental Death
    "unknown",                        # Mort
    "N",                              # Space Grandpa (died at 70)
    "",                               # SG Citation
    "USAF, Colonel",                  # Military Branch
    "Test pilot, Korea/Vietnam combat pilot", # Pre-NASA Career
    "BS Aeronautical Engineering Purdue; MBA USC", # Education
    "unknown",                        # Post-NASA Career
    "1925",                           # Birth Year
    "https://en.wikipedia.org/wiki/Henry_Charles_Gordon" # Citations
]

# Fix 09 (X-15): add White back
h09, r09 = read_tsv('09-x15-pilots-enriched.tsv')
r09.append(white_row)
# Adams should stay (X-15 is his primary program)

# Fix 10 (Dyna-Soar): add Gordon back, remove Dana/Knight/Thompson (in X-15)
h10, r10 = read_tsv('10-dyna-soar-pilots-enriched.tsv')
x15_names = {r[0].strip() for r in r09}
r10_deduped = [r for r in r10 if r[0].strip() not in x15_names]
r10_deduped.append(gordon_row)

# 11 (MOL) is already correct at 8 rows

# Write back
def write_tsv(fname, header, rows):
    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

write_tsv('09-x15-pilots-enriched.tsv', h09, r09)
write_tsv('10-dyna-soar-pilots-enriched.tsv', h10, r10_deduped)

# Final verification
all_names = set()
dupes = []
for fname in ['07E-lunar-enriched.tsv', '08E-non-lunar-apollo-enriched.tsv', '03E-non-apollo-enriched.tsv',
              '09-x15-pilots-enriched.tsv', '10-dyna-soar-pilots-enriched.tsv', '11-mol-full-enriched.tsv']:
    h, rows = read_tsv(fname)
    names = [r[0].strip() for r in rows]
    for n in names:
        if n in all_names:
            dupes.append(f'DUPLICATE: {n} in {fname}')
        all_names.add(n)
    print(f'{fname}: {len(rows)} rows')

print(f'\nTotal unique people across all 6 files: {len(all_names)}')
if dupes:
    print(f'\nDUPLICATES FOUND:')
    for d in dupes:
        print(f'  {d}')
else:
    print('NO DUPLICATES -- clean dataset.')
