#!/usr/bin/env python3
"""
Build Lists 1-5 from cached Wikipedia astronaut summary files (v1).

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-19T02:44:48Z (line 1517 / 2992)
What it does: Reads .md cached Wikipedia summaries from wiki-individual/,
              extracts astronaut metadata (name, group, DOB, missions, flew status),
              classifies each as Apollo 7-17 crew or non-Apollo using name matching,
              and writes 5 TSV lists:
                01-all-pre-1970-astronauts.tsv
                02-deduplicated-pre-1970.tsv
                03-non-apollo-astronauts.tsv
                04-non-apollo-flew.tsv
                05-non-apollo-never-flew.tsv

Status: SUPERSEDED by build_lists_v2.py (name-matching had bugs; v2 uses filename matching)
"""

import os, re, glob

cache_dir = "./Claude Compiled Data/Cached Pages/wiki-individual"
out_dir = "./Claude Compiled Data"

# Group metadata
group_names = {
    "1": "Group 1 — Mercury Seven",
    "2": "Group 2 — The New Nine",
    "3": "Group 3 — The Fourteen",
    "4": "Group 4 — The Scientists",
    "5": "Group 5",
    "6": "Group 6 — The Excess Eleven",
    "7": "Group 7 — MOL Transfer",
}

group_selection_dates = {
    "1": "1959-04-09",
    "2": "1962-09-17",
    "3": "1963-10-17",
    "4": "1965-06-28",
    "5": "1966-04-04",
    "6": "1967-08-04",
    "7": "1969-08-14",
}

# Apollo 7-17 crew (unique names, canonical forms)
apollo_crew = {
    "Wally Schirra", "Donn Eisele", "Walter Cunningham",
    "Frank Borman", "Jim Lovell", "William Anders",
    "James McDivitt", "David Scott", "Russell Schweickart",
    "Tom Stafford", "John Young", "Eugene Cernan",
    "Neil Armstrong", "Michael Collins", "Buzz Aldrin",
    "Pete Conrad", "Richard Gordon", "Alan Bean",
    "Jack Swigert", "Fred Haise",
    "Alan Shepard", "Stuart Roosa", "Edgar Mitchell",
    "Alfred Worden", "James Irwin",
    "Ken Mattingly", "Charles Duke",
    "Ronald Evans", "Harrison Schmitt",
}

# Month name to number
months = {"January":"01","February":"02","March":"03","April":"04","May":"05","June":"06",
          "July":"07","August":"08","September":"09","October":"10","November":"11","December":"12"}

def parse_date(text):
    """Try to parse 'August 5, 1930' or similar into YYYY-MM-DD"""
    if not text:
        return ""
    for mname, mnum in months.items():
        if mname in text:
            m = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', text)
            if m:
                return f"{m.group(3)}-{mnum}-{int(m.group(2)):02d}"
    return text.strip()

def extract_field(content, field_name):
    pattern = r'\*\*' + re.escape(field_name) + r':\*\*\s*(.*)'
    m = re.search(pattern, content)
    return m.group(1).strip() if m else ""

astronauts = []

