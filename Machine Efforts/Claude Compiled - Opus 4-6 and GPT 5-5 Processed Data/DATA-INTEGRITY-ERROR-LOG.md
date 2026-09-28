# Data Integrity / Veracity Error Log

Audit date: 2026-05-23  
Scope: `data/`, `Final - Analysis - Enriched Datasets/`, `Scripts Used/`, `Cached Pages/`, and `BUILD-LOG.md`.

This log records every issue found during the audit pass. It does not modify the underlying data.

## Executive Finding

The enriched TSVs are structurally well-formed: row lengths, date arithmetic, duplicate-name checks, and core partition counts pass for the six enriched files. The main remaining weakness is provenance/reproducibility: the original enrichment was manually composed, though a row-level provenance table now exists. The `Space Grandpa` field has been mostly reconciled with the later standardized-search audit; the only remaining standardized-search conflict is the low-confidence Curt Michel downgrade recommendation.

## E001: Core `Space Grandpa` Values Conflict With Later Standardized Search Audit

Severity: High  
Affected fields: `Space Grandpa`, `Space Grandpa Citation` in the core enriched TSVs.

Status update, 2026-05-24: Mostly resolved. High/medium standardized-search `SG=Y` recommendations were propagated to the final enriched TSVs for Neil Armstrong, Eugene Cernan, Walter Schirra, James McDivitt, Philip Chapman, Anthony England, Duane Graveline, and William Thornton. The standardized-search `Current SG` fields and `data/SG-audit-existing-sources.tsv` were updated accordingly.

Remaining conflict:

| Final file location | Person | Current final value | Conflicting audit location | Recommended value | Error detail |
|---|---|---:|---|---:|---|
| `Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv:32` | Frank Curtis Michel | `Y`, citation populated | `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv:14` | `N`, low confidence | This remains intentionally unmodified pending source adjudication. The current data says Michel remained active in research through death at 80 and published/maintained research at the threshold; the standardized audit says no documented 80+ public activity. |

Impact after correction: Current core-73 enriched count is `40/73` SG=Y. Among the 50 core astronauts who reached age 80+, the current final count is `40/50`.

## E002: `Space Grandpa` Evidence Trail Is Often Not Independently Auditable

Severity: High  
Locations:  
- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv:1`  
- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-lunar.tsv:1`

Observed at initial audit: The standardized search files included query strings, found flags, summaries, recommendations, confidence, and key evidence, but no URL/source columns. Many SG decisions were substantive but could not be independently verified from the TSV row alone.

Expected: Each positive or negative SG adjudication should carry source URLs or cached-page references sufficient to reproduce the classification.

Status update, 2026-05-23: Partially remediated for the standardized-search TSVs. Three URL-audit columns were appended to both files:
- `Evidence URLs`
- `Evidence URL Notes`
- `Evidence URL Status`

