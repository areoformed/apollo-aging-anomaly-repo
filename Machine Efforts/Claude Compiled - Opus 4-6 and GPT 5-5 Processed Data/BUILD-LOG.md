# Apollo Aging Anomaly Dataset — Build Log

**Build Date:** May 18, 2026
**QA Date:** May 18, 2026
**Builder:** Claude (clean-room extraction from cached Wikipedia sources)
**QA:** Claude (automated + manual verification)

---

## Methodology

**Approach:** Clean-room dataset construction. All biographical data extracted from individual Wikipedia articles, cached locally before extraction began. No pre-existing datasets were consulted. The goal is a researcher-grade dataset of all 73 NASA astronauts selected before 1970, partitioned by Apollo lunar flight participation.

**Source Tier Hierarchy:**
1. **Primary:** Individual Wikipedia biographical articles (73 cached locally in `Cached Pages/wiki-individual/`)
2. **Secondary:** Wikipedia list articles (`wiki-apollo-astronauts.md`, `wiki-astronauts-by-selection.md`, `wiki-group-6-scientists-1967.md`, `wiki-group-7-mol-transfer.md`)
3. **Tertiary:** Cross-referencing between Wikipedia articles for consistency

**Space Grandpa Criteria:**
- Documented evidence of sustained physical or intellectual activity at age 80+
- Must have specific, citeable events (not just "was still alive")
- Activities include: public speaking, publishing, receiving awards, physical feats, active professional work, founding organizations
- "Y" requires at least one concrete, dated activity at age 80+
- Astronauts who died before 80 are automatically "N"
- Edge cases resolved by requiring documented *sustained* activity, not single appearances

---

## Files Produced

### Base Lists (extracted from Wikipedia list articles)

| File | Description | Data Rows | Columns |
|------|-------------|-----------|---------|
| `01-all-pre-1970-astronauts.tsv` | Complete roster, all 7 groups (Mercury 7 through MOL Transfer) | 73 | 6 |
| `02-deduplicated-pre-1970.tsv` | Same as 01 (deduplication pass confirmed no duplicates) | 73 | 6 |
| `03-non-apollo-astronauts.tsv` | Astronauts who never flew Apollo 7-17 lunar missions | 44 | 6 |
| `04-non-apollo-flew.tsv` | Subset of 03: went to space on non-Apollo missions | 31 | 6 |
| `05-non-apollo-never-flew.tsv` | Subset of 03: never went to space | 13 | 6 |
| `06-apollo-applications.tsv` | Skylab + ASTP crews (reference/overlap file) | 12 | 7 |
| `07-lunar-astronauts.tsv` | All 24 astronauts who flew Apollo 8-17 | 24 | 7 |
| `08-non-lunar-apollo.tsv` | Apollo 7 + Apollo 9 crew not on later lunar missions | 5 | 5 |

### Enriched Files (extracted from individual Wikipedia articles)

| File | Description | Data Rows | Columns |
|------|-------------|-----------|---------|
| `07E-lunar-enriched.tsv` | Full biographical data for lunar Apollo astronauts | 24 | 23 |
| `08E-non-lunar-apollo-enriched.tsv` | Full biographical data for non-lunar Apollo astronauts | 5 | 23 |
| `03E-non-apollo-enriched.tsv` | Full biographical data for non-Apollo astronauts | 44 | 23 |

**Partition integrity:** 24 + 5 + 44 = 73 (complete, no overlaps, no gaps)

### 23-Column Schema (Enriched Files)

1. Name
2. Astronaut Group
3. Date of Birth
4. Date of Selection
5. Age at Selection
6. Went to Space
7. Moonwalker
8. Missions Flown
9. Number of Flights
10. Time in Space
11. Date of Death
12. Current Age or Age at Death
13. Status
14. Accidental Death
15. Mort (cause of death)
16. Space Grandpa
17. Space Grandpa Citation
18. Military Branch
19. Pre-NASA Career
20. Education
21. Post-NASA Career
22. Birth Year
23. Citations (Wikipedia URL)

### Supporting Files

| Directory | Contents |
|-----------|----------|
| `Cached Pages/wiki-individual/` | 73 cached Wikipedia article texts (one per astronaut) |
| `Cached Pages/` | 4 cached Wikipedia list articles |
| `Scripts Used/` | Empty (extraction done via Claude conversation) |

---

## QA Results

### PASSED

