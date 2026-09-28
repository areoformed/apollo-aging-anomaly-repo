#!/usr/bin/env python3
"""Stage 1b: enrich the Stage 1 cohort CSV with two coded fields + provenance.

Reads  apollo_era_astronaut_cohort.csv      (12 cols, from build_cohort.py)
Writes apollo_era_astronaut_cohort_v2.csv    (16 cols)

Added columns:
  cognitive_status_20260601  IMPAIRED_DOCUMENTED | INTACT_DOCUMENTED |
                             NO_EVIDENCE_EITHER_WAY | DIED_EARLY
  documentation_depth        HIGH | MEDIUM | LOW   (volume of coverage, not content)
  cognitive_source_url       provenance for an IMPAIRED/INTACT code ('' otherwise)
  cognitive_notes            per-row reasoning; semicolons only, no commas

Coding rules: see DECISIONS_and_CONTAMINATION.md, STAGE-1b section.
DIED_EARLY cutoff = died before 70th birthday; this script RECOMPUTES age at death
from the Stage 1 dates and asserts the code agrees (a real integrity check).
"""
import csv, re, sys, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "apollo_era_astronaut_cohort.csv")
OUT = os.path.join(HERE, "apollo_era_astronaut_cohort_v2.csv")
AGE_CUTOFF = 70  # DIED_EARLY iff age at death < this

VALID_COG = {"IMPAIRED_DOCUMENTED", "INTACT_DOCUMENTED",
             "NO_EVIDENCE_EITHER_WAY", "DIED_EARLY"}
VALID_DEPTH = {"HIGH", "MEDIUM", "LOW"}

