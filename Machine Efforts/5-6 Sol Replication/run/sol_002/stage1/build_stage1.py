#!/usr/bin/env python3
"""Deterministically build and validate the Stage 1 cohort artifacts."""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


OUT = Path(__file__).resolve().parent
CENSOR = date(2026, 6, 1)

NASA_GROUP = "https://www.nasa.gov/wp-content/uploads/2023/09/o57669480.pdf"
NASA_FACTBOOK = "https://www.nasa.gov/reference/astronaut-fact-book/"
APOLLO_ALL = "https://www.nasa.gov/specials/apollo50th/missions.html"
APOLLO1 = "https://www.nasa.gov/missions/apollo/apollo-1/detailed-biographies-of-the-apollo-1-crew/"
X15 = "https://www.nasa.gov/aeronautics/x-15/"
X15_WINGS = "https://www.nasa.gov/news-release/x-15-space-pioneers-now-honored-as-astronauts/"
DYNA = "https://repository.si.edu/bitstreams/43c20435-4d2a-4e72-bc24-4546bc6ef1f3/download"
DYNA_USAF = "https://www.aflcmc.af.mil/Portals/13/DynaSoar.pdf"
MOL = "https://www.nro.gov/news-media-featured-stories/news-media-archive/News-Article/Article/3227331/the-story-of-the-manned-orbiting-laboratory-part-two/"
MOL_NASA = "https://www.nasa.gov/history/55-years-ago-manned-orbiting-laboratory-cancellation/"

MISSION_URLS = {
    "Apollo 7": "https://www.nasa.gov/missions/apollo/about-apollo-7-the-first-crewed-apollo-space-mission/",
    "Apollo 8": "https://www.nasa.gov/missions/apollo/apollo-8-mission-details/",
    "Apollo 9": "https://www.nasa.gov/missions/apollo/apollo-9-mission-details/",
    "Apollo 10": "https://www.nasa.gov/missions/apollo/apollo-10-mission-details/",
    "Apollo 11": "https://www.nasa.gov/missions/apollo/apollo-11-mission-overview/",
    "Apollo 12": "https://www.nasa.gov/missions/apollo/apollo-12-the-pinpoint-mission/",
    "Apollo 13": "https://www.nasa.gov/missions/apollo/apollo-13-mission-details/",
    "Apollo 14": "https://www.nasa.gov/missions/apollo/apollo-14-mission-details/",
    "Apollo 15": "https://www.nasa.gov/missions/apollo/apollo-15-mission-details/",
    "Apollo 16": "https://www.nasa.gov/missions/apollo/apollo-16-mission-details/",
    "Apollo 17": "https://www.nasa.gov/missions/apollo/apollo-17-mission-details/",
}

NASA_SELECTION = {
    1: "1959-04-09",
    2: "1962-09-17",
    3: "1963-10-18",
    4: "1965-06-28",
    5: "1966-04-04",
    6: "1967-08-04",
}

