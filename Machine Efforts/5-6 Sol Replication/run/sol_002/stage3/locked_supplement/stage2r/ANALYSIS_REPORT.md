# Corrected Stage 2R Public-Function Analysis

## Corrected question and status

Among locked cohort members who reached age 80, this analysis compares `APOLLO_FLEW` with `OTHER_ALL` on public detection of at least one locked `QUALIFYING_FUNCTION_EVENT` at any age 80 or older through death or administrative censoring on 2026-06-01. This is public-evidence detection, not a clinical measure.

This is a transparently labeled post-lock endpoint correction. It retains the locked evidence, dates, adjudication, source rules, and person-level states, but supersedes the stale age-80-to-85 primary restriction. No event is discarded merely for occurring at age 85 or older.

## Unrestricted corrected primary

| Group | Detected / eligible | Risk (95% Clopper–Pearson CI) |
|---|---:|---:|
| APOLLO_FLEW | 3 / 22 | 13.6% (2.9%, 34.9%) |
| OTHER_ALL | 2 / 35 | 5.7% (0.7%, 19.2%) |

The unrestricted Apollo-minus-Other risk difference is **7.9%** (95% Newcombe CI -7.7% to 28.0%). The group-stratified 50,000-replicate person-level bootstrap interval (seed 20260721) is -6.9% to 24.4%.

The risk ratio is 2.386 (95% score CI 0.506 to 11.250); the odds ratio is 2.605 (95% conditional exact CI 0.268 to 33.213). The two-sided Fisher exact p-value is 0.3638.

The prespecified practical threshold remains 10 absolute percentage points. Corrected `PUBLIC FUNCTION` classification: **NOT_DETECTED**, direction **HIGHER**.

## Unequal observable time

The Aalen–Johansen curves start at age 80, treat first qualifying function as the event of interest, death first as competing, and 2026-06-01 as right censoring. They retain all age-80-plus events and never censor at age 85. These are subordinate descriptions, not eligibility restrictions or primary endpoints.

| Group | Years after 80 | Cumulative incidence | Under observation | Tail support |
|---|---:|---:|---:|---|
| APOLLO_FLEW | 5 | 4.5% | 18 / 22 | ADEQUATE_SUPPORT |
| APOLLO_FLEW | 10 | 9.1% | 12 / 22 | ADEQUATE_SUPPORT |
| APOLLO_FLEW | 15 | 14.1% | 2 / 22 | TAIL_SUPPORT_WARNING |
| OTHER_ALL | 5 | 2.9% | 25 / 35 | ADEQUATE_SUPPORT |
| OTHER_ALL | 10 | 6.0% | 11 / 35 | ADEQUATE_SUPPORT |
| OTHER_ALL | 15 | 6.0% | 2 / 35 | TAIL_SUPPORT_WARNING |

A zero-support readout is marked non-estimable rather than extending a plateau beyond observed support. Low-count or low-fraction tails are explicitly warned.

Potential follow-up runs from age 80 to death or administrative end; observed follow-up runs to first detected function, death first, or administrative end. Documentation depth, substantive sources, and independent publishers are descriptive ascertainment features only and were not used to condition, weight, or exclude endpoint observations.

| Group | Potential follow-up, median [Q1, Q3] y | Observed follow-up, median [Q1, Q3] y | Function / death / admin stops | Sources, median [Q1, Q3] | Publishers, median [Q1, Q3] |
|---|---:|---:|---:|---:|---:|
| APOLLO_FLEW | 10.62 [7.37, 13.14] | 10.55 [6.55, 12.14] | 3/14/5 | 2.0 [1.0, 3.0] | 2.0 [1.0, 3.0] |
| OTHER_ALL | 8.39 [4.92, 11.81] | 8.01 [4.57, 11.27] | 2/22/11 | 1.0 [0.5, 2.5] | 1.0 [0.5, 2.0] |

Full time-step curves, risk sets, readouts, descriptive distributions, and the SVG curve figure are retained as separate artifacts.

## Later achievement and locked sequences

Among detected people, first-event ages have range 81.98–90.64, median 88.43; latest-event ages have range 81.98–90.64, median 88.43. The complete person-level latest-age distribution is retained rather than reduced to this summary.

| Group | [80,85) | [85,90) | [90,95) | 95+ |
|---|---:|---:|---:|---:|
| APOLLO_FLEW | 1 | 1 | 1 | 0 |
| OTHER_ALL | 1 | 1 | 0 | 0 |
| ALL_ELIGIBLE | 2 | 2 | 1 | 0 |

The age-band entries count detected qualifying events, not people. The person-level table retains all event dates and ages plus first/latest ages.

| Group | Locked state | People |
|---|---|---:|
| APOLLO_FLEW | FUNCTION_ONLY | 2 |
| APOLLO_FLEW | IMPAIRMENT_THEN_FUNCTION | 1 |
| APOLLO_FLEW | NEITHER_FOUND | 19 |
| OTHER_ALL | FUNCTION_ONLY | 2 |
| OTHER_ALL | NEITHER_FOUND | 33 |

`NEITHER_FOUND` is left as a searched-public-record state. No health ordering is assigned to it.

## Sensitivities

| Analysis | Apollo detected / n | Comparator detected / n | Risk difference | 95% Newcombe CI |
|---|---:|---:|---:|---:|
| Unrestricted OTHER_ALL | 3 / 22 | 2 / 35 | 7.9% | -7.7% to 28.0% |
| CORE_NASA_NON_APOLLO | 3 / 22 | 2 / 28 | 6.5% | -11.4% to 26.9% |
| MILITARY_ONLY | 3 / 22 | 1 / 13 | 5.9% | -21.2% to 26.6% |
| Exclude R001 technical deviation | 2 / 21 | 2 / 35 | 3.8% | -10.8% to 23.6% |

`OTHER_AVAILABLE` and `OTHER_ALL` full-window eligible person-ID sets were verified as **identical**, so no duplicate numerical result is reported. `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY` are both nested within `OTHER_ALL`; they overlap by 6 eligible people and are not independent.

The separately labeled `NEITHER_FOUND` latent-event extremes answer a different, unobserved-event question: the Apollo-minus-Other bound is -86.4% under the worst assignment and 94.3% under the best assignment. These are not clinical estimates and do not change the public-detection primary.

| Plausible-date scenario | Apollo detected / n | Other detected / n | Risk difference | Eligibility changes | Detection/sequence changes | Date-only changes |
|---|---:|---:|---:|---:|---:|---:|
| EARLIEST_PLAUSIBLE_DATES | 3 / 22 | 2 / 35 | 7.9% | 0 | 0 | 1 |
| LATEST_PLAUSIBLE_DATES | 3 / 22 | 2 / 35 | 7.9% | 0 | 0 | 1 |

The plausible-date sensitivity uses locked earliest/latest bounds for age-80 eligibility and event timing/order. Age 85 is not a boundary.

## Interpretation

The unrestricted sign determines direction (HIGHER). The fixed strength rule yields NOT_DETECTED: the judgment follows the absolute 10-point threshold, the primary Newcombe interval, and direction checks in both nested composition sensitivities. The result concerns public detection under the locked search and source rules, not health, clinical function, survival, or absence of unpublished activity.

No original Stage 2 result was inspected, reconstructed, or compared.