Validation after URL enrichment:
- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-lunar.tsv`: 23 lines, 25 columns on every row; 22 astronaut rows; status counts `OK=10`, `PARTIAL=12`, `NEEDS_RESEARCH=0`.
- `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv`: 29 lines, 25 columns on every row; 28 astronaut rows; status counts `OK=13`, `PARTIAL=14`, `NEEDS_RESEARCH=1`.
- No blank `Evidence URLs`, `Evidence URL Notes`, or `Evidence URL Status` cells were found after enrichment.
- Existing SG values, `Recommended SG`, confidence, query, and summary fields were not intentionally changed during this URL-only pass.

Remaining row-level cautions found during URL enrichment:

| Location | Person | URL status | Error detail |
|---|---|---:|---|
| `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv:5` | Gerald Carr | `NEEDS_RESEARCH` | The located URLs support death at 88, a 2010 lecture at age 78, and an authorized biography, but do not yet substantiate strong public activity after age 80. |
| `.../SG-standardized-searches-control.tsv:19` | Anthony England | `PARTIAL` | University of Michigan sources support 2019 commencement speaking, 2024 building renaming, and dean emeritus profile, but contradict the row's claim that he served as dean through 2024 or retired in 2025. |
| `.../SG-standardized-searches-control.tsv:23` | John Llewellyn | `PARTIAL` | The row's `S4 Summary` says `NASA oral history 2001 only`; the surfaced 2001 NASA oral history appears to be for a different John Llewellyn, not astronaut John Anthony Llewellyn. |
| `.../SG-standardized-searches-control.tsv:29` | Paul Weitz | `OK` | URL enrichment found specific NSS evidence for Spacefest VII Skylab panel participation at age 83. This is stronger 80+ activity evidence than the row's `Key Evidence` note implies and may require classification adjudication. |

## E003: SG Evidence Was Deliberately Cleared for Some `SG=N` Rows

Severity: Medium  
Location: `Scripts Used/qa/qa_fix_enriched_tsvs.py:78-81` and duplicate `Scripts Used/qa/may19-qa-fixes.py:78-81`

Observed: The QA script blanks `Space Grandpa Citation` when `Space Grandpa=N` in `08E`. It preserved rationales only by printing them, not by writing them to the final TSV. `BUILD-LOG.md:122-124` notes Schirra, Eisele, and McDivitt rationales existed.

Affected final rows:
- `Final - Analysis - Enriched Datasets/08E-non-lunar-apollo-enriched.tsv:2`, Walter Schirra: `SG=N`, blank citation despite later evidence.
- `Final - Analysis - Enriched Datasets/08E-non-lunar-apollo-enriched.tsv:5`, James McDivitt: `SG=N`, blank citation despite later evidence.

Expected: Negative-evidence rationales should be stored consistently, either in `Space Grandpa Citation` or in a separate `SG Evidence/Rationale` column.

Status update, 2026-05-24: Resolved. Schirra and McDivitt were upgraded to `SG=Y` using standardized-search evidence, and both QA scripts now preserve SG citations/rationales rather than blanking them.

## E004: Negative-Evidence Notes Are Inconsistent Across Enriched Files

Severity: Low  
Affected rows:
- `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv:12`, Alvin Swauger White: `Space Grandpa=N`, citation says "No documented 80+ activity beyond retirement in Tucson".
- `Final - Analysis - Enriched Datasets/11-mol-full-enriched.tsv:5`, Francis Gregory Neubeck: `Space Grandpa=N`, citation says no documented activity at 80+ and last confirmed activity at 75.

Observed: Core QA blanked citations for `SG=N` in at least one file, but military/wider-cohort files retain negative-evidence notes in the same citation column.

Expected: The schema should choose one convention: blank citations for `SG=N`, or citation/rationale populated for both `Y` and `N`.

Status update, 2026-05-24: Resolved. The chosen convention is to populate `Space Grandpa Citation` as an SG rationale field for both `Y` and `N`. Current enriched files contain 53 `SG=N` rows and all 53 have populated citation/rationale cells.

## E005: Wider-Cohort SG Denominators in `BUILD-LOG.md` Are Stale

Severity: High  
Affected wider-cohort sections:

| Location | Observed log claim | Current final TSV reality | Error detail |
|---|---|---|---|
| `BUILD-LOG.md:327-329` | `09-x15-pilots-enriched.tsv` has 12 rows | `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv` has 13 rows | Three high-speed research pilots were appended later; core overlaps were deduplicated. |
| `BUILD-LOG.md:274` | X-15 SG rate `3/12 (25%)` | Current file: `2/13` overall; `2/4` among age-80+ rows | Current file has only Crossfield and Robert White as SG=Y. Armstrong and Engle were removed as core-73 overlaps. |
| `BUILD-LOG.md:394-396` | Dyna-Soar file has 8 rows | Current `10-dyna-soar-pilots-enriched.tsv` has 4 rows | Core and X-15 overlaps were removed. |
| `BUILD-LOG.md:386` | Dyna-Soar SG rate `1/8 (12.5%)` | Current file: `1/4` overall; `1/1` among age-80+ rows | Denominator changed after deduplication. |
| `BUILD-LOG.md:520-522` | MOL file has 17 rows | Current `11-mol-full-enriched.tsv` has 8 rows | Core-73 transfers and cross-program overlaps were removed. |
| `BUILD-LOG.md:511` | MOL SG rate `4/17 (23.5%)`; `4/14` among those who survived past the program | Current file: `2/8` overall; `2/3` among age-80+ rows | Deduplicated current file has Macleay and Abrahamson as SG=Y. |
| `BUILD-LOG.md:487` | Michael Adams is recorded as `Went to Space=N` | `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv:2` records `Went to Space=Y` | Log and final TSV disagree. |

Relevant scripts documenting the denominator changes:
- `Scripts Used/military-programs/dedup_military_files.py:50-61`
- `Scripts Used/military-programs/reconstruct_white_gordon.py:87-93`
- `Scripts Used/military-programs/append_x15_pilots.py:1-11`, `:66-87`

Expected: The build log should explicitly distinguish "full roster" counts from the current deduplicated unique-person files.

Status update, 2026-05-24: Resolved. `BUILD-LOG.md` now explicitly distinguishes historical full-roster/pre-dedup counts from current deduplicated final-file counts for X-15/high-speed, Dyna-Soar, and MOL. Michael Adams is documented as `Went to Space=Y` in the X-15 file and excluded from the current deduplicated MOL final file.

## E006: Enrichment Pipeline Is Not Fully Reproducible

Severity: High  
Locations:
- `Scripts Used/mid-period-extraction-log.md:65-66`
- `Scripts Used/extraction-log.md:34-37`
- `Scripts Used/extraction-log.md:113-115`

Observed: The three main enriched files were generated by Claude reading cached pages and writing TSV rows directly; `08E` is explicitly described as hand-constructed, not programmatically extracted.

Expected: Research-grade TSVs should have a deterministic extraction/enrichment script, or at minimum a row-level source/provenance file showing how each interpretive field was derived.

Impact: This particularly affects interpretive fields such as `Mort / cause note`, `Space Grandpa`, `Space Grandpa Citation`, `Pre-NASA Career`, `Education`, and `Post-NASA Career`.

Status update, 2026-05-24: Partially resolved. The original enrichment remains non-deterministic/manual, but `data/enriched-row-provenance-2026-05-24.tsv` now provides row-level source/provenance pointers for the interpretive final-file fields.

## E007: Multiple Scripts Still Reference Old Root-Level TSV Paths

Severity: Medium  
Locations include:
- `Scripts Used/enrichment/update_mort_fields.py:57-60`
- `Scripts Used/enrichment/upgrade_space_grandpas.py:24`, `:54`, `:62`
- `Scripts Used/qa/sg_denominator_breakdown.py:36-38`
- `Scripts Used/qa/lunar_median_ages.py:21`
- `Scripts Used/military-programs/dedup_military_files.py:24`, `:58-61`

Observed: These scripts open filenames such as `07E-lunar-enriched.tsv` from the working directory root. Those files are now located under `Final - Analysis - Enriched Datasets/`. Current root-level checks show all six expected root-level enriched files are missing.

Expected: Scripts should use the current canonical paths or define a single dataset root. As written, rerunning them from the current folder would fail or write to the wrong location if replacement files were created.

Status update, 2026-05-24: Resolved for the originally cited scripts. They now define/use `Final - Analysis - Enriched Datasets/` as the canonical dataset root rather than opening root-level TSV filenames.

## E008: Raw Base Lists Have Missing Date Values

Severity: Medium  
Affected fields: `Date of Birth`, `Date of Selection` in raw/reference TSVs.

Observed: The raw TSVs use blank cells where dates are expected. Enriched files often contain the corrected dates, so these raw files are stale or incomplete.

Locations:
- `data/01-all-pre-1970-astronauts.tsv` and `data/02-deduplicated-pre-1970.tsv` have identical missing-date cells:
  - `Date of Birth` blank at lines 6 Bassett, 7 Bean, 9 Borman, 12 Carpenter, 15 Chaffee, 17 Collins, 18 Conrad, 19 Cooper, 21 Cunningham, 23 Eisele, 27 Freeman, 29 Garriott, 33 Gordon, 46 Lovell, 49 McDivitt, 59 Schirra, 63 See, 65 Slayton, 66 Stafford, 74 Young.
  - `Date of Selection` blank at lines 10 Brand, 11 Bull, 13 Carr, 22 Duke, 25 Engle, 26 Evans, 29 Garriott, 30 Gibson, 31 Givens, 34 Graveline, 36 Haise, 40 Irwin, 41 Kerwin, 43 Lind, 45 Lousma, 47 Mattingly, 48 McCandless, 50 Michel, 51 Mitchell, 57 Pogue, 58 Roosa, 60 Schmitt, 67 Swigert, 70 Weitz, 73 Worden.
- `data/03-non-apollo-astronauts.tsv`:
  - `Date of Birth` blank at lines 3 Bassett, 7 Carpenter, 9 Chaffee, 11 Cooper, 15 Freeman, 17 Garriott, 39 See, 40 Slayton.
  - `Date of Selection` blank at lines 5 Brand, 6 Bull, 8 Carr, 14 Engle, 17 Garriott, 18 Gibson, 19 Givens, 21 Graveline, 26 Kerwin, 28 Lind, 30 Lousma, 31 McCandless, 32 Michel, 38 Pogue, 43 Weitz.
- `data/04-non-apollo-flew.tsv`:
  - `Date of Birth` blank at lines 5 Carpenter, 7 Cooper, 12 Garriott, 28 Slayton.
  - `Date of Selection` blank at lines 4 Brand, 6 Carr, 10 Engle, 12 Garriott, 13 Gibson, 18 Kerwin, 20 Lind, 21 Lousma, 22 McCandless, 27 Pogue, 31 Weitz.
- `data/05-non-apollo-never-flew.tsv`:
  - `Date of Birth` blank at lines 2 Bassett, 4 Chaffee, 6 Freeman, 13 See.
  - `Date of Selection` blank at lines 3 Bull, 7 Givens, 8 Graveline, 11 Michel.

Expected: Date columns should contain `YYYY-MM-DD` or have a documented missing-value convention.

Status update, 2026-05-24: Resolved. Recheck found 0 blank `Date of Birth` / `Date of Selection` cells across `data/01` through `data/05`.

## E009: Raw/Reference Files Use Partial Dates

Severity: Low  
Affected fields: `Date of Selection`.

Observed: Several raw/reference files use month-level dates (`YYYY-MM`) while enriched files use full dates.

Locations:
- `data/06-apollo-applications.tsv`: lines 3 Kerwin `1965-06`, 4 Weitz `1966-04`, 5 Bean `1963-10`, 6 Garriott `1965-06`, 7 Lousma `1966-04`, 8 Carr `1966-04`, 9 Gibson `1965-06`, 10 Pogue `1966-04`, 12 Brand `1966-04`.
- `data/07-lunar-astronauts.tsv`: lines 4 Anders, 7 Cernan, 9 Collins, 10 Aldrin, 12 Gordon, 13 Bean use `1963-10`; lines 14 Swigert, 15 Haise, 17 Roosa, 18 Mitchell, 20 Worden, 21 Irwin, 22 Mattingly, 23 Duke, 24 Evans use `1966-04`; line 25 Schmitt uses `1965-06`.
- `data/08-non-lunar-apollo.tsv`: lines 3 Eisele, 4 Cunningham, 6 Schweickart use `1963-10`.

Expected: Either full dates in `YYYY-MM-DD`, or a documented date-precision column.

Status update, 2026-05-24: Resolved. Recheck found 0 month-only `Date of Selection` values in `data/06-apollo-applications.tsv`, `data/07-lunar-astronauts.tsv`, and `data/08-non-lunar-apollo.tsv`.

## E010: Raw Base Lists Contain Placeholder `Astronaut Group` Values

Severity: Medium  
Affected field: `Astronaut Group`.

Observed: `Astronaut Group` contains the incomplete literal value `Group `.

Locations:
- `data/01-all-pre-1970-astronauts.tsv` and `data/02-deduplicated-pre-1970.tsv`: lines 10 Brand, 11 Bull, 13 Carr, 22 Duke, 25 Engle, 26 Evans, 29 Garriott, 30 Gibson, 31 Givens, 34 Graveline, 36 Haise, 40 Irwin, 41 Kerwin, 43 Lind, 45 Lousma, 47 Mattingly, 48 McCandless, 50 Michel, 51 Mitchell, 57 Pogue, 58 Roosa, 60 Schmitt, 67 Swigert, 70 Weitz, 73 Worden.
- `data/03-non-apollo-astronauts.tsv`: lines 5 Brand, 6 Bull, 8 Carr, 14 Engle, 17 Garriott, 18 Gibson, 19 Givens, 21 Graveline, 26 Kerwin, 28 Lind, 30 Lousma, 31 McCandless, 32 Michel, 38 Pogue, 43 Weitz.
- `data/04-non-apollo-flew.tsv`: lines 4 Brand, 6 Carr, 10 Engle, 12 Garriott, 13 Gibson, 18 Kerwin, 20 Lind, 21 Lousma, 22 McCandless, 27 Pogue, 31 Weitz.
- `data/05-non-apollo-never-flew.tsv`: lines 3 Bull, 7 Givens, 8 Graveline, 11 Michel.

Expected: Complete group values, such as `Group 6 — The Scientists`, not a placeholder.

Status update, 2026-05-24: Resolved. Recheck found 0 literal `Group ` placeholders across `data/01` through `data/05`.

## E011: Raw Mission Fields Include Non-Flown Support/Backup Associations

Severity: Medium  
Affected field: `Missions Flown` in raw files.

Observed examples:
- `data/03-non-apollo-astronauts.tsv:2`, Joseph Allen: raw `Missions Flown` includes `Apollo 15; STS-5; STS-51-A`; enriched `Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv:2` has actual flown missions `STS-5; STS-51-A`.
- `data/03-non-apollo-astronauts.tsv:6`, John Bull: raw `Missions Flown` has `Apollo 8`; enriched `.../03E-non-apollo-enriched.tsv:6` has `None`.
- `data/03-non-apollo-astronauts.tsv:19`, Edward Givens: raw `Missions Flown` has `Mercury finalist; Apollo 1; Apollo 7`; enriched `.../03E-non-apollo-enriched.tsv:19` has `None`.

Expected: If the column is named `Missions Flown`, it should contain actual flown missions only. Backup/support/finalist roles need a separate field.

Status update, 2026-05-24: Resolved for the raw `Missions Flown` files. The checked raw rows now match the actual-flown final values (`Allen=STS-5; STS-51-A`, `Bull=None`, `Givens=None`).

## E012: Raw-to-Enriched Name Keys Do Not Join Reliably

Severity: Medium  
Affected field: `Name`.

Observed examples:
- `data/03-non-apollo-astronauts.tsv:31` has `Byron Willis McCandless (later Bruce McCandless II)`; enriched file has `Bruce McCandless II`.
- `data/07-lunar-astronauts.tsv:5` has `Tom Stafford`; enriched file has `Thomas Stafford`.
- `data/08-non-lunar-apollo.tsv:2-6` uses common names (`Wally Schirra`, `Donn Eisele`, `Walter Cunningham`, `James McDivitt`, `Russell Schweickart`); enriched `08E` uses full legal names.

Expected: Add a stable person ID or name-mapping table if raw and enriched files are intended to join.

Status update, 2026-05-24: Resolved by mapping table. Display-name variants remain, but `data/person-id-alias-map-2026-05-24.tsv` now provides stable person IDs and raw-to-final alias mappings.

## E013: `data/SG-audit-existing-sources.tsv` Uses Sentinel Text in Date Column

Severity: Low  
Affected field: `Death Date`.

Observed: Living people have `Death Date=Living` instead of a blank date. Examples:
- `data/SG-audit-existing-sources.tsv:2`, Buzz Aldrin
- `data/SG-audit-existing-sources.tsv:9`, Charles Duke
- `data/SG-audit-existing-sources.tsv:23`, Russell Schweickart
- `data/SG-audit-existing-sources.tsv:24`, Joseph Allen
- `data/SG-audit-existing-sources.tsv:45`, Story Musgrave

Expected: Date columns should contain blank or `YYYY-MM-DD`; status should be stored in a separate status column.

Status update, 2026-05-24: Resolved. Recheck found 0 `Death Date=Living` sentinel cells, and `data/SG-audit-existing-sources.tsv` now has a separate `Status` column.

## E014: SSA Life Table Is Not a Normal TSV Without Comment-Skipping

Severity: Medium  
Location: `data/ssa-1930-male-cohort-lifetable.tsv:1-8`

Observed: Line 1 is a single-field comment header (`# SSA 1930 Male Cohort Life Table — q(x) values`), while the actual four-column header is line 8 (`age	qx	lx	dx`). A normal `csv.DictReader(... delimiter="\t")` reads line 1 as the header and treats lines 8+ as malformed four-column rows.

