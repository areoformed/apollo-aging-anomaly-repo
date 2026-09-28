#!/usr/bin/env python3
"""
Build Lists 1-5 from cached Wikipedia astronaut summary files (v2 -- PRODUCTION).

Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
Timestamp: 2026-05-19T02:47:47Z (line 1521 / 2996)
What it does: Same as v1 but fixes Apollo classification bugs by using FILENAME matching
              instead of name-string matching. Also uses explicit filename sets for
              flew/never-flew classification instead of heuristic content parsing.

Key improvement over v1:
  - apollo_7_17_files: set of filenames for reliable Apollo crew identification
  - flew_to_space_files: explicit set of non-Apollo astronauts who flew
  - never_flew_non_apollo: explicit set of astronauts who never flew
  - UNKNOWN status flagged for manual review instead of silent misclassification

Produces: Lists 01 through 05 as TSV files.
"""

import os, re, glob

cache_dir = "./Claude Compiled Data/Cached Pages/wiki-individual"
out_dir = "./Claude Compiled Data"

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

# Apollo 7-17 crew by FILENAME (reliable, no name-matching bugs)
apollo_7_17_files = {
    # Apollo 7
    "schirra-wally.md", "eisele-donn.md", "cunningham-walter.md",
    # Apollo 8
    "borman-frank.md", "lovell-jim.md", "anders-william.md",
    # Apollo 9
    "mcdivitt-james.md", "scott-david.md", "schweickart-russell.md",
    # Apollo 10 (Stafford, Young, Cernan -- also flew later lunar missions)
    "stafford-thomas.md", "young-john.md", "cernan-eugene.md",
    # Apollo 11
    "armstrong-neil.md", "collins-michael.md", "aldrin-buzz.md",
    # Apollo 12
    "conrad-pete.md", "gordon-richard.md", "bean-alan.md",
    # Apollo 13 (Lovell already listed)
    "swigert-jack.md", "haise-fred.md",
    # Apollo 14
    "shepard-alan.md", "roosa-stuart.md", "mitchell-edgar.md",
    # Apollo 15 (Scott already listed)
    "worden-alfred.md", "irwin-james.md",
    # Apollo 16 (Young already listed)
    "mattingly-ken.md", "duke-charles.md",
    # Apollo 17 (Cernan already listed)
    "evans-ronald.md", "schmitt-harrison.md",
}

# Known spaceflight astronauts among non-Apollo (by filename)
flew_to_space_files = {
    # Mercury/Gemini veterans not on Apollo 7-17
    "carpenter-scott.md",   # Mercury-Atlas 7
    "cooper-gordon.md",     # Mercury-Atlas 9, Gemini 5
    "glenn-john.md",        # Mercury-Atlas 6, STS-95
    "grissom-gus.md",       # Mercury-Redstone 4, Gemini 3
    "slayton-deke.md",      # ASTP
    "white-ed.md",          # Gemini 4
    # Group 4
    "garriott-owen.md",     # Skylab 3, STS-9
    "gibson-edward.md",     # Skylab 4
    "kerwin-joseph.md",     # Skylab 2
    # Group 5 non-Apollo
    "brand-vance.md",       # ASTP, STS-5, STS-41-B, STS-35
    "carr-gerald.md",       # Skylab 4
    "engle-joseph.md",      # STS-2, STS-51-I (also X-15)
    "lind-don.md",          # STS-51-B
    "lousma-jack.md",       # Skylab 3, STS-3
    "mccandless-bruce.md",  # STS-41-B, STS-31
    "pogue-william.md",     # Skylab 4
    "weitz-paul.md",        # Skylab 2, STS-6
    # Group 6
    "allen-joseph.md",      # STS-5, STS-51-A
    "england-anthony.md",   # STS-51-F
    "henize-karl.md",       # STS-51-F
    "lenoir-william.md",    # STS-5
    "musgrave-story.md",    # STS-6, STS-51-F, STS-33, STS-44, STS-61, STS-80
    "parker-robert.md",     # STS-9, STS-35
    "thornton-william.md",  # STS-8, STS-51-B
    # Group 7 -- all flew Shuttle
    "bobko-karol.md",       # STS-6, STS-51-D, STS-51-J
    "crippen-robert.md",    # STS-1, STS-7, STS-41-C, STS-41-G
    "fullerton-gordon.md",  # STS-3, STS-51-F
    "hartsfield-henry.md",  # STS-4, STS-41-D, STS-61-A
    "overmyer-robert.md",   # STS-5, STS-51-B
    "peterson-donald.md",   # STS-6
    "truly-richard.md",     # STS-2, STS-8
}

