# User-Requested Run-Level Distributions

Iterations per mortality scenario: 1,000,000
Runtime: 62.0 seconds

## Censoring Choice

The simulated cohorts draw full lifetimes from the SSA 1930 male life table under each hazard-scale scenario. I did not impose a plotting cap such as age 100. The observed Apollo reference ages are shown as right-censored lower-bound markers where living Apollo astronauts are part of the relevant rank set.

The SSA table itself ends when its survivor count reaches zero, so this is uncapped within the available life table rather than projected beyond the table.

## Age Statistics

- `age_22nd_longest_lived`: age of the 22nd-longest-lived person in a simulated 29-person group. This is the age through which the group still has 22 survivors.
- `age_13th_longest_lived`: age of the 13th-longest-lived person in a simulated 29-person group. This is the age through which the group still has 13 survivors.

| Observed marker | Age/count | Rank person | Censored? | Living in rank set |
| --- | --- | --- | --- | --- |
| age_22nd_longest_lived | 82.06 | Neil Armstrong | True | 6 |
| age_13th_longest_lived | 90.49 | Michael Collins | True | 6 |
| mental_vitality_count |  |  | False |  |

| Scenario | Age22 p2.5 | Age22 p50 | Age22 p97.5 | Age13 p2.5 | Age13 p50 | Age13 p97.5 |
| --- | --- | --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | 56 | 65 | 74 | 72 | 79 | 84 |
| Modestly healthy, 15 pct lower hazard | 57 | 67 | 76 | 74 | 81 | 86 |
| Healthy, 30 pct lower hazard | 60 | 70 | 78 | 77 | 83 | 88 |
| Very healthy, 45 pct lower hazard | 63 | 73 | 81 | 80 | 86 | 91 |
| Apollo-SMR-like hazard scale | 65 | 76 | 84 | 82 | 88 | 93 |

## Vitality Count Distributions

| Scenario | Rate % | Mean count | p2.5 | p50 | p97.5 | P(count >= 21) |
| --- | --- | --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | 16.17 | 1.93 | 0 | 2 | 5 | 0.00000000 |
| SSA general male, age-30 selected | 68.00 | 8.13 | 4 | 8 | 13 | 0.00000100 |
| Modestly healthy, 15 pct lower hazard | 16.17 | 2.21 | 0 | 2 | 5 | 0.00000000 |
| Modestly healthy, 15 pct lower hazard | 68.00 | 9.28 | 5 | 9 | 14 | 0.00000500 |
| Healthy, 30 pct lower hazard | 16.17 | 2.52 | 0 | 2 | 6 | 0.00000000 |
| Healthy, 30 pct lower hazard | 68.00 | 10.61 | 6 | 11 | 16 | 0.00009600 |
| Very healthy, 45 pct lower hazard | 16.17 | 2.88 | 0 | 3 | 6 | 0.00000000 |
| Very healthy, 45 pct lower hazard | 68.00 | 12.11 | 7 | 12 | 17 | 0.00087800 |
| Apollo-SMR-like hazard scale | 16.17 | 3.13 | 0 | 3 | 7 | 0.00000000 |
| Apollo-SMR-like hazard scale | 68.00 | 13.15 | 8 | 13 | 18 | 0.00304900 |

## Graphs

- `age_22nd_longest_lived_distribution.svg`
- `age_13th_longest_lived_distribution.svg`
- `mental_vitality_count_distribution.svg`