Expected: Either remove/comment metadata outside the TSV file, or require/comment-document parsers to skip leading `#` lines.

Status update, 2026-05-24: Resolved. `data/ssa-1930-male-cohort-lifetable.tsv` now begins with `age	qx	lx	dx`; former comment metadata was moved to `data/ssa-1930-male-cohort-lifetable-metadata.md`.

## E015: Several `Mort / cause note` Values Are Placeholders, Not Substantive Causes

Severity: Medium  
Affected field: `Mort / cause note` (renamed from `Mort` on 2026-05-24).

Observed placeholder or non-specific entries:
- `Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv:8`, Gerald Carr: `Brief illness (not further specified)`
- `.../03E-non-apollo-enriched.tsv:10`, Philip Chapman: `Not specified`
- `.../03E-non-apollo-enriched.tsv:14`, Joseph Engle: `Not specified`
- `.../03E-non-apollo-enriched.tsv:20`, John Glenn: `Not publicly disclosed (prior stroke, heart valve replacement surgery)`
- `.../03E-non-apollo-enriched.tsv:21`, Duane Graveline: `Not specified`
- `.../03E-non-apollo-enriched.tsv:28`, Don Lind: `Not specified`
- `.../03E-non-apollo-enriched.tsv:31`, Bruce McCandless II: `Not publicly disclosed`
- `.../03E-non-apollo-enriched.tsv:32`, Frank Curtis Michel: `Not specified`
- `.../03E-non-apollo-enriched.tsv:38`, William Pogue: `Natural causes`
- `.../03E-non-apollo-enriched.tsv:41`, William Thornton: `Not publicly disclosed`
- `Final - Analysis - Enriched Datasets/07E-lunar-enriched.tsv:7`, Eugene Cernan: `Ongoing health issues (family statement; no specific diagnosis disclosed)`
- `.../07E-lunar-enriched.tsv:12`, Richard Gordon: `Cause not specified on Wikipedia`
- `.../07E-lunar-enriched.tsv:16`, Ken Mattingly: `Not publicly disclosed`
- `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv:9`, Milton Thompson: `Natural causes`
- `.../09-x15-pilots-enriched.tsv:12`, Alvin White: `Cause not specified; died in Tucson at 87`
- `Final - Analysis - Enriched Datasets/10-dyna-soar-pilots-enriched.tsv:3`, James Wood: `Natural causes`
- `.../10-dyna-soar-pilots-enriched.tsv:4`, Albert Crews: `Not publicly disclosed`
- `.../10-dyna-soar-pilots-enriched.tsv:5`, Henry Gordon: `unknown`
- `Final - Analysis - Enriched Datasets/11-mol-full-enriched.tsv:8`, Robert Herres: `Not publicly disclosed`

