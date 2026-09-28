#!/usr/bin/env python3
"""
QA fixes for all three core enriched TSV files (07E, 08E, 03E).

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-19T09:47:10Z (line 2119)
What it does:
  - 07E: Fills blank Accidental Death fields with 'N', strips whitespace-only Mort,
          adds trailing newline
  - 08E: Fixes Group 3 selection date (1963-10-17 -> 1963-10-18), fills blank AD with 'N',
          strips Mort whitespace, preserves SG citations/rationales for SG=N astronauts
  - 03E: Fixes Group 3 selection date

Run from the Claude Compiled Data directory.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "Final - Analysis - Enriched Datasets"

def fix_07e():
    path = DATASET_DIR / '07E-lunar-enriched.tsv'
    with open(path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    header = lines[0]
    fixed_lines = [header]
    ad_fixed = 0
    mort_fixed = 0

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split('\t')
        # Column 13 = Accidental Death: blank -> N
        if len(fields) > 13 and fields[13].strip() == '':
            fields[13] = 'N'
            ad_fixed += 1
        # Column 14 = Mort: strip whitespace-only entries
        if len(fields) > 14 and fields[14].strip() == '' and fields[14] != '':
            fields[14] = ''
            mort_fixed += 1
        fixed_lines.append('\t'.join(fields))

    result = '\n'.join(fixed_lines) + '\n'
    with open(path, 'w') as f:
        f.write(result)
    print(f"07E: {ad_fixed} Accidental Death blanks -> N, {mort_fixed} Mort whitespace stripped, trailing newline added")

def fix_08e():
    path = DATASET_DIR / '08E-non-lunar-apollo-enriched.tsv'
    with open(path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    header = lines[0]
    fixed_lines = [header]
    date_fixed = 0
    ad_fixed = 0
    mort_fixed = 0

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split('\t')
        # Group 3 date: 1963-10-17 -> 1963-10-18
        if len(fields) > 3 and fields[3] == '1963-10-17':
            fields[3] = '1963-10-18'
            date_fixed += 1
        # Accidental Death: blank -> N
        if len(fields) > 13 and fields[13].strip() == '':
            fields[13] = 'N'
            ad_fixed += 1
        # Mort: strip whitespace-only
        if len(fields) > 14 and fields[14].strip() == '' and fields[14] != '':
            fields[14] = ''
            mort_fixed += 1
        fixed_lines.append('\t'.join(fields))

    result = '\n'.join(fixed_lines) + '\n'
    with open(path, 'w') as f:
        f.write(result)
    print(f"08E: {date_fixed} Group 3 dates fixed, {ad_fixed} AD blanks -> N, {mort_fixed} Mort whitespace stripped")

def fix_03e():
    path = DATASET_DIR / '03E-non-apollo-enriched.tsv'
    with open(path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    header = lines[0]
    fixed_lines = [header]
    date_fixed = 0

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split('\t')
        # Group 3 date: 1963-10-17 -> 1963-10-18
        if len(fields) > 3 and fields[3] == '1963-10-17':
            fields[3] = '1963-10-18'
            date_fixed += 1
        fixed_lines.append('\t'.join(fields))

    result = '\n'.join(fixed_lines) + '\n'
    with open(path, 'w') as f:
        f.write(result)
    print(f"03E: {date_fixed} Group 3 dates fixed")

fix_07e()
fix_08e()
fix_03e()
print("\nAll QA fixes applied.")