- **Row counts:** All three enriched files have correct row counts (24, 5, 44)
- **Column count:** All three enriched files have exactly 23 columns per row
- **No empty rows or malformed tabs:** Every data row has exactly 23 tab-delimited fields
- **Date format:** All Date of Birth, Date of Selection, and Date of Death values are in YYYY-MM-DD format
- **"The New Nine" naming:** All files use "The New Nine" (not "Next Nine") for Group 2
- **Moonwalker field:** Exactly 12 astronauts marked Y — Aldrin, Armstrong, Bean, Cernan, Conrad, Duke, Irwin, Mitchell, Scott, Schmitt, Shepard, Young. All others marked N. No non-lunar files contain any Y values.
- **Living astronauts:** All living astronauts have blank Date of Death and blank Mort fields (Aldrin, Duke, Haise, Schmitt, Scott in 07E; Schweickart in 08E; Allen, Brand, Crippen, England, Gibson, Holmquest, Kerwin, Lousma, Musgrave, Parker in 03E)
- **No duplicate names** across the three enriched files
- **Partition integrity:** 24 + 5 + 44 = 73, matching complete roster
- **Wikipedia citation URLs** present for every row in all enriched files

### ISSUES FOUND

#### Critical

**1. Accidental Death field inconsistency across files** — **FIXED May 19**
- 07E: 22 blank cells → "N"; 08E: 1 blank (Schweickart) → "N"
- All three files now use "N" for non-accidental, "Y" for accidental

#### Minor

**2. Group 3 selection date discrepancy** — **FIXED May 19**
- Standardized to `1963-10-18` across all files (NASA official date)
- 08E: 3 rows updated; 03E: 4 rows updated

**3. Trailing whitespace in Mort field for living astronauts** — **FIXED May 19**
- Aldrin (07E) and Schweickart (08E) Mort fields stripped to blank

**4. Space Grandpa Citation populated for SG=N entries (08E only)** — **FIXED May 19**
- Blanked SG Citation for SG=N entries in 08E for consistency
- Preserved content: Schirra ("Contributed to books at 82-84 but limited evidence of physical activities in final years"), Eisele ("Died at 57, not applicable"), McDivitt ("Appeared at Apollo 9 50th anniversary at 89 but limited documented evidence of sustained high acuity beyond commemorative events")

**5. Missing trailing newline in 07E** — **FIXED May 19**

**6. Name format inconsistency between base and enriched files**
- Base lists use common names (e.g., "Tom Stafford", "Wally Schirra")
- Enriched files use full legal names (e.g., "Thomas Stafford", "Walter Marty Schirra Jr.")
- This is by design but means the files cannot be joined by name without a mapping
- **Fix optional:** Not necessarily a problem since the enriched files are the authoritative versions

**7. Base list data quality issues (01, 02, 03)**
- 25 of 73 entries in 01 have incomplete Astronaut Group field (just "Group " with trailing space)
- Missions Flown field in base lists includes backup/support roles, not just actual flights
- These are known limitations of the initial Wikipedia list extraction and are corrected in the enriched files
- **No fix needed** in base lists since enriched files are canonical

---

## Known Gaps and Limitations

1. **Mort field specificity varies.** Phase 5 (May 19) resolved 10 of 11 investigated cases via obituary/news searches. Four definitive causes found (Lovell, Mitchell, Garriott, Truly). Remaining "Not publicly disclosed" entries reflect genuine non-disclosure by families, not missing research.

2. **Age calculations are decimal approximations.** "Current Age or Age at Death" values appear to be calculated to 2 decimal places from birth/death dates. The reference date for living astronauts' current ages is not explicitly stated but appears to be approximately May 2026.

3. **Time in Space format inconsistency.** 07E uses compact format ("12d 1h 53m"), 08E uses similar compact format ("12d 7h 15m"), but 03E uses mixed formats including "314 hours", "313 hours", and "4 hours, 56 minutes" alongside the day-hour-minute format. This will require normalization for quantitative analysis.

4. **Henize accidental death classification is debatable.** Karl Henize died of high-altitude pulmonary edema during a Mount Everest expedition at age 67. This is classified as Accidental Death = Y, which is defensible but could be argued either way.

5. **Wikipedia is the sole source.** No cross-referencing against NASA biographical databases, obituaries, or other primary sources. Wikipedia accuracy for well-known astronauts is generally high but not guaranteed.

6. **Space Grandpa is a subjective classification.** Despite having criteria, edge cases exist. Schirra was upgraded to Y on 2026-05-24 using standardized-search evidence; Curt Michel remains a low-confidence conflict (`current=Y`, standardized recommendation `N`). The threshold is "sustained" activity, which introduces judgment.

