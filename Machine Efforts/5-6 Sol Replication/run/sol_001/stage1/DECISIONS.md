# Stage 1 cohort decisions

Frozen before collection of person-level birth or death data: 2026-07-23T03:10:00Z.

## Primary roster/program sources used to define the frame

- NASA, *Astronaut Fact Book* (January 2023), astronaut selections by group: https://www.nasa.gov/wp-content/uploads/2023/08/astronaut-fact-book-jan-2023.pdf
- NASA, Apollo missions index and crew summaries: https://www.nasa.gov/specials/apollo50th/missions.html
- NASA, Apollo 7 mission history (example of prime and backup crew presentation): https://www.nasa.gov/missions/apollo/about-apollo-7-the-first-crewed-apollo-space-mission/
- NASA, X-15 research-aircraft roster (12 people who actually piloted the aircraft): https://www.nasa.gov/aeronautics/x-15/
- NASA, MOL cancellation history (all 17 USAF MOL pilots, in three selection groups): https://www.nasa.gov/history/55-years-ago-manned-orbiting-laboratory-cancellation/
- National Reconnaissance Office, MOL program history: https://www.nro.gov/About-NRO/history/history-MOL/
- U.S. Air Force Life Cycle Management Center, Dyna-Soar program history: https://www.aflcmc.af.mil/News/Article-Display/Article/1925643/history-in-two-dyna-soar/
- NASA, *Flights of Discovery* (NASA SP-4221), Dyna-Soar history: https://www.nasa.gov/wp-content/uploads/2023/04/sp-4221.pdf

## What counts as an Apollo flight

`apollo_flew=1` means the person was aboard at launch as prime flight crew on a crewed mission numbered Apollo 7 through Apollo 17, inclusive. The exposed group therefore includes Apollo 13 even though it did not land on the Moon. Mission membership is determined top-down from NASA mission pages, not from biographies and not from any mortality or aging analysis.

Apollo 1 is not a flight because it did not launch. Its three assigned prime crew members remain in the NASA selection frame and receive `apollo1_crew=1`, but Apollo 1 alone never causes `apollo_flew=1`.

Skylab and Apollo-Soyuz Test Project flights do not cause `apollo_flew=1`: they were outside the frozen numbered-mission range. Those flights may populate `first_spaceflight_date` or notes for comparison members. Uncrewed Apollo missions do not add people.

People who never flew in space remain in the cohort if a primary roster places them in a frozen NASA selection group or one of the three frozen flight-research program rosters.

## NASA astronaut-corps boundary

The same-era NASA frame is every person listed by NASA in U.S. astronaut selection Groups 1 through 7:

- Group 1, Mercury astronauts, April 1959 (7)
- Group 2, pilot astronauts, September 1962 (9)
- Group 3, pilot astronauts, October 1963 (14)
- Group 4, scientist astronauts, June 1965 (6)
- Group 5, pilot astronauts, April 1966 (19)
- Group 6, scientist astronauts, August 1967 (11)
- Group 7, former USAF MOL astronauts transferred to NASA, August 1969 (7)

Group 7 is included because it is a same-era transfer caused by MOL’s 1969 cancellation and predates the final numbered Apollo launches. Group 8 (1978) and later groups are excluded because of the nine-year post-Group-7 selection break and their Shuttle-era selection. Astronaut status does not depend on ever receiving a flight.

`core_nasa_non_apollo=1` is assigned to a Group 1–7 member only when `apollo_flew=0`.

## X-15 inclusion

Include all 12 people on NASA’s roster of pilots who actually flew an X-15, irrespective of employer (NASA/NACA, USAF, U.S. Navy, or North American Aviation). Ground-only support staff and pilots who trained but never made an X-15 flight are excluded. The output column is named `military_x15` by the required schema, but its documented meaning here is membership in the joint civilian/military X-15 flight-pilot roster.

## X-20 Dyna-Soar inclusion

Include every person formally selected or assigned as a Dyna-Soar pilot during the program: the six announced/initial pilots Neil Armstrong, William H. Dana, Henry C. Gordon, William J. Knight, Russell L. Rogers, and James W. Wood; Albert H. Crews Jr., subsequently added to the flight-pilot cadre; and Milton O. Thompson, whom an official NASA X-15 history/poster describes as selected in 1962 as the sole NASA test pilot for X-20. Because the vehicle never flew, actual flight is not required. Consultants without formal pilot assignment are excluded. Where a source describes Armstrong as a “consultant” rather than an assigned pilot, the row remains included but the source wording and the historical-status ambiguity are retained in `notes` instead of silently excluding him.

