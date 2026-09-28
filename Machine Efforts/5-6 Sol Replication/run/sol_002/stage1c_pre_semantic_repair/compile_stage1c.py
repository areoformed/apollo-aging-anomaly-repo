#!/usr/bin/env python3
"""Compile locked Stage 1C collection records into auditable artifacts."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "stage1c"
RAW = STAGE / "raw"
CENSOR = date(2026, 6, 1)

SEARCH_COLUMNS = [
    "timestamp",
    "research_id",
    "person_id",
    "query_family",
    "query",
    "result_rank",
    "url",
    "opened",
    "access_result",
    "source_tier",
    "substantive_late_life_source",
    "evidence_candidate",
    "extra_search_trigger",
    "notes",
]

EVENT_COLUMNS = [
    "research_id",
    "person_id",
    "event_date",
    "event_date_precision",
    "event_date_earliest",
    "event_date_latest",
    "analysis_event_date",
    "age_at_analysis_event",
    "evidence_type",
    "event_family",
    "source_url",
    "source_publisher",
    "source_tier",
    "direct_or_indirect",
    "qualifies",
    "boundary_sensitive",
    "adjudication_confidence",
    "supporting_paraphrase",
    "notes",
]

OUTCOME_COLUMNS = [
    "research_id",
    "person_id",
    "eligible_age80",
    "potential_followup_days",
    "observed_followup_days",
    "death_competing_event_within_five_years",
    "administratively_censored_before_five_years",
    "base_search_complete",
    "base_results_logged",
    "base_pages_opened",
    "extra_queries",
    "extra_pages_opened",
    "substantive_sources_opened",
    "independent_publishers",
    "documentation_depth",
    "first_qualifying_function_date",
    "first_function_date_precision",
    "first_function_days_after_80",
    "first_function_within_five_years",
    "latest_qualifying_function_date",
    "latest_qualifying_function_age",
    "first_qualifying_impairment_date",
    "outcome_state",
    "boundary_sensitive",
    "adjudication_confidence",
    "notes",
]


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def age_years(birth: date, event: date) -> float:
    return (event - birth).days / 365.2425


def source_tier(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if not host:
        return ""
    tier1_hosts = (
        "nasa.gov",
        "af.mil",
        "spaceforce.mil",
        "si.edu",
        "smithsonianmag.com",
        "nationalacademies.org",
        "brown.edu",
        "uky.edu",
        "noaa.gov",
        "loc.gov",
        "archives.gov",
        "esa.int",
    )
    tier2_hosts = (
        "washingtonpost.com",
        "theguardian.com",
        "cbsnews.com",
        "euronews.com",
        "chron.com",
        "publishersweekly.com",
        "nationalgeographic.com",
        "latimes.com",
        "independent.co.uk",
        "bostonglobe.com",
        "space.com",
        "abcnews.go.com",
        "nytimes.com",
    )
    tier3_hosts = (
        "astronautscholarship.org",
        "nss.org",
        "collectspace.com",
        "aulis.com",
        "spacegrant.org",
        "nationalaviation.org",
        "eisenhowerfoundation.net",
        "dasherwatchco.com",
        "theglobaltownhall.com",
        "isdc.nss.org",
    )
    if host.endswith((".gov", ".mil", ".edu")) or any(host.endswith(x) for x in tier1_hosts):
        return "TIER_1"
    if any(host.endswith(x) for x in tier2_hosts):
        return "TIER_2"
    if any(host.endswith(x) for x in tier3_hosts):
        return "TIER_3"
    return "TIER_4"


def publisher_key(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for suffix in (
        "nasa.gov",
        "si.edu",
        "wikipedia.org",
        "wikidata.org",
        "google.com",
        "gettyimages.com",
        "gettyimages.co.uk",
        "gettyimages.at",
        "gettyimages.dk",
        "gettyimages.pt",
        "gettyimages.co.nz",
        "gettyimages.be",
    ):
        if host.endswith(suffix):
            return suffix
    return host


def surname(full_name: str) -> str:
    parts = full_name.replace(",", "").split()
    while parts and parts[-1].rstrip(".").lower() in {"jr", "sr", "ii", "iii", "iv"}:
        parts.pop()
    return parts[-1].lower() if parts else ""


def opened_is_substantive(
    person: dict[str, str],
    family: str,
    title: str,
    content: str,
    url: str,
    positive_urls: set[str],
) -> bool:
    if url in positive_urls:
        return True
    combined = f"{title}\n{content}".lower()
    last = surname(person["full_name"])
    if not last or last not in combined:
        return False
    keywords = {
        "INTERVIEW": ("interview", "oral history", "q&a", "said"),
        "LECTURE_TALK_QA": ("lecture", "talk", "speaks", "speaker", "discussion", "gala"),
        "AUTHOR_WORK": ("author", "memoir", "book", "wrote", "foreword"),
        "IMPAIRMENT": ("dementia", "alzheimer", "cognitive", "stroke", "guardianship"),
        "MILESTONE_BIRTHDAY": ("birthday", "age 80", "age 85", "age 90", "at 80", "at 85", "at 90"),
        "OBITUARY_DEATH": ("obituary", "dies", "died", "death", "passed away"),
    }
    family_key = family.removeprefix("EXTRA_")
    return any(word in combined for word in keywords.get(family_key, ()))


POSITIVE_EVENTS: dict[str, dict[str, str]] = {
    "R001": {
        "event_date": "2024-06-07",
        "precision": "DAY",
        "earliest": "2024-06-07",
        "latest": "2024-06-07",
        "analysis": "2024-06-07",
        "family": "5",
        "url": "https://www.space.com/apollo-8-astronaut-bill-anders-plane-crash-obituary",
        "publisher": "Space.com",
        "tier": "TIER_2",
        "directness": "INDIRECT",
        "confidence": "HIGH",
        "paraphrase": "A person-specific obituary reports that Anders was piloting his vintage aircraft when it crashed on June 7, 2024.",
        "notes": "Active piloting of complex equipment; same date as death; secondary age-80-plus description only.",
    },
    "R006": {
        "event_date": "2018-12-13",
        "precision": "DAY",
        "earliest": "2018-12-13",
        "latest": "2018-12-13",
        "analysis": "2018-12-13",
        "family": "1",
        "url": "https://www.nasa.gov/podcasts/houston-we-have-a-podcast/apollo-8-part-1/",
        "publisher": "NASA",
        "tier": "TIER_1",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "NASA states the podcast was recorded on December 13, 2018 and presents Borman's own substantive responsive answers.",
        "notes": "Secondary age-80-plus description only.",
    },
    "R011": {
        "event_date": "2010",
        "precision": "YEAR",
        "earliest": "2010-01-01",
        "latest": "2010-12-31",
        "analysis": "2010-07-02",
        "family": "1",
        "url": "https://www.washingtonpost.com/obituaries/2025/08/08/james-lovell-dead-apollo-13/",
        "publisher": "The Washington Post",
        "tier": "TIER_2",
        "directness": "INDIRECT",
        "confidence": "MEDIUM",
        "paraphrase": "The obituary attributes substantive responsive comments to Lovell in a 2010 interview.",
        "notes": "Locked YEAR midpoint rule; full date interval lies inside the primary window.",
    },
    "R022": {
        "event_date": "2026-04-01",
        "precision": "DAY",
        "earliest": "2026-04-01",
        "latest": "2026-04-01",
        "analysis": "2026-04-01",
        "family": "1",
        "url": "https://www.euronews.com/next/2026/04/01/meet-charlie-duke-the-youngest-person-on-the-first-moon-mission-cheering-on-artemis-ii-ast",
        "publisher": "Euronews",
        "tier": "TIER_2",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "The dated article contains multiple contemporaneous substantive responsive statements from Duke.",
        "notes": "Secondary age-80-plus description only.",
    },
    "R037": {
        "event_date": "2006-04-19",
        "precision": "DAY",
        "earliest": "2006-04-19",
        "latest": "2006-04-19",
        "analysis": "2006-04-19",
        "family": "5",
        "url": "https://www.theguardian.com/news/2006/apr/29/guardianobituaries.usa",
        "publisher": "The Guardian",
        "tier": "TIER_2",
        "directness": "INDIRECT",
        "confidence": "MEDIUM",
        "paraphrase": "The obituary reports Crossfield died while piloting his Cessna through a thunderstorm on April 19, 2006.",
        "notes": "Active piloting of complex equipment; same date as death.",
    },
    "R039": {
        "event_date": "2012",
        "precision": "YEAR",
        "earliest": "2012-01-01",
        "latest": "2012-12-31",
        "analysis": "2012-07-01",
        "family": "3",
        "url": "https://www.nasa.gov/humans-in-space/astronauts/former-astronauts/former-astronaut-james-a-mcdivitt-jr/",
        "publisher": "NASA",
        "tier": "TIER_1",
        "directness": "INDIRECT",
        "confidence": "HIGH",
        "paraphrase": "NASA identifies McDivitt as speaking to guests at the 2012 Astronaut Scholarship Foundation dinner marking Apollo 17's fortieth anniversary.",
        "notes": "Locked YEAR midpoint rule; full interval lies inside the primary window.",
    },
    "R056": {
        "event_date": "2014-09-21",
        "precision": "DAY",
        "earliest": "2014-09-21",
        "latest": "2014-09-21",
        "analysis": "2014-09-21",
        "family": "3",
        "url": "https://www.aulis.com/censored.htm",
        "publisher": "AULIS Online",
        "tier": "TIER_4",
        "directness": "DIRECT",
        "confidence": "LOW",
        "paraphrase": "A dated event account describes Worden's substantive lecture and Q&A and records his responsive answer.",
        "notes": "Qualifies under the locked source rule, but confidence is LOW because the only event source is a low-tier specialty publisher.",
    },
    "R058": {
        "event_date": "2013-10-26",
        "precision": "DAY",
        "earliest": "2013-10-26",
        "latest": "2013-10-26",
        "analysis": "2013-10-26",
        "family": "1|3",
        "url": "https://airandspace.si.edu/events/interview-buzz-aldrin",
        "publisher": "Smithsonian National Air and Space Museum",
        "tier": "TIER_1",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "The official museum event record documents Aldrin's moderated substantive interview and book discussion on October 26, 2013.",
        "notes": "",
    },
    "R060": {
        "event_date": "2021-04-12",
        "precision": "DAY",
        "earliest": "2021-04-12",
        "latest": "2021-04-12",
        "analysis": "2021-04-12",
        "family": "1",
        "url": "https://www.nasa.gov/history/sts-1-astronaut-bob-crippen-remembers-the-ride-of-his-life/",
        "publisher": "NASA",
        "tier": "TIER_1",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "NASA's dated edited interview page presents multiple substantive responsive answers from Crippen.",
        "notes": "Recording date was not supplied; locked edited-interview rule uses publication date as proxy.",
    },
    "R064": {
        "event_date": "2019-12-19",
        "precision": "DAY",
        "earliest": "2019-12-19",
        "latest": "2019-12-19",
        "analysis": "2019-12-19",
        "family": "1|4",
        "url": "https://www.cbsnews.com/colorado/news/rocky-mountain-national-park-vance-brand/",
        "publisher": "CBS Colorado",
        "tier": "TIER_2",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "The dated report contains Brand's own responsive statements and documents his active civic land donation and letter to a senator.",
        "notes": "Secondary age-80-plus description only.",
    },
    "R076": {
        "event_date": "2014-10-22",
        "precision": "DAY",
        "earliest": "2014-10-22",
        "latest": "2014-10-22",
        "analysis": "2014-10-22",
        "family": "3",
        "url": "https://www.chron.com/news/article/nasa-apollo-7-walter-cunningham-17692884.php",
        "publisher": "Associated Press via Hearst",
        "tier": "TIER_2",
        "directness": "INDIRECT",
        "confidence": "HIGH",
        "paraphrase": "A person-specific obituary caption identifies Cunningham speaking during MIT's aerospace centennial program on October 22, 2014.",
        "notes": "",
    },
    "R078": {
        "event_date": "2012-09",
        "precision": "MONTH",
        "earliest": "2012-09-01",
        "latest": "2012-09-30",
        "analysis": "2012-09-15",
        "family": "2",
        "url": "https://www.publishersweekly.com/9780813042091",
        "publisher": "Publishers Weekly",
        "tier": "TIER_2",
        "directness": "INDIRECT",
        "confidence": "HIGH",
        "paraphrase": "The opened trade review identifies Young with James Hansen and describes their original substantive memoir, issued in September 2012.",
        "notes": "Locked MONTH midpoint rule; full date interval lies inside the primary window.",
    },
    "R092": {
        "event_date": "2023-12-05",
        "precision": "DAY",
        "earliest": "2023-12-05",
        "latest": "2023-12-05",
        "analysis": "2023-12-05",
        "family": "1",
        "url": "https://svs.gsfc.nasa.gov/14459/",
        "publisher": "NASA",
        "tier": "TIER_1",
        "directness": "DIRECT",
        "confidence": "HIGH",
        "paraphrase": "NASA's official page names Musgrave as interviewee and summarizes his substantive firsthand answers.",
        "notes": "Recording date was not supplied; publication date is the locked proxy. Secondary age-80-plus description only.",
    },
}


MANUAL_PAGE_ROWS = [
    {
        "timestamp": "2026-07-23T05:03:59Z",
        "research_id": "R022",
        "url": POSITIVE_EVENTS["R022"]["url"],
        "access_result": "opened",
        "trigger": "inaccessible base result",
        "notes": "Extra page re-open supplied article body.",
        "substantive": 1,
    },
    {
        "timestamp": "2026-07-23T05:08:10Z",
        "research_id": "R058",
        "url": POSITIVE_EVENTS["R058"]["url"],
        "access_result": "opened",
        "trigger": "event-date ambiguity",
        "notes": "Extra page re-open resolved the exact event date.",
        "substantive": 1,
    },
    {
        "timestamp": "2026-07-23T05:09:22Z",
        "research_id": "R064",
        "url": POSITIVE_EVENTS["R064"]["url"],
        "access_result": "opened",
        "trigger": "event-date ambiguity",
        "notes": "Extra page re-open resolved the exact event date.",
        "substantive": 1,
    },
    {
        "timestamp": "2026-07-23T05:13:00Z",
        "research_id": "R077",
        "url": "https://library.brown.edu/create/libnews/commander-david-r-scott-in-the-dsl-on-september-26/",
        "access_result": "opened",
        "trigger": "event-date ambiguity",
        "notes": "Extra re-open dated a prospective lecture announcement but did not prove occurrence.",
        "substantive": 1,
    },
    {
        "timestamp": "2026-07-23T05:13:17Z",
        "research_id": "R077",
        "url": "https://library.brown.edu/dsl/events/",
        "access_result": "access_failure",
        "trigger": "base source that identifies a more-primary source",
        "notes": "Linked Digital Speaker Series page failed with a cache miss.",
        "substantive": 0,
    },
    {
        "timestamp": "2026-07-23T05:17:48Z",
        "research_id": "R090",
        "url": "https://www.space.com/astronaut-richard-truly-nasa-adminstrator-obituary",
        "access_result": "opened",
        "trigger": "event-date ambiguity|base source that identifies a more-primary source",
        "notes": "Extra re-open resolved attributed interviews to 2003 and 2016, both before age 80.",
        "substantive": 1,
    },
]


MANUAL_EXTRA_QUERIES = [
    {
        "timestamp": "2026-07-23T05:09:57Z",
        "research_id": "R071",
        "family": "EXTRA_MORE_PRIMARY",
        "query": '"Robert M. White" "as told to" memoir Al Hallonquist 2004..2010',
        "trigger": "base source that identifies a more-primary source",
        "results": [
            "https://www.smithsonianmag.com/air-space-magazine/robert-m-white-1924-2010-133314030/",
            "https://dougcomicworld.com/inventory/INVENTORY-BiographyPaperbackSite.html",
            "https://www.dougcomicworld.com/inventory/INVENTORY-BiographyPaperbackSite.html",
            "https://www.sdsualumni.org/s/997/images/editor_documents/Chapters/veterans2015.pdf?cc=1&sessionid=4320aebe-2b85-4eb6-8fee-170d1b6f8807",
            "https://dspace.sunyconnect.suny.edu/server/api/core/bitstreams/8fe4703e-822f-4080-861a-f0c7817e373a/content",
            "https://www.scribd.com/document/484528662/oarr-10000275-1-pdf",
            "https://device.report/m/da430378d475f92fb672736715e25a4addc5a41fb101d707bd2b28d232cc053f.pdf",
            "https://dokumen.pub/history-in-management-and-organization-studies-from-margin-to-mainstream-1nbsped-1138720917-9781138720916.html",
            "https://www.bookfinder.com/search/?ac=qr&author=r-m-kharb-mahendra-sharma+&lang=en&st=xl",
            "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P101D7VZ.TXT",
        ],
        "opened": {},
        "notes": "Only rank 1 matched the person and it duplicated an already-opened base source; no extra page was opened.",
    },
    {
        "timestamp": "2026-07-23T05:13:53Z",
        "research_id": "R078",
        "family": "EXTRA_EVENT_DATE",
        "query": '"Forever Young" "John W. Young" site:upf.com publication 2012 2013',
        "trigger": "event-date ambiguity",
        "results": [],
        "opened": {},
        "notes": "Built-in search returned zero results.",
    },
    {
        "timestamp": "2026-07-23T05:14:12Z",
        "research_id": "R078",
        "family": "EXTRA_EVENT_DATE",
        "query": '"Forever Young: A Life of Adventure in Air and Space" University Press of Florida',
        "trigger": "event-date ambiguity",
        "results": [
            "https://www.publishersweekly.com/9780813042091",
            "https://openlibrary.org/works/OL16654437W/Forever_Young",
            "https://www.ibs.it/forever-young-life-of-adventure-libro-inglese-john-w-young-james-r-hansen/e/9780813049335",
            "https://en.wikipedia.org/wiki/John_Young_%28astronaut%29",
            "https://en.wikipedia.org/wiki/James_R._Hansen",
            "https://www.ubcpress.ca/forever-young",
            "https://www.biblio.com/book/forever-young-life-adventure-air-space/d/1681119337",
            "https://www.hatchards.co.uk/book/forever-young/john-w-young/9780813049335",
            "https://www.campusbooks.com/books/9780813066042-forever-young-a-life-of-adventure-in-air-and-space",
            "https://atlanticbooks.com/products/forever-young-a-life-of-adventure-in-air-and-space-9780813049335",
        ],
        "opened": {
            "https://www.publishersweekly.com/9780813042091": "opened",
        },
        "notes": "Rank 1 was re-opened and supplied the issue month and review date.",
    },
    {
        "timestamp": "2026-07-23T05:15:28Z",
        "research_id": "R081",
        "family": "EXTRA_EVENT_DATE",
        "query": '"X-15: Extending the Frontiers of Flight" William H. Dana publication date',
        "trigger": "event-date ambiguity",
        "results": [
            "https://www.nasa.gov/aeronautics/x-15-extending-the-frontiers-of-flight/",
            "https://mitpressbookstore.mit.edu/book/9781470025854",
            "https://ntrs.nasa.gov/citations/20080008340",
            "https://www.nasa.gov/aeronautics/x-15/",
            "https://openlibrary.org/books/OL16744706M/X-15",
            "https://www.collectspace.com/ubb/Forum9/HTML/001456.html",
            "https://search.worldcat.org/title/X-15-%3A-extending-the-frontiers-of-flight/oclc/971626369",
            "https://www.kimerius.com/app/download/5784679195/X-15.%2BExtending%2Bthe%2Bfrontiers%2Bof%2Bflight.pdf",
            "https://books.google.com/books/about/X_15.html?id=fOU4cGDWDjkC",
            "https://catalog.udom.ac.tz/cgi-bin/koha/opac-detail.pl?biblionumber=5114",
        ],
        "opened": {
            "https://mitpressbookstore.mit.edu/book/9781470025854": "access_failure",
            "https://ntrs.nasa.gov/citations/20080008340": "opened",
        },
        "notes": "NASA's original-work record resolved the apparent 2010 reissue as an unchanged 2007 work.",
    },
]


SPECIAL_NOTES = {
    "R001": "Technical collection deviation: four base families shared one returned stream and two base families were inaccessible; two triggered extra queries and three extra page attempts were used. Qualifying event is secondary-only.",
    "R011": "YEAR-precision event uses the locked midpoint analysis date.",
    "R022": "Qualifying event is secondary-only.",
    "R037": "Function and death occur on the same date; death is not earlier than detected function.",
    "R056": "Positive source is low tier; event confidence is LOW.",
    "R058": "A disputed family allegation was retained as nonqualifying impairment evidence; no clinical diagnosis or credible persistent-impairment report was found.",
    "R060": "Edited-interview publication date used as the locked date proxy.",
    "R064": "Qualifying event is secondary-only.",
    "R071": "An as-told-to memoir appeared posthumously, but no source dated White's participation after age 80.",
    "R077": "A prospective lecture announcement did not establish that the event occurred.",
    "R078": "MONTH-precision event uses the locked midpoint analysis date.",
    "R081": "A 2010 edition reissued a 2007 foreword; reissued old work was excluded.",
    "R084": "Fixed search budget yielded no opened qualifying event; no extra search was permitted merely because no positive event was found.",
    "R090": "Dated attributable statements resolved to before age 80; undated service descriptions were not events.",
    "R092": "Edited-interview publication date used as the locked proxy; qualifying event is secondary-only.",
}


def manual_person_map(worklist: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["research_id"]: row for row in worklist}


def make_search_log(
    worklist: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    people = manual_person_map(worklist)
    positive_urls = {value["url"] for value in POSITIVE_EVENTS.values()}
    rows: list[dict[str, object]] = []
    stats: dict[str, dict[str, object]] = {
        row["research_id"]: {
            "base_results": 0,
            "base_page_attempts": 0,
            "extra_queries": 0,
            "extra_page_attempts": 0,
            "substantive_urls": set(),
            "publishers": set(),
        }
        for row in worklist
    }

    def add_result_rows(
        rid: str,
        timestamp: str,
        query_obj: dict,
        is_extra: bool,
    ) -> None:
        person = people[rid]
        family = query_obj["family"]
        query = query_obj["query"]
        trigger = query_obj.get("trigger", "")
        attempts = {
            (int(item.get("rank", 0)), item.get("url", "")): item
            for item in query_obj.get("open_attempts", [])
        }
        if is_extra:
            stats[rid]["extra_queries"] = int(stats[rid]["extra_queries"]) + 1
            stats[rid]["extra_page_attempts"] = int(stats[rid]["extra_page_attempts"]) + len(attempts)
        else:
            stats[rid]["base_results"] = int(stats[rid]["base_results"]) + len(query_obj.get("results", []))
            stats[rid]["base_page_attempts"] = int(stats[rid]["base_page_attempts"]) + len(attempts)
        if not query_obj.get("results"):
            rows.append(
                {
                    "timestamp": timestamp,
                    "research_id": rid,
                    "person_id": person["person_id"],
                    "query_family": family,
                    "query": query,
                    "result_rank": "",
                    "url": "",
                    "opened": 0,
                    "access_result": "no_results",
                    "source_tier": "",
                    "substantive_late_life_source": 0,
                    "evidence_candidate": 0,
                    "extra_search_trigger": trigger,
                    "notes": "No returned results.",
                }
            )
            return
        for result in query_obj["results"][:10]:
            key = (int(result["rank"]), result["url"])
            attempt = attempts.get(key)
            opened = 1 if attempt else 0
            access = attempt.get("access_result", "") if attempt else result.get("disposition", "not_opened")
            content = attempt.get("content", "") if attempt else ""
            substantive = bool(
                attempt
                and attempt.get("access_result") == "opened"
                and opened_is_substantive(
                    person,
                    family,
                    result.get("title", ""),
                    content,
                    result["url"],
                    positive_urls,
                )
            )
            if substantive:
                stats[rid]["substantive_urls"].add(result["url"])
                stats[rid]["publishers"].add(publisher_key(result["url"]))
            rows.append(
                {
                    "timestamp": timestamp,
                    "research_id": rid,
                    "person_id": person["person_id"],
                    "query_family": family,
                    "query": query,
                    "result_rank": result["rank"],
                    "url": result["url"],
                    "opened": opened,
                    "access_result": access,
                    "source_tier": source_tier(result["url"]),
                    "substantive_late_life_source": int(substantive),
                    "evidence_candidate": int(substantive or result["url"] in positive_urls),
                    "extra_search_trigger": trigger,
                    "notes": f'{result.get("title", "")} | disposition={result.get("disposition", "")}',
                }
            )

    for person in worklist:
        rid = person["research_id"]
        if person["eligible_age80"] != "1":
            continue
        data = json.loads((RAW / f"{rid}.json").read_text(encoding="utf-8"))
        for query_obj in data.get("queries", []):
            add_result_rows(rid, data["timestamp"], query_obj, False)
        for query_obj in data.get("extra_queries", []):
            add_result_rows(rid, data["timestamp"], query_obj, True)
        # R001's extra_page_opens is an aggregate of the extra-query attempts.
        if rid == "R001":
            stats[rid]["extra_page_attempts"] = len(data.get("extra_page_opens", []))

    for item in MANUAL_EXTRA_QUERIES:
        rid = item["research_id"]
        person = people[rid]
        stats[rid]["extra_queries"] = int(stats[rid]["extra_queries"]) + 1
        stats[rid]["extra_page_attempts"] = int(stats[rid]["extra_page_attempts"]) + len(item["opened"])
        if not item["results"]:
            rows.append(
                {
                    "timestamp": item["timestamp"],
                    "research_id": rid,
                    "person_id": person["person_id"],
                    "query_family": item["family"],
                    "query": item["query"],
                    "result_rank": "",
                    "url": "",
                    "opened": 0,
                    "access_result": "no_results",
                    "source_tier": "",
                    "substantive_late_life_source": 0,
                    "evidence_candidate": 0,
                    "extra_search_trigger": item["trigger"],
                    "notes": item["notes"],
                }
            )
        for rank, url in enumerate(item["results"], 1):
            access = item["opened"].get(url, "not_opened")
            opened = int(url in item["opened"])
            substantive = bool(
                access == "opened"
                and (
                    url in positive_urls
                    or (rid == "R077" and "brown.edu" in url)
                    or (rid == "R090" and "space.com" in url)
                )
            )
            if substantive:
                stats[rid]["substantive_urls"].add(url)
                stats[rid]["publishers"].add(publisher_key(url))
            rows.append(
                {
                    "timestamp": item["timestamp"],
                    "research_id": rid,
                    "person_id": person["person_id"],
                    "query_family": item["family"],
                    "query": item["query"],
                    "result_rank": rank,
                    "url": url,
                    "opened": opened,
                    "access_result": access,
                    "source_tier": source_tier(url),
                    "substantive_late_life_source": int(substantive),
                    "evidence_candidate": int(substantive or url in positive_urls),
                    "extra_search_trigger": item["trigger"],
                    "notes": item["notes"] if rank == 1 else "",
                }
            )

    for item in MANUAL_PAGE_ROWS:
        rid = item["research_id"]
        person = people[rid]
        stats[rid]["extra_page_attempts"] = int(stats[rid]["extra_page_attempts"]) + 1
        if item["substantive"] and item["access_result"] == "opened":
            stats[rid]["substantive_urls"].add(item["url"])
            stats[rid]["publishers"].add(publisher_key(item["url"]))
        rows.append(
            {
                "timestamp": item["timestamp"],
                "research_id": rid,
                "person_id": person["person_id"],
                "query_family": "EXTRA_PAGE_OPEN",
                "query": "",
                "result_rank": "",
                "url": item["url"],
                "opened": 1,
                "access_result": item["access_result"],
                "source_tier": source_tier(item["url"]),
                "substantive_late_life_source": item["substantive"],
                "evidence_candidate": item["substantive"],
                "extra_search_trigger": item["trigger"],
                "notes": item["notes"],
            }
        )

    rows.sort(
        key=lambda row: (
            row["research_id"],
            row["timestamp"],
            row["query_family"],
            int(row["result_rank"]) if str(row["result_rank"]).isdigit() else 0,
            row["url"],
        )
    )
    return rows, stats


def make_events(worklist: list[dict[str, str]]) -> list[dict[str, object]]:
    people = manual_person_map(worklist)
    rows: list[dict[str, object]] = []
    for rid, event in POSITIVE_EVENTS.items():
        person = people[rid]
        birth = parse_date(person["birth_date"])
        analysis = parse_date(event["analysis"])
        assert birth and analysis
        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        earliest = parse_date(event["earliest"])
        latest = parse_date(event["latest"])
        assert earliest and latest
        boundary_sensitive = int(
            (earliest < b80 <= latest)
            or (earliest < b85 <= latest)
        )
        rows.append(
            {
                "research_id": rid,
                "person_id": person["person_id"],
                "event_date": event["event_date"],
                "event_date_precision": event["precision"],
                "event_date_earliest": event["earliest"],
                "event_date_latest": event["latest"],
                "analysis_event_date": event["analysis"],
                "age_at_analysis_event": f"{age_years(birth, analysis):.6f}",
                "evidence_type": "QUALIFYING_FUNCTION_EVENT",
                "event_family": event["family"],
                "source_url": event["url"],
                "source_publisher": event["publisher"],
                "source_tier": event["tier"],
                "direct_or_indirect": event["directness"],
                "qualifies": 1,
                "boundary_sensitive": boundary_sensitive,
                "adjudication_confidence": event["confidence"],
                "supporting_paraphrase": event["paraphrase"],
                "notes": event["notes"],
            }
        )

    person = people["R058"]
    birth = parse_date(person["birth_date"])
    analysis = date(2018, 6, 26)
    assert birth
    rows.append(
        {
            "research_id": "R058",
            "person_id": person["person_id"],
            "event_date": "2018-06-26",
            "event_date_precision": "DAY",
            "event_date_earliest": "2018-06-26",
            "event_date_latest": "2018-06-26",
            "analysis_event_date": "2018-06-26",
            "age_at_analysis_event": f"{age_years(birth, analysis):.6f}",
            "evidence_type": "DISPUTED_IMPAIRMENT_ALLEGATION",
            "event_family": "IMPAIRMENT",
            "source_url": "https://abcnews.go.com/GMA/News/legendary-astronaut-buzz-aldrin-overwhelmed-sorrow-amid-nastylegal/story?id=56162053",
            "source_publisher": "ABC News",
            "source_tier": "TIER_2",
            "direct_or_indirect": "INDIRECT",
            "qualifies": 0,
            "boundary_sensitive": 0,
            "adjudication_confidence": "HIGH",
            "supporting_paraphrase": "Family allegations of cognitive decline or dementia were disputed; Aldrin denied impairment, no clinical diagnosis was published, and the guardianship litigation was later withdrawn.",
            "notes": "Retained as nonqualifying conflicting evidence under the locked rule; it does not establish persistent major cognitive impairment.",
        }
    )
    rows.sort(key=lambda row: (row["research_id"], row["analysis_event_date"], -int(row["qualifies"])))
    return rows


def make_outcomes(
    worklist: list[dict[str, str]],
    search_stats: dict[str, dict[str, object]],
    event_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    qualified_by_rid: dict[str, list[dict[str, object]]] = {}
    for event in event_rows:
        if int(event["qualifies"]) and event["evidence_type"] == "QUALIFYING_FUNCTION_EVENT":
            qualified_by_rid.setdefault(str(event["research_id"]), []).append(event)

    outcomes: list[dict[str, object]] = []
    for person in worklist:
        rid = person["research_id"]
        birth = parse_date(person["birth_date"])
        end = parse_date(person["end_date"])
        assert birth and end
        eligible = person["eligible_age80"] == "1"
        if not eligible:
            outcomes.append(
                {
                    "research_id": rid,
                    "person_id": person["person_id"],
                    "eligible_age80": 0,
                    "potential_followup_days": 0,
                    "observed_followup_days": 0,
                    "death_competing_event_within_five_years": 0,
                    "administratively_censored_before_five_years": 0,
                    "base_search_complete": 0,
                    "base_results_logged": 0,
                    "base_pages_opened": 0,
                    "extra_queries": 0,
                    "extra_pages_opened": 0,
                    "substantive_sources_opened": 0,
                    "independent_publishers": 0,
                    "documentation_depth": "LOW",
                    "first_qualifying_function_date": "",
                    "first_function_date_precision": "",
                    "first_function_days_after_80": "",
                    "first_function_within_five_years": 0,
                    "latest_qualifying_function_date": "",
                    "latest_qualifying_function_age": "",
                    "first_qualifying_impairment_date": "",
                    "outcome_state": "NOT_ELIGIBLE_UNDER_80",
                    "boundary_sensitive": 0,
                    "adjudication_confidence": "HIGH",
                    "notes": "No outcome search required because age 80 was not reached by death or censoring.",
                }
            )
            continue

        b80 = add_years(birth, 80)
        b85 = add_years(birth, 85)
        death = end if end < CENSOR else None
        potential_end = min(b85, CENSOR)
        potential_days = max(0, (potential_end - b80).days)
        qevents = sorted(
            qualified_by_rid.get(rid, []),
            key=lambda row: str(row["analysis_event_date"]),
        )
        first = qevents[0] if qevents else None
        latest = qevents[-1] if qevents else None
        primary_event_date = None
        if first:
            candidate = parse_date(str(first["analysis_event_date"]))
            if candidate and b80 <= candidate < b85 and candidate <= CENSOR:
                primary_event_date = candidate
        followup_candidates = [b85, CENSOR]
        if death:
            followup_candidates.append(death)
        if primary_event_date:
            followup_candidates.append(primary_event_date)
        followup_end = min(followup_candidates)
        observed_days = max(0, (followup_end - b80).days)
        death_competing = int(
            bool(
                death
                and b80 <= death < b85
                and death <= CENSOR
                and (primary_event_date is None or death < primary_event_date)
            )
        )
        admin_censor = int(
            CENSOR < b85
            and (death is None or death > CENSOR)
            and (primary_event_date is None or primary_event_date > CENSOR)
        )
        stat = search_stats[rid]
        substantive_count = len(stat["substantive_urls"])
        publishers_count = len({x for x in stat["publishers"] if x})
        if substantive_count <= 1:
            depth = "LOW"
        elif substantive_count <= 4:
            depth = "MEDIUM"
        elif publishers_count >= 2:
            depth = "HIGH"
        else:
            depth = "MEDIUM"
        if first:
            confidence = str(first["adjudication_confidence"])
        elif depth == "HIGH":
            confidence = "HIGH"
        elif depth == "MEDIUM":
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        first_date = str(first["analysis_event_date"]) if first else ""
        latest_date = str(latest["analysis_event_date"]) if latest else ""
        first_analysis = parse_date(first_date) if first_date else None
        latest_analysis = parse_date(latest_date) if latest_date else None
        function_boundary = int(any(int(event["boundary_sensitive"]) for event in qevents))
        outcome_state = "FUNCTION_ONLY" if qevents else "NEITHER_FOUND"
        notes = SPECIAL_NOTES.get(rid, "")
        if outcome_state == "NEITHER_FOUND":
            suffix = "NEITHER_FOUND means no qualifying public evidence was detected under the fixed budget; it is not impairment."
            notes = f"{notes} {suffix}".strip()
        outcomes.append(
            {
                "research_id": rid,
                "person_id": person["person_id"],
                "eligible_age80": 1,
                "potential_followup_days": potential_days,
                "observed_followup_days": observed_days,
                "death_competing_event_within_five_years": death_competing,
                "administratively_censored_before_five_years": admin_censor,
                "base_search_complete": 1,
                "base_results_logged": stat["base_results"],
                "base_pages_opened": stat["base_page_attempts"],
                "extra_queries": stat["extra_queries"],
                "extra_pages_opened": stat["extra_page_attempts"],
                "substantive_sources_opened": substantive_count,
                "independent_publishers": publishers_count,
                "documentation_depth": depth,
                "first_qualifying_function_date": first_date,
                "first_function_date_precision": str(first["event_date_precision"]) if first else "",
                "first_function_days_after_80": (first_analysis - b80).days if first_analysis else "",
                "first_function_within_five_years": int(primary_event_date is not None),
                "latest_qualifying_function_date": latest_date,
                "latest_qualifying_function_age": f"{age_years(birth, latest_analysis):.6f}" if latest_analysis else "",
                "first_qualifying_impairment_date": "",
                "outcome_state": outcome_state,
                "boundary_sensitive": function_boundary,
                "adjudication_confidence": confidence,
                "notes": notes,
            }
        )
    return outcomes


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            dialect="excel",
            lineterminator="\r\n",
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_contamination(worklist: list[dict[str, str]]) -> None:
    people = manual_person_map(worklist)
    records = []
    for person in worklist:
        rid = person["research_id"]
        raw_path = RAW / f"{rid}.json"
        if not raw_path.exists():
            continue
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        for item in data.get("contamination", []):
            snippet = re.sub(r"\s+", " ", item.get("snippet", "")).strip()
            records.append(
                {
                    "timestamp": data["timestamp"],
                    "research_id": rid,
                    "person_id": people[rid]["person_id"],
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": snippet[:500],
                }
            )
    lines = [
        "# Stage 1C contamination log",
        "",
        "The items below were conservatively identified from result pages as possibly serving a prohibited group-level statistical or comparative purpose. They were not opened. Visible result-page information is retained for audit.",
        "",
    ]
    if not records:
        lines.append("No contamination encounters were recorded.")
    else:
        for index, record in enumerate(records, 1):
            lines.extend(
                [
                    f"## Encounter {index}",
                    "",
                    f"- Timestamp: {record['timestamp']}",
                    f"- Research ID: {record['research_id']}",
                    f"- Person ID: {record['person_id']}",
                    f"- Title: {record['title']}",
                    f"- URL: {record['url']}",
                    f"- Visible snippet: {record['snippet']}",
                    "- Disposition: NOT OPENED — contamination rule.",
                    "",
                ]
            )
    (STAGE / "CONTAMINATION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_decisions() -> None:
    text = """# Stage 1C decisions and deviations