7. **The 06 file (Apollo Applications) is a reference file, not a partition member.** Its 12 members overlap with both 07E and 03E. It documents Skylab and ASTP crew assignments for contextual use.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total astronauts in dataset | 73 |
| Flew to space | 60 |
| Never flew | 13 |
| Flew Apollo lunar missions (8-17) | 24 |
| Flew Apollo non-lunar (7, 9 only) | 5 |
| Non-Apollo astronauts | 44 |
| Moonwalkers | 12 |
| Still living (as of May 2026) | 16 |
| Deceased | 57 |
| Accidental deaths | 13 |
| Space Grandpa = Y | 40 |
| Space Grandpa = N | 33 |

Current canonical SG version, 2026-05-24: final enriched TSV values after applying high/medium standardized-search upgrades. The only remaining standardized-search conflict is the low-confidence Curt Michel recommendation (`current=Y`, `recommended=N`), retained as `Y` pending source adjudication.

### Space Grandpa by Group (after Phase 5)

| Group | SG=Y | Total | Rate |
|-------|------|-------|------|
| Lunar Apollo (07E) | 17 | 24 | 70.8% |
| Non-lunar Apollo (08E) | 4 | 5 | 80.0% |
| Non-Apollo control (03E) | 19 | 44 | 43.2% |

---

## Phase 5: Deep Verification (May 19, 2026)

### Mort Field Updates
Searched obituaries, NASA announcements, and news archives for 11 astronauts with missing/vague cause of death.

**Definitive causes found (4):**
- Jim Lovell: Complications of hip fracture from fall; cardiovascular disease contributing (Lake County coroner)
- Edgar Mitchell: Kidney cancer (renal carcinoma)
- Owen Garriott: Heart attack while hospitalized for broken neck from fall (WAFF Huntsville)
- Richard Truly: Complications of atypical Parkinson's disease (Washington Post)

**Partial (2):**
- Eugene Cernan: "Ongoing health issues" per family statement; no specific diagnosis
- Gerald Carr: "Brief illness" per funeral home; no specific diagnosis

**Not publicly disclosed (5):** Mattingly, Chapman, Glenn, McCandless, Thornton

### Space Grandpa Upgrades
Investigated 11 astronauts who lived past 80 but were marked SG=N. Searched web for evidence of sustained activity at 80+.

**Upgraded to Y (5, all in control group 03E):**
- Jack Lousma (age ~90, living): Multiple speaking events, Skylab 50th events (2017-2023)
- Gerald Carr (died at 88): Documentary interviews ages 84-88, artistic collaboration
- Owen Garriott (died at 88): Astronaut Hall of Fame induction at 80, AOPA event at 86
- Don Lind (died at 92): LDS Temple presidency, sustained speaking career
- Curt Michel (died at 80): Active daily research at Rice, book published at 80

**Confirmed N (6):** Parker, England, Holmquest, Thornton, McCandless, Hartsfield

**Note on visibility bias:** All 5 upgrades were in the control group. This suggests the initial Space Grandpa gradient (62.5% vs 22.7%) was partially inflated by visibility bias — famous lunar astronauts have better-documented late-life activities. The corrected gradient (62.5% vs 34.1%) still shows a lunar advantage but is less dramatic. This is methodologically important for the article.

---

*Build log updated May 19, 2026 (Phase 5 complete).*

---

## Phase 7a: X-15 Research Pilots (May 19, 2026)

### Overview

Extended the dataset beyond the core 73 NASA astronauts to include all 12 X-15 research pilots. The X-15 program (1959-1968) was a joint NASA/USAF/USN hypersonic flight research program that produced 199 flights across three airframes. Eight of the 12 pilots exceeded the USAF spaceflight threshold of 50 miles (80 km); one pilot (Joseph Walker) exceeded the FAI Karman line of 100 km on two flights.

### Pilots Found: 12