# name ^ birth ^ death ^ first qualifying spaceflight ^ NASA selection group
NASA_ROWS = """
M. Scott Carpenter^1925-05-01^2013-10-10^1962-05-24^1
L. Gordon Cooper Jr.^1927-03-06^2004-10-04^1963-05-15^1
John H. Glenn Jr.^1921-07-18^2016-12-08^1962-02-20^1
Virgil I. "Gus" Grissom^1926-04-03^1967-01-27^1961-07-21^1
Walter M. Schirra Jr.^1923-03-12^2007-05-03^1962-10-03^1
Alan B. Shepard Jr.^1923-11-18^1998-07-21^1961-05-05^1
Donald K. "Deke" Slayton^1924-03-01^1993-06-13^1975-07-15^1
Neil A. Armstrong^1930-08-05^2012-08-25^1966-03-16^2
Frank Borman^1928-03-14^2023-11-07^1965-12-04^2
Charles "Pete" Conrad Jr.^1930-06-02^1999-07-08^1965-08-21^2
James A. Lovell Jr.^1928-03-25^2025-08-07^1965-12-04^2
James A. McDivitt^1929-06-10^2022-10-13^1965-06-03^2
Elliot M. See Jr.^1927-07-23^1966-02-28^^2
Thomas P. Stafford^1930-09-17^2024-03-18^1965-12-15^2
Edward H. White II^1930-11-14^1967-01-27^1965-06-03^2
John W. Young^1930-09-24^2018-01-05^1965-03-23^2
Buzz Aldrin^1930-01-20^^1966-11-11^3
William A. Anders^1933-10-17^2024-06-07^1968-12-21^3
Charles A. Bassett II^1931-12-30^1966-02-28^^3
Alan L. Bean^1932-03-15^2018-05-26^1969-11-14^3
Eugene A. Cernan^1934-03-14^2017-01-16^1966-06-03^3
Roger B. Chaffee^1935-02-15^1967-01-27^^3
Michael Collins^1930-10-31^2021-04-28^1966-07-18^3
R. Walter Cunningham^1932-03-16^2023-01-03^1968-10-11^3
Donn F. Eisele^1930-06-23^1987-12-02^1968-10-11^3
Theodore C. Freeman^1930-02-18^1964-10-31^^3
Richard F. Gordon Jr.^1929-10-05^2017-11-06^1966-09-12^3
Russell L. Schweickart^1935-10-25^^1969-03-03^3
David R. Scott^1932-06-06^^1966-03-16^3
Clifton C. Williams Jr.^1932-09-26^1967-10-05^^3
Owen K. Garriott^1930-11-22^2019-04-15^1973-07-28^4
Edward G. Gibson^1936-11-08^^1973-11-16^4
Duane E. Graveline^1931-03-02^2016-09-05^^4
Joseph P. Kerwin^1932-02-19^^1973-05-25^4
F. Curtis Michel^1934-06-05^2015-02-26^^4
Harrison H. Schmitt^1935-07-03^^1972-12-07^4
Vance D. Brand^1931-05-09^^1975-07-15^5
John S. Bull^1934-09-25^2008-08-11^^5
Gerald P. Carr^1932-08-22^2020-08-26^1973-11-16^5
Charles M. Duke Jr.^1935-10-03^^1972-04-16^5
Joe H. Engle^1932-08-26^2024-07-10^1965-06-29^5
Ronald E. Evans^1933-11-10^1990-04-07^1972-12-07^5
Edward G. Givens Jr.^1930-01-05^1967-06-06^^5
Fred W. Haise Jr.^1933-11-14^^1970-04-11^5
James B. Irwin^1930-03-17^1991-08-08^1971-07-26^5
Don L. Lind^1930-05-18^2022-08-30^1985-04-29^5
Jack R. Lousma^1936-02-29^^1973-07-28^5
Thomas K. Mattingly II^1936-03-17^2023-10-31^1972-04-16^5
Bruce McCandless II^1937-06-08^2017-12-21^1984-02-03^5
Edgar D. Mitchell^1930-09-17^2016-02-04^1971-01-31^5
William R. Pogue^1930-01-23^2014-03-03^1973-11-16^5
Stuart A. Roosa^1933-08-16^1994-12-12^1971-01-31^5
John L. Swigert Jr.^1931-08-30^1982-12-27^1970-04-11^5
Paul J. Weitz^1932-07-25^2017-10-22^1973-05-25^5
Alfred M. Worden^1932-02-07^2020-03-18^1971-07-26^5
Joseph P. Allen^1937-06-27^^1982-11-11^6
Philip K. Chapman^1935-03-05^2021-04-05^^6
Anthony W. England^1942-05-15^^1985-07-29^6
Karl G. Henize^1926-10-17^1993-10-05^1985-07-29^6
Donald L. Holmquest^1939-04-07^^^6
William B. Lenoir^1939-03-14^2010-08-26^1982-11-11^6
John A. Llewellyn^1933-04-22^2013-07-02^^6
Story Musgrave^1935-08-19^^1983-04-04^6
Brian T. O'Leary^1940-01-27^2011-07-28^^6
Robert A. R. Parker^1936-12-14^^1983-11-28^6
William E. Thornton^1929-04-14^2021-01-11^1983-08-30^6
Karol J. Bobko^1937-12-23^2023-08-17^1983-04-04^7
Robert L. Crippen^1937-09-11^^1981-04-12^7
C. Gordon Fullerton^1936-10-11^2013-08-21^1982-03-22^7
Henry W. Hartsfield Jr.^1933-11-21^2014-07-17^1982-06-27^7
Robert F. Overmyer^1936-07-14^1996-03-22^1982-11-11^7
Donald H. Peterson^1933-10-22^2018-05-27^1983-04-04^7
Richard H. Truly^1937-11-12^2024-02-27^1981-11-12^7
""".strip()

