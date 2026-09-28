# AUDIT TRAIL — Apollo-era astronaut cohort dataset

Purpose: let another instance reproduce `apollo_era_astronaut_cohort_v2.csv` (and its Stage 1
parent) closely enough that any differences are differences of *judgment*, not of *method*.
This file records the environment, the exact procedure, the verbatim subagent prompts, the
source hierarchy, the prescribed search terms, the scripts, the contamination protocol, and
a per-agent index. Run date: **2026-06-09**. Censoring date (frozen): **2026-06-01**.

> Honesty note on completeness: the work was done by 17 parallel research subagents. Their
> **prompts, candidate seed data, prescribed search-term recipes, final outputs, and every
> cited URL are reproduced or pointed to here exactly.** What is *not* perfectly recoverable
> is each agent's keystroke-level sequence of individual `WebSearch` query strings and the
> full list of pages it opened-but-didn't-cite (the agents were not re-interrogated for their
> raw tool logs; the continuation channel was unavailable when this trail was written). Where
> a query string is given below it is either (a) the literal recipe I instructed the agent to
> use, or (b) a query the agent reported in its returned notes. Treat per-agent query lists as
> "the recipe each agent instantiated per person," not a byte-exact transcript.

---

## 0. Determinism boundary (what will and won't reproduce)

**Deterministic (should reproduce exactly):**
- Cohort membership and the four cohort labels — derived top-down from NASA selection-group
  rosters + Apollo crew lists, not from any external dataset. The 73-person frame is fixed by
  the identity Groups 1–7 = 7+9+14+6+19+11+7 = 73 (see §3).
- Both Python scripts and every validation assertion they enforce. Same scripts + same input
  rows → identical CSVs.
- The coding rulebooks (Stage 1 confidence rules; Stage 1b codes, windows, age-70 cutoff,
  impairment inclusion/exclusion). These are written down verbatim below.

**Stochastic / judgment-dependent (may differ on a re-run):**
- Which of several equally-authoritative sources gets *cited* for a given date (e.g., NASA
  bio PDF vs. NASA news release vs. major obituary) — the date should match; the URL may not.
- The live web: pages move, 403, or get re-dated; new deaths occur after 2026-06-09; archive
  captures differ.
- Stage 1b cognitive codes for borderline rows are explicit judgment calls (esp. **Fullerton**
  IMPAIRED vs NO_EVIDENCE; any INTACT resting on an evidence item near a window edge).
- LLM search phrasing: agents instantiate the prescribed recipes with their own wording, so
  the exact hit list varies even when the conclusion does not.

A faithful re-run should land the **same cohort**, the **same ~17 DIED_EARLY / 2 IMPAIRED
structure**, and the **same dates within ≤1 day** on the flagged rows — while individual
citation URLs and a handful of NO_EVIDENCE↔INTACT borderline calls may legitimately differ.

---

## 1. Environment & tools

- **Model / effort:** Claude (Fable 5), effort = max.
- **Working dir:** `…/Fable 5 – One Shot Data - Analysis/` (not a git repo).
- **Tools actually used:**
  - `WebSearch` (US results) and `WebFetch` (URL → markdown → Q&A; 15-min per-URL cache;
    cross-host redirects returned not followed; HTTP upgraded to HTTPS). Loaded via
    `ToolSearch "select:WebSearch,WebFetch"`.
  - `Agent` (subagent_type `general-purpose`) — fan-out research, run in parallel batches.
  - `Bash` (python3) for the build/validation scripts; `Write`/`Edit`/`Read` for files.
- **Not used:** no paid databases, no login-walled sources, no astronaut-mortality datasets.
  All evidence is public web (NASA, obituaries, museum/foundation/news/encyclopedia pages).
- **Clean-room rule (both stages):** do not open or read any group-level study of astronaut
  mortality / longevity / aging / cognitive outcomes; if one surfaces, log title+URL without
  opening and continue. (Encounters in §7.)

---

## 2. Method overview

1. **Frame the cohort top-down (§3).** Verify NASA selection Groups 1–7 rosters + Apollo
   prime crews from NASA primary sources. This fixes *who is in* and *which cohort* — before
   any vital data, so membership cannot be contaminated by outcome knowledge.