Expected: Either rename the field to `Mort / cause note`, or split into `Cause of Death`, `Cause Specificity`, and `Cause Source`.

Status update, 2026-05-24: Resolved by schema clarification. The final enriched files now use `Mort / cause note`, making clear that non-specific public-disclosure notes are not normalized medical causes of death. Recheck still finds 19 non-specific cause-note values, but they no longer live under a misleading `Mort` field.

## E016: `Time in Space` Contains an Unsubstantive `unknown`

Severity: Low  
Location: `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv:11`, Robert Michael White

Observed: `Time in Space=unknown`.

Expected: Use a numeric/normalized duration, blank with documented missingness, or an explicit precision/status field.

Status update, 2026-05-24: Resolved. Robert Michael White now has `Time in Space=Suborbital only`, matching the convention used for comparable X-15 rows.

## E017: Current Core SG Summary in `BUILD-LOG.md` Is Stale Relative to Standardized Searches

Severity: Medium  
Locations:
- `BUILD-LOG.md:174-185` now reports current canonical core SG totals after the 2026-05-24 standardized-search update.
- `BUILD-LOG.md:19-25` defines SG criteria requiring concrete dated activity at age 80+.

Observed: The later standardized search files change or contest nine core SG classifications, but the build log summary was not updated. This makes article-level claims ambiguous: they may refer to Phase 5 data, later standardized recommendations, or current final TSV values.