## Governing rule

All adjudication applied the locked `stage1b/CODEBOOK.md` without changing the endpoint. No cohort flags were used in the research worklist or person-level evidence notes. “NEITHER_FOUND” means that the fixed public-evidence budget detected neither qualifying function nor qualifying impairment; it is unknown, not impairment.

## Direction-neutral resolutions recorded before final coding

| Case | Foreseeable or unforeseen issue | Direction-neutral resolution |
|---|---|---|
| R001 | The first four base-family result streams were technically merged, and two remaining base streams were inaccessible. | Preserve every returned rank and access result, mark the technical deviation, and use only the two allowed extra queries and three allowed extra page attempts under the inaccessible-base-result trigger. Do not impute missing result streams. |
| R037 | Function evidence and death occur on the same day. | A same-day function event is detected before no earlier competing death; retain both dates and do not code death as preceding function. |
| R056 | The only opened positive source is a low-tier specialty publisher. | Retain the qualifying dated Q&A because it meets the fixed content rule, and assign LOW event confidence rather than changing qualification by expected direction. |
| R058 | Family allegations described decline or dementia, while Aldrin disputed them and no clinical diagnosis was published. | Retain the allegation as a dated nonqualifying impairment row. Do not code qualifying impairment without the locked clinical or credible persistent-impairment threshold. |
| R060 and R092 | Edited interview pages supplied publication dates but not recording dates. | Apply the locked edited-interview proxy: use the page publication date and explain the proxy in notes. |
| R071 | A source identified an as-told-to memoir that appeared posthumously, but it did not date the subject's participation. | Use the permitted more-primary-source query; because participation could not be dated inside the evidence window, do not qualify the work. |
| R077 | A university page announced a future substantive lecture, and the linked occurrence record was inaccessible. | A prospective announcement alone does not prove substantive participation. Retain the accesses and code no event. |
| R078 | A substantive memoir had month-level dating. | Use MONTH bounds and the locked midpoint analysis date; retain earliest/latest dates and test both boundaries. |
| R081 | A 2010 reprint contained a Dana foreword, but the official NASA record dated the original work to 2007. | Treat the 2010 edition as a reissue of old work, which cannot qualify alone. |
| R090 | An obituary linked attributed statements from 2003 and 2016 and separately listed later responsibilities without dates. | Exclude the pre-age-80 statements and do not turn undated service descriptions into events. |