2. **Stage 1 — vitals (§4).** Split the 73 names into 8 alphabetical batches; one subagent per
   batch independently verifies birth date, death date, and ALIVE/DEAD-as-of-2026-06-01
   against a fixed source hierarchy, treating my candidate values as unverified hypotheses.
   A 9th agent verifies the rosters/crews.
3. **Stage 1b — cognition (§5).** Same 8-batch split; one subagent per batch codes
   `cognitive_status_20260601` and `documentation_depth` from sources, under a fixed rulebook.
4. **Script + validate (§6).** `build_cohort.py` emits the 12-column CSV with hard checks;
   `build_stage1b.py` reads it, merges the codes, re-checks (incl. recomputing age-at-death to
   police the DIED_EARLY cutoff), and writes the 16-column `…_v2.csv`.

---

## 3. Cohort frame (Stage 0) — rosters & crews

**Agent:** id `a3258617ec2d705e8` (54 tool calls). Task: verify Groups 1–7 membership, the
Apollo 7–17 prime crews, per-group selection requirements, and the Apollo 1 crew — from NASA
primary sources only; log any mortality study without opening it.

**Authoritative sources it fetched (cite these to rebuild the frame):**
- NASA Astronaut Fact Book, Jan 2023 (official PDF) — the master roster + mission table:
  `https://www.nasa.gov/wp-content/uploads/2023/08/astronaut-fact-book-jan-2023.pdf`
  (landing page `https://www.nasa.gov/reference/astronaut-fact-book/`)
- Group selection articles (NASA History):
  - G1 `https://www.nasa.gov/history/65-years-ago-nasa-selects-americas-first-astronauts/`
  - G2 `https://www.nasa.gov/history/60-years-ago-nasa-selects-a-second-group-of-astronauts/`
  - G3 `https://www.nasa.gov/history/60-years-ago-nasa-selects-its-third-group-of-astronauts/`
  - G4 & G5 via NASA SP-4214 `https://www.nasa.gov/wp-content/uploads/2023/03/sp-4214.pdf`
  - G6 `https://www.nasa.gov/history/55-years-ago-nasa-selects-11-scientist-astronauts/`
  - G7 `https://www.nasa.gov/history/55-years-ago-nasa-group-7-astronaut-selection/`
- Apollo prime crews: `https://www.nasa.gov/mission/apollo-7/` … `/apollo-17/` (and `/apollo-1/`).

**Result:** rosters and all 11 crews matched the hypothesized lists with **zero discrepancies**;
counts 7/9/14/6/19/11/7 confirmed. Source-internal typos noted (Fact Book misprints McDivitt's
selection year as 1984; SP-4214 caption misdates Group 5 to 1967) but did not affect membership.
Confirmed every Apollo 7–17 crew member came from Groups 1–5 (only non-pilot-group flyer:
Schmitt, G4) and Apollo 1 = Grissom(G1)/White(G2)/Chaffee(G3).

**Cohort labels (full rationale in `DECISIONS_and_CONTAMINATION.md` D0–D11):**
`APOLLO_FLEW` (launched Apollo 7–17, 29) · `APOLLO1_CREW` (3) · `COMP_FLEW_OTHER` (flew only
Skylab/ASTP/Gemini/Mercury/Shuttle, 29) · `COMP_NEVER_FLEW` (12). Completeness identity:
29+3+29+12 = 73 = every member of Groups 1–7 exactly once.

---

## 4. Stage 1 — vitals procedure

### 4.1 Batches & agent IDs (alphabetical by surname)

