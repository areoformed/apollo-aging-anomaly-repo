#!/usr/bin/env python3
"""Reconstruct accidentally removed rows for Robert White and Henry Gordon.
Source: Session 8ed732b6 (May 19, 2026), line 3591.
The dedup script over-removed: White (X-15) matched the core-73 "Ed White" surname,
and Gordon (Dyna-Soar) matched "Richard Gordon". This script adds them back with
manually verified data and removes Dyna-Soar pilots who are already in X-15.
Also runs final cross-file duplicate verification.
"""

import csv, os

os.chdir("./Claude Compiled Data")

def read_tsv(fname):
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        rows = list(reader)
    return header, rows

# Robert White row (from cached wiki page)
white_row = [
    "Robert Michael White", "X-15 Research Pilot", "1924-07-06", "1958-01-01",
    "33.5", "Y", "N", "X-15 (16 flights)", "16", "unknown",
    "2010-03-17", "85.7", "Deceased", "N", "Age-related causes",
    "Y", "National Aviation Hall of Fame induction at 82 (2006)",
    "USAF, Major General", "Test pilot, WWII/Korea fighter pilot",
    "BS Electrical Engineering NYU; MBA George Washington",
    "Vietnam combat (Air Force Cross), F-15 program manager, AFFTC Commander, retired 1981",
    "1924", "https://en.wikipedia.org/wiki/Robert_Michael_White"
]

# Henry Gordon row (from cached wiki page)
gordon_row = [
    "Henry Charles Gordon", "X-20 Dyna-Soar Pilot", "1925-12-23", "1960-04-01",
    "34.3", "N", "N", "None (Dyna-Soar cancelled before flight)", "0", "",
    "1996-09-24", "70.8", "Deceased", "N", "unknown",
    "N", "", "USAF, Colonel", "Test pilot, Korea/Vietnam combat pilot",
    "BS Aeronautical Engineering Purdue; MBA USC", "unknown",
    "1925", "https://en.wikipedia.org/wiki/Henry_Charles_Gordon"
]

# Fix 09 (X-15): add White back
h09, r09 = read_tsv('09-x15-pilots-enriched.tsv')
r09.append(white_row)

# Fix 10 (Dyna-Soar): add Gordon back, remove Dana/Knight/Thompson (in X-15)
h10, r10 = read_tsv('10-dyna-soar-pilots-enriched.tsv')
x15_names = {r[0].strip() for r in r09}
r10_deduped = [r for r in r10 if r[0].strip() not in x15_names]
r10_deduped.append(gordon_row)

def write_tsv(fname, header, rows):
    with open(fname, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

write_tsv('09-x15-pilots-enriched.tsv', h09, r09)
write_tsv('10-dyna-soar-pilots-enriched.tsv', h10, r10_deduped)

# Final duplicate verification across all 6 files
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
