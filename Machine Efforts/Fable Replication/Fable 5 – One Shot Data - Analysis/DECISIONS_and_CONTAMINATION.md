# Apollo-era astronaut cohort — Stage 1 reference dataset

Built 2026-06-09. Censoring date 2026-06-01. One row per person, n = 73.
CSV: `apollo_era_astronaut_cohort.csv` (generated and validated by `build_cohort.py`).

## DECISIONS

**D0 — Unit and cohort labels.** One row per person (not per flight). Four labels:
- `APOLLO_FLEW` (29) — launched on a crewed Apollo mission (Apollo 7–17)
- `APOLLO1_CREW` (3) — Apollo 1 crew; died in the pad fire; never launched
- `COMP_FLEW_OTHER` (29) — comparison: same selection pool, never flew Apollo, flew in space in some other program
- `COMP_NEVER_FLEW` (12) — comparison: same selection pool, never flew in space at all

**D1 — "Flew Apollo" = launched aboard Apollo 7 through Apollo 17** (Oct 1968 – Dec 1972), the only crewed spaceflights of the Apollo program proper. Apollo 2–6 were uncrewed; Apollo 1 never launched (D2). 29 unique individuals; the four two-time Apollo flyers (Lovell 8+13, Young 10+16, Cernan 10+17, Scott 9+15) appear once with both missions listed in `apollo_missions`. Rationale: the question is exposure to an Apollo flight, so the criterion is launching, not mission assignment, lunar landing, or program affiliation. Crew lists verified against nasa.gov mission pages and NASA's Astronaut Fact Book (Jan 2023).

**D2 — Apollo 1 crew get their own cohort (`APOLLO1_CREW`), not membership in either main cohort.** Grissom, White, and Chaffee died 1967-01-27 in the AS-204 cabin fire during a launch-pad test. They never flew an Apollo mission, so they fail D1; but placing them in the comparison group would load three Apollo-caused deaths into the "never flew Apollo" arm, biasing it in an obvious way. A separate label preserves the information and forces the analyst to make an explicit choice. `apollo_missions` is left empty for them (the column means missions *flown*); the assignment is recorded in `notes`. Grissom and White had prior Mercury/Gemini flights (so they have `first_spaceflight_year`); Chaffee never flew.

**D3 — Skylab and Apollo–Soyuz are not Apollo.** The Apollo program ended with Apollo 17 (Dec 1972). Skylab (1973–74) and ASTP (1975) were separate programs that reused Apollo CSM hardware. The nine astronauts whose only spaceflights were Skylab/ASTP (Kerwin, Weitz; Garriott, Lousma; Carr, Gibson, Pogue; Brand, Slayton) are `COMP_FLEW_OTHER`, each flagged in `notes` as having flown Apollo-derived hardware so an analyst who prefers a hardware-based definition can reclassify them trivially. Apollo veterans who also flew Skylab/ASTP (Conrad, Bean, Stafford) remain `APOLLO_FLEW`; their `apollo_missions` lists Apollo flights only.