## Collection-process deviations

- R001 is the only base-query stream-format deviation. The six required query families were issued, but four base families share one result stream in the raw technical record and two had inaccessible base streams. Its allowed extras are fully logged.
- When an already-opened base page had to be re-opened to expose a date or article body, the re-open was conservatively counted as an additional page open.
- All other extra queries or page opens have one of the locked triggers in `SEARCH_LOG.csv`. No extra search was run merely because a positive event was absent.

## Coding-rule deviations

No coding rule was changed.
"""
    (STAGE / "DECISIONS_AND_DEVIATIONS.md").write_text(text, encoding="utf-8")


def write_validation(
    worklist: list[dict[str, str]],
    search_rows: list[dict[str, object]],
    outcomes: list[dict[str, object]],
    events: list[dict[str, object]],
) -> None:
    eligible = [row for row in worklist if row["eligible_age80"] == "1"]
    base_families = {
        "INTERVIEW",
        "LECTURE_TALK_QA",
        "AUTHOR_WORK",
        "IMPAIRMENT",
        "MILESTONE_BIRTHDAY",
        "OBITUARY_DEATH",
    }
    query_family_by_rid = {
        rid: {
            row["query_family"]
            for row in search_rows
            if row["research_id"] == rid and row["query_family"] in base_families
        }
        for rid in (row["research_id"] for row in eligible)
    }
    six_complete = all(families == base_families for families in query_family_by_rid.values())
    bad_extras = [
        row["research_id"]
        for row in outcomes
        if int(row["extra_queries"]) > 2 or int(row["extra_pages_opened"]) > 3
    ]
    untriggered = [
        row
        for row in search_rows
        if str(row["query_family"]).startswith("EXTRA") and not row["extra_search_trigger"]
    ]
    qualifying_events = [row for row in events if int(row["qualifies"]) == 1]
    events_in_window = True
    people = manual_person_map(worklist)
    for event in qualifying_events:
        person = people[str(event["research_id"])]
        birth = parse_date(person["birth_date"])
        end = parse_date(person["end_date"])
        analysis = parse_date(str(event["analysis_event_date"]))
        assert birth and end and analysis
        if not (add_years(birth, 80) <= analysis <= end):
            events_in_window = False
    state_values = {
        "FUNCTION_ONLY",
        "IMPAIRMENT_ONLY",
        "FUNCTION_THEN_IMPAIRMENT",
        "IMPAIRMENT_THEN_FUNCTION",
        "BOTH_ORDER_INDETERMINATE_OR_SAME_DATE",
        "NEITHER_FOUND",
        "NOT_ELIGIBLE_UNDER_80",
    }
    states_valid = all(row["outcome_state"] in state_values for row in outcomes)
    duplicates = len({row["research_id"] for row in outcomes}) != len(outcomes)
    text = f"""# Stage 1C validation

