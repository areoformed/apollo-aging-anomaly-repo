# Fact Accuracy Audit Addendum - 2026-05-24

Scope:
- Current compiled data: six final enriched TSVs in `Final - Analysis - Enriched Datasets/`.
- Yardstick only: `<workspace>/projects/apollo-aging-anomaly/astronaut-dataset.tsv`.
- Existing audits consulted: `DATA-INTEGRITY-ERROR-LOG.md`, `data/SG-audit-summary.md`, and `data/SG-audit-existing-sources.tsv`.

This addendum does not treat the older project file as canonical. It uses it as a comparison surface and then checks discrepancies against NASA or other reliable sources.

## Files Produced

- `Scripts Used/qa/fact_accuracy_audit_2026_05_24.py`
- `data/fact-audit-name-coverage-2026-05-24.tsv`
- `data/fact-audit-yardstick-diffs-2026-05-24.tsv`
- `data/fact-audit-yardstick-duplicates-2026-05-24.tsv`
- `data/fact-audit-source-findings-2026-05-24.tsv`

## Subagent Split

- Coverage/name reconciliation: compared all current final rows against the yardstick and resolved aliases/duplicates.
- Lunar Apollo: verified names, birth/death/status, group, selection date, and lunar membership for `07E`.
- Non-lunar Apollo: verified the five `08E` rows.
- Non-Apollo NASA core: verified all 44 `03E` rows.

## Coverage Result

Current final enriched data has 98 unique people across the six files. The yardstick has 99 rows but only 98 unique people. After alias/date matching:

- Current-only unique people: 0.
- Yardstick-only unique people: 0.
- Matched unique people: 98.

The apparent extra name is not a distinct missing person. The yardstick has duplicate rows for the same person:

| Yardstick row | Name | DOB | DOD | Wikipedia |
|---|---|---:|---:|---|
| `astronaut-dataset.tsv:88` | Donald Peterson | 1933-10-22 | 2018-05-27 | `Donald_Peterson_(astronaut)` |
| `astronaut-dataset.tsv:100` | Donald H. Peterson | 1933-10-22 | 2018-05-27 | `Donald_Peterson_(astronaut)` |

The current compiled data has this person once as `Donald Herod Peterson` in `03E-non-apollo-enriched.tsv:37`.

## Confirmed Corrections

| Finding | Field | Current | Yardstick | Verified | Recommendation |
|---|---|---:|---:|---:|---|
| Ronnie Walter Cunningham | `Time in Space` | `10d 23h 0m` | `10d 20h 8m` | Apollo 7 duration `10d 20h 9m 3s` | Correct current to `10d 20h 9m` or an explicitly seconds-preserving format. |
| NASA Group 6 scientist-astronauts | `Date of Selection` | `1967-08-04` | `1967-08-04` | NASA chronology places the announcement under Aug. 4, 1967 and cites NASA Release 67-211 / MSC Roundup 8/18/67 | Resolved on 2026-05-24 in current/raw data and extraction constants; corrected from `1967-08-11`, and Robert Parker's rounded `Age at Selection` was adjusted to `30.6`. |

Affected Group 6 rows in `03E-non-apollo-enriched.tsv`: Joseph Allen, Philip Chapman, Anthony England, Karl Henize, Donald Holmquest, William Lenoir, John Llewellyn, Story Musgrave, Brian O'Leary, Robert Parker, and William Thornton.

## Not Confirmed As Errors

- Birth dates, death dates, and living/deceased statuses: no confirmed current-data mismatch surfaced in the final enriched files after alias matching and spot checks. Jim Lovell's Aug. 7, 2025 death is already reflected in current data.
- Group labels: most `Group` differences are label style (`Group 2 - The New Nine` vs `NASA Group 2 - The Next Nine`) or primary-vs-all-membership differences in the wide comparison cohorts.
- Group 3 selection date: current uses `1963-10-18`; yardstick uses `1963-10-17`. NASA's historical article supports Oct. 18 as the announcement date. Treat this as a date-convention conflict unless the project standard is "selection board decision date."
- Mission lists: yardstick sometimes includes Apollo 1 assignments, Shuttle Approach and Landing Tests, or X-15 detail. Current core rows generally use actual flown space missions. That is defensible, but the field definition should be explicit.
- Source conflicts to annotate rather than silently change: Donn Eisele death date (`1987-12-01` vs one NASA PDF saying Dec. 2), Wally Schirra death date (`2007-05-03` vs one NASA page saying May 2), and Paul Weitz death date (`2017-10-22` vs a NASA Fact Book conflict noted by the subagent).

## Name Policy Recommendation

Add stable identity columns before publication-grade joins:

- `person_id`: normalized canonical-name plus birth date, or another stable ID.
- `canonical_name`: NASA/official full name where available.
- `display_name`: article-friendly/common name.
- `aliases`: common names and prior dataset names.

High-value alias examples: `Donald Herod Peterson` / `Donald H. Peterson` / `Donald Peterson`; `Walter Marty Schirra Jr.` / `Wally Schirra`; `Franklin Story Musgrave` / `Story Musgrave`; `Richard F. Gordon Jr.` / `Richard Gordon`; `Thomas P. Stafford` / `Thomas Stafford`; `Alfred M. Worden` / `Al Worden`.

## Sources Used

- NASA Astronaut Fact Book: https://www.nasa.gov/reference/astronaut-fact-book/
- NASA Group 3 history: https://www.nasa.gov/history/60-years-ago-nasa-selects-its-third-group-of-astronauts/
- NASA Group 6 history: https://www.nasa.gov/history/55-years-ago-nasa-selects-11-scientist-astronauts/
- NASA Astronautics and Aeronautics, 1967: https://www.nasa.gov/wp-content/uploads/2023/04/1967.pdf
- NASA Group 7 history: https://www.nasa.gov/history/55-years-ago-nasa-group-7-astronaut-selection/
- NASA Apollo 7 mission page: https://www.nasa.gov/mission_pages/apollo/missions/apollo7.html
- NASA Jim Lovell release: https://www.nasa.gov/news-release/acting-nasa-administrator-reflects-on-legacy-of-astronaut-jim-lovell/
