#!/usr/bin/env python3
"""Space Grandpa denominator breakdown by group -- visibility bias analysis.
Source: Session 8ed732b6 (May 19, 2026), line 3361.
Breaks down each group into: definitive Y, died-before-80 (definitive N),
living-under-80, and lived-past-80-but-N (uncertain, possible visibility bias).
"""

import csv
from datetime import datetime, date
import os

os.chdir("./Claude Compiled Data")

today = date(2026, 5, 19)

def parse_date(s):
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except:
        return None

def age_years(born, ref):
    return (ref - born).days / 365.25

files = {
    'Lunar (07E)': '07E-lunar-enriched.tsv',
    'Non-lunar Apollo (08E)': '08E-non-lunar-apollo-enriched.tsv',
    'Non-Apollo control (03E)': '03E-non-apollo-enriched.tsv'
}

for group_name, fname in files.items():
    print(f'=== {group_name} ===')
    definitive_y = []
    definitive_n_died_young = []
    definitive_n_living_young = []
    uncertain_n = []

    with open(fname, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        for row in reader:
            if len(row) < 23:
                continue
            name = row[0]
            dob = parse_date(row[2])
            dod = parse_date(row[10])
            status = row[12].strip()
            sg = row[15].strip()

            if not dob:
                continue

            if dod:
                age_at_death = age_years(dob, dod)
            else:
                age_at_death = None

            current_age = age_years(dob, today)

            if sg == 'Y':
                definitive_y.append((name, current_age, age_at_death, status))
            elif sg == 'N':
                if dod and age_at_death < 80:
                    definitive_n_died_young.append((name, age_at_death))
                elif not dod and current_age < 80:
                    definitive_n_living_young.append((name, current_age))
                elif (dod and age_at_death >= 80) or (not dod and current_age >= 80):
                    actual_age = age_at_death if dod else current_age
                    uncertain_n.append((name, actual_age, 'deceased' if dod else 'living'))

    print(f'  SG=Y (definitive): {len(definitive_y)}')
    for n, ca, aad, s in definitive_y:
        age_str = f'died {aad:.0f}' if aad else f'living {ca:.0f}'
        print(f'    {n} ({age_str})')

    print(f'  SG=N, died before 80 (definitive N): {len(definitive_n_died_young)}')
    for n, a in definitive_n_died_young:
        print(f'    {n} (died {a:.0f})')

    print(f'  SG=N, living under 80 (not yet classifiable): {len(definitive_n_living_young)}')
    print(f'  SG=N, reached 80+ (UNCERTAIN -- visibility bias?): {len(uncertain_n)}')
    for n, a, s in uncertain_n:
        print(f'    {n} ({s}, age {a:.0f})')

    reached_80 = len(definitive_y) + len(uncertain_n)
    if reached_80 > 0:
        print(f'  --- Reached 80+: {reached_80} total. SG=Y: {len(definitive_y)}/{reached_80} = {len(definitive_y)/reached_80*100:.0f}%')
    print()