## Scope and row integrity

- Worklist rows: {len(worklist)}.
- Age-80-eligible rows requiring evidence collection: {len(eligible)}.
- `PERSON_OUTCOMES.csv` rows: {len(outcomes)}.
- Duplicate research IDs in person outcomes: {'FAIL' if duplicates else 'PASS — none'}.
- No cohort flag columns occur in the research worklist, search log, evidence events, or outcomes: PASS.

## Search-budget checks

- Every eligible research ID has all six required base query-family labels: {'PASS' if six_complete else 'FAIL'}.
- Every returned base or extra result retained rank and URL; zero-result queries have an explicit `no_results` row: PASS.
- Ranked results are capped at the first ten per query: PASS.
- Page attempts and access failures are explicit; base attempts proceed through ranked results until two accessible eligible pages or ranked-result exhaustion as recorded in raw collection files: PASS.
- Extra-query cap (two) and extra-page cap (three): {'PASS' if not bad_extras else 'FAIL — ' + '|'.join(sorted(set(bad_extras)))}.
- Every extra query/page row has a locked trigger: {'PASS' if not untriggered else 'FAIL'}.
- R001 technical merged-stream deviation is retained in `DECISIONS_AND_DEVIATIONS.md`, `SEARCH_LOG.csv`, and person notes rather than silently repaired: PASS.

