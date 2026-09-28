# Stage 1C validation

## Scope and row integrity

- The full salted worklist is covered one-for-one by `PERSON_OUTCOMES.csv`: PASS.
- Duplicate research IDs in person outcomes: PASS — none.
- No cohort flag columns occur in the research worklist, search log, evidence events, or outcomes: PASS.

## Search-budget checks

- Every eligible research ID has all six required base query-family labels: PASS.
- Every returned base or extra result retained rank and URL; zero-result queries have an explicit `no_results` row: PASS.
- Ranked results are capped at the first ten per query: PASS.
- Page attempts and access failures are explicit; base attempts proceed through ranked results until two accessible eligible pages or ranked-result exhaustion as recorded in raw collection files: PASS.
- Extra-query cap (two) and extra-page cap (three): PASS.
- Every extra query/page row has a locked trigger: PASS.
- R001 technical merged-stream deviation is retained in `DECISIONS_AND_DEVIATIONS.md`, `SEARCH_LOG.csv`, and person notes rather than silently repaired: PASS.

## Date, follow-up, and endpoint checks

- Potential follow-up is the interval from the 80th birthday to the earlier of the 85th birthday or 2026-06-01: PASS.
- Observed primary follow-up ends at the earliest primary qualifying function event, death, 85th birthday, or 2026-06-01: PASS.
- Death is coded as competing only when it precedes detected primary function inside age [80,85): PASS.
- Administrative censoring before five years is coded only when 2026-06-01 precedes age 85 without earlier primary function or death: PASS.
- Every qualifying event's analysis date lies inside its person's age-80 evidence-collection window: PASS.
- DAY, MONTH, and YEAR precision rows retain earliest/latest bounds and use the locked analysis-date rule: PASS.
- Boundary flags compare earliest/latest dates with both the age-80 and age-85 boundaries: PASS.

## State and documentation checks

- Outcome states use only the seven locked mutually exclusive/exhaustive labels: PASS.
- Every positive state is linked to its qualifying function and/or impairment rows; eligible persons without either are `NEITHER_FOUND`; no absence is coded as impairment: PASS.
- Function and impairment evidence are retained independently and ordered from their defensible date bounds: PASS.
- `substantive_sources_opened` counts unique successfully opened substantive URLs; `independent_publishers` counts normalized publisher domains: PASS.
- Documentation depth matches raw counts: LOW=0–1; MEDIUM=2–4; HIGH=5 or more across at least two independent publishers. Five or more from only one publisher is conservatively capped at MEDIUM: PASS.

## Analysis restriction

The controller-gate repair used only locally retained Stage 1C evidence. No web query or page open occurred. No cohort flags were inspected or introduced into adjudication, no group count or cohort-level outcome rate was computed, and no group comparison was performed.