# name ^ birth ^ death ^ first spaceflight ^ vital URL ^ disambiguator
EXTERNAL_ROWS = """
Albert Scott Crossfield^1921-10-02^2006-04-19^^https://en.wikipedia.org/wiki/Albert_Scott_Crossfield^X-15 test pilot
Joseph A. Walker^1921-02-20^1966-06-08^1963-01-17^https://en.wikipedia.org/wiki/Joseph_A._Walker^X-15 test pilot
Robert M. White^1924-07-06^2010-03-17^1962-07-17^https://en.wikipedia.org/wiki/Robert_Michael_White^X-15 test pilot
Forrest S. Petersen^1922-05-16^1990-12-08^^https://en.wikipedia.org/wiki/Forrest_S._Petersen^X-15 test pilot
John B. McKay^1922-12-08^1975-04-27^1965-09-28^https://en.wikipedia.org/wiki/John_B._McKay^X-15 test pilot
Robert A. Rushworth^1924-10-09^1993-03-17^1963-06-27^https://en.wikipedia.org/wiki/Robert_A._Rushworth^X-15 test pilot
Milton O. Thompson^1926-05-04^1993-08-06^^https://en.wikipedia.org/wiki/Milton_Orville_Thompson^X-15 and Dyna-Soar test pilot
William J. "Pete" Knight^1929-11-18^2004-05-07^1966-11-18^https://en.wikipedia.org/wiki/William_J._Knight^X-15 and Dyna-Soar test pilot
William H. Dana^1930-11-03^2014-05-06^1966-11-01^https://en.wikipedia.org/wiki/William_H._Dana^X-15 test pilot
Michael J. Adams^1930-05-05^1967-11-15^1967-11-15^https://en.wikipedia.org/wiki/Michael_J._Adams^X-15 and MOL test pilot
Albert H. Crews Jr.^1929-03-23^2025-06-07^^https://en.wikipedia.org/wiki/Albert_H._Crews^Dyna-Soar and MOL astronaut
Henry C. Gordon^1925-12-23^1996-09-24^^https://en.wikipedia.org/wiki/Henry_Charles_Gordon^Dyna-Soar test pilot
Russell L. Rogers^1928-04-12^1967-09-13^^https://en.wikipedia.org/wiki/Russell_L._Rogers^Dyna-Soar test pilot
James W. Wood^1924-08-09^1990-01-01^^https://en.wikipedia.org/wiki/James_W._Wood^Dyna-Soar test pilot
John L. Finley^1935-12-22^2006-09-19^^https://en.wikipedia.org/wiki/John_L._Finley^MOL astronaut
Richard E. Lawyer^1932-11-08^2005-11-12^^https://en.wikipedia.org/wiki/Richard_E._Lawyer^MOL astronaut
Lachlan Macleay^1931-06-13^^^https://en.wikipedia.org/wiki/Lachlan_Macleay^MOL astronaut
Francis G. Neubeck^1932-04-11^^^https://en.wikipedia.org/wiki/Francis_G._Neubeck^MOL astronaut
James M. Taylor^1930-11-27^1970-09-04^^https://en.wikipedia.org/wiki/James_M._Taylor^MOL astronaut
James A. Abrahamson^1933-05-19^^^https://en.wikipedia.org/wiki/James_A._Abrahamson^MOL astronaut
Robert T. Herres^1932-12-01^2008-07-24^^https://en.wikipedia.org/wiki/Robert_T._Herres^MOL astronaut
Robert H. Lawrence Jr.^1935-10-02^1967-12-08^^https://en.wikipedia.org/wiki/Robert_Henry_Lawrence_Jr.^MOL astronaut
""".strip()

APOLLO_MISSIONS = {
    "Walter M. Schirra Jr.": ["Apollo 7"],
    "Donn F. Eisele": ["Apollo 7"],
    "R. Walter Cunningham": ["Apollo 7"],
    "Frank Borman": ["Apollo 8"],
    "James A. Lovell Jr.": ["Apollo 8", "Apollo 13"],
    "William A. Anders": ["Apollo 8"],
    "James A. McDivitt": ["Apollo 9"],
    "David R. Scott": ["Apollo 9", "Apollo 15"],
    "Russell L. Schweickart": ["Apollo 9"],
    "Thomas P. Stafford": ["Apollo 10"],
    "John W. Young": ["Apollo 10", "Apollo 16"],
    "Eugene A. Cernan": ["Apollo 10", "Apollo 17"],
    "Neil A. Armstrong": ["Apollo 11"],
    "Michael Collins": ["Apollo 11"],
    "Buzz Aldrin": ["Apollo 11"],
    "Charles \"Pete\" Conrad Jr.": ["Apollo 12"],
    "Richard F. Gordon Jr.": ["Apollo 12"],
    "Alan L. Bean": ["Apollo 12"],
    "John L. Swigert Jr.": ["Apollo 13"],
    "Fred W. Haise Jr.": ["Apollo 13"],
    "Alan B. Shepard Jr.": ["Apollo 14"],
    "Stuart A. Roosa": ["Apollo 14"],
    "Edgar D. Mitchell": ["Apollo 14"],
    "Alfred M. Worden": ["Apollo 15"],
    "James B. Irwin": ["Apollo 15"],
    "Thomas K. Mattingly II": ["Apollo 16"],
    "Charles M. Duke Jr.": ["Apollo 16"],
    "Ronald E. Evans": ["Apollo 17"],
    "Harrison H. Schmitt": ["Apollo 17"],
}

APOLLO1_NAMES = {
    'Virgil I. "Gus" Grissom',
    "Edward H. White II",
    "Roger B. Chaffee",
}

ACCIDENTAL_PRE1970 = {
    'Virgil I. "Gus" Grissom',
    "Elliot M. See Jr.",
    "Edward H. White II",
    "Charles A. Bassett II",
    "Roger B. Chaffee",
    "Theodore C. Freeman",
    "Clifton C. Williams Jr.",
    "Edward G. Givens Jr.",
    "Joseph A. Walker",
    "Michael J. Adams",
    "Russell L. Rogers",
    "Robert H. Lawrence Jr.",
}

X15_NAMES = {
    "Albert Scott Crossfield", "Joseph A. Walker", "Robert M. White",
    "Forrest S. Petersen", "John B. McKay", "Robert A. Rushworth",
    "Neil A. Armstrong", "Joe H. Engle", "Milton O. Thompson",
    'William J. "Pete" Knight', "William H. Dana", "Michael J. Adams",
}