for filepath in sorted(glob.glob(os.path.join(cache_dir, "*.md"))):
    with open(filepath, 'r') as f:
        content = f.read()

    fname = os.path.basename(filepath)

    # Extract group number
    group_line = ""
    for line in content.split('\n'):
        if line.startswith("Astronaut Group:"):
            group_line = line
            break

    group_num = ""
    if group_line:
        m = re.search(r'(\d)', group_line)
        if m:
            group_num = m.group(1)

    # Extract name
    full_name = extract_field(content, "Full Name")
    if not full_name:
        for line in content.split('\n'):
            if line.startswith('# '):
                full_name = line.lstrip('# ').split(':')[0].split(' - ')[0].strip()
                break

    # Extract DOB
    dob_raw = extract_field(content, "Date of Birth")
    dob = parse_date(dob_raw)

    # Extract missions
    missions_raw = ""
    for line in content.split('\n'):
        if 'Missions' in line and ('flown' in line.lower() or 'flew' in line.lower() or ':' in line):
            missions_raw = line.split(':', 1)[-1].strip() if ':' in line else ""

    if not missions_raw:
        m = re.search(r'(?:Missions?\s*(?:Flown|:))\s*[:\-]?\s*(.*?)(?:\n\n|\n\*\*|\n#)', content, re.IGNORECASE)
        if m:
            missions_raw = m.group(1).strip()

    if not missions_raw:
        m = re.search(r'(?:Space ?flights?|NASA Career|Missions)', content, re.IGNORECASE)
        if m:
            section_start = m.start()
            section = content[section_start:section_start+2000]
            mission_names = re.findall(r'(?:Mercury|Gemini|Apollo|Skylab|STS|Apollo.Soyuz)[\s\-][\w\-]+', section)
            if mission_names:
                missions_raw = ", ".join(dict.fromkeys(mission_names))

    if not missions_raw:
        missions_raw = "None"

    missions_raw = missions_raw.replace('**', '').strip()
    if missions_raw.startswith('-'):
        missions_raw = missions_raw.lstrip('- ')

    # Determine if flew to space
    flew = "N"
    never_flew_indicators = ["did not fly", "never flew", "no spaceflights", "resigned", "killed before", "none"]
    content_lower = content.lower()

    has_mission = bool(re.search(r'(?:Mercury|Gemini|Apollo|Skylab|STS|Spacelab|Apollo.Soyuz)', missions_raw))
    if has_mission and missions_raw != "None":
        flew = "Y"

    for indicator in never_flew_indicators:
        if indicator in content_lower[:3000]:
            if not has_mission:
                flew = "N"

    death_raw = extract_field(content, "Date of Death")
    cause = extract_field(content, "Cause of Death")
    if cause and any(x in cause.lower() for x in ["apollo 1", "t-38", "training", "car accident"]):
        if not has_mission or missions_raw == "None":
            flew = "N"

    # Determine if Apollo 7-17 crew (name matching -- has bugs, see v2)
    is_apollo = False
    simple_name = full_name.split('"')[-1].strip() if '"' in full_name else full_name

    for ac in apollo_crew:
        ac_parts = ac.split()
        name_parts = simple_name.split()
        if len(ac_parts) >= 2 and len(name_parts) >= 2:
            if ac_parts[-1].lower() == name_parts[-1].lower():
                is_apollo = True
                break
            if len(name_parts) >= 3 and ac_parts[-1].lower() == name_parts[-2].lower():
                is_apollo = True
                break

    # Manual overrides for tricky name matches
    name_lower = full_name.lower()
    if "grissom" in name_lower:
        is_apollo = False
    if "white" in name_lower and "edward" in name_lower:
        is_apollo = False
    if "chaffee" in name_lower:
        is_apollo = False
    for dead_early in ["freeman", "bassett", "see", "williams", "givens"]:
        if dead_early in name_lower:
            is_apollo = False
    if "slayton" in name_lower:
        is_apollo = False

    group_name = group_names.get(group_num, f"Group {group_num}")
    sel_date = group_selection_dates.get(group_num, "")

    astronauts.append({
        "name": full_name,
        "group": group_name,
        "group_num": group_num,
        "dob": dob,
        "selection_date": sel_date,
        "flew": flew,
        "missions": missions_raw,
        "is_apollo_7_17": is_apollo,
        "file": fname,
    })

# Write List #1
header = "Name\tAstronaut Group\tDate of Birth\tDate of Selection\tWent to Space\tMissions Flown\n"

with open(os.path.join(out_dir, "01-all-pre-1970-astronauts.tsv"), 'w') as f:
    f.write(header)
    for a in astronauts:
        f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# List #2 -- deduplicated
seen = {}
deduped = []
for a in astronauts:
    key = a['name'].lower()
    if key not in seen:
        seen[key] = a
        deduped.append(a)

with open(os.path.join(out_dir, "02-deduplicated-pre-1970.tsv"), 'w') as f:
    f.write(header)
    for a in deduped:
        f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# List #3 -- non-Apollo
non_apollo = [a for a in deduped if not a['is_apollo_7_17']]
with open(os.path.join(out_dir, "03-non-apollo-astronauts.tsv"), 'w') as f:
    f.write(header)
    for a in non_apollo:
        f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# List #4 -- non-Apollo who flew
non_apollo_flew = [a for a in non_apollo if a['flew'] == 'Y']
with open(os.path.join(out_dir, "04-non-apollo-flew.tsv"), 'w') as f:
    f.write(header)
    for a in non_apollo_flew:
        f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# List #5 -- non-Apollo who never flew
non_apollo_never = [a for a in non_apollo if a['flew'] == 'N']
with open(os.path.join(out_dir, "05-non-apollo-never-flew.tsv"), 'w') as f:
    f.write(header)
    for a in non_apollo_never:
        f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# Print summary
print(f"List #1: {len(astronauts)} astronauts")
print(f"List #2: {len(deduped)} (deduplicated)")
print(f"List #3: {len(non_apollo)} (non-Apollo)")
print(f"List #4: {len(non_apollo_flew)} (non-Apollo, flew)")
print(f"List #5: {len(non_apollo_never)} (non-Apollo, never flew)")
print(f"Verify: #4 + #5 = {len(non_apollo_flew) + len(non_apollo_never)} (should equal #3: {len(non_apollo)})")
print(f"Apollo 7-17 crew identified: {len([a for a in deduped if a['is_apollo_7_17']])}")

print("\nApollo 7-17 crew identified:")
for a in deduped:
    if a['is_apollo_7_17']:
        print(f"  {a['name']} ({a['group']})")

print("\nNon-Apollo astronauts:")
for a in non_apollo:
    print(f"  {a['name']} ({a['group']}) -- flew: {a['flew']}")