**D4 — Astronauts who never flew at all are included (`COMP_NEVER_FLEW`, 12).** Five died in accidents while on active astronaut duty before any flight (Freeman 1964; See and Bassett 1966; Givens 1967; Williams 1967) and seven left the program unflown (Graveline 1965; Bull 1968; Llewellyn 1968; O'Leary 1968; Michel 1969; Chapman 1972; Holmquest 1973). Rationale: all were selected, i.e., met the selection requirements; silently dropping the early accidental deaths would bias any survival comparison toward survivors ("immortal cohort" of the comparison arm). They carry an empty `first_spaceflight_year`, so excluding them is a one-line filter.

**D5 — Comparison bound: the NASA astronaut corps Groups 1–7 (selections 1959–1969), minus Apollo flyers and the Apollo 1 crew.** The selection requirements evolved across groups, so there is no single fixed standard; the operative standard I adopt is *"admitted to the NASA astronaut corps during the Apollo-era selections, under the pilot-astronaut or scientist-astronaut requirements from which Apollo crews were actually drawn."* Justification per group:
- Groups 1–3, 5 (pilot tracks; 1959/1962/1963/1966): supplied 28 of 29 Apollo flyers — definitionally "Apollo selection requirements." (Requirements drifted: Group 1 military test pilots <40; Group 2 test pilots <35 incl. civilians; Groups 3/5 relaxed to jet pilots with 1,000 hrs, age ≤34 / ≤36; all required degrees, height limits, U.S. citizenship. Sources: NASA history articles for each selection and NASA SP-4214.)
- Group 4 (1965 scientist-astronauts): supplied an Apollo crew member (Schmitt, Apollo 17), so the scientist-astronaut track (doctorate, NAS screening, age and height limits, subsequent jet training) also counts as "Apollo selection requirements." **IN.**
- Group 6 (1967 scientist-astronauts): selected under the same scientist-astronaut announcement structure as Group 4 (doctorate; NAS screening; born on/after 1930-08-01; ≤6 ft; citizen or naturalized), recruited for Apollo Applications. Same standard as a group that flew Apollo → **IN.**
- Group 7 (1969): the seven USAF Manned Orbiting Laboratory pilots NASA absorbed in Aug 1969 after MOL's cancellation — military test pilots taken into the corps (only those under ~35) while Apollo was still flying. Edge case: their *original* selection was by the USAF, not NASA, under MOL's own (materially equivalent, test-pilot) standards, and there was no open NASA competition. **IN, flagged**; `nasa_group = 7` makes exclusion a one-line filter. The 8th MOL transferee, Albert H. Crews, moved to NASA's Flight Crew Operations Directorate as a pilot but was *not* admitted to the astronaut corps → excluded.
- **OUT:** Group 8 (1978) and later — selected five-plus years after Apollo ended, under new Shuttle-era criteria; X-15 pilots who never joined the NASA corps (e.g., Joe Walker) — astronaut wings but not NASA astronauts; MOL pilots who never transferred; payload specialists; non-U.S. astronauts (task specifies American).
This bound has the convenient completeness property that Groups 1–7 sum to exactly 73 = 29 + 3 + 29 + 12, i.e., every member of the seven Apollo-era selection groups appears exactly once and nobody else appears at all — no silent exclusions possible.

**D6 — `first_spaceflight_year`** = year of the person's first flight above the U.S. 50-statute-mile boundary, in any program, including suborbital Mercury flights (Shepard 1961, Grissom 1961) and Engle's USAF X-15 astronaut-wing flights (first 1965-06-29). Empty = never flew in space. Rationale: first exposure to spaceflight is the analytically relevant event, and the 50-mile rule is the standard under which these individuals were credited as astronauts. Where "first orbital flight" differs (Shepard → 1971, Grissom → 1965, Engle → 1981), the row notes say so.

**D7 — Censoring.** `vital_status_20260601` is status as of 2026-06-01. Anyone alive on that date is ALIVE with an empty `death_date`, even if they were to die between 2026-06-01 and today (2026-06-09); no such case was found. Every ALIVE row was actively checked for death reports (targeted obituary searches through 2026-06-09), not just assumed from an old bio page.

**D8 — Citizenship.** "American astronauts" = U.S. citizens at selection (a NASA requirement in every group). Llewellyn (born Cardiff, Wales) and Chapman (born Melbourne, Australia) were naturalized U.S. citizens — the Group 6 announcement explicitly allowed citizens "naturalized by March 15, 1967" — so both are IN, with birthplaces noted. Collins (born Rome) and Anders (born Hong Kong) were citizens from birth (U.S. military families) — no edge case.

**D9 — Individual edge cases.**
- **Slayton (G1):** grounded 1962–72 for idiopathic atrial fibrillation before ever flying Mercury; ran Flight Crew Operations throughout Apollo; flew ASTP 1975. Stays `COMP_FLEW_OTHER`, but note that his non-Apollo status was *health-caused* — a selection-into-exposure caveat analysts should know about.
- **Engle (G5):** the only person in the pool with pre-NASA spaceflight (X-15, 1965); also the nearest "almost flew Apollo" case — he was the assigned Apollo 17 LMP until Schmitt replaced him. `COMP_FLEW_OTHER`.
- **Graveline (G4):** resigned weeks after selection (Aug 1965), never completed training. Retained under a strict "met the requirements at selection" reading; flagged in notes so analysts may exclude.
- **Mattingly (G5):** removed from Apollo 13 days before launch (measles exposure) but flew Apollo 16 → `APOLLO_FLEW` regardless.
- **Haise (G5):** Apollo 13 aborted its landing but he launched on an Apollo mission → `APOLLO_FLEW`; his 1977 Shuttle ALT glide flights are atmospheric, not spaceflight.
- **Glenn (G1):** flew STS-95 in 1998 at age 77, decades after the era — cohort unchanged (`COMP_FLEW_OTHER`), noted.
- Post-Apollo Shuttle flights by Apollo veterans (Young, Mattingly) don't change cohorts.

**D10 — Names** follow NASA biography style, nicknames in parentheses, no commas (CSV safety). Aldrin's legal name has been Buzz Aldrin since 1988.

**D11 — Sources and confidence.** Hierarchy: NASA bios/releases (nasa.gov, jsc.nasa.gov, history.nasa.gov, incl. archived captures) > major-outlet or official family/funeral-home obituaries > museum/foundation/specialist outlets (collectSPACE, Astronaut Scholarship Foundation, NM Museum of Space History, Space.com) > general references. Every cited URL was actually fetched and checked by a research agent during construction (2026-06-09); no URL is pattern-guessed. `confidence`: HIGH = NASA or major obituary confirms exactly; MEDIUM = a ≤1-day discrepancy exists between credible sources (explained in notes); LOW = genuine multi-source conflict (explained in notes). Date conflicts found and adjudicated:
- **Evans** death: NASA bio 1990-04-06 vs wire-report implication of 04-07 → NASA date used, MEDIUM.
- **Schirra** death: NASA people page 2007-05-02 vs AP/Britannica/family 2007-05-03 → 05-03 used, MEDIUM.
- **Swigert** death: NASA bio internally lists 1982-12-27 (data sheet) and 12-28 (narrative) → 12-27 used (corroborated), MEDIUM.
- **Weitz** death: 2017-10-22 / 10-23 / 10-24 across sources → best-attested 10-23 used, LOW.
- **Michel** death: working value 2015-02-23 was wrong → corrected to 2015-02-26 (NASA bio + NASA release + Rice University), HIGH.

**Completeness identity.** Groups 1–7: 7 + 9 + 14 + 6 + 19 + 11 + 7 = 73 = 29 `APOLLO_FLEW` + 3 `APOLLO1_CREW` + 29 `COMP_FLEW_OTHER` + 12 `COMP_NEVER_FLEW`. Roster sources: NASA Astronaut Fact Book (Jan 2023), https://www.nasa.gov/wp-content/uploads/2023/08/astronaut-fact-book-jan-2023.pdf; NASA history selection articles (65-years-ago Mercury Seven; 60-years-ago Groups 2 and 3; SP-4214 for Groups 4–5; 55-years-ago Groups 6 and 7); nasa.gov/mission/apollo-N pages for crews. Machine-checked: cohort/group totals, one row per person, each of Apollo 7–17 appearing on exactly 3 rows, date formats, death ≤ censoring date, status/death-field consistency, sort order.

## CONTAMINATION

- **No mortality/longevity study was consulted, opened, or copied at any point.** The cohort was constructed top-down from program structure (NASA selection-group rosters and Apollo mission crew lists from NASA sources), and per-person vital data came from NASA biographies, NASA news releases, and ordinary obituaries.
- Nine independent research agents performed the verification sweep with explicit instructions to record (and not open) any astronaut-mortality/longevity/aging study surfaced by their searches. **All nine reported zero such encounters** — no titles/URLs to log.
- Transparency note: the model performing this construction is generally aware, from training, that academic literature on astronaut mortality exists. No table, membership list, or result from any such work was retrieved or reproduced here; the membership of every cohort above is derivable purely from the NASA program records cited in D5/D11.

---

# STAGE 1b — cognitive-status and documentation-depth coding

Added 2026-06-09. Enriches the Stage 1 cohort with two coded fields plus provenance, in
`apollo_era_astronaut_cohort_v2.csv` (16 columns), generated and validated by
`build_stage1b.py` (reads the frozen Stage 1 CSV; does not alter it).

## STAGE-1b DECISIONS

**C0 — Two coded fields + per-row provenance.** Per Stage 1 discipline, each cognitive
code carries its own source URL (`cognitive_source_url`) and a reasoning line
(`cognitive_notes`); `documentation_depth` is justified inline in the same notes. No new
"confidence" column was added — the two genuinely low-confidence codings (C6) are flagged
in their notes and called out below instead.

**C1 — `cognitive_status_20260601` is an end-state measure, coded only from fetched
sources.** For the living it means status at the censoring date; for the deceased it means
late-life/end-of-life status. The four codes are exactly as briefed. I coded from sources,
never from fame: a household name with no qualifying dated evidence is `NO_EVIDENCE`
(e.g., David R. Scott, John W. Young, Ken Mattingly — all `documentation_depth = HIGH` yet
`NO_EVIDENCE`, the informative combination the task asked us to record honestly).

**C2 — Absence is never intactness.** `INTACT_DOCUMENTED` requires *affirmative, dated*
evidence of functioning cognition (a substantive interview, public talk/Q&A, authorship,
active piloting, or advisory/professional service). The absence of any impairment report
is coded `NO_EVIDENCE`, not intact. Conversely I did not infer impairment from frailty,
reclusiveness, or a non-cognitive illness.

**C3 — `DIED_EARLY` cutoff = died before the 70th birthday.** Rationale: 70 is a
conventional gerontological threshold for "late life" and roughly where dementia incidence
becomes appreciable, so deaths before 70 give no real late-life cognitive observation
window. `build_stage1b.py` *recomputes* age at death from the Stage 1 birth/death dates and
asserts the code agrees — a hard integrity check, not a hand assertion. 17 people qualify.
Two fall just under the line and are coded `DIED_EARLY` with the margin noted: **Conrad**
(69.1, motorcycle accident) and **Slayton** (69.3, brain-tumor complications). Two fall
just over (71) and are therefore coded on the merits, both `INTACT` on narrow windows:
**Lenoir** (71) and **O'Leary** (71). Slayton's glioblastoma and Henize's death are noted
as context but `DIED_EARLY` takes precedence over any cause-based cognitive inference.

**C4 — Qualifying window for `INTACT`.** To stop a vigorous-at-75 interview from certifying
someone who lived to 95, intact evidence had to be reasonably proximate to the end state:
for the living, dated **2023-01-01 to 2026-06-01**; for the deceased, **within 5 years of
death AND at age ≥ 70**. Evidence outside the window does not qualify — it is recorded in
the notes as the most-recent-but-stale item and the row is coded `NO_EVIDENCE` (e.g.,
**Hartsfield** Nov-2008 autograph show; **Thornton** 2013 panel; **Young** 2012 memoir;
**Scott** 2021 panel; **Brand** 2019 panel). This makes `NO_EVIDENCE` partly a statement
about *recency* of evidence, which the notes always disclose.

**C5 — What does and does not count as impairment.** Coded `IMPAIRED_DOCUMENTED` only on a
published diagnosis or credible report of dementia / persistent major cognitive decline.
Explicitly *excluded*: motor-only disease (Parkinson's with no reported cognitive
component — **Truly** "atypical Parkinson's," **Cooper** late Parkinson's mentions →
both not impaired); transient, recovered episodes (**Graveline**'s self-reported transient
global amnesia ~1999–2004 → not impaired, coded INTACT on later authorship); a terminal-
phase stroke/delirium in the final days only (**Carpenter**'s stroke ~1 month pre-death,
**Borman**'s final-days stroke, **Llewellyn** "following a stroke" of undocumented duration
→ none coded impaired); and a relative's condition (**Borman**'s wife Susan had Alzheimer's
— hers, not his). A resolved allegation followed by qualifying intact evidence codes INTACT
with the allegation noted (**Aldrin**: 2018 family guardianship petition alleging decline,
2018 UCLA evaluation finding full capacity, petition withdrawn 2019, continued public
activity at 95–96).