DYNA_NAMES = {
    "Albert H. Crews Jr.", "Henry C. Gordon", 'William J. "Pete" Knight',
    "Russell L. Rogers", "James W. Wood", "Milton O. Thompson",
}

MOL_GROUPS = {
    "1965-11-12": {
        "Michael J. Adams", "Albert H. Crews Jr.", "John L. Finley",
        "Richard E. Lawyer", "Lachlan Macleay", "Francis G. Neubeck",
        "James M. Taylor", "Richard H. Truly",
    },
    "1966-06-17": {
        "Karol J. Bobko", "Robert L. Crippen", "C. Gordon Fullerton",
        "Henry W. Hartsfield Jr.", "Robert F. Overmyer",
    },
    "1967-06-30": {
        "James A. Abrahamson", "Robert T. Herres",
        "Robert H. Lawrence Jr.", "Donald H. Peterson",
    },
}
MOL_NAMES = set().union(*MOL_GROUPS.values())

BACKUPS = {
    "Thomas P. Stafford": ["Apollo 7 backup commander (later Apollo 10 prime commander)"],
    "John W. Young": [
        "Apollo 7 backup command module pilot (later Apollo 10 and Apollo 16 prime)",
        "Apollo 13 backup commander (later Apollo 16 prime commander)",
        "Apollo 17 backup commander",
    ],
    "Eugene A. Cernan": [
        "Apollo 7 backup lunar module pilot (later Apollo 10 and Apollo 17 prime)",
        "Apollo 14 backup commander (later Apollo 17 prime commander)",
    ],
    "Neil A. Armstrong": ["Apollo 8 backup commander (later Apollo 11 prime commander)"],
    "Buzz Aldrin": ["Apollo 8 backup command module pilot (later Apollo 11 prime)"],
    "Fred W. Haise Jr.": [
        "Apollo 8 backup lunar module pilot (later Apollo 13 prime)",
        "Apollo 11 backup lunar module pilot (later Apollo 13 prime)",
        "Apollo 16 backup commander",
    ],
    'Charles "Pete" Conrad Jr.': ["Apollo 9 backup commander (later Apollo 12 prime commander)"],
    "Richard F. Gordon Jr.": [
        "Apollo 9 backup command module pilot (later Apollo 12 prime)",
        "Apollo 15 backup commander",
    ],
    "Alan L. Bean": ["Apollo 9 backup lunar module pilot (later Apollo 12 prime)"],
    "L. Gordon Cooper Jr.": ["Apollo 10 backup commander"],
    "Donn F. Eisele": ["Apollo 10 backup command module pilot"],
    "Edgar D. Mitchell": [
        "Apollo 10 backup lunar module pilot (later Apollo 14 prime)",
        "Apollo 16 backup lunar module pilot",
    ],
    "James A. Lovell Jr.": ["Apollo 11 backup commander (later Apollo 13 prime commander)"],
    "William A. Anders": ["Apollo 11 backup command module pilot"],
    "David R. Scott": ["Apollo 12 backup commander (later Apollo 15 prime commander)"],
    "Alfred M. Worden": ["Apollo 12 backup command module pilot (later Apollo 15 prime)"],
    "James B. Irwin": ["Apollo 12 backup lunar module pilot (later Apollo 15 prime)"],
    "John L. Swigert Jr.": ["Apollo 13 backup command module pilot; launched as prime substitute on Apollo 13"],
    "Charles M. Duke Jr.": [
        "Apollo 13 backup lunar module pilot (later Apollo 16 prime)",
        "Apollo 17 backup lunar module pilot",
    ],
    "Joe H. Engle": ["Apollo 14 backup lunar module pilot"],
    "Ronald E. Evans": ["Apollo 14 backup command module pilot (later Apollo 17 prime)"],
    "Vance D. Brand": ["Apollo 15 backup command module pilot"],
    "Harrison H. Schmitt": ["Apollo 15 backup lunar module pilot (later Apollo 17 prime)"],
    "Stuart A. Roosa": [
        "Apollo 16 backup command module pilot",
        "Apollo 17 backup command module pilot",
    ],
    "Thomas K. Mattingly II": ["Apollo 13 original prime command module pilot; removed before launch (later Apollo 16 prime)"],
}