| Batch | Agent ID | Names (n) | Tool calls |
|---|---|---|---|
| A–Br | `a4d0fe69d21f009de` | Aldrin, Allen, Anders, Armstrong, Bassett, Bean, Bobko, Borman, Brand (9) | 38 |
| Bu–Co | `afb22d13b3d3f1da5` | Bull, Carpenter, Carr, Cernan, Chaffee, Chapman, Collins, Conrad, Cooper (9) | 39 |
| Cr–Fu | `a2e7f3962da6e298e` | Crippen, Cunningham, Duke, Eisele, England, Engle, Evans, Freeman, Fullerton (9) | 39 |
| Ga–Ha | `ab43b6b6001a2337f` | Garriott, Gibson, Givens, Glenn, Gordon, Graveline, Grissom, Haise, Hartsfield (9) | 36 |
| He–Lo | `aa3dd2d1b9f31627a` | Henize, Holmquest, Irwin, Kerwin, Lenoir, Lind, Llewellyn, Lousma, Lovell (9) | 37 |
| Ma–Pa | `a7f7575ecdd559a4c` | Mattingly, McCandless, McDivitt, Michel, Mitchell, Musgrave, O'Leary, Overmyer, Parker (9) | 40 |
| Pe–Sh | `a4c411aefb6da0c4f` | Peterson, Pogue, Roosa, Schirra, Schmitt, Schweickart, Scott, See, Shepard (9) | 45 |
| Sl–Y | `ae4c8e13ea63cbfd8` | Slayton, Stafford, Swigert, Thornton, Truly, Weitz, White, Williams, Worden, Young (10) | 56 |

### 4.2 Verbatim Stage-1 prompt template (one per batch; only the PEOPLE list and a few
per-batch hints varied — see §4.5)

```
TASK: Verify vital records for N American astronauts for a historical biographical reference
table. Today is 2026-06-09; the dataset's censoring date is 2026-06-01.

SETUP: If WebSearch/WebFetch tools are not already available to you, first call ToolSearch
with query "select:WebSearch,WebFetch" to load them.

CONTAMINATION RULE (hard constraint): This dataset must be built only from primary/biographical
sources. Do NOT open, fetch, or read any scientific study, journal paper, preprint, or dataset
analyzing astronaut mortality, longevity, life expectancy, aging, or comparative health
outcomes (e.g., titles like "Mortality among US astronauts"). If your search results surface
such an item, do NOT click or fetch it — record its title and URL in a CONTAMINATION list at
the end of your reply and move on. Ordinary biographies, NASA pages, and news obituaries are
fine (an obituary is not a study).

SOURCE HIERARCHY (cite the best you can actually fetch): (1) nasa.gov / jsc.nasa.gov /
history.nasa.gov biography pages and NASA news releases; (2) official or major-outlet
obituaries (AP, NYT, Washington Post, Reuters, BBC, Houston Chronicle, regional papers) or
official family/foundation/military statements; (3) museum/foundation/military bios (Astronaut
Scholarship Foundation, National Aviation Hall of Fame, New Mexico Museum of Space History,
Arlington National Cemetery, USAF/Navy history pages); (4) spacefacts.de; (5) Wikipedia only
as a last resort (then mark confidence MEDIUM and say so in notes). Prefer non-paywalled pages
when quality is equal. A web.archive.org capture of an official page is acceptable and keeps
its tier. Cite ONLY URLs you actually fetched and on which you saw the relevant date. Never
invent or pattern-guess a URL.

FOR EACH PERSON BELOW (candidate data is an UNVERIFIED hypothesis — independently confirm or
correct it from sources you fetch):
1. Confirm exact birth date (YYYY-MM-DD); record the URL where you saw it as birth_url.
2. If deceased: confirm exact death date; record death_url. If candidate says ALIVE: run at
   least one targeted search for a death report ("<name> astronaut dies", "<name> obituary")
   paying special attention to 2024–2026, BEFORE accepting ALIVE. Catching recent deaths
   (2024–2026) is the single most important part of this job. Status is as of 2026-06-01.
3. Beware same-name confusion — the source must clearly be about the astronaut.
4. confidence: HIGH if NASA or a major obituary confirms the date(s); MEDIUM if only tier-4/5
   sources or a ≤1-day discrepancy exists (explain in notes); LOW if sources genuinely conflict.
5. Be efficient: ~2–4 page fetches per person is plenty. Report any date conflict you notice.

OUTPUT FORMAT — your entire final reply must be exactly (one ROW line per person, in order,
semicolons not commas inside notes):
ROW|Full Name|birth=YYYY-MM-DD|death=YYYY-MM-DD or NONE|status=DEAD or ALIVE|birth_url=URL|
death_url=URL or NONE|confidence=HIGH or MEDIUM or LOW|notes=short text
CONTAMINATION:
- title — URL (one per encountered study; or "- none")

PEOPLE (candidate data):
<the batch's 9–10 people, each with: full name, role/mission, candidate birth date,
 candidate death date or "believed ALIVE (verify through 2026-06-01)">
```

