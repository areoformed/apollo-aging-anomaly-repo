#!/usr/bin/env python3
"""
Update Mort / cause note fields with verified causes from research agent.

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-19T09:47:42Z (line 2131)
What it does: Applies verified cause-of-death strings to 07E (lunar) and 03E (control)
              enriched TSV files. Research agent had verified these from Wikipedia, obituaries,
              and family statements.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "Final - Analysis - Enriched Datasets"

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
    print(f"{label}: {updated} Mort / cause note fields updated\n")

print("Updating 07E...")
update_file(DATASET_DIR / '07E-lunar-enriched.tsv', mort_updates_07e, '07E')

print("Updating 03E...")
update_file(DATASET_DIR / '03E-non-apollo-enriched.tsv', mort_updates_03e, '03E')
