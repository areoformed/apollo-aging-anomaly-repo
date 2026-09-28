#!/usr/bin/env python3
"""Step 2 (V1): Extract structured data from cached Wikipedia articles into a TSV dataset.
Source: V1 pipeline, <workspace>/projects/apollo-aging-anomaly/02_extract_dataset.py
Conversation: early build (pre-May 18), projects/apollo-aging-anomaly/

Reads articles from wiki-articles/ folder (produced by 01_fetch_articles.py).
Uses curated lists for accidental deaths and moonwalkers rather than fragile text heuristics.
This is the V1 extractor -- superseded by the V2 clean-room build on May 18.
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

from bs4 import BeautifulSoup

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_TSV = PROJECT_DIR / "us-astronaut-groups-1-7.tsv"
CACHE_DIR = PROJECT_DIR / "wiki-articles"
OUTPUT_TSV = PROJECT_DIR / "astronaut-dataset.tsv"

TODAY = date(2026, 4, 23)

MOON_WALKERS = {
    "Neil Armstrong", "Buzz Aldrin", "Pete Conrad", "Alan Bean",
    "Alan Shepard", "Edgar Mitchell", "David Scott", "James Irwin",
    "John Young", "Charles Duke", "Eugene Cernan", "Harrison Schmitt",
}

BEYOND_LEO = MOON_WALKERS | {
    "Frank Borman", "Jim Lovell", "William Anders",
    "Thomas P. Stafford",
    "Michael Collins",
    "Richard F. Gordon Jr.",
    "Fred Haise", "Jack Swigert",
    "Al Worden",
    "Ken Mattingly",
    "Ronald Evans",
    "Stuart Roosa",
}

ACCIDENTAL_DEATHS = {
    "Iven C. Kincheloe": "F-104 crash",
    "Joseph A. Walker": "mid-air collision (XB-70/F-104)",
    "Michael J. Adams": "X-15 crash (Flight 191)",
    "Russell L. Rogers": "F-105 crash",
    "Gus Grissom": "Apollo 1 fire",
    "Ed White": "Apollo 1 fire",
    "Roger Chaffee": "Apollo 1 fire",
    "Theodore Freeman": "T-38 crash (bird strike)",
    "Elliot See": "T-38 crash",
    "Charles Bassett": "T-38 crash",
    "Clifton Williams": "T-38 crash",
    "Edward Givens": "automobile accident",
    "Robert H. Lawrence Jr.": "F-104 crash",
    "Robert Overmyer": "aircraft crash (aerobatics)",
    "Scott Crossfield": "private plane crash",
    "William Anders": "private plane crash",
    "Pete Conrad": "motorcycle accident",
}

KNOWN_OVERRIDES = {
    "Jack Swigert":       {"dob": date(1931, 8, 30), "dod": date(1982, 12, 27), "cause": "cancer (bone marrow)"},
    "Clifton Williams":   {"dob": date(1932, 9, 26), "dod": date(1967, 10, 5),  "cause": "T-38 crash"},
    "Edward Gibson":      {"dob": date(1936, 11, 8)},
    "Joseph Kerwin":      {"dob": date(1932, 2, 19)},
    "John S. Bull":       {"dob": date(1934, 9, 25), "dod": date(2008, 8, 11)},
    "Paul Weitz":         {"dob": date(1932, 7, 25), "dod": date(2017, 10, 22)},
    "James M. Taylor":    {"dob": date(1930, 3, 10)},
    "Donald Peterson":    {"dob": date(1933, 10, 22), "dod": date(2018, 5, 27)},
    "Philip Chapman":     {"dob": date(1935, 3, 5),  "dod": date(2021, 12, 5)},
    "William B. Lenoir":  {"dob": date(1939, 3, 14), "dod": date(2010, 8, 28)},
    "William Thornton":   {"dob": date(1929, 4, 14), "dod": date(2021, 1, 11)},
    "Donald H. Peterson": {"dob": date(1933, 10, 22), "dod": date(2018, 5, 27)},
    "Edward Givens":      {"dob": date(1930, 1, 5),  "dod": date(1967, 6, 6), "cause": "automobile accident"},
    "Donn Eisele":        {"dob": date(1930, 6, 23), "dod": date(1987, 12, 1), "cause": "cardiovascular"},
    "Neil Armstrong":         {"cause": "cardiovascular (bypass surgery complications)"},
    "Gordon Cooper":          {"cause": "cardiovascular (heart failure)"},
    "John Glenn":             {"cause": "cardiovascular (heart valve surgery complications)"},
    "Wally Schirra":          {"cause": "cancer (abdominal) / cardiovascular (heart attack)"},
    "Alan Shepard":           {"cause": "cancer (leukemia)"},
    "Deke Slayton":           {"cause": "cancer (brain)"},
    "Frank Borman":           {"cause": "stroke"},
    "John Young":             {"cause": "respiratory (pneumonia complications)"},
    "Michael Collins":        {"cause": "cancer"},
    "Walter Cunningham":      {"cause": "fall"},
    "Ronald Evans":           {"cause": "cardiovascular (heart attack)"},
    "Stuart Roosa":           {"cause": "pancreatic (pancreatitis)"},
    "Karol J. Bobko":         {"cause": "neurological (degenerative)"},
    "Henry Hartsfield":       {"cause": "surgical complications (back surgery)"},
    "Brian O'Leary":          {"cause": "cancer (intestinal)"},
    "C. Gordon Fullerton":    {"cause": "stroke"},
}


def parse_date(text):
    if not text:
        return None
    text = re.sub(r'\[.*?\]', '', text).strip()
    text = re.sub(r'\(.*?\)', '', text).strip()
    text = re.sub(r'<[^>]+>', '', text).strip()
    for pat, fmt in [
        (r'(\w+ \d{1,2}, \d{4})', '%B %d, %Y'),
        (r'(\d{1,2} \w+ \d{4})', '%d %B %Y'),
        (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
    ]:
        m = re.search(pat, text)
        if m:
            try:
                return datetime.strptime(m.group(1), fmt).date()
            except ValueError:
                continue
    return None


def parse_duration(text):
    if not text:
        return None
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[.*?\]', '', text).strip()
    days = hours = minutes = 0
    for val, unit in re.findall(r'(\d+)\s*([dhm])', text.lower()):
        v = int(val)
        if unit == 'd': days = v
        elif unit == 'h': hours = v
        elif unit == 'm': minutes = v
    if days or hours or minutes:
        return f"{days}d {hours}h {minutes}m"
    m = re.search(r'(\d+)\s*days?', text)
    if m:
        return f"{m.group(1)}d 0h 0m"
    return None


def infobox_field(soup, labels):
    for label in labels:
        for th in soup.find_all(['th', 'td']):
            if label.lower() in th.get_text(strip=True).lower():
                td = th.find_next_sibling('td')
                if td:
                    return td.get_text(separator=' ', strip=True)
    return None


def get_death_section_text(soup):
    for heading in soup.find_all(re.compile(r'^h[23]')):
        ht = heading.get_text().lower()
        if any(w in ht for w in ['death', 'later life', 'final years', 'personal life', 'legacy']):
            parts = []
            for sib in heading.find_next_siblings():
                if sib.name and re.match(r'^h[23]$', sib.name):
                    break
                parts.append(sib.get_text())
            return ' '.join(parts).lower()
    return ''


def extract_cause_from_text(text):
    for pat, cause in [
        (r'cancer|carcinoma|melanoma|leukemia|lymphoma|tumor|glioblastoma|malignant', 'cancer'),
        (r'heart (?:attack|failure|disease)|cardiac arrest|cardiovascular|myocardial|coronary', 'cardiovascular'),
        (r'stroke|cerebrovascular', 'stroke'),
        (r'pneumonia|respiratory failure|pulmonary', 'respiratory'),
        (r'alzheimer|dementia', 'neurological'),
        (r'renal|kidney failure', 'renal'),
        (r'pancreatitis|pancreatic', 'pancreatic'),
        (r'mesothelioma', 'mesothelioma'),
        (r'complications (?:from|of|resulting from) a fall', 'fall'),
    ]:
        if re.search(pat, text):
            return cause
    return None


def is_space_grandpa(name, dob, dod, full_text):
    if not dob:
        return False
    end = dod or TODAY
    age = (end - dob).days / 365.25
    if age < 80:
        return False
    if not dod:
        return True
    grandpa_keywords = [
        'public appearance', 'keynote', 'spoke at', 'speaking',
        'continued to', 'remained active', 'public event',
        'ceremony', 'commemorat', 'anniversary', 'honored',
        'advocate', 'advocacy', 'foundation', 'ambassador',
        'memoir', 'autobiography', 'book tour', 'lecture',
        'commencement', 'interview', 'documentary', 'testified',
        'congressional gold medal', 'presidential medal',
    ]
    count = sum(1 for kw in grandpa_keywords if kw in full_text)
    return count >= 2


def load_article(name, wiki_url):
    title = wiki_url.split("/wiki/")[-1]
    from urllib.parse import unquote
    title = unquote(title)
    filename = re.sub(r'[^\w\-.]', '_', title) + ".json"
    filepath = CACHE_DIR / filename
    if not os.path.exists(filepath):
        return None
    with open(filepath) as f:
        return json.load(f)


def main():
    with open(INPUT_TSV) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        rows = [r for r in reader if len(r) >= 4]

    people = {}
    for row in rows:
        name = row[0]
        if name not in people:
            people[name] = {'name': name, 'groups': [], 'wiki_url': row[3]}
        people[name]['groups'].append({'group': row[1], 'selection_date': row[2]})

    print(f"{len(people)} unique astronauts", file=sys.stderr)

    results = []
    missing_dob = []

    for name, person in people.items():
        article = load_article(name, person['wiki_url'])

        dob = dod = None
        time_in_space = missions = num_flights = military_branch = None
        cause_of_death = None

        if article and article.get('infobox_html'):
            soup = BeautifulSoup(article['infobox_html'], 'html.parser')
            dob = parse_date(infobox_field(soup, ['Born']))
            dod = parse_date(infobox_field(soup, ['Died']))
            time_in_space = parse_duration(infobox_field(soup, ['Time in space']))
            missions_raw = infobox_field(soup, ['Missions', 'Mission'])
            if missions_raw:
                missions = re.sub(r'\[.*?\]', '', missions_raw).strip()
            flights_raw = infobox_field(soup, ['Space flights', 'Spaceflights'])
            if flights_raw:
                m = re.search(r'(\d+)', flights_raw)
                num_flights = int(m.group(1)) if m else None
            branch_raw = infobox_field(soup, ['Branch', 'Branch/service', 'Service'])
            if branch_raw:
                military_branch = re.sub(r'\[.*?\]', '', branch_raw).strip()

        overrides = KNOWN_OVERRIDES.get(name, {})
        if 'dob' in overrides and not dob:
            dob = overrides['dob']
        if 'dod' in overrides and not dod:
            dod = overrides['dod']
        if 'cause' in overrides:
            cause_of_death = overrides['cause']

        if name in ACCIDENTAL_DEATHS:
            cause_of_death = ACCIDENTAL_DEATHS[name]
            accidental = True
        else:
            accidental = False
            if not cause_of_death and dod and article:
                full_soup = BeautifulSoup(article['html'], 'html.parser')
                death_text = get_death_section_text(full_soup)
                if death_text:
                    cause_of_death = extract_cause_from_text(death_text)
                if not cause_of_death:
                    last_text = full_soup.get_text()[-3000:].lower()
                    cause_of_death = extract_cause_from_text(last_text)

        primary_group = None
        for g in person['groups']:
            if 'NASA' in g['group']:
                primary_group = g
                break
        if not primary_group:
            primary_group = person['groups'][-1]

        all_groups = '; '.join(g['group'] for g in person['groups'])

        sel_date = None
        sel_str = primary_group['selection_date']
        for pat, fmt in [(r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'), (r'(\d{4}-\d{2})', '%Y-%m')]:
            m = re.match(pat, sel_str)
            if m:
                try:
                    sel_date = datetime.strptime(m.group(1) + ('-01' if len(m.group(1)) == 7 else ''), '%Y-%m-%d').date()
                except ValueError:
                    pass
                break

        age_at_sel = round((sel_date - dob).days / 365.25, 1) if dob and sel_date else None
        if dob:
            age = round(((dod or TODAY) - dob).days / 365.25, 1)
        else:
            age = None

        status = 'Deceased' if dod else ('Living' if dob else 'Unknown')

        full_text = ''
        if article:
            full_text = BeautifulSoup(article['html'], 'html.parser').get_text().lower()
        space_grandpa = is_space_grandpa(name, dob, dod, full_text)

        if not dob:
            missing_dob.append(name)

        results.append({
            'Name': name,
            'Primary Group': primary_group['group'],
            'All Groups': all_groups,
            'Date of Birth': str(dob) if dob else '',
            'Date of Selection': sel_str,
            'Age at Selection': str(age_at_sel) if age_at_sel else '',
            'Date of Death': str(dod) if dod else '',
            'Age': str(age) if age else '',
            'Status': status,
            'Accidental Death': 'Yes' if accidental else ('No' if dod else ''),
            'Cause of Death': cause_of_death or '',
            'Space Grandpa': 'Yes' if space_grandpa else 'No',
            'Time in Space': time_in_space or '',
            'Number of Flights': str(num_flights) if num_flights else '',
            'Missions': missions or '',
            'Beyond LEO': 'Yes' if name in BEYOND_LEO else 'No',
            'Moonwalker': 'Yes' if name in MOON_WALKERS else 'No',
            'Military Branch': military_branch or '',
            'Wikipedia': person['wiki_url'],
        })

    fieldnames = [
        'Name', 'Primary Group', 'All Groups', 'Date of Birth',
        'Date of Selection', 'Age at Selection', 'Date of Death', 'Age',
        'Status', 'Accidental Death', 'Cause of Death', 'Space Grandpa',
        'Time in Space', 'Number of Flights', 'Missions', 'Beyond LEO',
        'Moonwalker', 'Military Branch', 'Wikipedia',
    ]

    with open(OUTPUT_TSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(results)

    print(f"\nWrote {len(results)} rows to {OUTPUT_TSV}", file=sys.stderr)


if __name__ == '__main__':
    main()
