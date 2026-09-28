#!/usr/bin/env python3
"""Build the frozen, direction-neutral Stage 1 cohort and evidence ledger."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "stage1"
CENSOR = "2026-06-01"
FETCHED_AT = "2026-07-23T03:16:00Z"

FACTBOOK = "https://www.nasa.gov/wp-content/uploads/2023/08/astronaut-fact-book-jan-2023.pdf"
APOLLO = "https://www.nasa.gov/specials/apollo50th/missions.html"
APOLLO1 = "https://www.nasa.gov/apollo-1-resources/"
X15 = "https://www.nasa.gov/aeronautics/x-15/"
DYNA = "https://www.aflcmc.af.mil/News/Article-Display/Article/1925643/history-in-two-dyna-soar/"
MOL = "https://www.nasa.gov/history/55-years-ago-manned-orbiting-laboratory-cancellation/"
NRO_MOL = "https://www.nro.gov/About-NRO/history/history-MOL/"

POST_2022_DEATH = {
    "R. Walter Cunningham": "https://www.nasa.gov/news-release/apollo-astronaut-walter-cunningham-dies-at-90/",
    "Frank Borman": "https://www.nasa.gov/news-release/nasa-administrator-honors-life-of-apollo-astronaut-frank-borman/",
    "Karol J. Bobko": "https://www.nasa.gov/wp-content/uploads/2023/09/bobko-karol.pdf",
    "Thomas K. Mattingly II": "https://www.nasa.gov/wp-content/uploads/2023/11/mattingly-thomas.pdf",
    "Thomas P. Stafford": "https://www.nasa.gov/iss-ac-stafford-in-memoriam/",
    "Richard H. Truly": "https://www.nasa.gov/news-release/nasa-honors-life-of-former-administrator-astronaut-richard-truly/",
    "William A. Anders": "https://science.nasa.gov/missions/landsat/remembering-bill-anders/",
    "Joe H. Engle": "https://www.nasa.gov/news-release/nasa-remembers-retired-astronaut-us-air-force-pilot-joe-engle/",
    "James A. Lovell Jr.": "https://www.nasa.gov/news-release/acting-nasa-administrator-reflects-on-legacy-of-astronaut-jim-lovell/",
    "Albert H. Crews Jr.": "https://www.collectspace.com/ubb/Forum38/HTML/002640.html",
}

CURRENT = {
    "Buzz Aldrin": "https://www.nasa.gov/former-astronaut-buzz-aldrin/",
    "Russell L. Schweickart": "https://www.nasa.gov/people/russell-l-schweickart/",
    "David R. Scott": "https://www.nasa.gov/former-astronaut-david-r-scott/",
    "Edward G. Gibson": "https://www.nasa.gov/people/edward-g-gibson/",
    "Joseph P. Kerwin": "https://www.nasa.gov/people/joseph-p-kerwin/",
    "Harrison H. Schmitt": "https://www.nasa.gov/people/harrison-h-schmitt/",
    "Vance D. Brand": "https://www.nasa.gov/people/vance-d-brand/",
    "Charles M. Duke Jr.": "https://www.nasa.gov/people/charles-m-duke-jr/",
    "Fred W. Haise Jr.": "https://www.nasa.gov/people/fred-w-haise-jr/",
    "Jack R. Lousma": "https://www.nasa.gov/people/jack-r-lousma/",
    "Joseph P. Allen IV": "https://www.nasa.gov/people/joseph-p-allen/",
    "Anthony W. England": "https://www.nasa.gov/people/anthony-w-england/",
    "Donald L. Holmquest": "https://en.wikipedia.org/wiki/Donald_Holmquest",
    "Story Musgrave": "https://www.nasa.gov/people/story-musgrave/",
    "Robert A. R. Parker": "https://www.nasa.gov/people/robert-a-r-parker/",
    "Robert L. Crippen": "https://www.nasa.gov/people/robert-l-crippen/",
    "Lachlan Macleay": "https://en.wikipedia.org/wiki/Lachlan_Macleay",
    "Francis G. Neubeck": "https://en.wikipedia.org/wiki/Francis_G._Neubeck",
    "James A. Abrahamson": "https://www.af.mil/About-Us/Biographies/Display/Article/107876/james-a-abrahamson/",
}

EXTRA_SOURCE = {
    "Albert Scott Crossfield": "https://en.wikipedia.org/wiki/Scott_Crossfield",
    "Joseph A. Walker": "https://www.nasa.gov/people/joseph-a-walker/",
    "Robert M. White": "https://www.latimes.com/archives/la-xpm-2010-mar-24-la-me-robert-white24-2010mar24-story.html",
    "Forrest S. Petersen": "https://www.nasa.gov/history/x15/peters.html",
    "John B. McKay": "https://en.wikipedia.org/wiki/John_B._McKay",
    "Robert A. Rushworth": "https://nationalaviation.org/enshrinee/robert-a-rushworth/",
    "Milton O. Thompson": "https://www.nasa.gov/people/milton-o-thompson/",
    "William J. Knight": "https://www.nasa.gov/history/x15/knight.html",
    "William H. Dana": "https://www.nasa.gov/people/william-h-dana/",
    "Michael J. Adams": "https://www.nasa.gov/history/x15/adams.html",
    "Henry C. Gordon": "https://en.wikipedia.org/wiki/Henry_Charles_Gordon",
    "Russell L. Rogers": "https://en.wikipedia.org/wiki/Russell_L._Rogers",
    "James W. Wood": "https://en.wikipedia.org/wiki/James_W._Wood",
    "Albert H. Crews Jr.": "https://www.collectspace.com/ubb/Forum38/HTML/002640.html",
    "John L. Finley": "https://en.wikipedia.org/wiki/John_L._Finley",
    "Richard E. Lawyer": "https://en.wikipedia.org/wiki/Richard_E._Lawyer",
    "Lachlan Macleay": "https://en.wikipedia.org/wiki/Lachlan_Macleay",
    "Francis G. Neubeck": "https://en.wikipedia.org/wiki/Francis_G._Neubeck",
    "James M. Taylor": "https://en.wikipedia.org/wiki/James_M._Taylor",
    "James A. Abrahamson": "https://www.af.mil/About-Us/Biographies/Display/Article/107876/james-a-abrahamson/",
    "Robert T. Herres": "https://en.wikipedia.org/wiki/Robert_T._Herres",
    "Robert H. Lawrence Jr.": "https://www.nasa.gov/history/space-station-20th-cygnus-spacecraft-honors-robert-lawrence/",
}

GROUP_DATE = {
    1: "1959-04-09",
    2: "1962-09-17",
    3: "1963-10-18",
    4: "1965-06-28",
    5: "1966-04-04",
    6: "1967-08-04",
    7: "1969-08-14",
}

BACKUPS = {
    "Walter M. Schirra Jr.": "Apollo 1:CDR (final backup)",
    "Donn F. Eisele": "Apollo 1:CMP (final backup)|Apollo 10:CMP",
    "R. Walter Cunningham": "Apollo 1:LMP (final backup)",
    "James A. McDivitt": "Apollo 1:CDR (original backup)",
    "David R. Scott": "Apollo 1:CMP (original backup)|Apollo 12:CDR|Apollo 17:CDR (original backup)",
    "Russell L. Schweickart": "Apollo 1:LMP (original backup)",
    "Thomas P. Stafford": "Apollo 7:CDR",
    "John W. Young": "Apollo 7:CMP|Apollo 13:CDR|Apollo 17:CDR (final backup)",
    "Eugene A. Cernan": "Apollo 7:LMP|Apollo 14:CDR",
    "Neil A. Armstrong": "Apollo 8:CDR",
    "Buzz Aldrin": "Apollo 8:CMP",
    "Fred W. Haise Jr.": "Apollo 8:LMP|Apollo 11:LMP|Apollo 16:CDR",
    "Charles P. Conrad Jr.": "Apollo 9:CDR",
    "Richard F. Gordon Jr.": "Apollo 9:CMP|Apollo 15:CDR",
    "Alan L. Bean": "Apollo 9:LMP",
    "L. Gordon Cooper Jr.": "Apollo 10:CDR",
    "Edgar D. Mitchell": "Apollo 10:LMP|Apollo 16:LMP",
    "James A. Lovell Jr.": "Apollo 11:CDR",
    "William A. Anders": "Apollo 11:CMP",
    "Alfred M. Worden": "Apollo 12:CMP|Apollo 17:CMP (original backup)",
    "James B. Irwin": "Apollo 12:LMP|Apollo 17:LMP (original backup)",
    "John L. Swigert Jr.": "Apollo 13:CMP (initial backup; reassigned to prime)",
    "Thomas K. Mattingly II": "Apollo 13:CMP (post-substitution backup; original prime)",
    "Charles M. Duke Jr.": "Apollo 13:LMP|Apollo 17:LMP (final backup)",
    "Ronald E. Evans Jr.": "Apollo 14:CMP",
    "Joe H. Engle": "Apollo 14:LMP",
    "Vance D. Brand": "Apollo 15:CMP",
    "Harrison H. Schmitt": "Apollo 15:LMP",
    "Stuart A. Roosa": "Apollo 16:CMP|Apollo 17:CMP (final backup)",
}

MISSION_BACKUP_URL = {
    "Apollo 1": APOLLO1,
    "Apollo 7": "https://www.nasa.gov/missions/apollo/about-apollo-7-the-first-crewed-apollo-space-mission/",
    "Apollo 8": "https://www.nasa.gov/mission/apollo-8/",
    "Apollo 9": "https://www.nasa.gov/missions/apollo/apollo-9-mission-details/",
    "Apollo 10": "https://www.nasa.gov/missions/apollo/apollo-10-mission-details/",
    "Apollo 11": "https://www.nasa.gov/image-article/preparing-apollo-11/",
    "Apollo 12": "https://www.nasa.gov/history/50-years-ago-nasa-names-apollo-12-crew/",
    "Apollo 13": "https://www.nasa.gov/history/apollo-13-crew-returns-to-houston/",
    "Apollo 14": "https://www.nasa.gov/missions/apollo/apollo-14-mission-details/",
    "Apollo 15": "https://www.nasa.gov/missions/apollo/apollo-15-mission-details/",
    "Apollo 16": "https://www.nasa.gov/missions/apollo/apollo-16-mission-details/",
    "Apollo 17": "https://www.nasa.gov/history/50-years-ago-nasa-names-crew-for-apollo-17-the-last-moon-landing-mission/",
}

rows: list[dict[str, str]] = []


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def add(
    name: str,
    birth: str,
    death: str = "",
    *,
    group: int | None = None,
    selection: str | None = None,
    space: str = "",
    apollo: str = "",
    apollo1: int = 0,
    x15: int = 0,
    dyna: int = 0,
    mol: int = 0,
    accident: int = 0,
    disambiguator: str = "",
    source: str = "",
    confidence: str = "high",
    notes: str = "",
) -> None:
    apollo_flag = int(bool(apollo))
    core = int(group is not None and not apollo_flag)
    other = int(not apollo_flag and bool(core or x15 or dyna or mol))
    if selection is None:
        selection = GROUP_DATE[group] if group else ""
    if group:
        birth_url = FACTBOOK
    else:
        birth_url = source or EXTRA_SOURCE[name]
    death_url = ""
    if death:
        death_url = POST_2022_DEATH.get(name, FACTBOOK if group else (source or EXTRA_SOURCE[name]))
    membership_urls = []
    if group:
        membership_urls.append(FACTBOOK)
    if apollo_flag:
        membership_urls.append(APOLLO)
    if apollo1:
        membership_urls.append(APOLLO1)
    if x15:
        membership_urls.append(X15)
    if dyna:
        membership_urls.append(DYNA)
    if mol:
        membership_urls.extend([MOL, NRO_MOL])
    membership_urls = list(dict.fromkeys(membership_urls))
    tags = []
    if group:
        tags.append(f"NASA astronaut group {group}")
    if x15:
        tags.append("X-15 pilot")
    if dyna:
        tags.append("Dyna-Soar/X-20 pilot")
    if mol:
        tags.append("MOL astronaut")
    if apollo1:
        tags.append("Apollo 1 crew")
    dis = disambiguator or "; ".join(tags)
    row = {
        "person_id": slug(name),
        "full_name": name,
        "search_disambiguator": dis,
        "birth_date": birth,
        "death_date": death,
        "vital_status_20260601": "dead" if death and death <= CENSOR else "alive",
        "first_selection_date": selection,
        "first_spaceflight_date": space,
        "apollo_flew": str(apollo_flag),
        "apollo_missions": apollo,
        "apollo1_crew": str(apollo1),
        "core_nasa_non_apollo": str(core),
        "military_x15": str(x15),
        "military_dyna_soar": str(dyna),
        "military_mol": str(mol),
        "other_all": str(other),
        "pre1970_accidental_death": str(accident),
        "backup_crew_roles": BACKUPS.get(name, ""),
        "membership_source_urls": "|".join(membership_urls),
        "birth_source_url": birth_url,
        "death_source_url": death_url,
        "confidence": confidence,
        "notes": notes,
    }
    rows.append(row)


# NASA astronaut groups 1-7.
add("M. Scott Carpenter", "1925-05-01", "2013-10-10", group=1, space="1962-05-24")
add("L. Gordon Cooper Jr.", "1927-03-06", "2004-10-04", group=1, space="1963-05-15")
add("John H. Glenn Jr.", "1921-07-18", "2016-12-08", group=1, space="1962-02-20")
add("Virgil I. Grissom", "1926-04-03", "1967-01-27", group=1, space="1961-07-21", apollo1=1, accident=1)
add("Walter M. Schirra Jr.", "1923-03-12", "2007-05-03", group=1, space="1962-10-03", apollo="Apollo 7")
add("Alan B. Shepard Jr.", "1923-11-18", "1998-07-21", group=1, space="1961-05-05", apollo="Apollo 14")
add("Donald K. Slayton", "1924-03-01", "1993-06-13", group=1, space="1975-07-15")

add("Neil A. Armstrong", "1930-08-05", "2012-08-25", group=2, selection="", space="1966-03-16", apollo="Apollo 11", x15=1, dyna=1, notes="Selected for the initial Dyna-Soar pilot cadre in April 1960; exact day was not established, so first_selection_date is blank.")
add("Frank Borman", "1928-03-14", "2023-11-07", group=2, space="1965-12-04", apollo="Apollo 8")
add("Charles P. Conrad Jr.", "1930-06-02", "1999-07-08", group=2, space="1965-08-21", apollo="Apollo 12")
add("James A. Lovell Jr.", "1928-03-25", "2025-08-07", group=2, space="1965-12-04", apollo="Apollo 8|Apollo 13")
add("James A. McDivitt", "1929-06-10", "2022-10-13", group=2, space="1965-06-03", apollo="Apollo 9")
add("Elliot M. See Jr.", "1927-07-23", "1966-02-28", group=2, accident=1)
add("Thomas P. Stafford", "1930-09-17", "2024-03-18", group=2, space="1965-12-15", apollo="Apollo 10")
add("Edward H. White II", "1930-11-14", "1967-01-27", group=2, space="1965-06-03", apollo1=1, accident=1)
add("John W. Young", "1930-09-24", "2018-01-05", group=2, space="1965-03-23", apollo="Apollo 10|Apollo 16")

add("Buzz Aldrin", "1930-01-20", group=3, space="1966-11-11", apollo="Apollo 11")
add("William A. Anders", "1933-10-17", "2024-06-07", group=3, space="1968-12-21", apollo="Apollo 8", notes="Died in a private-aircraft crash after the frozen pre-1970 accident cutoff.")
add("Charles M. Bassett II", "1931-12-30", "1966-02-28", group=3, accident=1)
add("Alan L. Bean", "1932-03-15", "2018-05-26", group=3, space="1969-11-14", apollo="Apollo 12")
add("Eugene A. Cernan", "1934-03-14", "2017-01-16", group=3, space="1966-06-03", apollo="Apollo 10|Apollo 17")
add("Roger B. Chaffee", "1935-02-15", "1967-01-27", group=3, apollo1=1, accident=1)
add("Michael Collins", "1930-10-31", "2021-04-28", group=3, space="1966-07-18", apollo="Apollo 11")
add("R. Walter Cunningham", "1932-03-16", "2023-01-03", group=3, space="1968-10-11", apollo="Apollo 7")
add("Donn F. Eisele", "1930-06-23", "1987-12-02", group=3, space="1968-10-11", apollo="Apollo 7")
add("Theodore C. Freeman", "1930-02-18", "1964-10-31", group=3, accident=1)
add("Richard F. Gordon Jr.", "1929-10-05", "2017-11-06", group=3, space="1966-09-12", apollo="Apollo 12")
add("Russell L. Schweickart", "1935-10-25", group=3, space="1969-03-03", apollo="Apollo 9")
add("David R. Scott", "1932-06-06", group=3, space="1966-03-16", apollo="Apollo 9|Apollo 15")
add("Clifton C. Williams Jr.", "1932-09-26", "1967-10-05", group=3, accident=1)

add("Owen K. Garriott", "1930-11-22", "2019-04-15", group=4, space="1973-07-28")
add("Edward G. Gibson", "1936-11-08", group=4, space="1973-11-16")
add("Duane E. Graveline", "1931-03-02", "2016-09-05", group=4)
add("Joseph P. Kerwin", "1932-02-19", group=4, space="1973-05-25")
add("Curt Michel", "1934-06-05", "2015-02-26", group=4)
add("Harrison H. Schmitt", "1935-07-03", group=4, space="1972-12-07", apollo="Apollo 17")

add("Vance D. Brand", "1931-05-09", group=5, space="1975-07-15")
add("John S. Bull", "1934-09-11", "2008-08-11", group=5)
add("Gerald P. Carr", "1932-08-22", "2020-08-26", group=5, space="1973-11-16")
add("Charles M. Duke Jr.", "1935-10-03", group=5, space="1972-04-16", apollo="Apollo 16")
add("Joe H. Engle", "1932-08-26", "2024-07-10", group=5, selection="", space="1965-06-29", x15=1, notes="Joined the X-15 pilot roster in 1963 before NASA Group 5; exact X-15 selection day was not established, so first_selection_date is blank.")
add("Ronald E. Evans Jr.", "1933-11-10", "1990-04-07", group=5, space="1972-12-07", apollo="Apollo 17")
add("Edward G. Givens Jr.", "1930-01-05", "1967-06-06", group=5, accident=1)
add("Fred W. Haise Jr.", "1933-11-14", group=5, space="1970-04-11", apollo="Apollo 13")
add("James B. Irwin", "1930-03-17", "1991-08-08", group=5, space="1971-07-26", apollo="Apollo 15")
add("Don L. Lind", "1930-05-18", "2022-08-30", group=5, space="1985-04-29")
add("Jack R. Lousma", "1936-02-29", group=5, space="1973-07-28")
add("Thomas K. Mattingly II", "1936-03-17", "2023-10-31", group=5, space="1972-04-16", apollo="Apollo 16")
add("Bruce McCandless II", "1937-06-08", "2017-12-21", group=5, space="1984-02-03")
add("Edgar D. Mitchell", "1930-09-17", "2016-02-04", group=5, space="1971-01-31", apollo="Apollo 14")
add("William R. Pogue", "1930-01-23", "2014-03-03", group=5, space="1973-11-16")
add("Stuart A. Roosa", "1933-08-16", "1994-12-12", group=5, space="1971-01-31", apollo="Apollo 14")
add("John L. Swigert Jr.", "1931-08-30", "1982-12-27", group=5, space="1970-04-11", apollo="Apollo 13")
add("Paul J. Weitz", "1932-07-25", "2017-10-22", group=5, space="1973-05-25")
add("Alfred M. Worden", "1932-02-07", "2020-03-18", group=5, space="1971-07-26", apollo="Apollo 15")

add("Joseph P. Allen IV", "1937-06-27", group=6, space="1982-11-11")
add("Philip K. Chapman", "1935-03-05", "2021-04-05", group=6)
add("Anthony W. England", "1942-05-15", group=6, space="1985-07-29")
add("Karl G. Henize", "1926-10-17", "1993-10-05", group=6, space="1985-07-29", notes="Died during a Mount Everest expedition after the frozen pre-1970 accident cutoff.")
add("Donald L. Holmquest", "1939-04-07", group=6)
add("William B. Lenoir", "1939-03-14", "2010-08-26", group=6, space="1982-11-11")
add("John A. Llewellyn", "1933-04-22", "2013-07-02", group=6)
add("Story Musgrave", "1935-08-19", group=6, space="1983-04-04", notes="A self-labeled, unverified 2026 death claim was rejected; current institutional/reference records supported alive at censor.")
add("Brian T. O'Leary", "1940-01-27", "2011-07-28", group=6)
add("Robert A. R. Parker", "1936-12-14", group=6, space="1983-11-28")
add("William E. Thornton", "1929-04-14", "2021-01-11", group=6, space="1983-08-30")

add("Karol J. Bobko", "1937-12-23", "2023-08-17", group=7, selection="1966-06-17", space="1983-04-04", mol=1)
add("Robert L. Crippen", "1937-09-11", group=7, selection="1966-06-17", space="1981-04-12", mol=1)
add("C. Gordon Fullerton", "1936-10-11", "2013-08-21", group=7, selection="1966-06-17", space="1982-03-22", mol=1)
add("Henry W. Hartsfield Jr.", "1933-11-21", "2014-07-17", group=7, selection="1966-06-17", space="1982-06-27", mol=1)
add("Robert F. Overmyer", "1936-07-14", "1996-03-22", group=7, selection="1966-06-17", space="1982-11-11", mol=1, notes="Died in an aircraft accident after the frozen pre-1970 accident cutoff.")
add("Donald H. Peterson", "1933-10-22", "2018-05-27", group=7, selection="1967-06-30", space="1983-04-04", mol=1)
add("Richard H. Truly", "1937-11-12", "2024-02-27", group=7, selection="1965-11-12", space="1981-11-12", mol=1)

# X-15 pilots not already in NASA groups 1-7.
add("Albert Scott Crossfield", "1921-10-02", "2006-04-19", x15=1, selection="", source=EXTRA_SOURCE["Albert Scott Crossfield"], notes="X-15 pilot selection predates the frozen NASA astronaut classes; exact formal roster date was not established. Died in an aircraft accident after the frozen pre-1970 cutoff.", confidence="medium")
add("Joseph A. Walker", "1921-02-20", "1966-06-08", x15=1, selection="", space="1963-01-17", accident=1, source=EXTRA_SOURCE["Joseph A. Walker"], notes="Exact X-15 selection day was not established.")
add("Robert M. White", "1924-07-06", "2010-03-17", x15=1, selection="", space="1962-07-17", source=EXTRA_SOURCE["Robert M. White"], notes="Exact X-15 selection day was not established.", confidence="medium")
add("Forrest S. Petersen", "1922-05-16", "1990-12-08", x15=1, selection="", source=EXTRA_SOURCE["Forrest S. Petersen"], notes="Exact X-15 selection day was not established.", confidence="medium")
add("John B. McKay", "1922-12-08", "1975-04-27", x15=1, selection="", space="1965-09-28", source=EXTRA_SOURCE["John B. McKay"], notes="Exact X-15 selection day was not established.", confidence="medium")
add("Robert A. Rushworth", "1924-10-09", "1993-03-18", x15=1, selection="", space="1963-06-27", source=EXTRA_SOURCE["Robert A. Rushworth"], notes="National Aviation Hall of Fame and death-index/obituary-derived references support March 18; one NASA image page says March 17. Exact X-15 selection day was not established.", confidence="medium")
add("Milton O. Thompson", "1926-05-04", "1993-08-06", x15=1, dyna=1, selection="", source=EXTRA_SOURCE["Milton O. Thompson"], notes="NASA identifies him as the sole NASA X-20 test pilot, selected in 1962; exact selection day was not established.")
add("William J. Knight", "1929-11-18", "2004-05-07", x15=1, dyna=1, selection="", space="1967-10-17", source=EXTRA_SOURCE["William J. Knight"], notes="Selected for the initial Dyna-Soar cadre in April 1960; exact day was not established.")
add("William H. Dana", "1930-11-03", "2014-05-06", x15=1, dyna=1, selection="", space="1966-11-01", source=EXTRA_SOURCE["William H. Dana"], notes="Selected for the initial Dyna-Soar cadre in April 1960; exact day was not established.")
add("Michael J. Adams", "1930-05-05", "1967-11-15", x15=1, mol=1, selection="1965-11-12", space="1967-11-15", accident=1, source=EXTRA_SOURCE["Michael J. Adams"])

# Dyna-Soar/X-20 pilots not already represented.
add("Henry C. Gordon", "1925-12-23", "1996-09-24", dyna=1, selection="", source=EXTRA_SOURCE["Henry C. Gordon"], notes="Selected for the initial Dyna-Soar cadre in April 1960; exact day was not established.", confidence="medium")
add("Russell L. Rogers", "1928-04-12", "1967-09-13", dyna=1, selection="", accident=1, source=EXTRA_SOURCE["Russell L. Rogers"], notes="Selected for the initial Dyna-Soar cadre in April 1960; exact day was not established. Death followed an F-105 engine failure/ejection accident.", confidence="medium")
add("James W. Wood", "1924-08-09", "1990-01-01", dyna=1, selection="", source=EXTRA_SOURCE["James W. Wood"], notes="Selected for the initial Dyna-Soar cadre in April 1960; exact day was not established.", confidence="medium")
add("Albert H. Crews Jr.", "1929-03-23", "2025-06-07", dyna=1, mol=1, selection="1962-04-20", source=EXTRA_SOURCE["Albert H. Crews Jr."], notes="Dyna-Soar designee and later MOL Group 1 member; never flew in space.", confidence="medium")

# MOL selectees not already represented.
add("John L. Finley", "1935-12-22", "2006-09-19", mol=1, selection="1965-11-12", source=EXTRA_SOURCE["John L. Finley"], confidence="medium")
add("Richard E. Lawyer", "1932-11-08", "2005-11-12", mol=1, selection="1965-11-12", source=EXTRA_SOURCE["Richard E. Lawyer"], confidence="medium")
add("Lachlan Macleay", "1931-06-13", mol=1, selection="1965-11-12", source=EXTRA_SOURCE["Lachlan Macleay"], confidence="medium")
add("Francis G. Neubeck", "1932-04-11", mol=1, selection="1965-11-12", source=EXTRA_SOURCE["Francis G. Neubeck"], confidence="medium")
add("James M. Taylor", "1930-11-27", "1970-09-04", mol=1, selection="1965-11-12", source=EXTRA_SOURCE["James M. Taylor"], notes="Died in a T-38 crash after the frozen pre-1970 cutoff.", confidence="medium")
add("James A. Abrahamson", "1933-05-19", mol=1, selection="1967-06-30", source=EXTRA_SOURCE["James A. Abrahamson"])
add("Robert T. Herres", "1932-12-01", "2008-07-24", mol=1, selection="1967-06-30", source=EXTRA_SOURCE["Robert T. Herres"], confidence="medium")
add("Robert H. Lawrence Jr.", "1935-10-02", "1967-12-08", mol=1, selection="1967-06-30", accident=1, source=EXTRA_SOURCE["Robert H. Lawrence Jr."])


COLUMNS = [
    "person_id",
    "full_name",
    "search_disambiguator",
    "birth_date",
    "death_date",
    "vital_status_20260601",
    "first_selection_date",
    "first_spaceflight_date",
    "apollo_flew",
    "apollo_missions",
    "apollo1_crew",
    "core_nasa_non_apollo",
    "military_x15",
    "military_dyna_soar",
    "military_mol",
    "other_all",
    "pre1970_accidental_death",
    "backup_crew_roles",
    "membership_source_urls",
    "birth_source_url",
    "death_source_url",
    "confidence",
    "notes",
]

STAGE.mkdir(exist_ok=True)
with (STAGE / "cohort.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)

source_rows: list[dict[str, str]] = []


def log_source(
    person_id: str,
    query: str,
    url: str,
    fact: str,
    tier: str,
    *,
    opened: str,
    result: str,
    notes: str = "",
) -> None:
    source_rows.append(
        {
            "timestamp": FETCHED_AT,
            "person_id": person_id,
            "query_or_direct_navigation": query,
            "result_rank": "",
            "url": url,
            "opened": opened,
            "access_result": result,
            "fact_supported": fact,
            "source_tier": tier,
            "notes": notes,
        }
    )


for row in rows:
    pid = row["person_id"]
    name = row["full_name"]
    for url in row["membership_source_urls"].split("|"):
        if url:
            log_source(pid, f"direct roster navigation for {name}", url, "frozen roster membership and/or Apollo flight membership", "official", opened="1", result="opened")
    birth_tier = "official" if ("nasa.gov" in row["birth_source_url"] or ".af.mil" in row["birth_source_url"]) else "reference"
    birth_opened = "1" if row["birth_source_url"] == FACTBOOK else "0"
    log_source(
        pid,
        f"{name} birth date {row['search_disambiguator']}",
        row["birth_source_url"],
        f"birth_date={row['birth_date']}",
        birth_tier,
        opened=birth_opened,
        result="opened" if birth_opened == "1" else "web_search_result_fetched",
    )
    if row["first_selection_date"]:
        if row["military_mol"] == "1" and row["first_selection_date"] in {"1965-11-12", "1966-06-17", "1967-06-30"}:
            selection_url = MOL
        elif row["military_dyna_soar"] == "1" and not row["core_nasa_non_apollo"] == "1":
            selection_url = DYNA
        else:
            selection_url = FACTBOOK
        log_source(
            pid,
            f"{name} first formal roster selection date",
            selection_url,
            f"first_selection_date={row['first_selection_date']}",
            "official",
            opened="1",
            result="opened",
        )
    if row["first_spaceflight_date"]:
        flight_url = X15 if row["military_x15"] == "1" and row["first_spaceflight_date"] < "1968-01-01" else FACTBOOK
        log_source(
            pid,
            f"{name} first qualifying spaceflight date",
            flight_url,
            f"first_spaceflight_date={row['first_spaceflight_date']}",
            "official",
            opened="1",
            result="opened",
        )
    if row["death_date"]:
        death_tier = "official" if ("nasa.gov" in row["death_source_url"] or ".af.mil" in row["death_source_url"]) else ("major_reference" if any(host in row["death_source_url"] for host in ("latimes.com", "collectspace.com", "nationalaviation.org")) else "reference")
        log_source(
            pid,
            f"{name} death date {row['search_disambiguator']}",
            row["death_source_url"],
            f"death_date={row['death_date']}; vital_status_20260601=dead",
            death_tier,
            opened="1" if row["death_source_url"] == FACTBOOK else "0",
            result="opened" if row["death_source_url"] == FACTBOOK else "web_search_result_fetched",
        )
        if row["pre1970_accidental_death"] == "1":
            log_source(
                pid,
                f"{name} accident circumstance and date",
                row["death_source_url"],
                "pre1970_accidental_death=1",
                death_tier,
                opened="1" if row["death_source_url"] == FACTBOOK else "0",
                result="opened" if row["death_source_url"] == FACTBOOK else "web_search_result_fetched",
            )
    else:
        current_url = CURRENT[name]
        tier = "official" if ("nasa.gov" in current_url or ".af.mil" in current_url) else "reference"
        log_source(
            pid,
            f"{name} alive 2024 2025 2026 {row['search_disambiguator']} -obituary",
            current_url,
            "targeted living-person search; no verified death through censor; vital_status_20260601=alive",
            tier,
            opened="0",
            result="web_search_result_fetched",
            notes="Direction-neutral targeted search used name plus disambiguator; same-name and unsupported death claims were rejected where encountered.",
        )
    if row["backup_crew_roles"]:
        missions = sorted(set(re.findall(r"Apollo \d+", row["backup_crew_roles"])), key=lambda x: int(x.split()[1]))
        for mission in missions:
            log_source(
                pid,
                f"official {mission} backup crew {name}",
                MISSION_BACKUP_URL[mission],
                f"backup_crew_roles includes {mission}",
                "official",
                opened="0",
                result="web_search_result_fetched",
            )

SOURCE_COLUMNS = [
    "timestamp",
    "person_id",
    "query_or_direct_navigation",
    "result_rank",
    "url",
    "opened",
    "access_result",
    "fact_supported",
    "source_tier",
    "notes",
]
with (STAGE / "SOURCE_LOG.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=SOURCE_COLUMNS)
    writer.writeheader()
    writer.writerows(source_rows)

print(f"wrote {len(rows)} cohort rows and {len(source_rows)} source-log rows")