Expected: Add a "current canonical SG version" marker and update summary counts after standardized-search adjudication.

Status update, 2026-05-24: Partially resolved. `BUILD-LOG.md` and `data/SG-audit-summary.md` now identify the current canonical SG version and report updated final counts (`07E=17/24`, `08E=4/5`, `03E=19/44`, total `40/73`; `40/50` among age-80+ core rows). The only remaining standardized-search conflict is the low-confidence Curt Michel downgrade recommendation.

## E018: Core and Wider-Cohort SG Denominators Mix Different Universes

Severity: Medium  
Locations:
- Core files: `03E`, `07E`, `08E` together are a complete 73-person pre-1970 NASA astronaut partition.
- Wider files: `09`, `10`, `11` are deduplicated add-on comparison cohorts, not full program rosters.

Observed current final counts:
- Core 73: `40/73` SG=Y currently; `40/50` among age-80+ current final data.
- X-15/current high-speed file: `2/13` SG=Y; `2/4` among age-80+.
- Dyna-Soar current file: `1/4` SG=Y; `1/1` among age-80+.
- MOL current file: `2/8` SG=Y; `2/3` among age-80+.

Expected: Every published SG rate should state whether the denominator is all rows, only age-80+ rows, full roster, or deduplicated unique-person comparison cohort.

