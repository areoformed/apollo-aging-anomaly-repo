#!/usr/bin/env python3
"""Phase 5: Update Mort fields with verified causes of death from obituary research.
Source: Session 8ed732b6 (May 19, 2026), line 2132.
Applied after deep verification (searching obituaries, NASA announcements, news archives)
for 11 astronauts with missing or vague cause of death.
"""

import os

os.chdir("./Claude Compiled Data")

mort_updates_07e = {
    "Eugene Cernan": "Ongoing health issues (family statement; no specific diagnosis disclosed)",
    "Jim Lovell": "Complications of hip fracture from fall; cardiovascular disease contributing",
    "Ken Mattingly": "Not publicly disclosed",
    "Edgar Mitchell": "Kidney cancer (renal carcinoma)",
}

mort_updates_03e = {
    "Gerald Paul Carr": "Brief illness (not further specified)",
    "Owen Kay Garriott": "Heart attack while hospitalized for broken neck from fall",
    "John Herschel Glenn Jr.": "Not publicly disclosed (prior stroke, heart valve replacement surgery)",
    "Bruce McCandless II": "Not publicly disclosed",
    "William Edgar Thornton": "Not publicly disclosed",
    "Richard Harrison Truly": "Complications of atypical Parkinson's disease",
}

def update_file(path, updates, label):
    with open(path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    header = lines[0]
    fixed_lines = [header]
    updated = 0

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split('\t')
        name = fields[0]
        if name in updates:
            old_mort = fields[14]
            fields[14] = updates[name]
            updated += 1
            print(f"  {name}: '{old_mort}' -> '{updates[name]}'")
        fixed_lines.append('\t'.join(fields))

    result = '\n'.join(fixed_lines) + '\n'
    with open(path, 'w') as f:
        f.write(result)
    print(f"{label}: {updated} Mort fields updated\n")

print("Updating 07E...")
update_file('07E-lunar-enriched.tsv', mort_updates_07e, '07E')

print("Updating 03E...")
update_file('03E-non-apollo-enriched.tsv', mort_updates_03e, '03E')