### 4.3 Prescribed search-term recipes (Stage 1)

Per person, instantiated from the prompt:
- Death check for anyone believed alive (and to confirm cause/date for the dead):
  `"<name> astronaut dies"` and `"<name> obituary"`, with attention to 2024–2026.
- Birth/death confirmation: fetch the highest-tier page available — typically the NASA
  biographical-data PDF at `https://www.nasa.gov/wp-content/uploads/<yyyy>/<mm>/<surname>_<first>.pdf`
  (agents discovered these via `"<name> NASA biographical data"` / site results, **not** by
  guessing the slug), else a NASA news release, else a major obituary.
- The single most important instruction: **never accept ALIVE without an explicit recent
  death search** — this is what caught Lovell (d. 2025-08-07) and confirmed the 16 survivors.

### 4.4 Where the per-row winning sources live

Every confirmed date's source is in the CSV columns **`birth_source_url`** and
**`death_source_url`** (and `confidence` + `notes`). That column pair *is* the per-row vitals
provenance — there are 73×2 cited URLs; they are not duplicated here to avoid drift. The
canonical file is `apollo_era_astronaut_cohort.csv` (Stage 1) / `…_v2.csv` (carries them forward).

### 4.5 Per-batch special hints I injected (these steer reproduction of the hard rows)

- **He–Lo:** "James Lovell reportedly died in 2025 — confirm the exact date from NASA or a
  major obituary." (Seeded the 2025-08-07 catch.)