**C6 — The two `IMPAIRED_DOCUMENTED` codings, and their confidence.**
- **Donald H. Peterson** — *higher confidence.* The Washington Post obituary (2018-05-29)
  reports he died of Alzheimer's disease and bone cancer. Caveat logged in the row: the
  WaPo page returned HTTP 403 on fetch, so the exact wording was confirmed via Wikipedia's
  citation of that obituary and corroborated by spacefacts.de; the family funeral-home obit
  names no illness. A named dementia diagnosis in a national obituary clears the bar.
- **C. Gordon Fullerton** — *explicit judgment call, lower confidence.* No dementia label.
  The basis is a severe stroke (late 2009) followed by multi-year incapacity that NASA's
  own memorial describes in cognitive/communicative terms ("worked hard to regain his body
  and **mind**," his "sense of humor returned" then his "condition worsened"), with
  confinement to long-term care "for most of the past 3½ years." Under C5's
  persistent-post-stroke clause this is sufficient, but it rests on interpretation of
  memorial prose rather than a diagnosis. An analyst who wants a diagnosis-only definition
  of impairment should reclassify Fullerton to `NO_EVIDENCE`; the note carries the source
  language verbatim so the call can be audited or reversed without re-research.

**C7 — `documentation_depth` is volume, not content, and is independent of the cognitive
code.** HIGH = extensive coverage including later life (multiple substantive
profiles/interviews/books/documentaries; national obituaries); LOW = little beyond an
official NASA bio and a local/funeral-home obit; MEDIUM = between. Graded from what the
searches actually surfaced. The 4 LOW-depth people (**Bull, Givens, Holmquest, Parker**)
are all coded `NO_EVIDENCE` or `DIED_EARLY` — low depth *causes* missing cognitive
evidence, exactly the honest LOW+NO_EVIDENCE pairing the task wanted surfaced. Depth tracks
public profile, not the Stage 1 cohort: it is not a function of whether someone flew Apollo.

**C8 — Provenance quality, flagged where thin.** Most INTACT rows cite a dated interview,
talk, or news item. A few rest on weaker-but-still-affirmative provenance, flagged in their
notes: **Aldrin** (the astronaut's own dated X/Twitter post, with national 95th-birthday
coverage as corroboration); **Carr** (live Skype Q&As documented via the *Searching for
Skylab* film record); **Shepard** and **O'Leary** (authorship — a co-authored book / a
signed cover essay — rather than an interview); **Lenoir** (advisory/organizational service
described in an institutional obituary). All are dated and within-window; none is coded from
mere reputation.