# full_name -> (cog_status, depth, cog_source_url, cognitive_notes)
# URL is '' for DIED_EARLY and NO_EVIDENCE_EITHER_WAY rows.
S = {
"Buzz Aldrin": ("INTACT_DOCUMENTED","HIGH","https://x.com/TheRealBuzz/status/1881260001991471500",
 "INTACT: own dated X post 2025-01-20 marking 95th birthday plus ongoing public statements at 95-96; 2018 family guardianship petition alleged decline but an April 2018 UCLA evaluation found full decisional capacity and the petition was withdrawn March 2019; resolved-allegation-then-intact precedence; national 95th-birthday coverage Jan 2025 corroborates"),
"Joseph P. Allen": ("INTACT_DOCUMENTED","MEDIUM","https://www.giant.fm/parke-county/news/local-news/local-retired-astronaut-joseph-p-allen-presented-with-sagamore-of-the-wabash/",
 "INTACT: state Sagamore of the Wabash award ceremony 2024-10-17 (age 87) with substantive quoted remarks on spaceflight; resides in a senior-living community with no cognitive condition reported (absence not coded)"),
"William A. Anders": ("INTACT_DOCUMENTED","HIGH","https://plus.nasa.gov/video/earthrise-a-conversation-with-apollo-8-astronaut-bill-anders/",
 "INTACT: NASA+ filmed conversation published 2023-12-29 (age 90); was the sole pilot of his own aircraft when killed 2024-06-07; the crash is not treated as cognitive evidence either way"),
"Neil A. Armstrong": ("INTACT_DOCUMENTED","HIGH","https://www.cnn.com/2012/05/25/world/asia/neil-armstrong-rare-interview/index.html",
 "INTACT: hour-long CPA Australia interview reported 2012-05-25 (age 81) about 3 months pre-death; also 2010 congressional testimony; no cognitive-decline reports"),
"Charles A. Bassett II": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: T-38 crash 1966 at 34; no impairment reports; coverage from Wikipedia/NASA history/retrospectives"),
"Alan L. Bean": ("INTACT_DOCUMENTED","HIGH","https://www.geekwire.com/2018/apollo-12-moon-missions-artistic-astronaut-alan-bean-dies-86-sudden-illness/",
 "INTACT: working professional painter giving interviews to the end; fell ill May 2018 (age 86) while traveling to a speaking engagement two weeks before death"),
"Karol J. Bobko": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: searched 2018-23 interviews/appearances and dementia terms with none qualifying; NYT obit (via Wikipedia) cites complications of an unspecified degenerative nervous-system disease with no cognitive component reported so not coded impaired"),
"Frank Borman": ("INTACT_DOCUMENTED","HIGH","https://billingsgazette.com/news/local/years-later-apollo-commander-talks-the-cold-war-faith-divisiveness/article_40d28210-a02c-5f04-9a4a-2292c9735a19.html",
 "INTACT: substantive Billings Gazette Q&A 2018-12-25 (age 90) inside the 5-year window; wife Susan's Alzheimer's was hers not his; his only end-stage event was a stroke in the final days"),
"Vance D. Brand": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: searched 2023-26 incl ASTP 50th (July 2025) coverage and found no Brand appearance or fresh quote; most recent affirmative item is a 2019-10-03 NASA panel (age 88; outside window); no impairment reports"),
"John S. Bull": ("NO_EVIDENCE_EITHER_WAY","LOW","",
 "NO_EVIDENCE: searched obituary/oral-history/dementia; collectSPACE 2008 obit shows no late-life activity and no impairment; most recent trace is 1989 NASA retirement (outside the 2004+ window)"),
"M. Scott Carpenter": ("INTACT_DOCUMENTED","HIGH","https://www.colorado.edu/today/2012/05/21/cu-astronaut-alumnus-scott-carpenter-looks-back-50th-anniversary-aurora-7-mission",
 "INTACT: substantive CU Boulder interview 2012-05-21 (age 87) plus Feb 2012 Friendship 7 50th events with media Q&A; a Sept 2013 stroke about a month pre-death is terminal-period and not coded as impairment"),
"Gerald P. Carr": ("INTACT_DOCUMENTED","MEDIUM","https://en.wikipedia.org/wiki/Searching_for_Skylab",
 "INTACT: live (Skype) Q&A appearances at Searching for Skylab premieres 2018-07-05 and 2019-02-08 (age 85-86) and featured in the 2019 documentary; documented via the film record; no impairment reports"),
"Eugene A. Cernan": ("INTACT_DOCUMENTED","HIGH","https://www.bluesci.co.uk/posts/the-last-lunar-explorer-an-interview-with-gene-cernan-the-last-man-to-walk-on-the-moon",
 "INTACT: filmed in-person interview summer 2015 in London (age 81) and The Last Man on the Moon promotion incl an AARP award Feb 2016 (age 81); no impairment reports"),
"Roger B. Chaffee": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: Apollo 1 fire 1967 at 31; not applicable; commemorative coverage but no standalone biography"),
"Philip K. Chapman": ("INTACT_DOCUMENTED","MEDIUM","https://nss.org/remembering-dr-philip-chapman-1935-2021/",
 "INTACT: NSS memorial quotes June 2020 interviews (age 85) with substantive remarks on private spaceflight; portrayed as articulate and engaged; no impairment reports"),
"Michael Collins": ("INTACT_DOCUMENTED","HIGH","https://www.collectspace.com/news/news-071719a-michael-collins-apollo-11-50th-interview.html",
 "INTACT: original collectSPACE interview 2019-07-17 (age 88) plus many Apollo 11 50th interviews; active on Twitter to April 2021 days before death; no impairment reports"),
"Charles (Pete) Conrad Jr.": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: died 1999 at 69.1 of injuries from a motorcycle accident he was riding (months under the 70 cutoff); no impairment reports"),
"L. Gordon Cooper Jr.": ("INTACT_DOCUMENTED","HIGH","https://www.publishersweekly.com/978-0-06-019416-1",
 "INTACT: authored memoir Leap of Faith (2000 PW review; age 73) plus 2003 documentary recollections; some bios mention Parkinson's late but fetched obits report no cognitive component so motor-only and not coded impaired"),
"Robert L. Crippen": ("INTACT_DOCUMENTED","HIGH","https://www.creating-space.art/p/asf-ahof-rendezvous-2025",
 "INTACT: in-person ASF Hall of Fame panel 2025-05-30 (age 87) and announced speaker for the STS-1 45th dinner Jan 2026; dementia search negative"),
"Walter Cunningham": ("INTACT_DOCUMENTED","HIGH","https://www.spokesman.com/stories/2022/aug/26/walter-cunningham-the-last-astronaut-of-apollo-7-r/",
 "INTACT: press interview 2022-08-26 (age 90) about 4 months pre-death with Artemis quotes; obits show no impairment"),
"Charles M. Duke Jr.": ("INTACT_DOCUMENTED","HIGH","https://www.euronews.com/next/2026/04/01/meet-charlie-duke-the-youngest-person-on-the-first-moon-mission-cheering-on-artemis-ii-ast",
 "INTACT: Euronews interview 2026-04-01 (age 90) with Artemis II quotes plus a Judson University chapel talk 2025-10-22; dementia search negative"),
"Donn F. Eisele": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: heart attack 1987 at 57; no impairment reports"),
"Anthony W. England": ("INTACT_DOCUMENTED","MEDIUM","https://www.michigandaily.com/news/administration/u-m-dearborn-engineering-building-renamed-tony-england-engineering-lab-building/",
 "INTACT: Michigan Daily interview 2024-03-11 (age 81) and engineering-building dedication remarks 2024-04-19; dementia search negative"),
"Joe H. Engle": ("NO_EVIDENCE_EITHER_WAY","HIGH","",
 "NO_EVIDENCE: searched 2019-24 interviews and four obituaries; most recent in-window item is attendance-only at a Mar 2022 group event; family obit thanks caregivers for support 'the past few years' (unspecified; not coded impaired)"),
"Ronald E. Evans": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: heart attack 1990 at 56; no impairment reports"),
"Theodore C. Freeman": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: T-38 crash 1964 at 34; no impairment reports"),
"C. Gordon Fullerton": ("IMPAIRED_DOCUMENTED","MEDIUM","https://www.nasa.gov/centers/dryden/Features/fullerton_memorial.html",
 "IMPAIRED (judgment call): severe stroke late 2009 (age 73); NASA release says he was confined to long-term care for most of the next 3.5 years; the Dryden memorial says he worked to regain his body AND mind and his humor returned before his condition worsened; multi-year incapacity with a cognitive/communicative component meets the persistent-post-stroke rule"),
"Owen K. Garriott": ("INTACT_DOCUMENTED","HIGH","https://www.enidnews.com/news/enid-born-astronaut-owen-k-garriott-dies-at-age-88/article_8399eb14-5fc5-11e9-ae04-1fdf50dd8bc0.html",
 "INTACT: public interview at the Enid children's museum 2015-08-01 (age 84); national obits"),
"Edward G. Gibson": ("INTACT_DOCUMENTED","MEDIUM","https://www.iflscience.com/50-years-of-skylab-our-interview-with-its-last-astronaut-68911",
 "INTACT: substantive Skylab 50th interview 2023-05-12 (age 86) plus a Museum of Flight panel 2023-05-13; no impairment reports"),
"Edward G. Givens Jr.": ("DIED_EARLY","LOW","",
 "DIED_EARLY: car accident 1967 at 37; sparse coverage (often called the forgotten astronaut); no impairment reports"),
"John H. Glenn Jr.": ("INTACT_DOCUMENTED","HIGH","https://www.nationalgeographic.com/science/article/john-glenn-interview-astronaut-space",
 "INTACT: final National Geographic interview 2016-10-24 (age 95) with the reporter noting astonishing recall; a 2014 stroke affected vision only"),
"Richard F. Gordon Jr.": ("INTACT_DOCUMENTED","MEDIUM","https://careerthoughts.com/richard-gordon/",
 "INTACT: substantive career Q&A at Spacefest V May 2013 (age 83); national obits but few later-life profiles"),
"Duane E. Graveline": ("INTACT_DOCUMENTED","MEDIUM","http://web.archive.org/web/20160723094658/https://www.spacedoc.com/",
 "INTACT: ran spacedoc.com with monthly newsletters into Feb 2016 (age 85); site live six weeks pre-death; self-reported transient global amnesia about 1999-2004 was transient and recovered so not coded impaired"),
"Virgil I. (Gus) Grissom": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: Apollo 1 fire 1967 at 40; multiple biographies; extensive historical coverage"),
"Fred W. Haise Jr.": ("INTACT_DOCUMENTED","HIGH","https://geospatial.yale.edu/posts/2025-10-23-out-of-this-world-apollo-13-astronaut-fred-haise-shares-lessons-in-resilience",
 "INTACT: hour-long Yale talk and Q&A Sept 2025 (recap 2025-10-23; age 91) with sharp recall; no impairment reports"),
"Henry W. Hartsfield Jr.": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: searched 2009-14 talks/interviews/autograph shows and obituaries; most recent item is a Nov 2008 KSC autograph show (outside the 2009+ window); no impairment reports"),
"Karl G. Henize": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: died 1993 at 66 of altitude illness while climbing Mount Everest (under the 70 cutoff); no impairment reports"),
"Donald L. Holmquest": ("NO_EVIDENCE_EITHER_WAY","LOW","",
 "NO_EVIDENCE: searched 2023-26 activity and dementia/obituary; only undated traces (NASA bio; active State Bar of Texas listing); nothing dated either way; little beyond official bios"),
"James B. Irwin": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: heart attack 1991 at 61 during a Colorado speaking tour; no impairment reports; prominent post-NASA ministry and books"),
"Joseph P. Kerwin": ("INTACT_DOCUMENTED","HIGH","https://spacecenter.org/featured_events/skylab-50th-anniversary-celebration/",
 "INTACT: in-person Skylab 50th Legends and Leaders panel 2023-05-19 (age 91) plus a 3-part video interview recorded 2023-04-27; no impairment reports"),
"William B. Lenoir": ("INTACT_DOCUMENTED","MEDIUM","https://news.mit.edu/2010/obit-lenoir",
 "INTACT (advisory service): MIT obit documents he chaired an alumni education committee in 2009 (age 70) and was leading his class 50th-reunion organizing at death Aug 2010 (age 71); the bicycle-accident head-injury death is not counted as cognitive evidence"),
"Don L. Lind": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: fetched family obit plus collectSPACE/Church News/KSL and none mention dementia or cognitive decline; no qualifying interview/talk at age 87+ found; most recent dated quote is a 2005 NASA oral history"),
"John A. Llewellyn": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: died 2013 at 80 following a stroke but duration undocumented so not coded impaired; searched 2008-13 Wales/USF/Tampa interviews and found none verifiable; retired about 2007 just before the window"),
"Jack R. Lousma": ("INTACT_DOCUMENTED","HIGH","https://greatscience.com/about/media-press/50th-anniversary-splashdown-celebration/",
 "INTACT: public Capsule Chat talk and meet-and-greet 2023-09-23 (age 87) plus a Skylab 50th panel and two 2023 podcasts; no impairment reports"),
"James A. Lovell Jr.": ("INTACT_DOCUMENTED","HIGH","https://www.cbsnews.com/chicago/news/jim-lovell-wakeup-message-artemis-ii/",
 "INTACT: recorded a substantive Artemis II wake-up message about June 2025 (age 97) two months before death; played April 2026 per NASA via CBS; obits report no impairment; April 2020 Apollo 13 50th interviews are pre-window"),
"Thomas K. (Ken) Mattingly II": ("NO_EVIDENCE_EITHER_WAY","HIGH","",
 "NO_EVIDENCE: searched 2018-23 interviews/panels and dementia; absent from the Apr 2022 Apollo 16 50th event and the 2020 Apollo 13 50th documentary; most recent activity is a 2010 Smithsonian panel (outside window); no impairment reports"),
"Bruce McCandless II": ("INTACT_DOCUMENTED","HIGH","https://www.nationalgeographic.com/science/article/first-untethered-spacewalk-bruce-mccandless-astronaut-space-science",
 "INTACT: substantive National Geographic interview conducted July 2017 (published 2018-02-07; age 80) about 5 months pre-death plus a 2015 Denver museum panel; no impairment reports"),
"James A. McDivitt": ("INTACT_DOCUMENTED","HIGH","https://sandiegoairandspace.org/newsletters/article/apollo-9-celebrates-50th-anniversary-at-air-space-museum",
 "INTACT: on-stage Apollo 9 50th panel 2019-03-13 (age 89) telling mission stories; died in his sleep at 93; no impairment reports"),
"F. Curtis Michel": ("INTACT_DOCUMENTED","MEDIUM","https://eos.org/articles/f-curtis-michel-1934-2015",
 "INTACT: Eos professional obit describes active research and mentoring to the end; he argued the Voyager 1 heliopause question during the 2012-14 debate (age 78-80) and kept a Rice office; modest popular coverage"),
"Edgar D. Mitchell": ("INTACT_DOCUMENTED","HIGH","https://www.huffpost.com/entry/moonwalker-edgar-mitchell-denies-saying-ets-prevented-nuclear-war_n_55d61660e4b07addcb45eb80",
 "INTACT: coherent direct statements to HuffPost 2015-08-27 (age 84) correcting fabricated quotes plus a 2014 interview; eccentric UFO content is irrelevant to coherence per rules"),
"Story Musgrave": ("INTACT_DOCUMENTED","HIGH","https://nss.org/legendary-nasa-astronaut-story-musgrave-to-receive-award-at-the-nss-international-space-development-conference/",
 "INTACT: featured speaker receiving the NSS Heinlein Award at ISDC 2025-06-22 (age 89) plus a Dec 2023 NASA video interview; active on speaker circuits 2026"),
"Brian T. O'Leary": ("INTACT_DOCUMENTED","MEDIUM","https://www.infinite-energy.com/iemagazine/issue93/index.html",
 "INTACT: authored the cover essay in Infinite Energy issue 93 (Sept/Oct 2010; age 70) inside the narrow window plus an early-March 2011 written statement; died July 2011 of cancer soon after diagnosis; 2008-09 books are pre-window"),
"Robert F. Overmyer": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: died 1996 at 59 in a VK-30 test-flight crash; national wire obits; no impairment reports"),
"Robert A. R. Parker": ("NO_EVIDENCE_EITHER_WAY","LOW","",
 "NO_EVIDENCE: searched 2023-26 talks/interviews and dementia/health with nothing qualifying and no impairment reports; most recent substantive items are a 2002 NASA oral history and an undated ESA interview; retired from JPL 2005"),
"Donald H. Peterson": ("IMPAIRED_DOCUMENTED","MEDIUM","https://www.washingtonpost.com/local/obituaries/donald-peterson-sr-who-spacewalked-from-the-shuttle-challenger-dies-at-84/2018/05/29/d1d8d148-634d-11e8-a69c-b944de66d9e7_story.html",
 "IMPAIRED: Washington Post obit (2018-05-29) reports he died at home of Alzheimer's disease and bone cancer; the WaPo page returned 403 so exact wording was confirmed via Wikipedia's citation of it and corroborated by spacefacts.de (Alzheimer and bone cancer); the family funeral-home obit names no illness"),
"William R. Pogue": ("INTACT_DOCUMENTED","HIGH","https://voicesofoklahoma.com/interviews/pogue-william/",
 "INTACT: substantive Voices of Oklahoma oral-history interview 2012-08-08 (age 82) plus memoir But for the Grace of God (2011; age 81); dementia search clean"),
"Stuart A. Roosa": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: died 1994 at 61 of pancreatitis complications; no impairment reports; an authorized biography exists"),
"Walter M. Schirra Jr.": ("INTACT_DOCUMENTED","HIGH","https://www.deseret.com/2007/5/4/20016640/walter-schirra-dies-at-84/",
 "INTACT: AP interview April 2007 (age 84) weeks before death quoted in the 2007-05-04 Deseret obit plus co-authored The Real Space Cowboys (2005; age 82); died of a heart attack; no cognitive reports"),
"Harrison H. Schmitt": ("INTACT_DOCUMENTED","HIGH","https://starlust.org/even-at-90-apollo-17-astronaut-harrison-schmitt-would-be-more-than-happy-to-go-back-to-the-moon/",
 "INTACT: in-person AP interview 2026-04-22 (age 90) with substantive helium-3 and return-to-Moon remarks plus a 2026-04-10 radio interview; dementia search clean"),
"Russell L. (Rusty) Schweickart": ("INTACT_DOCUMENTED","HIGH","https://www.imperial.ac.uk/news/265593/imperial-students-honoured-with-planetary-defence/",
 "INTACT: presented the Schweickart Prize in person with remarks 2025-06-30 (age 89) plus a 2023 podcast; ongoing asteroid-defense advocacy; dementia search clean"),
"David R. Scott": ("NO_EVIDENCE_EITHER_WAY","HIGH","",
 "NO_EVIDENCE: searched 2023-26 interviews/appearances/auction provenance/tributes and dementia; most recent affirmative item is an in-person Apollo 15 50th panel 2021-07-27 (outside window); a June 2025 exhibit director said he could not reach Scott; no impairment reports"),
"Elliot M. See Jr.": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: T-38 crash 1966 at 38; NASA history retrospectives; no dedicated biography"),
"Alan B. Shepard Jr.": ("INTACT_DOCUMENTED","HIGH","https://en.wikipedia.org/wiki/Moon_Shot",
 "INTACT: co-authored Moon Shot (published May 1994; age 70) within the window and chaired the Astronaut Scholarship Foundation until Oct 1997 (age 73); died 1998 of leukemia; no cognitive-decline reports"),
"Donald K. (Deke) Slayton": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: died 1993 at 69.3 of brain-tumor complications (months under the 70 cutoff; the tumor is noted as context not coded as dementia); autobiography and Moon Shot coverage"),
"Thomas P. Stafford": ("INTACT_DOCUMENTED","HIGH","https://www.space.com/nasa-astronaut-thomas-stafford-obituary",
 "INTACT: chaired NASA's ISS advisory safety task force until death 2024-03-18 (age 93) per obit plus dated Weatherford OK appearances Nov 2022 (age 92); no impairment reports"),
"John L. (Jack) Swigert Jr.": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: died 1982 at 51 of cancer weeks after winning a US House seat; no impairment reports; extensive Apollo 13 coverage"),
"William E. Thornton": ("NO_EVIDENCE_EITHER_WAY","MEDIUM","",
 "NO_EVIDENCE: searched 2016-21 talks/appearances and dementia; obits give no late-life or illness detail; most recent affirmative items are a 2013 Skylab panel (age 84) and a 2010 interview (outside the 2016+ window)"),
"Richard H. Truly": ("NO_EVIDENCE_EITHER_WAY","HIGH","",
 "NO_EVIDENCE: searched 2019-24 appearances and dementia with nothing in window; WaPo obit gives cause as complications of atypical Parkinson's disease (motor; cognition not documented so not coded impaired); most recent affirmative item is a 2012 Mines interview"),
"Paul J. Weitz": ("INTACT_DOCUMENTED","MEDIUM","https://www.americaspace.com/2013/07/30/nostalgia-for-an-age-yet-to-come-reflections-on-astronaut-scholarship-foundations-skylab-40th-anniversary-celebration/",
 "INTACT: live panel Q&A with quick humorous exchanges at the Skylab 40th anniversary 2013-07-27 (age 81) per a dated AmericaSpace report; nothing later found; died 2017 of myelodysplastic syndrome"),
"Edward H. White II": ("DIED_EARLY","HIGH","",
 "DIED_EARLY: Apollo 1 fire 1967 at 36; extensive histories and film portrayals"),
"Clifton C. Williams Jr.": ("DIED_EARLY","MEDIUM","",
 "DIED_EARLY: T-38 crash 1967 at 35; encyclopedia and memorial coverage; no dedicated books"),
"Alfred M. Worden": ("INTACT_DOCUMENTED","HIGH","http://www.collectspace.com/sightings/sightings-worden.html",
 "INTACT: dated appearance-calendar entries incl Huntsville 2019-07-16 (age 87) and ISDC/Paris Air Show panels June 2019; the foundation said he postponed appearances after a sudden infection just before death 2020-03-18"),
"John W. Young": ("NO_EVIDENCE_EITHER_WAY","HIGH","",
 "NO_EVIDENCE: searched 2013-17 appearances and dementia with nothing qualifying after the window start; most recent affirmative item is the memoir Forever Young (Sept 2012; outside window); reported late decline was never credibly documented as cognitive"),
}