Status update, 2026-05-24: Partially resolved. `BUILD-LOG.md` now labels the current core and wider-cohort denominators and separates historical full-roster counts from deduplicated final-file counts. Existing older narrative sections may still contain historical context, but they are now annotated where the denominator changed.

## E019: Walter Cunningham `Time in Space` Is Incorrect

Severity: High  
Location: `Final - Analysis - Enriched Datasets/08E-non-lunar-apollo-enriched.tsv:4`

Observed: Ronnie Walter Cunningham has `Time in Space=10d 23h 0m`.

Expected: NASA's Apollo 7 mission page gives the mission duration as `10 days, 20 hours, 9 minutes, 3 seconds`; NASA biography/release text also describes Cunningham as having about 263 hours in space. The final TSV should use a dataset-standard equivalent such as `10d 20h 9m`, or preserve seconds in a normalized duration field.

Audit output: `data/fact-audit-source-findings-2026-05-24.tsv`, F001.

## E020: Group 6 Scientist-Astronaut Selection Date Is Wrong If Field Means NASA Announcement Date

Severity: High  
Status: Resolved on 2026-05-24 in current TSVs and extraction constants.  
Affected field: `Date of Selection` in `Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv`.

Prior observed: All 11 NASA Group 6 scientist-astronaut rows used `1967-08-11`.

Current status: Corrected to `1967-08-04` in the final enriched non-Apollo TSV, the raw/reference pre-1970 TSVs, and the Group 6 constants in the data-extraction scripts. Robert A. R. Parker's rounded `Age at Selection` was adjusted from `30.7` to `30.6`.