| Pilot | Affiliation | X-15 Flights | Exceeded 50 mi? | Exceeded 100 km? | Died | Age at Death |
|-------|-------------|--------------|------------------|-------------------|------|-------------|
| Michael James Adams | USAF | 7 | Y | N | 1967-11-15 | 37 |
| Neil Armstrong | NASA | 7 | N | N | 2012-08-25 | 82 |
| Albert Scott Crossfield | NAA | 14 | N | N | 2006-04-19 | 84 |
| William Harvey Dana | NASA | 16 | Y | N | 2014-05-06 | 83 |
| Joseph Henry Engle | USAF | 16 | Y | N | 2024-07-10 | 91 |
| William John Knight | USAF | 16 | Y | N | 2004-05-07 | 74 |
| John Barron McKay | NASA | 29 | Y | N | 1975-04-27 | 52 |
| Forrest Silas Petersen | USN | 5 | N | N | 1990-12-08 | 68 |
| Robert Aitken Rushworth | USAF | 34 | Y | N | 1993-03-18 | 68 |
| Milton Orville Thompson | USN Reserve | 14 | N | N | 1993-08-06 | 67 |
| Joseph Albert Walker | NASA | 25 | Y | Y (2 flights) | 1966-06-08 | 45 |
| Robert Michael White | USAF | 16 | Y | N | 2010-03-17 | 85 |

### Overlap with Core 73 Dataset

Two X-15 pilots also appear in the core 73 NASA astronauts:

1. **Neil Armstrong** -- X-15 pilot (7 flights, 1960-1962) AND Group 2 -- The New Nine / Apollo 11 crew. Appears in `07E-lunar-enriched.tsv`. His X-15 flights predated his NASA astronaut selection. He did NOT qualify as an astronaut via X-15 (max altitude 207,500 ft / 63 km, below 80 km threshold).

2. **Joseph Henry Engle** -- X-15 pilot (16 flights, 1963-1965) AND Group 5 -- The Original Nineteen / STS-2, STS-51-I. Appears in `03E-non-apollo-enriched.tsv`. He earned USAF astronaut wings via X-15 before joining NASA. He was the youngest pilot to qualify as astronaut at the time and the last surviving X-15 pilot (died July 2024).

No other X-15 pilots appear in the core 73. Some future astronauts served as X-15 chase pilots (Michael Collins, Fred Haise, Jim McDivitt) but did not fly the X-15 itself.

### Space Grandpa Classification

Current final-file note, 2026-05-24: the table below records the original full X-15 roster classification before later deduplication and append work. The current deduplicated file `09-x15-pilots-enriched.tsv` has 13 rows: Armstrong and Engle were removed as core-73 overlaps, and Alvin White, Iven Kincheloe, and Bill Bridgeman were appended as high-speed research pilots. Current final SG rate is `2/13` overall and `2/4` among age-80+ rows.

| Pilot | Lived Past 80? | SG | Rationale |
|-------|---------------|-----|-----------|
| Adams | No (37) | N | Killed in X-15 crash |
| Armstrong | Yes (82) | N | No documented sustained activity at 80+ |
| Crossfield | Yes (84) | Y | Flew 200 hrs/year through 80s; trained Wright Experience pilots 2001-2003; giving speech at Maxwell AFB at time of fatal flight at 84 |
| Dana | Yes (83) | N | Parkinson's disease; no documented sustained activity at 80+ |
| Engle | Yes (91) | Y | Inducted International Air & Space Hall of Fame at 82; active interviews and public appearances through 80s and early 90s |
| Knight | No (74) | N | Died of leukemia |
| McKay | No (52) | N | Died of complications from 1962 X-15 crash injuries |
| Petersen | No (68) | N | Died of brain tumor |
| Rushworth | No (68) | N | Died of heart attack |
| Thompson | No (67) | N | Natural causes |
| Walker | No (45) | N | Killed in F-104/XB-70 mid-air collision |
| White | Yes (85) | Y | Inducted National Aviation Hall of Fame at 82 (July 2006); attended 2005 NASA astronaut wings ceremony at Edwards at 80 |

Historical full-roster/pre-dedup SG rate: 3/12 (25%). Current deduplicated final-file SG rate: 2/13 (15.4%) overall; 2/4 (50.0%) among age-80+ rows.

### Accidental Deaths

Current deduplicated final file: 5 of 13 (38.5%):
- Michael Adams: X-15-3 structural failure during reentry (1967)
- Scott Crossfield: Cessna 210A crash in thunderstorm (2006)
- Joseph Walker: F-104N/XB-70 mid-air collision during formation flight (1966)
- Iven Kincheloe: F-104A crash at Edwards AFB (1958)
- Bill Bridgeman: Grumman Goose crash near Catalina Island (1968)

### "Went to Space" Field Notes