TARGETED_LIVING = {
    "Buzz Aldrin": ("2026-07-23T03:53:52Z", '"Buzz Aldrin" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Russell L. Schweickart": ("2026-07-23T03:53:52Z", '"Russell Schweickart" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "David R. Scott": ("2026-07-23T03:53:52Z", '"David Scott" Apollo astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Charles M. Duke Jr.": ("2026-07-23T03:53:52Z", '"Charles Duke" Apollo astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Fred W. Haise Jr.": ("2026-07-23T03:54:13Z", '"Fred Haise" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Harrison H. Schmitt": ("2026-07-23T03:54:13Z", '"Harrison Schmitt" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Edward G. Gibson": ("2026-07-23T03:54:13Z", '"Edward Gibson" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Joseph P. Kerwin": ("2026-07-23T03:54:13Z", '"Joseph Kerwin" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Vance D. Brand": ("2026-07-23T03:54:37Z", '"Vance Brand" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Jack R. Lousma": ("2026-07-23T03:54:37Z", '"Jack Lousma" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Joseph P. Allen": ("2026-07-23T03:54:37Z", '"Joseph P. Allen" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Anthony W. England": ("2026-07-23T03:54:37Z", '"Anthony England" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Donald L. Holmquest": ("2026-07-23T03:54:56Z", '"Donald Holmquest" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Story Musgrave": ("2026-07-23T03:54:56Z", '"Story Musgrave" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Robert A. R. Parker": ("2026-07-23T03:54:56Z", '"Robert A. R. Parker" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Robert L. Crippen": ("2026-07-23T03:54:56Z", '"Robert Crippen" NASA astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Lachlan Macleay": ("2026-07-23T03:55:19Z", '"Lachlan Macleay" MOL astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "Francis G. Neubeck": ("2026-07-23T03:55:19Z", '"Francis G. Neubeck" MOL astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
    "James A. Abrahamson": ("2026-07-23T03:55:19Z", '"James Alan Abrahamson" MOL astronaut (death OR obituary) after:2023-12-31 before:2026-06-02'),
}


def parse_iso(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def person_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(v for v in values if v))


people: list[dict[str, object]] = []
by_name: dict[str, dict[str, object]] = {}

for line in NASA_ROWS.splitlines():
    name, birth, death, first_flight, group_text = line.split("^")
    group = int(group_text)
    selection = NASA_SELECTION.get(group, "")
    row: dict[str, object] = {
        "full_name": name,
        "birth_date": birth,
        "death_date": death,
        "first_spaceflight_date": first_flight,
        "first_selection_date": selection,
        "nasa_group": group,
        "vital_url": NASA_GROUP,
        "search_disambiguator": "NASA astronaut",
    }
    people.append(row)
    by_name[name] = row

for line in EXTERNAL_ROWS.splitlines():
    name, birth, death, first_flight, vital_url, disambiguator = line.split("^")
    row = {
        "full_name": name,
        "birth_date": birth,
        "death_date": death,
        "first_spaceflight_date": first_flight,
        "first_selection_date": "",
        "nasa_group": 0,
        "vital_url": vital_url,
        "search_disambiguator": disambiguator,
    }
    people.append(row)
    by_name[name] = row

# MOL is the earliest exact included-program selection for these people.
for mol_date, names in MOL_GROUPS.items():
    for name in names:
        current = str(by_name[name]["first_selection_date"])
        if not current or mol_date < current:
            by_name[name]["first_selection_date"] = mol_date

# Crews' exact earlier Dyna-Soar military-astronaut designation date is documented.
by_name["Albert H. Crews Jr."]["first_selection_date"] = "1962-04-20"

# Their X-15 participation predates their later NASA selections, but a fetched
# full-date X-15 selection/assignment source was not established.
by_name["Neil A. Armstrong"]["first_selection_date"] = ""
by_name["Joe H. Engle"]["first_selection_date"] = ""

for index, row in enumerate(people, start=1):
    name = str(row["full_name"])
    nasa = int(row["nasa_group"]) > 0
    missions = APOLLO_MISSIONS.get(name, [])
    apollo = bool(missions)
    x15 = name in X15_NAMES
    dyna = name in DYNA_NAMES
    mol = name in MOL_NAMES
    death_value = str(row["death_date"])
    death = parse_iso(death_value)
    membership_urls: list[str] = []
    if nasa:
        membership_urls.append(NASA_GROUP)
    if apollo:
        membership_urls.append(APOLLO_ALL)
    if name in APOLLO1_NAMES:
        membership_urls.append(APOLLO1)
    if x15:
        membership_urls.append(X15)
    if dyna:
        membership_urls.extend([DYNA, DYNA_USAF])
    if mol:
        membership_urls.extend([MOL, MOL_NASA])

    notes = [f"NASA astronaut selection Group {row['nasa_group']}." if nasa else ""]
    if not row["first_selection_date"]:
        notes.append("Exact first included-program selection date was not established from a fetched source; left blank.")
    if x15 and nasa and not row["first_selection_date"]:
        notes.append("X-15 activity predates later NASA selection; exact X-15 assignment date was not established, so the later NASA date was not substituted.")
    if name == "Thomas K. Mattingly II":
        notes.append("Removed from the Apollo 13 prime crew approximately 72 hours before launch after rubella exposure; later launched on Apollo 16.")
    if name == "John L. Swigert Jr.":
        notes.append("Moved from Apollo 13 backup CMP to the launched prime crew before launch.")
    if name == "Walter M. Schirra Jr.":
        notes.append("NASA historical sources show a one-day death-date discrepancy; 2007-05-03 follows the current Astronaut Fact Book.")
    if name == "Albert H. Crews Jr.":
        notes.append("A targeted follow-up corrected an earlier unsupported transcription; fetched biography reports death 2025-06-07.")
    if name in {"Anthony W. England", "James A. Abrahamson"}:
        notes.append("Targeted obituary search produced a same-name false positive that was disambiguated by role.")

    row.update({
        "person_id": f"p{index:03d}_{person_key(name)}",
        "vital_status_20260601": "deceased" if death and death <= CENSOR else "alive",
        "apollo_flew": int(apollo),
        "apollo_missions": "|".join(missions),
        "apollo1_crew": int(name in APOLLO1_NAMES),
        "core_nasa_non_apollo": int(nasa and not apollo),
        "military_x15": int(x15),
        "military_dyna_soar": int(dyna),
        "military_mol": int(mol),
        "other_all": int((not apollo) and (nasa or x15 or dyna or mol)),
        "pre1970_accidental_death": int(name in ACCIDENTAL_PRE1970),
        "backup_crew_roles": "|".join(BACKUPS.get(name, [])),
        "membership_source_urls": "|".join(dedupe(membership_urls)),
        "birth_source_url": str(row["vital_url"]),
        "death_source_url": (NASA_FACTBOOK if nasa else str(row["vital_url"])) if death_value else "",
        "confidence": "high" if nasa else "medium",
        "notes": " ".join(v for v in notes if v),
    })

columns = [
    "person_id", "full_name", "search_disambiguator", "birth_date",
    "death_date", "vital_status_20260601", "first_selection_date",
    "first_spaceflight_date", "apollo_flew", "apollo_missions",
    "apollo1_crew", "core_nasa_non_apollo", "military_x15",
    "military_dyna_soar", "military_mol", "other_all",
    "pre1970_accidental_death", "backup_crew_roles",
    "membership_source_urls", "birth_source_url", "death_source_url",
    "confidence", "notes",
]

with (OUT / "cohort.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle, fieldnames=columns, extrasaction="ignore",
        dialect="excel", lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(people)

source_columns = [
    "timestamp", "person_id", "query_or_direct_navigation", "result_rank",
    "url", "opened", "access_result", "fact_supported", "source_tier",
    "notes",
]
source_rows: list[dict[str, object]] = []


def log_source(
    timestamp: str,
    row: dict[str, object],
    navigation: str,
    url: str,
    fact: str,
    tier: str,
    notes: str,
    opened: int = 1,
    rank: str = "direct",
    access: str = "fetched",
) -> None:
    source_rows.append({
        "timestamp": timestamp,
        "person_id": row["person_id"],
        "query_or_direct_navigation": navigation,
        "result_rank": rank,
        "url": url,
        "opened": opened,
        "access_result": access,
        "fact_supported": fact,
        "source_tier": tier,
        "notes": notes,
    })


official_fetch_times = {
    NASA_GROUP: "2026-07-23T03:44:16Z",
    NASA_FACTBOOK: "2026-07-23T03:51:22Z",
    APOLLO_ALL: "2026-07-23T03:44:16Z",
    APOLLO1: "2026-07-23T03:50:59Z",
    X15: "2026-07-23T03:44:16Z",
    X15_WINGS: "2026-07-23T03:50:59Z",
    DYNA: "2026-07-23T03:47:15Z",
    DYNA_USAF: "2026-07-23T03:45:33Z",
    MOL: "2026-07-23T03:50:42Z",
    MOL_NASA: "2026-07-23T03:50:42Z",
    **{
        url: (
            "2026-07-23T03:56:09Z"
            if mission in {"Apollo 9", "Apollo 12"}
            else "2026-07-23T03:55:41Z"
        )
        for mission, url in MISSION_URLS.items()
    },
}

for row in people:
    name = str(row["full_name"])
    for url in str(row["membership_source_urls"]).split("|"):
        membership_tier = "2" if url == DYNA else "1"
        log_source(
            official_fetch_times.get(url, "2026-07-23T03:51:22Z"),
            row, "direct navigation", url, "program or mission membership",
            membership_tier,
            "Primary official roster, mission, or program-history source."
            if membership_tier == "1"
            else "Smithsonian/National Air and Space Museum curated program history.",
        )
    birth_url = str(row["birth_source_url"])
    birth_tier = "1" if birth_url == NASA_GROUP else "3"
    birth_time = "2026-07-23T03:44:16Z" if birth_tier == "1" else "2026-07-23T04:00:17Z"
    if name in {"Albert H. Crews Jr.", "Henry C. Gordon"}:
        birth_time = "2026-07-23T04:00:53Z"
    log_source(
        birth_time, row, "direct navigation", birth_url, "birth date",
        birth_tier,
        "NASA biographical summary." if birth_tier == "1" else "Accessible individual biography; used only for vital dates.",
    )
    death_url = str(row["death_source_url"])
    if death_url:
        death_tier = "1" if death_url == NASA_FACTBOOK else "3"
        death_time = "2026-07-23T03:51:22Z" if death_tier == "1" else "2026-07-23T04:00:17Z"
        if name in {"Albert H. Crews Jr.", "Henry C. Gordon"}:
            death_time = "2026-07-23T04:00:53Z"
        log_source(
            death_time, row, "direct navigation", death_url,
            "death date and deceased status", death_tier,
            "Current NASA fact book." if death_tier == "1" else "Accessible individual biography; used only for vital dates.",
        )
    if row["first_spaceflight_date"]:
        flight_url = X15_WINGS if name in X15_NAMES and (
            not int(row["nasa_group"]) or name == "Joe H. Engle"
        ) else NASA_FACTBOOK
        log_source(
            official_fetch_times[flight_url], row, "direct navigation",
            flight_url, "first qualifying spaceflight date", "1",
            "Official NASA flight/program source.",
        )
    for mission in APOLLO_MISSIONS.get(name, []):
        log_source(
            official_fetch_times[MISSION_URLS[mission]], row,
            "direct navigation", MISSION_URLS[mission],
            f"{mission} launched crew", "1",
            "Official NASA mission-detail page.",
        )
    for role in BACKUPS.get(name, []):
        mission_match = re.match(r"(Apollo \d+)", role)
        if mission_match:
            mission = mission_match.group(1)
            log_source(
                official_fetch_times[MISSION_URLS[mission]], row,
                "direct navigation", MISSION_URLS[mission],
                f"{mission} backup/crew rotation role", "1",
                "Official NASA mission-detail page; rotation text normalized in cohort.",
            )
    if name in TARGETED_LIVING:
        timestamp, query = TARGETED_LIVING[name]
        false_note = ""
        if name == "Anthony W. England":
            false_note = " Same-name obituary snippet referred to a different Anthony England and was not opened."
        if name == "James A. Abrahamson":
            false_note = " Same-name obituary snippet referred to a different James A. Abrahamson and was not opened."
        log_source(
            timestamp, row, query, "", "living-status check through censor",
            "not_applicable", "No applicable death or obituary result through 2026-06-01." + false_note,
            opened=0, rank="", access="search completed; no applicable result",
        )

# Preserve the two failed biography opens before corrected URLs were found.
for failed_name, failed_url in (
    ("Albert H. Crews Jr.", "https://en.wikipedia.org/wiki/Albert_H._Crews_Jr."),
    ("Henry C. Gordon", "https://en.wikipedia.org/wiki/Henry_C._Gordon"),
):
    log_source(
        "2026-07-23T04:00:17Z", by_name[failed_name],
        "direct navigation", failed_url, "no fact supported", "3",
        "Initial biography URL returned an internal error; not used.",
        opened=1, rank="direct", access="internal error",
    )

with (OUT / "SOURCE_LOG.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle, fieldnames=source_columns, dialect="excel",
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(source_rows)

# Assertions enforce the requested schema and logical invariants.
assert len(people) == 95
assert len({row["person_id"] for row in people}) == 95
assert len({str(row["full_name"]).casefold() for row in people}) == 95
assert sum(int(row["nasa_group"]) > 0 for row in people) == 73
assert sum(int(row["apollo_flew"]) for row in people) == 29
assert sum(int(row["core_nasa_non_apollo"]) for row in people) == 44
assert sum(int(row["military_x15"]) for row in people) == 12
assert sum(int(row["military_dyna_soar"]) for row in people) == 6
assert sum(int(row["military_mol"]) for row in people) == 17
assert sum(int(row["other_all"]) for row in people) == 66
assert sum(int(row["apollo1_crew"]) for row in people) == 3
assert sum(int(row["pre1970_accidental_death"]) for row in people) == 12
assert sum(row["vital_status_20260601"] == "alive" for row in people) == 19
assert set(TARGETED_LIVING) == {
    str(row["full_name"]) for row in people
    if row["vital_status_20260601"] == "alive"
}
for row in people:
    assert int(row["other_all"]) == int(
        not int(row["apollo_flew"]) and any(
            int(row[field]) for field in (
                "core_nasa_non_apollo", "military_x15",
                "military_dyna_soar", "military_mol",
            )
        )
    )
    assert not (int(row["apollo_flew"]) and int(row["other_all"]))
    for field in ("birth_date", "death_date", "first_selection_date", "first_spaceflight_date"):
        if row[field]:
            date.fromisoformat(str(row[field]))
    if row["vital_status_20260601"] == "alive":
        assert not row["death_date"]
        assert not row["death_source_url"]
    else:
        assert parse_iso(str(row["death_date"])) <= CENSOR
        assert row["death_source_url"]
    assert row["membership_source_urls"]
    assert row["birth_source_url"]

overlap_x15_dyna = sorted(X15_NAMES & DYNA_NAMES)
overlap_x15_mol = sorted(X15_NAMES & MOL_NAMES)
overlap_dyna_mol = sorted(DYNA_NAMES & MOL_NAMES)
overlap_nasa_mol = sorted(
    name for name in MOL_NAMES if int(by_name[name]["nasa_group"]) > 0
)
overlap_apollo_x15 = sorted(set(APOLLO_MISSIONS) & X15_NAMES)

validation = f"""# Stage 1 validation

## Cohort counts

- Deduplicated people: 95
- NASA selection Groups 1-7: 73
- Distinct people launched on Apollo 7-17: 29
- Core NASA non-Apollo members: 44
- X-15 actual pilots: 12
- Dyna-Soar selected-to-fly pilots: 6
- MOL selectees: 17
- `other_all=1`: 66
- Apollo 1 crew flags: 3
- Pre-1970 accidental-death flags: 12
- Alive at 2026-06-01: 19
- Deceased by 2026-06-01: 76

These are roster and data-integrity counts only. No outcome contrast was calculated.

## Overlap checks

- Apollo/X-15: {len(overlap_apollo_x15)} ({'|'.join(overlap_apollo_x15)})
- X-15/Dyna-Soar: {len(overlap_x15_dyna)} ({'|'.join(overlap_x15_dyna)})
- X-15/MOL: {len(overlap_x15_mol)} ({'|'.join(overlap_x15_mol)})
- Dyna-Soar/MOL: {len(overlap_dyna_mol)} ({'|'.join(overlap_dyna_mol)})
- NASA Groups 1-7/MOL: {len(overlap_nasa_mol)} ({'|'.join(overlap_nasa_mol)})
- The 29 Apollo flyers all have `other_all=0`, including Neil Armstrong, whose X-15 flag remains 1.
- The later `MILITARY_ONLY` definition is reproducible as `(military_x15 OR military_dyna_soar OR military_mol) AND apollo_flew=0`; no such downstream group was analyzed here.

## Duplicate and schema checks

- `person_id`: 95 unique values; no duplicates.
- Case-folded `full_name`: 95 unique values; no duplicates.
- CSV header exactly matches the requested 23-column order.
- CSV was written with Python's `csv` module using CRLF records and RFC 4180 quoting.
- Multi-value cells use `|`.
- All Boolean columns contain only `0` or `1`.

## Date and status checks

- Every non-empty date parses as ISO `YYYY-MM-DD`.
- Every `alive` row has an empty `death_date` and empty `death_source_url`.
- Every `deceased` row has a death date on or before 2026-06-01 and a fetched death source URL.
- Every row has a fetched membership URL and a fetched birth source URL.
- All 19 apparently living people have a targeted, disambiguated death/obituary search spanning 2024-01-01 through 2026-06-01 recorded in `SOURCE_LOG.csv`.
- Anthony W. England and James A. Abrahamson produced same-name obituary snippets for other people; role disambiguation prevented false matches.

## Unresolved or qualified items

- Exact first included-program selection dates were not located for several X-15-only and Dyna-Soar-only pilots; those cells remain blank and are called out in row notes rather than imputed.
- X-15 `first_spaceflight_date` uses the fixed U.S. 50-mile threshold. Crossfield, Petersen, and Thompson did not have a qualifying X-15 flight and therefore remain blank.
- Walter Schirra's death date has a one-day discrepancy among NASA historical pages; the current NASA Astronaut Fact Book value, 2007-05-03, was retained and noted.
- Albert Crews' death date was corrected to 2025-06-07 after a targeted follow-up found the accessible individual biography. The earlier unsupported transcription was discarded and documented in `ACTION_LOG.md`.
- Individual vital dates for the 22 non-NASA-roster-only people rely on fetched Tier 3 biographies because the official program rosters establish membership but generally do not publish complete exact vital dates. Those rows are marked `medium` confidence.
- Backup roles are normalized from official mission pages. Mattingly's late Apollo 13 prime-crew removal and Swigert's crossover from backup to launched prime crew are explicitly retained.
"""
(OUT / "VALIDATION.md").write_text(validation, encoding="utf-8")

contamination = """# Contamination log

No prohibited source was opened.

The searches did not expose a mortality/aging study or another source whose purpose was statistical or comparative analysis of people in the named cohorts or programs. Accordingly, there are no result-page encounters requiring a title/URL/snippet entry under the contamination rule.

All inclusion decisions were made top-down from primary NASA, U.S. Air Force, Smithsonian/National Air and Space Museum, and National Reconnaissance Office roster or program-history sources. Individual biographies were used only for person-level vital facts when an official roster did not contain them.
"""
(OUT / "CONTAMINATION.md").write_text(contamination, encoding="utf-8")

complete = """# Stage 1 complete

## Required outputs

- `stage1/DECISIONS.md`
- `stage1/cohort.csv`
- `stage1/SOURCE_LOG.csv`
- `stage1/VALIDATION.md`
- `stage1/CONTAMINATION.md`
- `stage1/STAGE_COMPLETE.md`

## Audit and reproducibility outputs

- `CONTEXT_ATTESTATION.md`
- `ACTION_LOG.md`
- `stage1/build_stage1.py`
- `stage1/validate_stage1.py`

Stage 1 roster construction, person-level vital-data collection, source logging, and validation are complete as censored on 2026-06-01.

No group-level outcome contrast or analysis was performed.
"""
(OUT / "STAGE_COMPLETE.md").write_text(complete, encoding="utf-8")

print(
    f"wrote {len(people)} cohort rows, {len(source_rows)} source-log rows, "
    "VALIDATION.md, CONTAMINATION.md, and STAGE_COMPLETE.md"
)