- **Bu–Co:** same-name cautions for "John Bull" and "Michael Collins."
- **Pe–Sh / others:** same-name cautions ("David Scott", "Robert Parker", "Edward Gibson").
- Candidate seed dates were supplied for all 73 (the agent's job was to confirm/correct).

### 4.6 Corrections & conflicts the verification produced (seed → adopted)

| Person | Field | Seed | Adopted | Why / confidence |
|---|---|---|---|---|
| F. Curtis Michel | death | 2015-02-23 | **2015-02-26** | NASA bio + NASA release + Rice obit all say Feb 26 → HIGH |
| Ronald Evans | death | 1990-04-07 | **1990-04-06** | NASA bio 04-06 vs a wire story implying 04-07 → MEDIUM |
| Walter Schirra | death | 2007-05-03 | **2007-05-03** | kept over NASA people-page 05-02 (AP/Britannica/family 05-03) → MEDIUM |
| Jack Swigert | death | 1982-12-27 | **1982-12-27** | NASA bio internally lists 12-27 and 12-28; Britannica 12-27 → MEDIUM |
| Paul Weitz | death | 2017-10-22 | **2017-10-23** | three-way split 10-22/23/24; best-attested 10-23 → LOW |
| Frank Borman | birth source | — | NM Space Museum bio | NASA release gave only age; birth date taken from tier-3 source |
| C. Gordon Fullerton | birthplace | — | Rochester NY (birth) | NASA release calls Portland OR his hometown, not birthplace (note only) |

All other 66 rows confirmed the seed dates. Vital-status result: 16 ALIVE / 57 DEAD at
2026-06-01.

---

## 5. Stage 1b — cognition procedure

### 5.1 Batches & agent IDs (same alphabetical split)

| Batch | Agent ID | Tool calls |
|---|---|---|
| A–Br | `a189e1b7ad2668873` | 56 |
| Bu–Co | `afecbd3caea07fd03` | 54 |
| Cr–Fu | `a8a539d39699cd1c0` | 62 |
| Ga–Ha | `a400173165255e1cc` | 55 |
| He–Lo | `ad9809270daa754c5` | 36 |
| Ma–Pa | `ad8349dbc1d6d6b7e` | 47 |
| Pe–Sh | `af29a7d72e700cc53` | 54 |
| Sl–Y | `a6b205f25295cdbec` | 53 |

(Same name membership per batch as the Stage 1 table in §4.1.)

### 5.2 Verbatim Stage-1b coding rulebook (identical across batches)

```
CODES for cognitive status (status as of 2026-06-01; for the deceased = end-of-life status):
- IMPAIRED_DOCUMENTED: published diagnosis or credible public report (obituary, family
  statement, court filing, reputable press) of dementia or persistent major cognitive decline.
  NOT sufficient: motor-only disease (e.g., Parkinson's with no reported cognitive component);
  transient fully-recovered episodes; a stroke/delirium only in the final days; allegations
  later resolved. Sufficient: persistent post-stroke incapacity that sources describe as
  affecting communication/cognition over an extended period. Cite URL.
- INTACT_DOCUMENTED: affirmative DATED public evidence of functioning cognition late in life —
  substantive interviews, public talks/Q&As, authorship, active piloting, professional/advisory
  service. Evidence must fall in the person's QUALIFYING WINDOW (living: 2023-01-01 to
  2026-06-01; deceased: within 5 years of death AND at age 70+). Cite the MOST RECENT qualifying
  item you can verify (dated article/video/event page; web.archive.org ok).
- NO_EVIDENCE_EITHER_WAY: neither documented. Do NOT infer intactness from absence of impairment
  reports or from undated/generic "remained active" claims. If the best affirmative evidence
  falls OUTSIDE the window, code NO_EVIDENCE and put the stale evidence in notes.
- DIED_EARLY: pre-assigned (died before 70th birthday). Echo it; do ONE quick search to grade
  documentation depth; flag any impairment report you happen to see.
Precedence: documented end-state impairment overrides earlier intact evidence; a resolved
impairment allegation followed by qualifying intact evidence codes INTACT with the allegation
noted.

documentation_depth (independent of what coverage says): HIGH = extensive coverage incl. later
life (multiple substantive profiles/interviews/books/documentaries; national obituaries); LOW =
little beyond official NASA bio and a funeral-home/local obit; MEDIUM = in between. Grade from
what your searches actually surface; 2-6 word justification in notes.

SEARCH DISCIPLINE per non-DIED_EARLY person (2-5 searches typical):
(a) "<name> astronaut interview/talk <recent years>";
(b) "<name> dementia OR Alzheimer's";
(c) for deceased, read the obituary (often states final illness).

OUTPUT — entire final reply exactly:
ROW|Full Name|cog=CODE|cog_url=URL or NONE|depth=HIGH or MEDIUM or LOW|cnotes=short; semicolons
not commas; for INTACT give evidence type + date + age; for NO_EVIDENCE say what you searched and
most recent non-qualifying evidence; for IMPAIRED give gist of report wording
CONTAMINATION:
- title — URL (or "- none")
```

(The same hard CONTAMINATION-RULE paragraph as Stage 1 preceded the rulebook in every batch.)

### 5.3 Age-70 `DIED_EARLY` cutoff

Chosen cutoff: **died before the 70th birthday** ⇒ `DIED_EARLY` (no real late-life observation
window). Rationale in `DECISIONS…` C3. Borderline rows coded DIED_EARLY with margin noted:
Conrad (69.1), Slayton (69.3). Just-over rows coded on the merits: Lenoir (71), O'Leary (71).
`build_stage1b.py` recomputes age at death from the Stage 1 dates and **fails** if any
`DIED_EARLY` row is ≥70 or any non-DIED_EARLY decedent is <70 — so this cutoff is enforced
mechanically, not by hand.

### 5.4 Per-person leads I seeded each cognition agent with

Each agent received, per person, a one-line hypothesis + the most promising lead to verify
(e.g. *Aldrin*: note the 2018 guardianship petition + 2018 cognitive eval + 2019 withdrawal,
apply the precedence rule; *Fullerton* KEY CASE: fetch the NASA Dryden memorial + collectSPACE
and quote the post-stroke language, then apply the persistent-incapacity rule; *Peterson* KEY
CASE: fetch the Crowder funeral-home obit + collectSPACE and check for Alzheimer's; *Lind*:
read the family obit explicitly for any dementia mention; *Lovell*: note the April-2020 Apollo
13 interviews are just OUTSIDE the post-2020-08-07 window — require later evidence; *Scott*,
*Young*, *Mattingly*: flagged as low-profile "hard cases," code NO_EVIDENCE unless a dated
in-window item is found). These leads are the steering that makes the hard rows reproduce; the
agents were told to verify, not trust, them.

### 5.5 Where the per-row winning sources live

`cognitive_source_url` + `cognitive_notes` in `…_v2.csv`. For INTACT/IMPAIRED the URL is the
evidence page; for NO_EVIDENCE/DIED_EARLY the URL is empty and the note states what was searched
and the most-recent non-qualifying item. (40 INTACT and 2 IMPAIRED rows carry a URL; 31 do not —
enforced by the build script.)

### 5.6 Notable coding outcomes (where a re-run most needs to match the *method*, not luck)

- **2 IMPAIRED only:** Peterson (Alzheimer's named in WaPo obit; WaPo 403'd so wording
  confirmed via its Wikipedia citation + spacefacts.de) and Fullerton (explicit judgment call
  on post-stroke "body and mind" memorial language; reclassifiable to NO_EVIDENCE under a
  diagnosis-only definition).
- **14 NO_EVIDENCE**, incl. three HIGH-documentation famous names (Scott, Young, Mattingly) —
  the deliberate "absence ≠ intact" result.
- **Excluded from impairment by rule:** motor-only Parkinson's (Truly, Cooper), final-days
  stroke (Carpenter, Borman, Llewellyn), transient global amnesia (Graveline), spouse's illness
  (Borman's wife). Each documented in its note.
- Distribution: INTACT 40 / DIED_EARLY 17 / NO_EVIDENCE 14 / IMPAIRED 2; depth HIGH 40 /
  MEDIUM 29 / LOW 4. The 4 LOW-depth rows (Bull, Givens, Holmquest, Parker) are all
  NO_EVIDENCE/DIED_EARLY — low profile causing missing evidence.

---

## 6. Scripts (deterministic stage)

Both live in the working dir and embed their data inline (no hidden inputs).

### 6.1 `build_cohort.py` → `apollo_era_astronaut_cohort.csv`
- Holds the 73 rows as a Python list `R` (12 fields each), built from §3 frame + §4 verified
  vitals.
- Asserts: exactly 73 rows; surnames in sorted order (suffix-stripped); no commas/quotes/newlines
  in any field; valid cohort label; group ∈ 1–7; ISO birth date; if DEAD a valid death_date
  ≤ 2026-06-01 and > birth and a death_url; if ALIVE empty death fields; valid confidence;
  `apollo_missions` non-empty iff cohort APOLLO_FLEW; first-flight year format; never-flew rows
  carry no flight year; **group counts == {1:7,2:9,3:14,4:6,5:19,6:11,7:7}**; **cohort counts ==
  {APOLLO_FLEW:29, APOLLO1_CREW:3, COMP_FLEW_OTHER:29, COMP_NEVER_FLEW:12}**; **each of Apollo
  7–17 appears on exactly 3 rows**. Fails loudly (exit 1) on any violation.
- Run: `python3 build_cohort.py` → `OK: wrote … 73 rows (16 ALIVE / 57 DEAD …)`.

### 6.2 `build_stage1b.py` → `apollo_era_astronaut_cohort_v2.csv`
- Reads the Stage 1 CSV; holds the codes as dict `S` (name → cog, depth, cog_url, cnotes).
- Asserts: every CSV name coded and vice-versa (no missing/extra); valid code & depth; no
  commas/quotes/newlines; IMPAIRED/INTACT ⇒ has http URL, others ⇒ empty URL; **integrity:
  recomputes age at death and requires DIED_EARLY ⟺ (DEAD and age<70)**. Emits the code/depth
  tallies and a cohort×status cross-tab (descriptive only).
- Run order: `python3 build_cohort.py && python3 build_stage1b.py`.
- Last run: `OK: wrote …_v2.csv with 73 rows, 16 columns` · INTACT 40 / DIED_EARLY 17 /
  NO_EVIDENCE 14 / IMPAIRED 2 · depth HIGH 40 / MEDIUM 29 / LOW 4.

---

## 7. Contamination protocol & log

**Rule (verbatim in every agent prompt):** do not open any study/paper/preprint/dataset on
astronaut mortality/longevity/aging/cognitive outcomes; log title+URL without opening; continue.

- **Stage 1 (vitals):** all 9 agents reported **"- none"**. No study encountered.
- **Stage 1b (cognition):** name+"dementia/Alzheimer's" searches surfaced group-level
  space-radiation/cognition items. Recorded **without opening** (distinct items across batches):
  - *Space Radiation Could Accelerate Alzheimer's in Astronaut Brains* — https://www.space.com/19082-space-radiation-astronauts-alzheimers.html
  - *Does Deep Space Travel Cause Alzheimer's?* (Smithsonian) — https://www.smithsonianmag.com/science-nature/does-deep-space-travel-cause-alzheimers-94946/
  - *Astronauts with Alzheimer's* (UTMB Medical Discovery News podcast) — https://www.utmb.edu/mdnews/podcast/episode/astronauts-with-alzheimer's
  - *Ionizing radiation, cerebrovascular disease, and consequent dementia: a review…* — https://pmc.ncbi.nlm.nih.gov/articles/PMC9640983/
  - *Low doses of proton/iron/silicon radiation on spatial learning in an Alzheimer's mouse model* — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3941486/
  - *Continuous & Intermittent Artificial Gravity vs cognitive effects of 60 days head-down bed rest* — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8009974/

None is an astronaut-mortality/longevity **cohort** study (the specific Stage-1 hazard), and
none was read. Every per-person code rests on bios/interviews/event pages/news/obituaries.

---

## 8. Reproduction runbook (from scratch)

1. Load web tools: `ToolSearch "select:WebSearch,WebFetch"`.
2. **Frame:** spawn one agent with the §3 task; fetch the Fact Book + 6 selection articles +
   11 mission pages; confirm Groups 1–7 (73 people) and Apollo 7–17 crews; assign the 4 cohort
   labels per `DECISIONS…` D0–D11. Expect zero roster discrepancies.
3. **Vitals:** split the 73 into the 8 alphabetical batches (§4.1); spawn 8 agents in parallel
   with the §4.2 prompt + each batch's people + the §4.5 hints. Enforce the "never accept ALIVE
   without a recent-death search" rule. Collect ROW outputs.
4. **Cognition:** spawn 8 agents in parallel with the §5.2 rulebook + the §5.4 per-person leads.
   Collect ROW outputs.
5. **Build:** transcribe verified vitals into `build_cohort.py`'s `R` and codes into
   `build_stage1b.py`'s `S`; run both; the assertions catch transcription errors.
6. **Document:** regenerate `DECISIONS_and_CONTAMINATION.md` (decisions D0–D11, C0–C9) and this
   trail. Compare your CSV to the reference per §0's determinism boundary.

## 9. File manifest

| File | Role |
|---|---|
| `apollo_era_astronaut_cohort.csv` | Stage 1 deliverable (12 cols), from `build_cohort.py` |
| `apollo_era_astronaut_cohort_v2.csv` | **Canonical** Stage 1+1b (16 cols), from `build_stage1b.py` |
| `DECISIONS_and_CONTAMINATION.md` | Decision log (D0–D11 vitals/cohort; C0–C9 cognition) + contamination |
| `build_cohort.py` | Generates+validates Stage 1 CSV |
| `build_stage1b.py` | Merges+validates cognition fields → v2 CSV |
| `AUDIT_TRAIL.md` | This file |

All per-row source URLs live in the CSV provenance columns
(`birth_source_url`, `death_source_url`, `cognitive_source_url`) — that is the authoritative,
non-duplicated source list; this trail documents the *process* that produced them.