The "Went to Space" field uses the USAF definition (50 miles / 80 km) as the primary threshold, consistent with how the USAF awarded astronaut wings to its X-15 pilots. The FAI Karman line (100 km) is noted in Citations where relevant.
- 8 pilots exceeded 50 mi (80 km): Adams, Dana, Engle, Knight, McKay, Rushworth, Walker, White
- 1 pilot exceeded 100 km (FAI): Walker only
- 4 pilots did not reach space: Armstrong (63 km), Crossfield (27 km), Petersen (31 km), Thompson (65 km)

### Cached Source Pages

All source pages cached in `Cached Pages/military-programs/x-15/`:
- `wiki-north-american-x-15.md` -- Main program article
- `wiki-list-of-x15-flights.md` -- Flight list article
- `wiki-michael-adams.md`
- `wiki-neil-armstrong-x15.md` (X-15-specific extract; full bio in `Cached Pages/wiki-individual/`)
- `wiki-scott-crossfield.md`
- `wiki-william-dana.md`
- `wiki-joe-engle-x15.md` (X-15-specific extract; full bio in core 03E)
- `wiki-william-knight.md`
- `wiki-john-mckay.md`
- `wiki-forrest-petersen.md`
- `wiki-robert-rushworth.md`
- `wiki-milton-thompson.md`
- `wiki-joseph-walker.md`
- `wiki-robert-white.md`

### Sources Used

- Wikipedia articles (primary, cached locally before extraction)
- NASA X-15 Pilots page and individual NASA biographies (flight count cross-reference)
- Obituaries: Washington Post (White, Engle), Space.com (Dana, Crossfield), NASA news releases (Dana)
- AOPA (Crossfield crash report), NTSB final report
- National Aviation Hall of Fame (White induction details)
- UW Magazine (Crossfield late-life activities)

### Known Gaps

1. **Date of Selection precision varies.** For pilots assigned to the program before their first flight (Rushworth, White, Petersen designated ~1958), exact assignment dates are approximated. First X-15 flight date used where program entry date unavailable.
2. **Flight count discrepancies.** Sources disagree on exact flight counts for some pilots (e.g., Walker: 24 vs 25; McKay: 29 vs 30; Crossfield: 14 free flights out of 16 captive + 14 free). Counts from the main Wikipedia X-15 article and individual biographies were cross-referenced; the most commonly cited free-flight figure was used.
3. **Armstrong and Engle "Went to Space" via X-15.** Armstrong's field reads "N (via X-15)" to clarify he did not reach space on X-15 flights specifically. Engle's reads "Y" because he exceeded 50 mi on three X-15 flights. Both obviously went to space on later missions (Gemini/Apollo and Shuttle respectively).
4. **Crossfield was not a NASA or military pilot** during X-15 tenure -- he flew as North American Aviation's chief engineering test pilot. His military branch (USN) reflects earlier service, not his X-15 affiliation.
5. **All 12 X-15 pilots are now deceased.** Joe Engle, the last survivor, died July 10, 2024. This means the cohort's longevity data is complete.

### File Produced

| File | Description | Data Rows | Columns |
|------|-------------|-----------|---------|
| `09-x15-pilots-enriched.tsv` | Deduplicated biographical data for X-15/high-speed research pilots outside the core-73 files | 13 | 23 |

---

*Build log updated May 19, 2026 (Phase 7a complete).*

---

## Phase 7b: X-20 Dyna-Soar Pilot Roster (May 19, 2026)

### Overview
Extended the dataset with a clean-room roster of all Boeing X-20 Dyna-Soar pilot selectees. The Dyna-Soar was a USAF spaceplane program (1957-1963) that selected military and civilian test pilots before cancellation on December 10, 1963. These pilots form a comparison cohort: same era, same physical fitness standards, same test-pilot career track as NASA astronauts, but different program exposure.

### Pilots Found: 8

**Original seven (selected April 1960, secretly):**
1. Neil Armstrong (NASA) — departed mid-1962 for NASA Group 2
2. William Harvey Dana (NASA) — departed mid-1962
3. Henry Charles Gordon (USAF)
4. William John "Pete" Knight (USAF)
5. Russell Lee Rogers (USAF)
6. Milton Orville Thompson (NASA)
7. James Wayne Wood (USAF)

**Added later:**
8. Albert Hanlin Crews Jr. (USAF) — selected April 20, 1962; assigned as pilot September 20, 1962

### Overlaps with Core 73

| Dyna-Soar Pilot | Core 73 Entry | Core Group |
|-----------------|---------------|------------|
| Neil Armstrong | Yes — `07E-lunar-enriched.tsv` | Group 2 — The New Nine |

