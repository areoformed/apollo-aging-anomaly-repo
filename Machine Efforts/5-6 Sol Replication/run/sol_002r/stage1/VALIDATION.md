# Stage 1 validation

## Cohort counts

- Deduplicated people: 95
- NASA selection Groups 1-7: 73
- Distinct people launched on Apollo 7-17: 29
- Core NASA non-Apollo members: 44
- X-15 actual pilots: 12
- Dyna-Soar selected-to-fly pilots: 6
- MOL selectees: 17
- `other_all=1`: 66
- Apollo 1 crew flags: 3
- Pre-1970 accidental-death flags: 12
- Alive at 2026-06-01: 19
- Deceased by 2026-06-01: 76

These are roster and data-integrity counts only. No outcome contrast was calculated.

## Overlap checks

- Apollo/X-15: 1 (Neil A. Armstrong)
- X-15/Dyna-Soar: 2 (Milton O. Thompson|William J. "Pete" Knight)
- X-15/MOL: 1 (Michael J. Adams)
- Dyna-Soar/MOL: 1 (Albert H. Crews Jr.)
- NASA Groups 1-7/MOL: 7 (C. Gordon Fullerton|Donald H. Peterson|Henry W. Hartsfield Jr.|Karol J. Bobko|Richard H. Truly|Robert F. Overmyer|Robert L. Crippen)
- The 29 Apollo flyers all have `other_all=0`, including Neil Armstrong, whose X-15 flag remains 1.
- The later `MILITARY_ONLY` definition is reproducible as `(military_x15 OR military_dyna_soar OR military_mol) AND apollo_flew=0`; no such downstream group was analyzed here.

## Duplicate and schema checks

- `person_id`: 95 unique values; no duplicates.
- Case-folded `full_name`: 95 unique values; no duplicates.
- CSV header exactly matches the requested 23-column order.
- CSV was written with Python's `csv` module using CRLF records and RFC 4180 quoting.
- Multi-value cells use `|`.
- All Boolean columns contain only `0` or `1`.

## Date and status checks

- Every non-empty date parses as ISO `YYYY-MM-DD`.
- Every `alive` row has an empty `death_date` and empty `death_source_url`.
- Every `deceased` row has a death date on or before 2026-06-01 and a fetched death source URL.
- Every row has a fetched membership URL and a fetched birth source URL.
- All 19 apparently living people have a targeted, disambiguated death/obituary search spanning 2024-01-01 through 2026-06-01 recorded in `SOURCE_LOG.csv`.
- Anthony W. England and James A. Abrahamson produced same-name obituary snippets for other people; role disambiguation prevented false matches.

## Unresolved or qualified items

- Exact first included-program selection dates were not located for several X-15-only and Dyna-Soar-only pilots; those cells remain blank and are called out in row notes rather than imputed.
- X-15 `first_spaceflight_date` uses the fixed U.S. 50-mile threshold. Crossfield, Petersen, and Thompson did not have a qualifying X-15 flight and therefore remain blank.
- Walter Schirra's death date has a one-day discrepancy among NASA historical pages; the current NASA Astronaut Fact Book value, 2007-05-03, was retained and noted.
- Albert Crews' death date was corrected to 2025-06-07 after a targeted follow-up found the accessible individual biography. The earlier unsupported transcription was discarded and documented in `ACTION_LOG.md`.
- Individual vital dates for the 22 non-NASA-roster-only people rely on fetched Tier 3 biographies because the official program rosters establish membership but generally do not publish complete exact vital dates. Those rows are marked `medium` confidence.
- Backup roles are normalized from official mission pages. Mattingly's late Apollo 13 prime-crew removal and Swigert's crossover from backup to launched prime crew are explicitly retained.
