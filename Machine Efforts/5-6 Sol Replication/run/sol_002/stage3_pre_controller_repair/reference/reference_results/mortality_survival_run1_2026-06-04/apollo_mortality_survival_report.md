# Apollo 7-17 Mortality, Survival, and Late-Life Vitality Analysis

Analysis date: 2026-06-04

## Methods

- Apollo 7-17 = all rows in `07E-lunar-enriched.tsv` plus `08E-non-lunar-apollo-enriched.tsv`.
- Other same-era astronauts = core NASA non-Apollo rows plus the deduplicated X-15/high-speed, X-20 Dyna-Soar, and MOL military comparison rows.
- Astronaut-vs-general SMR and Monte Carlo calculations include accidental deaths, matching the all-cause SSA life table.
- Apollo-vs-other direct comparisons use a separate `Other Apollo-available` cohort that removes non-Apollo pre-1970 accidental deaths.
- The exclusion is operationalized from available fields as `Accidental Death=Y` and death date before 1970; the list is shown so narrower training-only exclusions can be audited.
- General-population baseline = local `ssa-1930-male-cohort-lifetable.tsv`, described by its metadata as SSA Actuarial Study 116, Table 7, year of birth 1930, male cohort.
- Baseline is conditional on survival to age 30. It is not a health-screened astronaut-candidate table.
- Monte Carlo uses 200,000 iterations with seed 15170505.
- Mental vitality is proxied only by the dataset's `Space Grandpa` field. SSA contains mortality only, so no general-population vitality rate is inferred.

## SSA 1930 Male Baseline Conditional on Age 30

- Mean death age from age 30: 74.28
- Median death age from age 30: 76.80
- Survival from age 30 to 80: 41.2%
- Survival from age 30 to 90: 12.5%
- Survival from age 30 to 95: 4.0%

## Cohort Summary

| Cohort | N | Deaths | Living/censored | Accidental deaths | Pre-1970 accidents | Mean age | Median age | Reached 80 % | Reached 90 % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Apollo 7-17 | 29 | 23 | 6 | 2 | 0 | 83.1 | 88.1 | 75.9 | 44.8 |
| Other astronauts including military, all deaths | 69 | 56 | 13 | 19 | 14 | 72.4 | 80.5 | 52.2 | 17.4 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 42 | 13 | 5 | 0 | 81.2 | 84.6 | 65.5 | 21.8 |
| All same-era astronauts including Apollo and military | 98 | 79 | 19 | 21 | 14 | 75.5 | 84.1 | 59.2 | 25.5 |

## Pre-1970 Accidental Death Exclusions for Apollo-vs-Other

| Name | Source | Death date | Age | Cause note |
| --- | --- | --- | --- | --- |
| Charles Arthur Bassett II | Core NASA non-Apollo | 1966-02-28 | 34.2 | T-38 aircraft crash during approach to McDonnell Aircraft facility in St. Louis |
| Roger Bruce Chaffee | Core NASA non-Apollo | 1967-01-27 | 31.9 | Asphyxia from toxic gases during Apollo 1 cabin fire |
| Theodore Cordy Freeman | Core NASA non-Apollo | 1964-10-31 | 34.7 | T-38A Talon crash caused by bird strike (goose) during approach to Ellington AFB |
| Edward Galen Givens Jr. | Core NASA non-Apollo | 1967-06-06 | 37.4 | Automobile accident near the Manned Spacecraft Center in Houston |
| Virgil Ivan "Gus" Grissom | Core NASA non-Apollo | 1967-01-27 | 40.8 | Asphyxiation in Apollo 1 cabin fire during pre-launch test |
| Elliot McKay See Jr. | Core NASA non-Apollo | 1966-02-28 | 38.6 | T-38 jet aircraft crash at McDonnell Aircraft facility in St. Louis |
| Edward Higgins White II | Core NASA non-Apollo | 1967-01-27 | 36.2 | Asphyxiation, smoke inhalation, and thermal burns during Apollo 1 cabin fire |
| Clifton Curtis Williams Jr. | Core NASA non-Apollo | 1967-10-05 | 35.0 | T-38 crash near Tallahassee, Florida due to mechanical aileron failure |
| Michael James Adams | X-15/high-speed pilots | 1967-11-15 | 37.5 | X-15-3 structural failure during reentry; aircraft broke apart at ~65,000 ft after hypersonic spin |
| Joseph Albert Walker | X-15/high-speed pilots | 1966-06-08 | 45.3 | Mid-air collision; F-104N Starfighter struck XB-70 Valkyrie during formation flight near Barstow, CA |
| Iven Carl Kincheloe Jr. | X-15/high-speed pilots | 1958-07-26 | 30.1 | F-104A crash at Edwards AFB; downward ejection seat at low altitude |
| William Barton Bridgeman | X-15/high-speed pilots | 1968-09-29 | 52.3 | Grumman Goose amphibian crash near Catalina Island; body never recovered |
| Russell Lee Rogers | X-20 Dyna-Soar pilots | 1967-09-13 | 39.4 | F-105 engine failure; ejected but parachute failed to deploy; Kadena AFB, Okinawa |
| Robert Henry Lawrence Jr. | MOL military astronauts | 1967-12-08 | 32.2 | F-104 Starfighter crash during flight test training at Edwards AFB; aircraft flared too late, landing gear failure, ejection seat fired sideways, parachute failed to deploy |

