#!/usr/bin/env python3
"""V1 combined fetch + extract script (predecessor to 01+02 split).
Source: <workspace>/projects/apollo-aging-anomaly/fetch_astronaut_data.py
Conversation: early build (pre-May 18).

This was the original all-in-one script that both fetched Wikipedia articles and
extracted structured data. It was later split into 01_fetch_articles.py and
02_extract_dataset.py for cleaner separation of concerns. Both V1 scripts are
superseded by the V2 clean-room build (May 18).
"""

import csv
import json
import re
import time
import sys
from datetime import datetime, date
from pathlib import Path
from urllib.parse import unquote, quote

import requests
from bs4 import BeautifulSoup

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "us-astronaut-groups-1-7.tsv"
OUTPUT_FILE = PROJECT_DIR / "astronaut-dataset.tsv"
CACHE_FILE = PROJECT_DIR / ".wiki-cache.json"

HEADERS = {"User-Agent": "ApolloAgingResearch/1.0 (personal research project)"}

MOON_WALKERS = {
    "Neil Armstrong", "Buzz Aldrin", "Pete Conrad", "Alan Bean",
    "Alan Shepard", "Edgar Mitchell", "David Scott", "James Irwin",
    "John Young", "Charles Duke", "Eugene Cernan", "Harrison Schmitt"
}

BEYOND_LEO = MOON_WALKERS | {
    "Frank Borman", "Jim Lovell", "William Anders",
    "Thomas P. Stafford", "John Young", "Eugene Cernan",
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
    "Robert Overmyer": "aircraft crash",
    "Scott Crossfield": "private plane crash",
    "William Anders": "private plane crash",
    "Pete Conrad": "motorcycle accident",
}

KNOWN_DEATHS = {
    "Jack Swigert": (date(1982, 12, 27), "cancer (bone marrow)"),
    "Clifton Williams": (date(1967, 10, 5), "T-38 crash"),
    "Edward Givens": (date(1967, 6, 6), "automobile accident"),
}

KNOWN_DOB = {
    "Clifton Williams": date(1932, 9, 26),
    "Edward Gibson": date(1936, 11, 8),
    "Joseph Kerwin": date(1932, 2, 19),
    "John S. Bull": date(1934, 9, 25),
    "Paul Weitz": date(1932, 7, 25),
    "James M. Taylor": date(1930, 3, 10),
    "Donald Peterson": date(1933, 10, 22),
    "Philip Chapman": date(1935, 3, 5),
    "William B. Lenoir": date(1939, 3, 14),
    "William Thornton": date(1929, 4, 14),
    "Donald H. Peterson": date(1933, 10, 22),
}

KNOWN_DOD = {
    "Clifton Williams": date(1967, 10, 5),
    "Paul Weitz": date(2017, 10, 22),
    "John S. Bull": date(2008, 8, 11),
    "William B. Lenoir": date(2010, 8, 28),
    "William Thornton": date(2021, 1, 11),
    "Donald Peterson": date(2018, 5, 27),
    "Donald H. Peterson": date(2018, 5, 27),
    "Jack Swigert": date(1982, 12, 27),
}

TODAY = date(2026, 4, 23)

# NOTE: Full implementation omitted for brevity -- see the original file at
# <workspace>/projects/apollo-aging-anomaly/fetch_astronaut_data.py
# This script is archived here for provenance tracking.
print("This is an archived V1 script. See the original file for full implementation.")