def age_at(birth, death):
    b, d = date.fromisoformat(birth), date.fromisoformat(death)
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))

with open(SRC, newline="") as fh:
    rows = list(csv.DictReader(fh))

errors = []
csv_names = {r["full_name"] for r in rows}
extra = set(S) - csv_names
missing = csv_names - set(S)
if extra:   errors.append(f"Stage1b names not in CSV: {sorted(extra)}")
if missing: errors.append(f"CSV names not coded in Stage1b: {sorted(missing)}")

cog_counts, depth_counts = {}, {}
for r in rows:
    name = r["full_name"]
    if name not in S:
        continue
    cog, depth, url, cnotes = S[name]
    if cog not in VALID_COG:     errors.append(f"{name}: bad cog {cog}")
    if depth not in VALID_DEPTH: errors.append(f"{name}: bad depth {depth}")
    for fld in (cog, depth, url, cnotes):
        if "," in fld or '"' in fld or "\n" in fld:
            errors.append(f"{name}: comma/quote/newline in a Stage1b field")
    # provenance discipline: IMPAIRED/INTACT require a URL; others must be blank
    if cog in {"IMPAIRED_DOCUMENTED", "INTACT_DOCUMENTED"}:
        if not url.startswith("http"): errors.append(f"{name}: {cog} needs a source URL")
    else:
        if url: errors.append(f"{name}: {cog} must have empty source URL")
    # integrity: DIED_EARLY <=> DEAD and age-at-death < cutoff (recomputed here)
    is_dead = r["vital_status_20260601"] == "DEAD"
    if cog == "DIED_EARLY":
        if not is_dead:
            errors.append(f"{name}: DIED_EARLY but not DEAD")
        else:
            a = age_at(r["birth_date"], r["death_date"])
            if a >= AGE_CUTOFF:
                errors.append(f"{name}: coded DIED_EARLY but age at death {a} >= {AGE_CUTOFF}")
    else:
        if is_dead:
            a = age_at(r["birth_date"], r["death_date"])
            if a < AGE_CUTOFF:
                errors.append(f"{name}: age at death {a} < {AGE_CUTOFF} but not coded DIED_EARLY")
    cog_counts[cog] = cog_counts.get(cog, 0) + 1
    depth_counts[depth] = depth_counts.get(depth, 0) + 1

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

new_cols = ["cognitive_status_20260601", "documentation_depth",
            "cognitive_source_url", "cognitive_notes"]
fieldnames = list(rows[0].keys()) + new_cols
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        cog, depth, url, cnotes = S[r["full_name"]]
        r.update(dict(zip(new_cols, (cog, depth, url, cnotes))))
        w.writerow(r)

print(f"OK: wrote {os.path.basename(OUT)} with {len(rows)} rows, {len(fieldnames)} columns")
print(f"cognitive_status: {cog_counts}")
print(f"documentation_depth: {depth_counts}")
# cross-tab cohort x cognitive_status (descriptive only)
xt = {}
for r in rows:
    xt.setdefault(r["cohort"], {}).setdefault(S[r["full_name"]][0], 0)
    xt[r["cohort"]][S[r["full_name"]][0]] += 1
print("cohort x cognitive_status:")
for c in sorted(xt):
    print(f"  {c}: {xt[c]}")
