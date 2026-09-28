#!/usr/bin/env python3
"""Compute median and mean ages for all 24 lunar astronauts.
Source: Session 8ed732b6 (May 19-20, 2026), line 3818.
Breaks down into all-24, deceased-only, and living subsets.
Also counts astronauts who reached 80+.
"""

import csv, datetime, os

os.chdir("./Claude Compiled Data")

today = datetime.date(2026, 5, 20)

with open('07E-lunar-enriched.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

ages = []
deceased_ages = []
living_ages = []

for r in rows:
    dob = datetime.date.fromisoformat(r['Date of Birth'])
    name = r['Name']
    if r['Status'] == 'Deceased':
        dod = datetime.date.fromisoformat(r['Date of Death'])
        age = (dod - dob).days / 365.25
        deceased_ages.append((name, age))
    else:
        age = (today - dob).days / 365.25
        living_ages.append((name, age))
    ages.append((name, age, r['Status']))

all_sorted = sorted(ages, key=lambda x: x[1])
dec_sorted = sorted(deceased_ages, key=lambda x: x[1])

print('=== ALL 24 (current age for living, age at death for deceased) ===')
for name, age, status in all_sorted:
    marker = ' [LIVING]' if status == 'Living' else ''
    print(f'  {name}: {age:.1f}{marker}')

all_vals = sorted([a[1] for a in ages])
n = len(all_vals)
if n % 2 == 0:
    median = (all_vals[n//2 - 1] + all_vals[n//2]) / 2
else:
    median = all_vals[n//2]
print(f'\nMedian (all 24): {median:.1f}')
print(f'Mean (all 24): {sum(all_vals)/len(all_vals):.1f}')

print(f'\n=== DECEASED ONLY ({len(dec_sorted)}) ===')
for name, age in dec_sorted:
    print(f'  {name}: {age:.1f}')

dec_vals = sorted([a[1] for a in deceased_ages])
n2 = len(dec_vals)
if n2 % 2 == 0:
    dec_median = (dec_vals[n2//2 - 1] + dec_vals[n2//2]) / 2
else:
    dec_median = dec_vals[n2//2]
print(f'\nMedian (deceased only, n={n2}): {dec_median:.1f}')
print(f'Mean (deceased only): {sum(dec_vals)/len(dec_vals):.1f}')

print(f'\n=== LIVING ({len(living_ages)}) ===')
for name, age in sorted(living_ages, key=lambda x: x[1]):
    print(f'  {name}: {age:.1f}')

over_80 = [a for a in ages if a[1] >= 80]
print(f'\nReached 80+: {len(over_80)}/24')
for name, age, status in sorted(over_80, key=lambda x: x[1]):
    marker = ' [LIVING]' if status == 'Living' else ''
    print(f'  {name}: {age:.1f}{marker}')
