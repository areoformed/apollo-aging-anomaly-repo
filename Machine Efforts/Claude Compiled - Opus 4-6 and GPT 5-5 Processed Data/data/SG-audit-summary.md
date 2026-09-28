# Space Grandpa Classification Audit — Source Documentation

**Audit Date:** May 19, 2026
**Auditor:** Claude (automated review of existing sources)
**Scope:** All 73 NASA astronauts selected pre-1970; audit covers the 50 who reached age 80+

---

## Update: 2026-05-23 URL Evidence Addendum

A later URL-enrichment pass was completed for the `Space Grandpa` standardized-search rows only. That pass added `Evidence URLs`, `Evidence URL Notes`, and `Evidence URL Status` columns to:

- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-lunar.tsv`
- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv`

This May 19 summary remains the baseline existing-source audit and was not recalculated. See `DATA-INTEGRITY-ERROR-LOG.md`, E002, for URL-enrichment status counts and remaining row-level cautions.

---

## Update: 2026-05-24 Current Canonical SG Pass

The final enriched TSVs now apply the high/medium-confidence standardized-search `SG=Y` recommendations for Neil Armstrong, Eugene Cernan, Walter Schirra, James McDivitt, Philip Chapman, Anthony England, Duane Graveline, and William Thornton. The low-confidence Curt Michel downgrade recommendation was not applied; Michel remains `SG=Y` pending source adjudication.

Current canonical core count: `40/73` SG=Y overall, and `40/50` SG=Y among astronauts who reached age 80+.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total astronauts who reached 80+ | 50 |
| Classified SG=Y | 40 |
| Classified SG=N | 10 |

### Evidence Strength Breakdown (SG=Y astronauts only)

| Strength | Count | Description |
|----------|-------|-------------|
| Strong | 18 | Multiple specific dated events; evidence clearly supports classification |
| Moderate | 20 | 1-2 documented events or pattern-based evidence; meets threshold but minimally |
| Weak | 2 | Vague citations lacking specific dates or events |

### Evidence Strength Breakdown (SG=N astronauts)

| Strength | Count | Description |
|----------|-------|-------------|
| None | 10 | No evidence of 80+ activity found in any source consulted |

### Sources Consulted

| Source Level | SG=Y Count | SG=N Count | Total |
|-------------|------------|------------|-------|
| Wikipedia only | 24 | 1 | 25 |
| Wikipedia + Phase 5 search | 8 | 9 | 17 |
| Standardized search audit + URL evidence | 8 | 0 | 8 |

---

## Key Findings

### 1. Wikipedia-only classifications dominate the Y group

24 of 40 SG=Y classifications (60%) rely solely on Wikipedia. No web search or cross-referencing was performed for these astronauts. This is not necessarily a problem — many of these are high-visibility lunar astronauts whose late-life activities are well-documented on Wikipedia — but it means the evidence trail is a single source.

### 2. Phase 5 searches were concentrated on N-to-Y upgrades

The Phase 5 deep verification was specifically designed to investigate SG=N astronauts who lived past 80. It successfully upgraded 5 astronauts (Lousma, Carr, Garriott, Lind, Michel) from N to Y. All were in the control group (Non-Apollo). Phase 5 also investigated death causes for several astronauts.

### 3. Two SG=Y classifications have weak evidence

- **Story Musgrave** (Non-Apollo, living, age 90): Citation says "active speaker and consultant" but the cached Wikipedia page's last specific event is a 2012 convention at age 76. No documented 80+ events. His SG=Y may rest on general reputation rather than documented evidence.
- **Don Lind** (Non-Apollo, died at 92): Phase 5 upgraded from N to Y citing "LDS Temple presidency service" and "sustained speaking through age 92" but the cached Wikipedia page has no specific post-80 events. The source of the upgrade evidence is unclear.

### 4. Previously contested SG=N classifications were updated

The 2026-05-24 pass upgraded Eugene Cernan, James McDivitt, Wally Schirra, and William Thornton to `SG=Y` using standardized-search URL evidence. Neil Armstrong, Philip Chapman, Anthony England, and Duane Graveline were also upgraded on the same basis.

### 5. Living astronauts with SG=N are under-investigated

Two living astronauts are classified N with no evidence found:
- **Donald Holmquest** (87, living): Resides in Menlo Park; no public profile
- **Robert Parker** (89, living): No post-retirement (2005) activity documented

---

## Astronauts Most Needing Standardized Search Verification

### Priority 1 — Current Y classifications with weak evidence (verify before publication)

1. **Franklin Story Musgrave** — SG=Y but no specific documented 80+ events in Wikipedia
2. **Don Lind** — SG=Y from Phase 5 upgrade but cached page lacks support

### Priority 2 — Remaining low-confidence standardized conflict

3. **Frank Curtis Michel** — current final `SG=Y`; standardized-search recommendation `N` is low confidence and conflicts with existing research/activity notes at the age-80 threshold.

### Priority 3 — Living N-classified astronauts (may have undocumented activity)

4. **Robert Allan Ridley Parker** — Living at 89; no post-2005 activity found
5. **Donald Lee Holmquest** — Living at 87; no public profile

### Priority 4 — N classifications that likely need deeper search despite Phase 5

6. **Ken Mattingly** — Lived to 87; Phase 5 only investigated death cause, not SG status

---

## Methodology Note

This audit examined three source layers:
1. **Enriched TSV data** (`Space Grandpa` and `Space Grandpa Citation`): The SG classification and citation/rationale as recorded
2. **BUILD-LOG.md**: Documentation of Phase 5 searches and decisions
3. **Cached Wikipedia pages** (73 files in `Cached Pages/wiki-individual/`): The primary source text, checked for 80+ evidence that might have been missed during initial extraction

No new web searches were conducted. All assessments are based on existing cached materials.

---

## Evidence Strength Criteria

- **Strong**: 3+ specific dated events at 80+, OR definitive single evidence (e.g., book published at 88, fatal aircraft crash at 90)
- **Moderate**: 1-2 specific dated events, OR pattern-based evidence ("active speaker through 80s") with at least one anchor
- **Weak**: General statements without specific dates, OR single minimal evidence point
- **None**: No evidence found in any consulted source

---

*Audit produced May 19, 2026. Output file updated May 24, 2026: `data/SG-audit-existing-sources.tsv` (50 rows, 11 columns after adding `Status`).*
