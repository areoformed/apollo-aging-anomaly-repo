# Simple 80+ Mental-Vitality Rate Grid

## Simplification

This run treats mental vitality as one blanket 80+ probability, rather than applying age-bucket rates. That avoids false precision: the archived sources do not support reliable 80-84, 85-89, 90-94, 95-99, 100-104, and 105-110 mental-vitality rates.

## Source Context

Cao/GBD gives dementia-free rates by age band. These are upper-bound context only, because a person can be dementia-free and still have MCI, functional limitation, or low public/participatory vitality.

| Requested bucket | Source bucket | Dementia-free % | Low 95 % | High 95 % | Note |
| --- | --- | --- | --- | --- | --- |
| 80-84 | 80-84 years | 86.6 | 86.0 | 87.2 | Source age band exists. |
| 85-89 | 85-89 years | 79.1 | 78.3 | 79.9 | Source age band exists. |
| 90-94 | 90-94 years | 69.7 | 68.5 | 70.8 | Source age band exists. |
| 95-99 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |
| 100-104 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |
| 105-110 | 95+ years | 50.7 | 48.8 | 52.5 | Source aggregates 95+; not separately estimable here. |

## Simulation Rate Grid

For the simple Monte Carlo/exact mixture, I used a broad blanket 80+ grid: 35%, 46%, 57%, and 68%. The upper value is the broad HRS-HCAP normal-cognition anchor for U.S. adults 65+ (68%), which is probably optimistic for 80+. The lower value is a conservative public/participatory-vitality sensitivity, not a direct medical prevalence estimate.

| Rate key | Rate % | Basis |
| --- | --- | --- |
| lower_strict_public_participation_sensitivity | 35.0 | Deliberately conservative sensitivity for public/participatory vitality; not a direct medical prevalence estimate. |
| interior_low | 46.0 | Evenly spaced interior point between lower and upper simple bounds. |
| interior_high | 57.0 | Evenly spaced interior point between lower and upper simple bounds. |
| upper_hcap_normal_cognition_overall | 68.0 | HRS-HCAP broad normal-cognition anchor from 65+ adults: 1 - dementia 10 pct - MCI 22 pct. Optimistic for 80+. |

## Key Results

Probability shown here is exact probability of Apollo-like longevity plus vitality: N80 >= 22, N90 >= 13, and vitality count >= 21.

| Mortality scenario | Vitality % | Expected N80 | Expected vital count | P(long+vital) |
| --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | 35 | 11.96 | 4.18 | 3.350e-14 |
| SSA general male, age-30 selected | 46 | 11.96 | 5.50 | 6.006e-12 |
| SSA general male, age-30 selected | 57 | 11.96 | 6.82 | 2.974e-10 |
| SSA general male, age-30 selected | 68 | 11.96 | 8.13 | 6.205e-09 |
| Healthy, 30 pct lower hazard | 35 | 15.60 | 5.46 | 1.166e-10 |
| Healthy, 30 pct lower hazard | 46 | 15.60 | 7.17 | 1.886e-08 |
| Healthy, 30 pct lower hazard | 57 | 15.60 | 8.89 | 8.310e-07 |
| Healthy, 30 pct lower hazard | 68 | 15.60 | 10.61 | 0.00001521 |
| Apollo-SMR-like hazard scale | 35 | 19.34 | 6.77 | 2.505e-08 |
| Apollo-SMR-like hazard scale | 46 | 19.34 | 8.90 | 0.00000359 |
| Apollo-SMR-like hazard scale | 57 | 19.34 | 11.02 | 0.00013727 |
| Apollo-SMR-like hazard scale | 68 | 19.34 | 13.15 | 0.00213091 |

## Graphs

- `simple_80plus_probability_heatmap.svg`
- `simple_80plus_expected_vital_count.svg`
