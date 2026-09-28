# Stage 1 Cohort Decisions

Prespecified before assembly of person-level birth and death fields. Censoring date: **2026-06-01**.

## Unit and deduplication

The unit is a person, not a seat, mission, selection event, or program assignment. A person appearing in more than one source receives one row and one stable, lowercase, sequence-prefixed name-slug `person_id`. Program flags may overlap. Names are reconciled using full names, service/NASA affiliation, and program history; name spelling alone is never the sole deduplication key.

`other_all=1` exactly when `apollo_flew=0` and at least one of `core_nasa_non_apollo`, `military_x15`, `military_dyna_soar`, or `military_mol` is 1. Therefore `other_all` can never include an Apollo 7–17 flyer. The later “MILITARY_ONLY” comparator is not constructed in Stage 1; its documented definition is the union of the three military-program flags restricted to `apollo_flew=0`.

## Apollo definition

An Apollo flight for `apollo_flew` is a **launched crewed mission numbered Apollo 7 through Apollo 17**, inclusive. A person receives `apollo_flew=1` only if physically launched as prime/flight crew on at least one of those missions. `apollo_missions` lists all such launched missions in numeric order, pipe-separated.

NASA’s mission roster identifies Apollo 7 as the first crewed Apollo flight and lists Apollo 7–17 crews: <https://www.nasa.gov/specials/apollo50th/missions.html>.

- **Apollo 1:** unlaunched. Grissom, White, and Chaffee receive `apollo1_crew=1`, `apollo_flew=0` unless independently launched on Apollo 7–17 (none did), and remain in the NASA comparison family.
- **Skylab:** not an Apollo 7–17 flight. Skylab flight experience is reflected only in `first_spaceflight_date` and notes where useful.
- **Apollo–Soyuz Test Project:** not an Apollo 7–17 flight. Its flight experience is handled like Skylab.
- **Never flew:** retained when included by a top-down roster; `first_spaceflight_date` remains empty.

## NASA astronaut-corps boundary

Include every person in **NASA astronaut selection groups 1 through 7**: Group 1 (April 1959) through the seven former MOL astronauts transferred into NASA as Group 7 (August 1969). Exclude Group 8 (January 1978) and later. The break is exact and source-driven: NASA’s own selection table places Groups 1–7 in 1959–1969, then Group 8 in 1978: <https://www.nasa.gov/wp-content/uploads/2023/09/o57669480.pdf>.

Among these members, `core_nasa_non_apollo=1` exactly when `apollo_flew=0`. Resignations, medical disqualification, preflight death, retirement, and never flying do not remove a rostered member.

`first_selection_date` is the earliest documented full-date selection/transfer into any included program. NASA selection-announcement dates take priority. If an authoritative source supplies only month/year or year, the field is left empty rather than inventing a day, with the partial date explained in `notes`.

## X-15

Include the **12 pilots who actually flew an X-15**, not chase pilots, support pilots, engineers, managers, or merely assigned alternates. NASA’s official flown-pilot roster is controlling: <https://www.nasa.gov/aeronautics/x-15/>.

The column name `military_x15` follows the requested schema but includes all 12 flown research pilots, including NASA and North American Aviation civilian pilots. The flag records program history and can overlap NASA/Apollo membership.

For `first_spaceflight_date`, an X-15 flight counts when it reached at least 50 statute miles (264,000 feet), the U.S. astronaut-wing threshold used in NASA’s official retrospective recognition: <https://www.nasa.gov/news-release/x-15-space-pioneers-now-honored-as-astronauts/>. Lower X-15 flights are not coded as spaceflight.

## X-20 Dyna-Soar

Include the **six people selected to fly Dyna-Soar**: Albert H. Crews Jr., Henry C. Gordon, William J. “Pete” Knight, Russell L. Rogers, James W. Wood, and Milton O. Thompson. The controlling Smithsonian National Air and Space Museum history expressly distinguishes these six selected flyers from Neil A. Armstrong and William H. Dana, who supported development but were not in that selected-to-fly list: <https://repository.si.edu/bitstreams/43c20435-4d2a-4e72-bc24-4546bc6ef1f3/download>.

Accordingly, Armstrong and Dana do not receive `military_dyna_soar=1`. Consultants, engineers, and support personnel are excluded. Dyna-Soar never launched a person, so it creates no `first_spaceflight_date` by itself. The official Air Force program history supplies the 1957–1963 scope: <https://www.aflcmc.af.mil/Portals/13/DynaSoar.pdf>.

## Manned Orbiting Laboratory

Include all **17 crewmembers selected in the three MOL groups**, including members who left before program cancellation and the seven who later transferred to NASA. The National Reconnaissance Office’s official three-group roster controls inclusion: <https://www.nro.gov/news-media-featured-stories/news-media-archive/News-Article/Article/3227331/the-story-of-the-manned-orbiting-laboratory-part-two/>.

Exclude program staff, instructors, contractors, and applicants who were not selected. MOL never launched a crew, so it creates no `first_spaceflight_date` by itself. Later NASA flights are recorded independently.

## Backup crews

Backup assignment does **not** define an untreated control and does not alter `apollo_flew`. `backup_crew_roles` records official Apollo 7–17 backup assignments as `Apollo N backup <role>`, pipe-separated. When the same person later launched as prime crew on Apollo 7–17, the entry also notes the later prime mission. Same-mission substitution is explicitly recorded (for example, a backup who launched after replacing a prime crewmember), as are removed prime assignments when material to interpreting the rotation. Support crews are not treated as backup crews.

Backup rosters are taken from NASA mission-detail pages. The mission’s launched crew always controls `apollo_flew`, including late substitutions.

## Accidental-death flag

`pre1970_accidental_death=1` only when a fetched source supports both:

1. death before `1970-01-01`; and
2. an external accidental event (aviation/spacecraft/vehicle crash, fire, or comparable unintended trauma).

Illness, natural causes, suicide, homicide, undetermined cause, and later death attributed to earlier injuries are not silently inferred as accidental; ambiguous cases remain flagged in `notes` and receive 0 unless the evidence supports both conditions.

## Vital status and dates

Dates use ISO `YYYY-MM-DD`. `death_date` is empty for a person alive on 2026-06-01. `vital_status_20260601` is `alive` or `deceased` as of that date, not current status after the censoring date. For every apparently living person, a targeted query for death/obituary notices dated from 2024 through 2026-06-01 is required and logged.

## Source hierarchy and confidence

1. **Tier 1:** NASA, USAF/Department of the Air Force, NRO, other U.S. government records, official military academy/agency notices, and contemporaneous mission/program documents.
2. **Tier 2:** family-authorized institutional obituaries, universities, museums/archives with curatorial responsibility, and major national/local news obituaries.
3. **Tier 3:** specialist historical references or reputable secondary biographical databases used only when higher-tier material is silent or inaccessible.

Mortality/aging studies and comparative or statistical analyses of the named cohorts/programs are prohibited sources and are never opened. Primary rosters determine inclusion top-down.

Row `confidence` is:

- `high`: membership and vital facts are supported by Tier 1 sources, or a Tier 1 membership source plus an unambiguous Tier 2 obituary;
- `medium`: at least one required fact relies on Tier 3, an indirect institutional source, or a partial-date source;
- `low`: identity/inclusion or vital status remains materially unresolved.

Every membership, birth, and death field must point to a fetched URL. Conflicts are not averaged: the higher-tier, more specific source controls, while the conflict remains visible in `notes` and `SOURCE_LOG.csv`.
