#!/usr/bin/env python3
"""Phase 5: Upgrade Space Grandpa classifications after deep web verification.
Source: Session 8ed732b6 (May 19, 2026), line 2141.
Investigated 11 astronauts who lived past 80 but were marked SG=N.
Upgraded 5 (all in control group 03E) based on documented sustained activity at 80+.
Also recalculates SG statistics across all three enriched files.
"""

import os

os.chdir("./Claude Compiled Data")

sg_upgrades = {
    "Jack Robert Lousma": "Multiple speaking events 2017-2023; Skylab 50th anniversary podcast and museum appearances at 87 (2023); Chaffee memorial events at 81-82",
    "Gerald Paul Carr": "Documentary 'The Artist & The Astronaut' interviews ages 84-88 (2016-2020); continued artistic collaboration with wife Pat Musick",
    "Owen Kay Garriott": "U.S. Astronaut Hall of Fame induction at 80 (2011); AOPA Kennedy Space Center event at 86 (2017); active ham radio community",
    "Don Leslie Lind": "LDS Temple presidency service in later years; sustained speaking through age 92; memorial renaming of Astro Camp training area",
    "Frank Curtis Michel": "Active daily research at Rice University through death at 80; published Handbook of High-Energy Astrophysics Experiments at 80; research papers through 2014",
}

path = '03E-non-apollo-enriched.tsv'
with open(path, 'r') as f:
    content = f.read()

lines = content.split('\n')
header = lines[0]
fixed_lines = [header]
upgraded = 0

for line in lines[1:]:
    if not line.strip():
        continue
    fields = line.split('\t')
    name = fields[0]
    if name in sg_upgrades:
        old_sg = fields[15]
        fields[15] = 'Y'
        fields[16] = sg_upgrades[name]
        upgraded += 1
        print(f"  {name}: SG {old_sg} -> Y")
    fixed_lines.append('\t'.join(fields))

result = '\n'.join(fixed_lines) + '\n'
with open(path, 'w') as f:
    f.write(result)

print(f"\n03E: {upgraded} Space Grandpa upgrades applied")

# Recalculate stats
print("\n--- Updated Space Grandpa Counts ---")
for fname, label in [('07E-lunar-enriched.tsv', 'Lunar'), ('08E-non-lunar-apollo-enriched.tsv', 'Non-lunar Apollo'), ('03E-non-apollo-enriched.tsv', 'Control (non-Apollo)')]:
    with open(fname, 'r') as f:
        flines = f.read().strip().split('\n')[1:]
    total = len(flines)
    sg_y = sum(1 for l in flines if l.split('\t')[15] == 'Y')
    pct = (sg_y / total * 100) if total else 0
    print(f"  {label}: {sg_y}/{total} = {pct:.1f}%")