# Never flew to space (among non-Apollo)
never_flew_non_apollo = {
    "bassett-charles.md",    # Died T-38 crash 1966
    "chaffee-roger.md",      # Died Apollo 1 fire -- never flew to space
    "freeman-theodore.md",   # Died T-38 crash 1964
    "williams-clifton.md",   # Died T-38 crash 1967
    "see-elliot.md",         # Died T-38 crash 1966
    "givens-edward.md",      # Died car accident 1967
    "bull-john.md",          # Medical disqualification
    "graveline-duane.md",    # Resigned 1965
    "michel-curt.md",        # Resigned 1969
    "holmquest-donald.md",   # Resigned 1973, never flew
    "llewellyn-anthony.md",  # Resigned 1968
    "oleary-brian.md",       # Resigned 1968
    "chapman-philip.md",     # Resigned 1972, never flew
}

months = {"January":"01","February":"02","March":"03","April":"04","May":"05","June":"06",
          "July":"07","August":"08","September":"09","October":"10","November":"11","December":"12"}

def parse_date(text):
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
    group_num = ""
    for line in content.split('\n'):
        if line.startswith("Astronaut Group:"):
            m = re.search(r'(\d)', line)
            if m:
                group_num = m.group(1)
            break

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

    # Determine Apollo status by filename
    is_apollo = fname in apollo_7_17_files

    # Determine flew status by filename
    if is_apollo:
        flew = "Y"
    elif fname in flew_to_space_files:
        flew = "Y"
    elif fname in never_flew_non_apollo:
        flew = "N"
    else:
        flew = "UNKNOWN"  # Flag for manual review

    # Extract missions from content
    missions = []
    mission_pattern = r'((?:Mercury|Gemini|Apollo|Skylab|STS|Apollo.Soyuz)[\s\-][\w\-/]+)'
    found = re.findall(mission_pattern, content)
    if found:
        seen_missions = []
        for m in found:
            m_clean = m.strip().rstrip('.,;:')
            if m_clean not in seen_missions:
                seen_missions.append(m_clean)
        missions = seen_missions
    missions_str = "; ".join(missions[:10]) if missions else ("None" if flew == "N" else "unknown")

    group_name = group_names.get(group_num, f"Group {group_num}")
    sel_date = group_selection_dates.get(group_num, "")

    astronauts.append({
        "name": full_name,
        "group": group_name,
        "group_num": group_num,
        "dob": dob,
        "selection_date": sel_date,
        "flew": flew,
        "missions": missions_str,
        "is_apollo": is_apollo,
        "file": fname,
    })

# Write all lists
header = "Name\tAstronaut Group\tDate of Birth\tDate of Selection\tWent to Space\tMissions Flown\n"

def write_list(filename, data):
    with open(os.path.join(out_dir, filename), 'w') as f:
        f.write(header)
        for a in data:
            f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

# List 1: all
write_list("01-all-pre-1970-astronauts.tsv", astronauts)

# List 2: deduplicated
seen = {}
deduped = []
for a in astronauts:
    key = a['file']
    if key not in seen:
        seen[key] = True
        deduped.append(a)
write_list("02-deduplicated-pre-1970.tsv", deduped)

# List 3: non-Apollo
non_apollo = [a for a in deduped if not a['is_apollo']]
write_list("03-non-apollo-astronauts.tsv", non_apollo)

# List 4: non-Apollo, flew
non_apollo_flew = [a for a in non_apollo if a['flew'] == 'Y']
write_list("04-non-apollo-flew.tsv", non_apollo_flew)

# List 5: non-Apollo, never flew
non_apollo_never = [a for a in non_apollo if a['flew'] == 'N']
write_list("05-non-apollo-never-flew.tsv", non_apollo_never)

# Summary
print(f"List #1: {len(astronauts)}")
print(f"List #2: {len(deduped)}")
print(f"List #3: {len(non_apollo)}")
print(f"List #4: {len(non_apollo_flew)} (flew)")
print(f"List #5: {len(non_apollo_never)} (never flew)")
print(f"#4 + #5 = {len(non_apollo_flew) + len(non_apollo_never)} (should = #3: {len(non_apollo)})")
print(f"Apollo 7-17: {len([a for a in deduped if a['is_apollo']])}")

# Check for UNKNOWN flew status
unknowns = [a for a in non_apollo if a['flew'] == 'UNKNOWN']
if unknowns:
    print(f"\nWARNING: {len(unknowns)} astronauts with UNKNOWN flew status:")
    for a in unknowns:
        print(f"  {a['name']} ({a['file']})")

# Verify Apollo crew
print(f"\nApollo 7-17 ({len([a for a in deduped if a['is_apollo']])} crew):")
for a in sorted([a for a in deduped if a['is_apollo']], key=lambda x: x['name']):
    print(f"  {a['name']}")
