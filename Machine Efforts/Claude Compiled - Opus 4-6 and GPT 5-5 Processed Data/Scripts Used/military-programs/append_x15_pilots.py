#!/usr/bin/env python3
"""
Append 3 missing high-speed research pilots to the X-15 file.

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-20T07:06:32Z (line 3683)
What it does: After V1-vs-V2 name comparison found 3 missing people,
              this script appends rows for:
  - Alvin Swauger White (XB-70 Valkyrie chief test pilot, died at 87)
  - Iven Carl Kincheloe Jr. (X-2 altitude record holder, killed in F-104 crash at 30)
  - William Barton Bridgeman (D-558-II Skyrocket pilot, killed in plane crash at 52)

Run from the Claude Compiled Data directory.
"""

import csv

# Read existing file
with open('09-x15-pilots-enriched.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    header = next(reader)
    rows = list(reader)

print(f"Before: {len(rows)} rows")

# Three new rows
new_rows = [
    [
        "Alvin Swauger White", "High-Speed Research Pilot", "1918-12-09", "1958-01-01",
        "39.1", "N", "N", "XB-70 Valkyrie (chief test pilot, first flights of both XB-70s, Mach 3)",
        "0", "0", "2006-04-29", "87.4", "Deceased", "N",
        "Cause not specified; died in Tucson at 87", "N",
        "No documented 80+ activity beyond retirement in Tucson",
        "US Army Air Forces, pilot", "WWII P-51 pilot (355th FG), D-Day through V-E Day",
        "BS Mechanical Engineering UC Berkeley 1947",
        "TWA pilot 1966; aviation consultant 1969; retired to Tucson",
        "1918",
        "https://en.wikipedia.org/wiki/Alvin_S._White"
    ],
    [
        "Iven Carl Kincheloe Jr.", "High-Speed Research Pilot", "1928-07-02", "1956-01-01",
        "27.5", "N", "N", "Bell X-2 (altitude record 126,200 ft); selected for X-15 (never flew)",
        "0", "0", "1958-07-26", "30.1", "Deceased", "Y",
        "F-104A crash at Edwards AFB; downward ejection seat at low altitude",
        "N", "",
        "USAF, Captain", "Korean War ace (5 MiG-15 kills), Century Series test pilot",
        "BS Aeronautical Engineering Purdue 1949",
        "Died before X-15 flight; posthumous: Kincheloe AFB named after him",
        "1928",
        "https://en.wikipedia.org/wiki/Iven_C._Kincheloe"
    ],
    [
        "William Barton Bridgeman", "High-Speed Research Pilot", "1916-06-25", "1951-01-01",
        "34.5", "N", "N", "D-558-II Skyrocket (Mach 1.88 speed record; 79,494 ft altitude record)",
        "0", "0", "1968-09-29", "52.3", "Deceased", "Y",
        "Grumman Goose amphibian crash near Catalina Island; body never recovered",
        "N", "",
        "US Navy, pilot", "WWII Navy combat pilot (Pearl Harbor, Pacific)",
        "BS Geology UC",
        "Douglas Aircraft test pilot; Grumman test programs; published memoir The Lonely Sky (1955)",
        "1916",
        "https://en.wikipedia.org/wiki/Bill_Bridgeman"
    ]
]

rows.extend(new_rows)

with open('09-x15-pilots-enriched.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)

print(f"After: {len(rows)} rows")

# Final count across all files
total = 0
for fname in ['07E-lunar-enriched.tsv', '08E-non-lunar-apollo-enriched.tsv', '03E-non-apollo-enriched.tsv',
              '09-x15-pilots-enriched.tsv', '10-dyna-soar-pilots-enriched.tsv', '11-mol-full-enriched.tsv']:
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        rows_f = list(reader)
        total += len(rows_f)
        print(f"  {fname}: {len(rows_f)} rows")

print(f"\nGrand total unique people: {total}")
