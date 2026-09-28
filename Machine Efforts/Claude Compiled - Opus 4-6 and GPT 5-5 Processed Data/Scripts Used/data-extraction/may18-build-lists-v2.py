#!/usr/bin/env python3
"""V2 Clean-Room Build: Generate Lists 01-05 from cached Wikipedia individual articles.
Source: Session 8ed732b6 (May 18, 2026), line 1522.
This was the production version (v2, corrected name matching via filename sets).

Reads cached .md files from wiki-individual/, classifies Apollo 7-17 crew by filename,
and produces 5 TSV files:
  01-all-pre-1970-astronauts.tsv
  02-deduplicated-pre-1970.tsv
  03-non-apollo-astronauts.tsv
  04-non-apollo-flew.tsv
  05-non-apollo-never-flew.tsv
"""

import os, re, glob

cache_dir = "./Claude Compiled Data/Cached Pages/wiki-individual"
out_dir = "./Claude Compiled Data"

group_names = {
    "1": "Group 1 -- Mercury Seven",
    "2": "Group 2 -- The New Nine",
    "3": "Group 3 -- The Fourteen",
    "4": "Group 4 -- The Scientists",
    "5": "Group 5",
    "6": "Group 6 -- The Excess Eleven",
    "7": "Group 7 -- MOL Transfer",
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
    "carpenter-scott.md", "cooper-gordon.md", "glenn-john.md",
    "grissom-gus.md", "slayton-deke.md", "white-ed.md",
    "garriott-owen.md", "gibson-edward.md", "kerwin-joseph.md",
    "brand-vance.md", "carr-gerald.md", "engle-joseph.md",
    "lind-don.md", "lousma-jack.md", "mccandless-bruce.md",
    "pogue-william.md", "weitz-paul.md",
    "allen-joseph.md", "england-anthony.md", "henize-karl.md",
    "lenoir-william.md", "musgrave-story.md", "parker-robert.md",
    "thornton-william.md",
    "bobko-karol.md", "crippen-robert.md", "fullerton-gordon.md",
    "hartsfield-henry.md", "overmyer-robert.md", "peterson-donald.md",
    "truly-richard.md",
}

never_flew_non_apollo = {
    "bassett-charles.md", "chaffee-roger.md", "freeman-theodore.md",
    "williams-clifton.md", "see-elliot.md", "givens-edward.md",
    "bull-john.md", "graveline-duane.md", "michel-curt.md",
    "holmquest-donald.md", "llewellyn-anthony.md", "oleary-brian.md",
    "chapman-philip.md",
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

    group_num = ""
    for line in content.split('\n'):
        if line.startswith("Astronaut Group:"):
            m = re.search(r'(\d)', line)
            if m:
                group_num = m.group(1)
            break

    full_name = extract_field(content, "Full Name")
    if not full_name:
        for line in content.split('\n'):
            if line.startswith('# '):
                full_name = line.lstrip('# ').split(':')[0].split(' - ')[0].strip()
                break

    dob_raw = extract_field(content, "Date of Birth")
    dob = parse_date(dob_raw)

    is_apollo = fname in apollo_7_17_files

    if is_apollo:
        flew = "Y"
    elif fname in flew_to_space_files:
        flew = "Y"
    elif fname in never_flew_non_apollo:
        flew = "N"
    else:
        flew = "UNKNOWN"

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

header = "Name\tAstronaut Group\tDate of Birth\tDate of Selection\tWent to Space\tMissions Flown\n"

def write_list(filename, data):
    with open(os.path.join(out_dir, filename), 'w') as f:
        f.write(header)
        for a in data:
            f.write(f"{a['name']}\t{a['group']}\t{a['dob']}\t{a['selection_date']}\t{a['flew']}\t{a['missions']}\n")

write_list("01-all-pre-1970-astronauts.tsv", astronauts)

seen = {}
deduped = []
for a in astronauts:
    key = a['file']
    if key not in seen:
        seen[key] = True
        deduped.append(a)
write_list("02-deduplicated-pre-1970.tsv", deduped)

non_apollo = [a for a in deduped if not a['is_apollo']]
write_list("03-non-apollo-astronauts.tsv", non_apollo)

non_apollo_flew = [a for a in non_apollo if a['flew'] == 'Y']
write_list("04-non-apollo-flew.tsv", non_apollo_flew)

non_apollo_never = [a for a in non_apollo if a['flew'] == 'N']
write_list("05-non-apollo-never-flew.tsv", non_apollo_never)

print(f"List #1: {len(astronauts)}")
print(f"List #2: {len(deduped)}")
print(f"List #3: {len(non_apollo)}")
print(f"List #4: {len(non_apollo_flew)} (flew)")
print(f"List #5: {len(non_apollo_never)} (never flew)")
print(f"Apollo 7-17: {len([a for a in deduped if a['is_apollo']])}")