Affected rows:
- `03E-non-apollo-enriched.tsv:2`, Joseph Percival Allen IV
- `03E-non-apollo-enriched.tsv:10`, Philip Kenyon Chapman
- `03E-non-apollo-enriched.tsv:13`, Anthony Wayne England
- `03E-non-apollo-enriched.tsv:24`, Karl Gordon Henize
- `03E-non-apollo-enriched.tsv:25`, Donald Lee Holmquest
- `03E-non-apollo-enriched.tsv:27`, William Benjamin Lenoir
- `03E-non-apollo-enriched.tsv:29`, John Anthony Llewellyn
- `03E-non-apollo-enriched.tsv:33`, Franklin Story Musgrave
- `03E-non-apollo-enriched.tsv:34`, Brian Todd O'Leary
- `03E-non-apollo-enriched.tsv:36`, Robert Allan Ridley Parker
- `03E-non-apollo-enriched.tsv:41`, William Edgar Thornton

Expected: NASA's official `Astronautics and Aeronautics, 1967` chronology places the announcement under `August 4` and says NASA announced selection of the 11 civilian scientist-astronauts, citing `NASA Release 67-211` and `MSC Roundup, 8/18/67`. NASA's 55-year retrospective also says NASA and the National Academy of Sciences announced the 11 new scientist-astronauts on `1967-08-04` and lists the names as formally announced on that date. If `Date of Selection` means NASA announcement/selection date, these rows should be `1967-08-04`.

Source of original error: `Scripts Used/data-extraction/build_lists_v2.py:41` and related extraction scripts previously hard-coded Group 6 as `1967-08-11`, likely inherited from the cached Wikipedia lead sentence. The same cached page's selection section contradicts the lead and says the names were officially announced on `1967-08-04`.

Audit output: `data/fact-audit-source-findings-2026-05-24.tsv`, F002.

## Verification Notes

Checks that passed:
- All enriched TSV files in `Final - Analysis - Enriched Datasets/` have exactly 23 columns per row.
- Both standardized-search TSVs have consistent 25-column rows after URL enrichment.
- No exact duplicate names or surname+birthdate duplicates were found across the six final enriched TSVs.
- `Age at Selection` recalculates from `Date of Birth` and `Date of Selection` within rounding tolerance for final enriched files.
- `Current Age or Age at Death` recalculates from `Date of Birth` and `Date of Death` or a May 2026 current-date reference within rounding tolerance for final enriched files.
- Final enriched files consistently use `Y`/`N` for `Space Grandpa` and `Accidental Death`.

Substantive but limited:
- Many biographical fields are useful and concrete, but the final TSVs still need caution for publication-grade SG analysis because one low-confidence standardized-search conflict remains (Curt Michel), the original enrichment was not deterministic, and several standardized-search URL statuses remain `PARTIAL` or `NEEDS_RESEARCH`.

## Change Log

### 2026-05-23 Initial Error Log Creation

Created `DATA-INTEGRITY-ERROR-LOG.md` and logged 18 findings:
- E001-E004: `Space Grandpa` classification conflicts, missing source URLs, cleared negative evidence, and inconsistent negative-evidence note conventions.
- E005, E017, E018: stale core/wider-cohort SG denominators and mixed denominator universes.
- E006-E007: non-reproducible manual enrichment and stale root-level script paths.
- E008-E014: raw-list missing dates, partial dates, placeholder `Group ` values, mission-field contamination, unreliable name joins, sentinel date text, and SSA TSV comment-header parsing issue.
- E015-E016: non-substantive `Mort` values and `Time in Space=unknown`.
- Added verification notes for checks that passed: final enriched TSV row width, standardized-search TSV row width, duplicate-key scan, date/age arithmetic, and binary `Y`/`N` field consistency.

### 2026-05-23 Line Reference Correction

Corrected E017's build-log location from an overly broad/stale range to `BUILD-LOG.md:174-183`, which is where the core SG total and group-rate summary currently appears.

### 2026-05-23 E002 URL-Enrichment Attempt Interrupted

Started a narrow follow-up task to add source URLs for E002 (`Space Grandpa` evidence trail), including inspecting the standardized-search TSV schemas and launching one GPT-5.5 sidecar for rows 2-12 of `SG-standardized-searches-lunar.tsv`. The task was interrupted before any URL evidence was written to the TSVs or this log. The sidecar was shut down without incorporating output. No E002 URL-enrichment changes have been applied yet.

### 2026-05-23 E002 URL-Enrichment Completed

Completed the narrow URL-enrichment pass for the `Space Grandpa` evidence trail only.

