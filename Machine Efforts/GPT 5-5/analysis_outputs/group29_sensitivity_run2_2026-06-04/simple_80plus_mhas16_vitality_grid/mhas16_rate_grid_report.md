# Simple 80+ Mental-Vitality Rate Grid: MHAS 16% Lower Anchor

## Simplification

This run applies one blanket 80+ mental-vitality probability rather than assigning age-bucket-specific probabilities. That avoids pretending the available sources can support precise rates for 80-84, 85-89, 90-94, 95-99, 100-104, and 105-110.

## Lower And Upper Bounds

Lower bound: 54/334 = 16.17%. This is treated here as an MHAS-derived/user-supplied lower anchor. The saved MHAS documentation verifies the cohort and cognitive-status machinery, but the 54/334 count has not yet been reproduced from the MHAS microdata in this workspace.

Upper bound: 68.0%, from the broad HRS-HCAP normal-cognition anchor among U.S. adults 65+ (10% dementia and 22% MCI). This remains optimistic for 80+.

## Dementia-Free Context

Cao/GBD dementia-free values remain upper-bound context only; dementia-free is looser than mental vitality.

| Requested bucket | Source bucket | Dementia-free % | Low 95 % | High 95 % | Note |
| --- | --- | --- | --- | --- | --- |
| 80-84 | 80-84 years | 86.6 | 86.0 | 87.2 | Source age band exists. |
| 85-89 | 85-89 years | 79.1 | 78.3 | 79.9 | Source age band exists. |
| 90-94 | 90-94 years | 69.7 | 68.5 | 70.8 | Source age band exists. |
| 95-99 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |
| 100-104 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |
| 105-110 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |

## Simulation Rate Grid

| Rate key | Rate % | Basis |
| --- | --- | --- |
| lower_mhas_54_of_334_youthful_cognition | 16.17 | MHAS-derived user-supplied lower anchor: 54 of 334 age-80+ individuals retained youthful cognitive function. Not recomputed from MHAS microdata in this run. |
| interior_low_between_mhas_and_hcap | 33.45 | Evenly spaced interior point between MHAS lower anchor and HRS-HCAP upper anchor. |
| interior_high_between_mhas_and_hcap | 50.72 | Evenly spaced interior point between MHAS lower anchor and HRS-HCAP upper anchor. |
| upper_hcap_normal_cognition_overall | 68.00 | HRS-HCAP broad normal-cognition anchor for U.S. adults 65+: 1 - dementia 10 pct - MCI 22 pct. Optimistic for 80+. |

## Key Results

Probability shown here is exact probability of Apollo-like longevity plus vitality: N80 >= 22, N90 >= 13, and vitality count >= 21.

This table shows a compact subset of mortality scenarios. The full grid, including modestly healthy and very healthy scenarios, is in `mhas16_rate_grid_summary.csv`.

| Mortality scenario | Vitality % | Expected N80 | Expected vital count | P(long+vital) |
| --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | 16.17 | 11.96 | 1.93 | 7.100e-21 |
| SSA general male, age-30 selected | 33.45 | 11.96 | 4.00 | 1.390e-14 |
| SSA general male, age-30 selected | 50.72 | 11.96 | 6.06 | 3.639e-11 |
| SSA general male, age-30 selected | 68.00 | 11.96 | 8.13 | 6.205e-09 |
| Healthy, 30 pct lower hazard | 16.17 | 15.60 | 2.52 | 2.872e-17 |
| Healthy, 30 pct lower hazard | 33.45 | 15.60 | 5.22 | 4.903e-11 |
| Healthy, 30 pct lower hazard | 50.72 | 15.60 | 7.91 | 1.089e-07 |
| Healthy, 30 pct lower hazard | 68.00 | 15.60 | 10.61 | 0.0000152131 |
| Apollo-SMR-like hazard scale | 16.17 | 19.34 | 3.13 | 7.324e-15 |
| Apollo-SMR-like hazard scale | 33.45 | 19.34 | 6.47 | 1.070e-08 |
| Apollo-SMR-like hazard scale | 50.72 | 19.34 | 9.81 | 0.0000195446 |
| Apollo-SMR-like hazard scale | 68.00 | 19.34 | 13.15 | 0.0021309070 |

## Graphs

- `mhas16_probability_heatmap.svg`
- `mhas16_expected_vital_count.svg`