Only 1 core overlap. Historical full-roster notes include Armstrong for program context; the current deduplicated `10-dyna-soar-pilots-enriched.tsv` excludes Armstrong because he is retained in the core-73 lunar file. Albert Crews transferred to NASA JSC after MOL cancellation (1969) but was excluded from NASA astronaut corps due to age (40); he is NOT in the core 73.

### "Went to Space" Determination

Three Dyna-Soar pilots later reached space:
- **Neil Armstrong:** Gemini 8, Apollo 11 (via NASA)
- **William Dana:** 2 X-15 flights above 50 miles (awarded NASA civilian astronaut wings retroactively in 2005)
- **William Knight:** 1 X-15 flight above 50 miles (awarded USAF astronaut wings)

Milton Thompson flew 14 X-15 flights but never exceeded the 50-mile threshold (peak: 214,100 ft = 40.5 miles).

### Space Grandpa Classification

Current final-file note, 2026-05-24: the table below records the original full Dyna-Soar roster before cross-program deduplication. The current `10-dyna-soar-pilots-enriched.tsv` excludes core/X-15 overlaps and has 4 rows: Russell Rogers, James Wood, Albert Crews, and Henry Gordon.

| Pilot | Lived Past 80? | SG | Rationale |
|-------|---------------|-----|-----------|
| Armstrong | Yes (82) | N | No documented sustained activity at 80+ |
| Dana | Yes (83) | N | Parkinson's disease; limited activity evidence after age 80 |
| Gordon | No (70) | N | |
| Knight | No (74) | N | |
| Rogers | No (39) | N | Killed in F-105 accident |
| Thompson | No (67) | N | |
| Wood | No (65) | N | |
| Crews | Yes (96) | Y | Attended NRO MOL 50th anniversary at age 90 (June 2019) |

Historical full-roster/pre-dedup SG rate: 1/8 (12.5%). Current deduplicated final-file SG rate: 1/4 (25.0%) overall; 1/1 (100.0%) among age-80+ rows.

### Accidental Deaths

Current deduplicated final file: 1 of 4, Russell Lee Rogers (F-105 engine failure, parachute malfunction, Kadena AFB, 1967).

### File Produced

| File | Description | Data Rows | Columns |
|------|-------------|-----------|---------|
| `10-dyna-soar-pilots-enriched.tsv` | Deduplicated biographical data for X-20 Dyna-Soar pilot selectees outside core/X-15 files | 4 | 23 |

### Cached Source Pages

All source pages cached in `Cached Pages/military-programs/dyna-soar/`:
- `wiki-boeing-x20-dyna-soar.md` — Main program article
- `wiki-albert-crews.md`
- `wiki-william-knight.md`
- `wiki-james-wood.md`
- `wiki-henry-gordon.md`
- `wiki-russell-rogers.md`
- `wiki-william-dana.md`
- `wiki-milton-thompson.md`

Neil Armstrong's Wikipedia page was already cached in `Cached Pages/wiki-individual/` from Phase 1.

### Sources Used
- Wikipedia articles (primary, cached locally)
- Web searches for obituaries, NASA bios, USAF records, aviation history sites
- PBS NOVA Astrospies profiles
- NASA JSC Oral History Project
- Space.com (Albert Crews profile)

### Known Gaps

1. **Selection date precision:** The original seven were selected "in April 1960" — no more specific date is documented. Date of Selection is recorded as `1960-04-01` (first of month convention). Crews' selection is better documented: April 20, 1962.
2. **Henry Gordon post-military career:** No public sources document his career after USAF retirement. His Wikipedia article and astronautix.com entry both lack this information.
3. **Milton Thompson cause of death:** Sources say "natural causes" but no specific diagnosis is publicly available.
4. **Time in Space for X-15 pilots:** Recorded as approximate ("~20m" for Dana's 2 qualifying flights, "~10m" for Knight's 1 qualifying flight). X-15 flights lasted roughly 10-12 minutes each; precise above-50-mile durations are not readily available.
5. **Dana and Knight flight counts:** The "Number of Flights" field records their 16 total X-15 flights each, not just the space-qualifying ones. This mirrors how the core-73 files count total missions.

---

*Build log updated May 19, 2026 (Phase 7b complete).*

---

## Phase 7c: Manned Orbiting Laboratory (MOL) Full Roster (May 19, 2026)

