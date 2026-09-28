#!/usr/bin/env python3
"""Step 1: Fetch Wikipedia articles via MediaWiki API and cache locally as JSON.
Source: V1 pipeline, <workspace>/projects/apollo-aging-anomaly/01_fetch_articles.py
Conversation: early build (pre-May 18), projects/apollo-aging-anomaly/

Uses the action=parse endpoint which returns parsed HTML (no images, no raw wikitext overhead).
Stores one JSON file per unique astronaut with: title, HTML text, categories, and infobox HTML.
Skips articles that are already cached.
Rate-limited to 1 request per second per Wikipedia's API etiquette.
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, quote

import requests
from bs4 import BeautifulSoup

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "us-astronaut-groups-1-7.tsv"
CACHE_DIR = PROJECT_DIR / "wiki-articles"
API_BASE = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "ApolloAgingResearch/1.0 (personal research; [EMAIL])"}


def title_from_url(url):
    return unquote(url.split("/wiki/")[-1])


def safe_filename(title):
    return re.sub(r'[^\w\-.]', '_', title) + ".json"


def fetch_article(title):
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text|categories|sections",
        "disabletoc": "true",
        "disableeditsection": "true",
        "redirects": "1",
    }
    resp = requests.get(API_BASE, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        return None, data["error"].get("info", "Unknown error")

    parsed = data["parse"]
    html = parsed["text"]["*"]

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["img", "figure", "style", "script"]):
        tag.decompose()
    for tag in soup.find_all(class_=re.compile(r"mw-empty|navbox|sidebar|mbox|ambox|metadata")):
        tag.decompose()
    clean_html = str(soup)

    infobox_tag = soup.find("table", class_=re.compile(r"infobox|vcard"))
    infobox_html = str(infobox_tag) if infobox_tag else None

    return {
        "title": parsed["title"],
        "html": clean_html,
        "infobox_html": infobox_html,
        "categories": [c["*"] for c in parsed.get("categories", [])],
        "sections": [s["line"] for s in parsed.get("sections", [])],
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }, None


def main():
    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        urls = {}
        for row in reader:
            if len(row) >= 4:
                name = row[0]
                if name not in urls:
                    urls[name] = row[3]

    print(f"{len(urls)} unique astronauts to fetch", file=sys.stderr)

    already_cached = 0
    fetched = 0
    failed = []

    for i, (name, url) in enumerate(urls.items()):
        title = title_from_url(url)
        filename = safe_filename(title)
        filepath = CACHE_DIR / filename

        if os.path.exists(filepath):
            already_cached += 1
            continue

        print(f"[{i+1}/{len(urls)}] Fetching {name} ({title})...", file=sys.stderr, end=" ")

        article, error = fetch_article(title)
        if article:
            article["source_name"] = name
            article["source_url"] = url
            with open(filepath, "w") as f:
                json.dump(article, f, indent=2)
            print(f"OK ({len(article['html'])//1024}KB)", file=sys.stderr)
            fetched += 1
        else:
            print(f"FAILED: {error}", file=sys.stderr)
            failed.append((name, title, error))

        time.sleep(1.0)

    print(f"\nDone: {fetched} fetched, {already_cached} cached, {len(failed)} failed", file=sys.stderr)
    if failed:
        print("\nFailed articles:", file=sys.stderr)
        for name, title, error in failed:
            print(f"  {name}: {title} -- {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
