# Stage 1 Validation

Validation timestamp: 2026-07-23T03:25:01Z  
Censor date: 2026-06-01  
Validator: `python3 validate_stage1.py`

## Result

PASS — `cohort_rows=95 source_rows=552 checks=2194 all_checks_passed=1`

## Mechanical checks performed

- `cohort.csv` has the exact required 23-column header and order.
- `SOURCE_LOG.csv` has the exact required 10-column header and order.
- The cohort contains 95 unique `person_id` values and 95 unique full names.
- Identity, disambiguator, membership-source, and birth-source fields are nonblank for every person.
- Every date is either blank by rule or a valid full ISO `YYYY-MM-DD` date.
- Every binary field contains only `0` or `1`.
- Censor status is mechanically consistent with death date and the 2026-06-01 censor.
- `apollo_flew` is mechanically consistent with `apollo_missions`.
- `core_nasa_non_apollo` and `other_all` exactly follow the frozen formulas in `DECISIONS.md`.
- Structural roster counts reconcile to the frozen source rosters: 29 Apollo flyers, 3 Apollo 1 crew, 44 core NASA non-Apollo members, 12 X-15 pilots, 8 Dyna-Soar/X-20 pilots, 17 MOL selectees, and 66 members of the non-Apollo union.
- All 12 positive pre-1970 accidental-death flags have a death date before 1970-01-01 and an explicit evidence-ledger row.
- Every birth URL appears in that person's source ledger.
- Every deceased person's death URL is nonblank and appears in that person's source ledger.
- Every apparently living person has a direction-neutral targeted-search entry; living records have no fabricated death URL.
- Every membership URL, nonblank exact selection date, nonblank first-spaceflight date, and backup-role assignment is represented in the source ledger.

## Recorded limitations

- Exact first-selection dates are blank where the consulted source established only a month or year. No synthetic day was imputed.
- Several non-NASA pilot/selectee birth or death dates rely on reference or major-reference sources and are marked `medium` confidence.
- Robert A. Rushworth's death date is recorded as 1993-03-18; the row notes a one-day conflict with a NASA image page.
- The Dyna-Soar/X-20 boundary includes Milton O. Thompson because NASA identifies him as the sole NASA X-20 test pilot; the roster-boundary rationale is preserved in `DECISIONS.md`.
- No comparative mortality, survival, longevity, exposure-effect, or other group-outcome calculation was run in Stage 1.