**C9 — Coding distribution (descriptive only; no analysis performed or implied).**
INTACT 40 · DIED_EARLY 17 · NO_EVIDENCE 14 · IMPAIRED 2. Depth: HIGH 40 · MEDIUM 29 ·
LOW 4. The script also emits a cohort × cognitive-status cross-tab purely as a data-quality
readout (e.g., it shows the comparison arms carry most of the `NO_EVIDENCE` mass, which is a
*coverage* artifact to be aware of, not a finding).

## STAGE-1b CONTAMINATION

Unlike Stage 1, the cognitive sweep **did** surface group-level studies — searching any
astronaut's name beside "Alzheimer's/dementia" pulls in the space-radiation-and-cognition
literature. Per the rule, agents recorded these **without opening them** and moved on.
None is an astronaut mortality/longevity *cohort* study (the Stage 1 hazard); they are
radiation/aging-mechanism papers and press coverage thereof. Distinct items encountered:

- *Space Radiation Could Accelerate Alzheimer's in Astronaut Brains* — https://www.space.com/19082-space-radiation-astronauts-alzheimers.html
- *Does Deep Space Travel Cause Alzheimer's?* (Smithsonian) — https://www.smithsonianmag.com/science-nature/does-deep-space-travel-cause-alzheimers-94946/
- *Astronauts with Alzheimer's* (UTMB Medical Discovery News podcast) — https://www.utmb.edu/mdnews/podcast/episode/astronauts-with-alzheimer's
- *Ionizing radiation, cerebrovascular disease, and consequent dementia: a review…* — https://pmc.ncbi.nlm.nih.gov/articles/PMC9640983/
- *The effects of low doses of proton, iron or silicon radiation on spatial learning in a mouse model of Alzheimer's disease* — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3941486/
- *Continuous and Intermittent Artificial Gravity as a Countermeasure to the Cognitive Effects of 60 Days of Head-Down Tilt Bed Rest* — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8009974/