Roster amendment recorded 2026-07-23T03:51:00Z: the initial pre-biography freeze named seven Dyna-Soar pilots. During official-source cross-checking, NASA material explicitly identified Milton O. Thompson as a selected X-20 test pilot. The top-down rule (“formally selected or assigned”) therefore requires retaining Thompson as an eighth flagged person. This amendment is documented rather than silently backfilled; the ambiguity between announced USAF astronaut cadre and NASA project-test-pilot status is carried in `notes` and `confidence`.

## MOL inclusion

Include all 17 pilots in the three USAF MOL selection groups identified by NASA/NRO: eight selected 1965-11-12, five selected in 1966, and four selected in 1967. Include members who died before program cancellation, members who later transferred to NASA, and members who never flew in space. Administrative staff and prospective applicants not selected into one of these groups are excluded.

## Overlap and deduplication

One row represents one human being. Stable `person_id` values are name-based ASCII slugs. Program flags may overlap freely. In particular, MOL-to-NASA transfers, X-15/Dyna-Soar pilots, and later Apollo astronauts retain every applicable membership flag.

`other_all=1` is the union of `core_nasa_non_apollo`, `military_x15`, `military_dyna_soar`, and `military_mol` after deduplication, restricted to `apollo_flew=0`. It must be zero for every Apollo flyer.

The later `MILITARY_ONLY` comparator, if constructed in a later stage, is the union of the three military-program-history flags restricted to `apollo_flew=0`. No such comparator or outcome analysis is constructed in Stage 1.

## Backup crews

Backup assignment is descriptive metadata, never an untreated-control definition. `backup_crew_roles` records mission and role for final official backup crews of Apollo 7–17. When a person later crossed from backup to prime, the later prime mission is visible in `apollo_missions`. Known crew substitutions or changes (for example, Apollo 13 and the Apollo 17 backup change) are described in notes where supported. Backup-only status never causes `apollo_flew=1`.

## Accidental-death flag

`pre1970_accidental_death=1` only for a death before 1970-01-01 that an official biography, accident history, or major-outlet obituary attributes to an acute external accident (aircraft/spacecraft crash, vehicle crash, fire, or comparable event). It is zero for later accidents, disease, natural causes, suicide unless authoritatively classed otherwise, unknown causes, and people alive at censoring. The underlying date and description are retained in `notes`; this flag is descriptive and no adjustment or outcome contrast is performed.

## Dates, censoring, and status

The censoring instant is the end of 2026-06-01. Dates use ISO `YYYY-MM-DD`. `death_date` is empty and `vital_status_20260601=alive` when no death on or before the censor date is found after a targeted obituary/death search covering 2024-01-01 through 2026-06-01. A death after the censor date, if encountered, is noted but the person remains alive at the censor date and `death_date` stays empty.

`first_selection_date` is the earliest documented formal selection date into any frozen roster. If a primary source gives only month/year, the value is left empty rather than inventing a day and the partial date is noted. `first_spaceflight_date` is the first launch date of an orbital mission or an X-15 flight that crossed the contemporaneous U.S. 50-mile astronaut threshold. It is empty for a person with no qualifying flight.

## Search disambiguators

`search_disambiguator` is frozen as a direction-neutral, non-outcome phrase based on the earliest or defining roster, such as `NASA astronaut`, `X-15 test pilot`, `Dyna-Soar pilot`, or `MOL astronaut`. It never contains longevity, death, health, comparison-group, or exposure language.

## Source hierarchy and confidence

1. **Tier 1:** NASA, USAF/Space Force, NRO, military service, federal archive, mission press kit, or official institutional biography/roster.
2. **Tier 2:** Major national/regional newspaper obituary, wire service, university, professional society, museum, family-authorized obituary/funeral notice, or contemporaneous reputable magazine.
3. **Tier 3:** Carefully cross-checked reference biography or encyclopedia used only when Tier 1/2 does not expose the needed exact fact.

`confidence=high` requires an official roster source plus an authoritative exact-date source for birth and (if dead) death, with no identity conflict. `medium` marks a fact supported by a reputable but nonofficial exact-date source, a partial selection date, a roster-status ambiguity, or minor source disagreement resolved in notes. `low` marks unresolved identity, inclusion, or date conflict. Uncertain inclusions remain as rows and are flagged; they are never silently dropped.

Every nonempty membership/birth/death claim will carry a fetched URL in `cohort.csv` and a corresponding entry in `SOURCE_LOG.csv`.