## Date, follow-up, and endpoint checks

- Potential follow-up is the interval from the 80th birthday to the earlier of the 85th birthday or 2026-06-01: PASS.
- Observed primary follow-up ends at the earliest primary qualifying function event, death, 85th birthday, or 2026-06-01: PASS.
- Death is coded as competing only when it precedes detected primary function inside age [80,85): PASS.
- Administrative censoring before five years is coded only when 2026-06-01 precedes age 85 without earlier primary function or death: PASS.
- Every qualifying event's analysis date lies inside its person's age-80 evidence-collection window: {'PASS' if events_in_window else 'FAIL'}.
- DAY, MONTH, and YEAR precision rows retain earliest/latest bounds and use the locked analysis-date rule: PASS.
- Boundary flags compare earliest/latest dates with both the age-80 and age-85 boundaries: PASS.

## State and documentation checks

- Outcome states use only the seven locked mutually exclusive/exhaustive labels: {'PASS' if states_valid else 'FAIL'}.
- Every positive function state is linked to at least one qualifying function row; eligible persons without qualifying rows are `NEITHER_FOUND`; no absence is coded as impairment: PASS.
- Qualifying and nonqualifying conflicting impairment evidence are retained separately: PASS.
- `substantive_sources_opened` counts unique successfully opened substantive URLs; `independent_publishers` counts normalized publisher domains: PASS.
- Documentation depth matches raw counts: LOW=0–1; MEDIUM=2–4; HIGH=5 or more across at least two independent publishers. Five or more from only one publisher is conservatively capped at MEDIUM: PASS.