No abstract, table, or result from any of the above was read; each was identified from the
search-result title/snippet alone and skipped. All per-person codings rest solely on
biographies, interviews, event pages, news, and obituaries.

## Stage 1b data dictionary (added columns)

- `cognitive_status_20260601`: `IMPAIRED_DOCUMENTED` | `INTACT_DOCUMENTED` |
  `NO_EVIDENCE_EITHER_WAY` | `DIED_EARLY` (see C1–C6).
- `documentation_depth`: `HIGH` | `MEDIUM` | `LOW` — volume of public coverage, content-
  blind (C7).
- `cognitive_source_url`: provenance for an `IMPAIRED`/`INTACT` code; empty for
  `NO_EVIDENCE`/`DIED_EARLY` (enforced by the build script).
- `cognitive_notes`: per-row evidence and reasoning; semicolons only, no commas; for INTACT
  gives evidence type + date + age, for NO_EVIDENCE gives what was searched and the most
  recent non-qualifying item, for IMPAIRED gives the gist of the source wording.

---

## Data dictionary (column semantics)

- `cohort`: see D0. Filter on this, not on `apollo_missions`.
- `nasa_group`: NASA astronaut selection group 1–7 (Group 7 = 1969 USAF MOL transfers).
- `birth_date`, `death_date`: YYYY-MM-DD; `death_date` empty for ALIVE.
- `vital_status_20260601`: ALIVE/DEAD as of 2026-06-01 (D7).
- `apollo_missions`: Apollo missions *flown* (semicolon-separated); empty for everyone outside `APOLLO_FLEW` including the Apollo 1 crew (D2).
- `first_spaceflight_year`: per D6; empty = never flew in space.
- `birth_source_url` / `death_source_url`: fetched-and-verified source for the respective date (D11).
- `confidence` + `notes`: see D11; notes use semicolons (no commas anywhere — the CSV is comma-safe without quoting).