Changes made:
- Added `Evidence URLs`, `Evidence URL Notes`, and `Evidence URL Status` columns to `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-lunar.tsv`.
- Added the same three columns to `Final - Analysis - Enriched Datasets/Standardized Searches/SG-standardized-searches-control.tsv`.
- Populated URL evidence for all 50 standardized-search astronaut rows: 22 lunar/non-lunar-Apollo rows and 28 non-Apollo control rows.
- Updated E002 above with the new URL-enrichment status, validation counts, and remaining row-level cautions.
- Updated the executive finding and verification notes in this log so they no longer describe the standardized-search TSVs as 22-column/no-URL files after remediation.
- Added a dated URL-evidence addendum to `data/SG-audit-summary.md` so the older May 19 existing-source audit now points readers to the enriched standardized-search files.

Controls and validation:
- No existing SG classification, recommendation, confidence, query, summary, or key-evidence columns were intentionally changed.
- Validated both standardized-search TSVs at 25 columns on every row.
- Confirmed there are no blank `Evidence URLs`, `Evidence URL Notes`, or `Evidence URL Status` cells.
- Status counts after enrichment: lunar `OK=10`, `PARTIAL=12`, `NEEDS_RESEARCH=0`; control `OK=13`, `PARTIAL=14`, `NEEDS_RESEARCH=1`.

Recovery note:
- An initial CSV-writer attempt failed on quote handling and truncated `SG-standardized-searches-lunar.tsv` to the enriched header only. The file was immediately restored from the previously inspected row content and rewritten with the URL columns; subsequent row-count and column-count validation passed.

### 2026-05-24 Supplemental Fact Accuracy Audit

Fanned out four read-only subagents to check coverage/name reconciliation, lunar Apollo rows, non-lunar Apollo rows, and non-Apollo NASA core rows against the older project dataset at `<workspace>/projects/apollo-aging-anomaly/astronaut-dataset.tsv`, treating that file as a yardstick rather than canonical.

Outputs created:
- `Scripts Used/qa/fact_accuracy_audit_2026_05_24.py`
- `data/fact-audit-name-coverage-2026-05-24.tsv`
- `data/fact-audit-yardstick-diffs-2026-05-24.tsv`
- `data/fact-audit-yardstick-duplicates-2026-05-24.tsv`
- `data/fact-audit-source-findings-2026-05-24.tsv`
- `data/fact-accuracy-audit-2026-05-24.md`

Key results:
- The yardstick has 99 rows but 98 unique people; its apparent extra name is a duplicate pair, `Donald Peterson` / `Donald H. Peterson`, both pointing to the same DOB, death date, and Wikipedia URL. Current data has the person once as `Donald Herod Peterson`.
- No confirmed current-data mismatch was found for birth dates, death dates, or living/deceased statuses after alias matching and spot checks.
- Added E019 for Cunningham's incorrect `Time in Space`.
- Added E020 for the Group 6 selection-date issue, later confirmed against NASA's `Astronautics and Aeronautics, 1967` chronology as `1967-08-04` if the field means NASA announcement date.

### 2026-05-24 Group 6 Selection Date Correction

Corrected the Group 6 `Date of Selection` from `1967-08-11` to `1967-08-04` in the relevant data tables and extraction constants, using NASA's `Astronautics and Aeronautics, 1967` chronology / NASA Release 67-211 as the controlling source for announcement date. Also updated Robert Parker's rounded `Age at Selection` from `30.7` to `30.6`, regenerated the yardstick-diff audit TSV, and marked F002/E020 as resolved while preserving the source note.

### 2026-05-24 E003-E017 Current-State Recheck

Fanned out five read-only subagents to independently recheck E003-E017 by issue family, then ran a saved local recheck script for reproducible summary counts.

Outputs created:
- `Scripts Used/qa/recheck_error_log_e003_e017_2026_05_24.py`
- `data/error-log-E003-E017-recheck-2026-05-24.tsv`

Key results:
- At that time, E003-E010 and E012-E017 remained open in current files.
- At that time, E011 was partially resolved in checked enriched examples but remained open in raw/reference mission fields.
- No data corrections were applied during this pass; only `DATA-INTEGRITY-ERROR-LOG.md` was updated with current-state status checks.

### 2026-05-24 E003-E017 Correction Pass

Applied scoped corrections for E003-E017 and reran the saved recheck script.

Outputs created:
- `Scripts Used/qa/apply_error_log_e003_e017_corrections_2026_05_24.py`
- `data/person-id-alias-map-2026-05-24.tsv`
- `data/enriched-row-provenance-2026-05-24.tsv`
- `data/ssa-1930-male-cohort-lifetable-metadata.md`

Key results:
- Resolved E003-E005 and E007-E016.
- Partially resolved E006 with row-level provenance; a deterministic enrichment pipeline still does not exist.
- Partially resolved E017/E018 by updating canonical SG and denominator documentation; the only remaining standardized-search SG conflict is Curt Michel (`current=Y`, `recommended=N`, low confidence).
- Current final SG counts are `40/73` overall and `40/50` among core astronauts who reached age 80+.