## Standardized Mortality Ratio

| Cohort | N | Observed deaths | Expected deaths | SMR | 95% low | 95% high |
| --- | --- | --- | --- | --- | --- | --- |
| Apollo 7-17 | 29 | 23 | 50.31 | 0.46 | 0.30 | 0.69 |
| Other astronauts including military, all deaths | 69 | 56 | 77.03 | 0.73 | 0.56 | 0.94 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 42 | 76.72 | 0.55 | 0.40 | 0.74 |
| All same-era astronauts including Apollo and military | 98 | 79 | 127.34 | 0.62 | 0.50 | 0.77 |

Interpretation: SMR below 1.0 means fewer deaths than expected from summed age-specific all-cause hazard under the SSA 1930 male table after conditioning on survival to age 30.

## Monte Carlo Against SSA 1930 Male Age-30 Baseline

| Cohort | N | Observed deaths | Sim mean deaths | Deaths p2.5 | Deaths p97.5 | P(sim deaths >= obs) | Obs mean age | Sim mean age | P(sim mean >= obs) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Apollo 7-17 | 29 | 23 | 20.36 | 17 | 24 | 0.1247 | 83.12 | 70.09 | 0.0000 |
| Other astronauts including military, all deaths | 69 | 56 | 35.86 | 30 | 42 | 0.0000 | 72.36 | 63.38 | 0.0000 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 42 | 35.55 | 30 | 41 | 0.0211 | 81.22 | 69.99 | 0.0000 |
| All same-era astronauts including Apollo and military | 98 | 79 | 56.21 | 49 | 63 | 0.0000 | 75.54 | 65.38 | 0.0000 |

## Retention of Public Mental Vitality Proxy

| Cohort | N | Reached 80 | SG=Y among 80+ | SG=Y among 80+ % | SG=Y all | SG=Y all % |
| --- | --- | --- | --- | --- | --- | --- |
| Apollo 7-17 | 29 | 22 | 21 | 95.5 | 21 | 72.4 |
| Other astronauts including military, all deaths | 69 | 36 | 24 | 66.7 | 24 | 34.8 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 36 | 24 | 66.7 | 24 | 43.6 |
| All same-era astronauts including Apollo and military | 98 | 58 | 45 | 77.6 | 45 | 45.9 |

Caution: this is a public-evidence proxy for high late-life activity, not a clinical cognition measure.

### Vitality Proxy Direct Comparison

| Comparison | Apollo SG=Y | Apollo 80+ denom | Other SG=Y | Other 80+ denom | Risk diff pct pts | Fisher p |
| --- | --- | --- | --- | --- | --- | --- |
| Apollo vs other Apollo-available, SG among 80+ | 21 | 22 | 24 | 36 | 28.8 | 0.0111 |
| Apollo vs other all, SG among 80+ | 21 | 22 | 24 | 36 | 28.8 | 0.0111 |

## Direct Apollo-vs-Other Survival Tests

| Comparison | Apollo deaths | Other deaths | Apollo test events | Apollo expected events | Log-rank z | Chi-square | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Apollo vs other Apollo-available excl. pre-1970 accidents | 23 | 42 | 22.0 | 26.0 | -1.04 | 1.08 | 0.2989 |
| Apollo vs other all deaths included | 23 | 56 | 22.0 | 30.5 | -1.99 | 3.96 | 0.0465 |

## Generated Files

- `cohort_summary.csv`
- `smr_summary.csv`
- `monte_carlo_summary.csv`
- `monte_carlo_death_count_distribution.csv`
- `mental_vitality_summary.csv`
- `kaplan_meier_points.csv`
- `person_level_analysis.csv`
- `pre1970_accident_exclusions.csv`
- `km_astronauts_vs_ssa.svg`
- `km_apollo_vs_other_available.svg`
- `smr_summary.svg`
- `mental_vitality_sg80.svg`
- `monte_carlo_deaths_apollo.svg`
- `monte_carlo_deaths_other_all.svg`