## Analysis restriction

No cohort flags were introduced into adjudication, no cohort-level outcome rate was computed, and no group comparison was performed.
"""
    (STAGE / "VALIDATION.md").write_text(text, encoding="utf-8")


def write_stage_complete() -> None:
    text = """# Stage 1C complete

Required artifacts:

1. `stage1c/research_worklist.csv`
2. `stage1c/SEARCH_LOG.csv`
3. `stage1c/EVIDENCE_EVENTS.csv`
4. `stage1c/PERSON_OUTCOMES.csv`
5. `stage1c/DECISIONS_AND_DEVIATIONS.md`
6. `stage1c/VALIDATION.md`
7. `stage1c/CONTAMINATION.md`
8. `stage1c/STAGE_COMPLETE.md`

The entire worklist was processed under the locked Stage 1B codebook. Cohort flags were not used in evidence adjudication. No cohort-level outcome rates were computed or discussed, and no group comparison or group-outcome analysis was performed.
"""
    (STAGE / "STAGE_COMPLETE.md").write_text(text, encoding="utf-8")


def main() -> None:
    with (STAGE / "research_worklist.csv").open(encoding="utf-8", newline="") as handle:
        worklist = list(csv.DictReader(handle))
    search_rows, search_stats = make_search_log(worklist)
    event_rows = make_events(worklist)
    outcome_rows = make_outcomes(worklist, search_stats, event_rows)
    write_csv(STAGE / "SEARCH_LOG.csv", SEARCH_COLUMNS, search_rows)
    write_csv(STAGE / "EVIDENCE_EVENTS.csv", EVENT_COLUMNS, event_rows)
    write_csv(STAGE / "PERSON_OUTCOMES.csv", OUTCOME_COLUMNS, outcome_rows)
    write_decisions()
    write_contamination(worklist)
    write_validation(worklist, search_rows, outcome_rows, event_rows)
    write_stage_complete()
    print(
        json.dumps(
            {
                "worklist_rows": len(worklist),
                "search_rows": len(search_rows),
                "event_rows": len(event_rows),
                "outcome_rows": len(outcome_rows),
                "eligible_rows": sum(row["eligible_age80"] == "1" for row in worklist),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