### Overview
Extended the dataset with a clean-room roster of ALL Manned Orbiting Laboratory (MOL) astronaut selectees across all three selection groups. The MOL was a classified USAF space station program (1963-1969, codenamed "Dorian") that selected military test pilots for crewed reconnaissance missions before cancellation on June 10, 1969. Seven of the youngest MOL pilots transferred to NASA as Astronaut Group 7 and later flew Space Shuttle missions. The remaining 10 did not transfer (3 had already departed the program; 7 exceeded NASA's age-35 cutoff).

### Selectees Found: 17

**MOL Group 1 (November 12, 1965) — 8 pilots:**
1. Michael James Adams (USAF) — died 1967 in X-15 crash
2. Albert Hanlin Crews Jr. (USAF) — transferred to NASA JSC as test pilot (not astronaut); died 2025 at 96
3. John Lawrence Finley (USN) — resigned April 1968; died 2006 at 70
4. Richard Earl Lawyer (USAF) — died 2005 at 73
5. Lachlan Macleay (USAF) — living at 94
6. Francis Gregory Neubeck (USAF) — living at 94
7. James Martin Taylor (USAF) — died 1970 in T-38 crash at 39
8. Richard Harrison Truly (USN) — transferred to NASA Group 7; died 2024 at 86

**MOL Group 2 (June 17, 1966) — 5 pilots:**
9. Karol Joseph Bobko (USAF) — transferred to NASA Group 7; died 2023 at 85
10. Robert Laurel Crippen (USN) — transferred to NASA Group 7; living at 88
11. Charles Gordon Fullerton (USAF) — transferred to NASA Group 7; died 2013 at 76
12. Henry Warren Hartsfield Jr. (USAF) — transferred to NASA Group 7; died 2014 at 80
13. Robert Franklyn Overmyer (USMC) — transferred to NASA Group 7; died 1996 at 59

**MOL Group 3 (June 30, 1967) — 4 pilots:**
14. James Alan Abrahamson (USAF) — living at 93
15. Robert Tralles Herres (USAF) — died 2008 at 75
16. Robert Henry Lawrence Jr. (USAF) — first African-American astronaut selectee; died 1967 in F-104 crash at 32
17. Donald Herod Peterson (USAF) — transferred to NASA Group 7; died 2018 at 84

### Overlaps with Core 73

| MOL Pilot | Core 73 Entry | Core Group |
|-----------|---------------|------------|
| Richard H. Truly | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| Karol J. Bobko | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| Robert L. Crippen | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| C. Gordon Fullerton | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| Henry W. Hartsfield Jr. | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| Robert F. Overmyer | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |
| Donald H. Peterson | Yes — `03E-non-apollo-enriched.tsv` | Group 7 — MOL Transfer |

7 overlaps (all NASA Group 7 transfers). Historical full-roster notes include them for program context; the current deduplicated `11-mol-full-enriched.tsv` excludes these core-73 transfers.

### Cross-Overlap with Dyna-Soar Roster (Phase 7b)

| Pilot | MOL File | Dyna-Soar File |
|-------|----------|----------------|
| Albert Hanlin Crews Jr. | MOL Group 1 | `10-dyna-soar-pilots-enriched.tsv` |

1 cross-overlap. Crews was selected for Dyna-Soar (1962), then MOL (1965), then transferred to NASA JSC as a test pilot (1969). He never flew in space. The current deduplicated MOL final file excludes Crews because he is retained in the Dyna-Soar file.

### "Went to Space" Determination

Historical full MOL roster: 7 of 17 selectees eventually flew in space via NASA Space Shuttle after transferring to NASA Group 7. Michael Adams reached 81 km on X-15 Flight 191, which qualifies as suborbital spaceflight by the U.S. 50-mile definition, but this was an X-15 flight, not an MOL mission. Current deduplicated final files record Adams in `09-x15-pilots-enriched.tsv` with `Went to Space=Y` and exclude him from `11-mol-full-enriched.tsv`; the current MOL final file has 0/8 `Went to Space=Y`.

### Space Grandpa Classification

Current final-file note, 2026-05-24: the table below records the historical full MOL roster. The current deduplicated `11-mol-full-enriched.tsv` has 8 rows after removing core-73 transfers plus Adams and Crews cross-program overlaps.

| Pilot | Lived Past 80? | SG | Rationale |
|-------|---------------|-----|-----------|
| Adams | No (37) | N | Killed in X-15 crash |
| Crews | Yes (96) | Y | 2015 NRO panel at 86; public speaking on MOL history into 90s |
| Finley | No (70) | N | |
| Lawyer | No (73) | N | |
| Macleay | Yes (94) | Y | 2019 NRO MOL panel at 88; contributed to "Spies in Space" publication |
| Neubeck | Yes (94) | N | Living at 94 but no documented activity at 80+; last confirmed active 2008 (PBS documentary at 75) |
| Taylor | No (39) | N | Killed in T-38 crash |
| Truly | Yes (86) | N | |
| Bobko | Yes (85) | N | |
| Crippen | Yes (88) | Y | Wright Brothers Memorial Trophy at 86 (2023); living at 88 |
| Fullerton | No (76) | N | |
| Hartsfield | Yes (80) | N | |
| Overmyer | No (59) | N | Killed in aircraft crash |
| Abrahamson | Yes (93) | Y | 2015 NRO panel at 82; GeoEye/DigitalGlobe board chairmanship at 80 |
| Herres | No (75) | N | |
| Lawrence | No (32) | N | Killed in F-104 crash |
| Peterson | Yes (84) | N | |

Historical full-roster/pre-dedup SG rate: 4/17 (23.5%). Current deduplicated final-file SG rate: 2/8 (25.0%) overall; 2/3 (66.7%) among age-80+ rows.

### Accidental Deaths

Historical full roster: Adams (X-15, 1967), Taylor (T-38, 1970), Lawrence (F-104, 1967), plus Overmyer (Cirrus VK-30, 1996) = 4/17 accidental deaths. Current deduplicated MOL final file retains Taylor and Lawrence only: 2/8 (25.0%).

### File Produced

| File | Description | Data Rows | Columns |
|------|-------------|-----------|---------|
| `11-mol-full-enriched.tsv` | Deduplicated biographical data for MOL selectees outside core/X-15/Dyna-Soar files | 8 | 23 |

### Cached Source Pages

All source pages cached in `Cached Pages/military-programs/mol/`:
- `wiki-mol-program.md` — Main MOL Wikipedia article (astronaut sections)
- `wiki-michael-adams.md`
- `wiki-albert-crews.md`
- `wiki-john-finley.md`
- `wiki-richard-lawyer.md`
- `wiki-lachlan-macleay.md`
- `wiki-francis-neubeck.md`
- `wiki-james-taylor.md`
- `wiki-james-abrahamson.md`
- `wiki-robert-herres.md`
- `wiki-robert-lawrence.md`

The 7 NASA Group 7 transfer pilots already had Wikipedia pages cached in `Cached Pages/wiki-individual/` from Phase 1.

### Sources Used
- Wikipedia articles (primary, cached locally)
- NASA history articles ("55 Years Ago: MOL Cancellation" and "50 Years Ago: NASA Benefits from MOL Cancellation")
- Wikipedia: NASA Astronaut Group 7 article (for transfer details and age-limit rationale)
- NRO declassified records and 2015/2019 panel event documentation
- PBS NOVA "Astrospies" profiles
- Web searches for obituaries, USAF biographies, space history sites
- Smithsonian Air & Space Magazine ("The MOL-Men Come Into the Light")
- Space.com MOL coverage

### Known Gaps

1. **Francis Neubeck current status:** Wikipedia lists him as living at 94, but no verifiable activity has been documented since 2008 (PBS documentary appearance at age 75). No obituary found. Space Grandpa is marked N due to lack of documented 80+ activity despite likely being alive.
2. **Albert Crews cause of death:** Wikipedia records his death on June 7, 2025 at age 96 but no specific cause of death is publicly available. No obituary was found in searches.
3. **James Taylor education details:** Only BS in Electrical Engineering from University of Michigan is documented. Pre-USAF background is sparse — no high school or advanced degrees found.
4. **Robert Herres cause of death:** Died July 24, 2008 at age 75. No specific cause of death documented in Wikipedia or web searches.
5. **Michael Adams "Went to Space":** Adams reached 81 km (266,000 ft) on X-15 Flight 191, qualifying for USAF astronaut wings (above 50 miles). However, this was not an MOL mission. Current deduplicated final files retain Adams in `09-x15-pilots-enriched.tsv` with `Went to Space=Y` and exclude him from `11-mol-full-enriched.tsv`.
6. **MOL selection dates as "Date of Selection":** The TSV records MOL group selection dates, not NASA transfer dates (August 14, 1969). The 7 NASA transfers have their NASA Group 7 selection date (1969-08-14) in the core 03E file. This file uses their original MOL selection dates. Analysts joining the files should note this intentional difference.

---

*Build log updated May 19, 2026 (Phase 7c complete).*
