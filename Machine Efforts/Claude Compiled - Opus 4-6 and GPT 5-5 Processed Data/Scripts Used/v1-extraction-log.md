# v1 Script Extraction Log

**Source conversation:** `7f7e191c-4c17-49e5-830d-c58195e61e2c`
**JSONL file:** 185MB, 13,990 lines
**Date range:** 2026-04-17 through 2026-04-22
**Extraction date:** 2026-05-22
**Extraction method:** grep + targeted line extraction from JSONL

---

## Key Finding

**The v1 session produced NO standalone Python or Bash scripts for Apollo data work.**

The v1 session was a planning and manual compilation session. All data was compiled by the model directly from its training knowledge and WebFetch results, then written as markdown tables or TSV files via Write tool calls. The 80 inline Python scripts found in the conversation were ALL for non-Apollo work (Track daily log queries, Swiggy order analysis, vision pipeline, session hooks).

The actual scripted data pipeline (build_lists_v1.py, build_lists_v2.py, update_mort_fields.py, parse_ssa_lifetable.py) was produced in the v2 session (8ed732b6, May 19-20).

---

## Apollo Artifacts Produced in v1

### 1. Data Files

| Line | Timestamp | Tool | File | Description |
|------|-----------|------|------|-------------|
| 13744 | 2026-04-22T08:16:16Z | Write | `output/us-astronaut-groups-1-7.tsv` | 121-row TSV: X-15 through NASA Group 7, plus Dyna-Soar and MOL. 4 columns: Name, Group, Selection Date, Wikipedia Link. Compiled from Wikipedia WebFetch. Moved to `projects/apollo-aging-anomaly/` at line 13760. |
| pre-existing | compiled early April 2026 | Write | `projects/apollo-aging-anomaly/cohort-data.md` | 29 Apollo 7-17 astronauts with DOB, DOD, age, cause of death, moon status, cognitive decline notes. Hand-compiled markdown tables. Read at line 939. |

### 2. Research / Methodology Documents

| Line | Timestamp | Tool | File | Description |
|------|-----------|------|------|-------------|
| 538 | 2026-04-17T06:46:02Z | Write | `projects/apollo-aging-anomaly/tomorrow-steps.md` | Session planning: 3-session workflow for SMR computation. Dosing prerequisites, dataset hygiene steps, E computation method, OpenEpi SMR calculator. Updated at line 575 with five-gate QA framework. |
| pre-existing | compiled early April 2026 | Write | `projects/apollo-aging-anomaly/comparison-data.md` | SSA 1930 male cohort links, published SMRs (Elgart, Hammer, Reynolds), Navy 1000 Aviators study, statistical methods list. 85 lines. Read at line 529. |
| pre-existing | compiled early April 2026 | Write | `projects/apollo-aging-anomaly/novelty-assessment.md` | Assessment that the compound claim (longevity + cognitive preservation, Apollo-specific) is substantially novel. Read at line 523. |

### 3. WebFetch Calls (Data Gathering)

| Line | Timestamp | URL | Purpose |
|------|-----------|-----|---------|
| 564 | 2026-04-17T06:54:42Z | `atlaslongitudinaldatasets.ac.uk/datasets/thousand-aviator-study` | Check Thousand Aviator Study access. Result: 403, confirmed study details via web search. |
| 2844 | 2026-04-19T07:17:41Z | `en.wikipedia.org/wiki/List_of_Apollo_astronauts` | Cross-reference Apollo cohort list. |
| 13734 | 2026-04-22T08:13:50Z | `en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection` | Source for astronaut groups 1-7 TSV. First fetch. |
| 13738 | 2026-04-22T08:14:57Z | `en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection` | Second fetch for full coverage. |

### 4. In-Session Computations (Not Scripted)

At line 944 (2026-04-17T14:39:01Z), the model computed summary statistics from the cohort data in its context window:
- Median age at end of observation (all 29): 88
- Median age at death (deceased, n=23): 86
- Median birth year: 1930
- Sorted age distribution provided
- 6 living, all 90+, youngest 90

At lines 2774-2779 (2026-04-19), Monte Carlo simulation approach was discussed:
- Parametric bootstrap from SSA life table
- Three implementation paths discussed (Excel, Python, R)
- No code was written; deferred to future session

---

## Files Saved to Scripts Used/

### data-extraction/
- `v1-compile-astronaut-groups-tsv.py` -- Documentation of how 121-row TSV was compiled (model inline, not scripted). SUPERSEDED.
- `v1-compile-apollo-cohort-data.py` -- Documentation of 29-astronaut cohort hand-compilation. SUPERSEDED.
- `build_lists_v1.py` -- (already present, from v2 session 8ed732b6)
- `build_lists_v2.py` -- (already present, from v2 session 8ed732b6)

### web-fetching/
- `v1-webfetch-calls.sh` -- Documents the 4 WebFetch MCP calls with URLs, prompts, and purposes.

### life-tables/
- `v1-ssa-methodology-plan.py` -- Documents SSA life table approach planned but not implemented in v1.

### military-programs/
- `v1-military-program-groups.py` -- Documents the 6 military programs compiled in the v1 TSV.

### qa/
- `v1-cohort-verification-steps.py` -- Documents QA steps executed (manual) and deferred.

### enrichment/
- No v1 enrichment scripts exist. Enrichment was a v2 concept.
- `update_mort_fields.py` -- (already present, from v2 session 8ed732b6)

---

## Non-Apollo Python Scripts Found (80 total, not extracted)

All 80 inline Python scripts in this conversation were for non-Apollo work:
- **Track daily log queries** (lines 182, 191, 333, 359, etc.): medication dosing, pomodoro counts, email stats
- **Swiggy order analysis** (lines 1307, 2927, 2929, etc.): sweet drink patterns, order history
- **Weekly work summary** (lines 3309, 3325): therapist report from daily logs
- **Medication log patching** (lines 3993, 3995, 4005): April 19 evening med entries
- **Vision pipeline analysis** (lines 6164, 6166): A2 Sonnet image description output
- **Session hooks** (line 11841): session-start.py verification

---

## v1 vs v2 Comparison

| Aspect | v1 (7f7e191c, Apr 17-22) | v2 (8ed732b6, May 19-20) |
|--------|--------------------------|--------------------------|
| Approach | Manual compilation + planning | Systematic scripted pipeline |
| Data source | Model knowledge + 4 WebFetches | 70+ per-astronaut Wikipedia fetches, cached |
| Scripts produced | 0 (all inline/manual) | 4+ (build_lists, update_mort_fields, parse_ssa) |
| Output format | Markdown tables + 1 TSV | Structured TSV pipeline (Lists 01-08, enriched) |
| Astronaut groups | X-15 through Group 7 (121 rows, 4 cols) | Groups 1-7 only (deduped, 6+ cols) |
| QA | Manual spot-checking | Filename-based classification, manual review flags |
| Life table work | Methodology planned | parse_ssa_lifetable.py implemented |
| Enrichment | Not attempted | DOB, DOD, cause of death, missions enriched |
