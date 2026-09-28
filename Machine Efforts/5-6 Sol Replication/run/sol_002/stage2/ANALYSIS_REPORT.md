# Stage 2 analysis report

## Questions and interpretation

This report asks whether the future-defined `APOLLO_FLEW` cohort has descriptively unusual survival and publicly documented late-life functioning. The public-function endpoint is detection of qualifying public evidence, not cognitive-intactness prevalence and not a clinical diagnosis. All astronaut contrasts are descriptive and noncausal.

## Data and methods

The locked cohort contains the prespecified Apollo, NASA non-Apollo, X-15, Dyna-Soar, and MOL rosters censored on 2026-06-01. The primary survival analysis starts at the common 1973-01-01 landmark among people alive then. Its estimand is Apollo-minus-comparator Kaplan–Meier RMST through 50 years. Primary and composition intervals use 50,000 stratified person-level percentile bootstrap replicates, seed 20260721.

The age-adjusted sensitivity is a Cox model from the landmark with Apollo status and linear age at landmark, Efron ties, and conventional Wald intervals. Schoenfeld-residual tests are diagnostics, not replacements for RMST.

The secondary birth-origin curves are explicitly retrospective and future-flight-selected. `OTHER_AVAILABLE` is identical to `OTHER_ALL` after the 1973 landmark and in the age-80 risk set; it is shown only in the birth-origin description and is not duplicate sensitivity evidence.

For the official population benchmark, [SSA Actuarial Study 120 Table 11](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_11.html) supplies exact-year male cohort life expectancy at birth, while the official cohort tables for [1920](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1920.html), [1930](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1930.html), [1940](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1940.html), and [1950](https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1950.html) supply survival to age 80. Exact birth years use linear interpolation for S80. The preferred 2023 full file was inaccessible in this sandbox, so the fallback was frozen before models. SSA expectations are nonexchangeable population benchmarks.

The primary public-function analysis starts on each eligible person's 80th birthday. First qualifying function before age 85 is the event of interest, death first is competing, and administrative end or the 85th birthday is censoring. Five-year risks use Aalen–Johansen; risk-difference intervals use the same 50,000-replicate stratified bootstrap. Secondary any-age-80-plus detection reports exact binomial group intervals, Newcombe risk-difference intervals, risk ratios, conditional-exact odds-ratio intervals, and Fisher's exact test.

## Survival results

| Group | N | Deaths / censored | Death proportion (exact 95% CI) | Observed attained-age median (exact 95% CI) | IQR |
|---|---|---|---|---|---|
| APOLLO_FLEW | 29 | 23 / 6 | 79.3% (60.3, 92.0) | 88.1 (82.8, 90.8) y | 82.1–90.9 y |
| OTHER_ALL | 66 | 53 / 13 | 80.3% (68.7, 89.1) | 80.6 (71.5, 85.5) y | 67.0–88.4 y |
| CORE_NASA_NON_APOLLO | 44 | 34 / 10 | 77.3% (62.2, 88.5) | 84.4 (77.6, 87.2) y | 70.9–88.8 y |
| MILITARY_ONLY | 30 | 26 / 4 | 86.7% (69.3, 96.2) | 75.1 (68.4, 84.6) y | 65.9–85.7 y |

These attained-age values are observed ages at death or censor, not completed lifetimes for survivors. Exact intervals are Clopper–Pearson for death proportions and distribution-free order-statistic intervals for the observed attained-age median.

| Contrast | RMST Apollo | RMST comparator | Difference (95% bootstrap CI) |
|---|---|---|---|
| APOLLO_FLEW vs OTHER_ALL | 40.57 y | 39.90 y | 0.67 (-5.09, 6.10) y |
| APOLLO_FLEW vs CORE_NASA_NON_APOLLO | 40.57 y | 43.54 y | -2.97 (-8.48, 2.24) y |
| APOLLO_FLEW vs MILITARY_ONLY | 40.57 y | 35.92 y | 4.65 (-2.38, 11.59) y |

The primary Apollo-minus-`OTHER_ALL` 50-year RMST difference is **0.67 years** (95% percentile bootstrap **-5.09 to 6.10**). The fixed practical threshold is 5.0 years.

In the age-adjusted Cox sensitivity, the Apollo hazard ratio is **0.795679** (95% CI **0.474366 to 1.334634**, supplementary p=0.386427). The Apollo Schoenfeld-residual diagnostic has p=0.730762; the full term and approximate global diagnostics are retained in `ph_diagnostic.csv`.

The official male cohort benchmark predicts S80 of **37.1%** for the Apollo birth-year mix and **37.2%** for `OTHER_ALL`. Observed proportions reaching 80 were **75.9%** and **53.0%**, respectively. This large excess over general-population expectation is compatible with survival to astronaut/test-pilot selection, medical screening, and healthy-selectee effects; it is not an Apollo-flight causal effect.

The birth-origin Kaplan–Meier description and attained-age summaries are retained in `km_birth_selected_ages.csv`, `survival_group_summary.csv`, and the SVG figures. They must not be read as baseline-randomized survival because Apollo status is assigned by a future flight.

## Publicly documented late-life functioning

| Contrast | CIF Apollo | CIF comparator | Risk difference (95% bootstrap CI) |
|---|---|---|---|
| APOLLO_FLEW vs OTHER_ALL | 4.5% | 2.9% | 1.7 (-8.6, 13.6) pp |
| APOLLO_FLEW vs CORE_NASA_NON_APOLLO | 4.5% | 3.6% | 1.0 (-10.7, 13.6) pp |
| APOLLO_FLEW vs MILITARY_ONLY | 4.5% | 7.7% | -3.1 (-23.1, 13.6) pp |
| APOLLO_FLEW vs OTHER_ALL, R001 excluded | 4.8% | 2.9% | 1.9 (-8.6, 14.3) pp |

The primary Apollo-minus-`OTHER_ALL` five-year public-function detection risk difference is **1.7 percentage points** (95% percentile bootstrap **-8.6 to 13.6**). The fixed practical threshold is 10 percentage points.

For the secondary any-time endpoint, Apollo has **3/22** detections and `OTHER_ALL` has **2/35**. The crude risk difference is **7.9 pp** (95% CI **-13.9 to 31.8**), risk ratio **2.386364** (95% CI 0.432528 to 13.166147), and odds ratio **2.605263** (conditional exact 95% CI 0.268174 to 33.212813); supplementary Fisher p=0.363805.

The R001-excluded analyses are technical-deviation sensitivities only. They do not replace the primary estimates and are not independent confirmations. Documentation depth and raw source counts are described without conditioning; MEDIUM/HIGH is not treated as adjustment or complete-case correction.

Excluding R001 changes the five-year risk difference from 1.7 to **1.9 pp** and the crude any-time difference from 7.9 to **3.8 pp**.

### Source availability

| Group | LOW / MEDIUM / HIGH | Substantive sources median (IQR) | Independent publishers median (IQR) |
|---|---|---|---|
| APOLLO_FLEW | 7 / 13 / 2 | 2.00 (1.00–3.00) | 2.00 (1.00–3.00) |
| OTHER_ALL | 18 / 15 / 2 | 1.00 (0.50–2.50) | 1.00 (0.50–2.00) |
| CORE_NASA_NON_APOLLO | 14 / 12 / 2 | 1.50 (0.00–2.25) | 1.00 (0.00–2.00) |
| MILITARY_ONLY | 7 / 6 / 0 | 1.00 (1.00–2.00) | 1.00 (1.00–2.00) |

These differences describe the search record; no endpoint is conditioned on documentation depth.

### Later events, temporal sequences, and latent bounds

| Group | Detected / eligible | Latest qualifying-event age median (IQR) | Range |
|---|---|---|---|
| APOLLO_FLEW | 3 / 22 | 88.4 (85.2–89.5) y | 82.0–90.6 y |
| OTHER_ALL | 2 / 35 | 86.1 (84.8–87.4) y | 83.6–88.6 y |
| CORE_NASA_NON_APOLLO | 2 / 28 | 86.1 (84.8–87.4) y | 83.6–88.6 y |
| MILITARY_ONLY | 1 / 13 | 83.6 (83.6–83.6) y | 83.6–83.6 y |

Among Apollo-eligible people, the locked full-window states comprise 2 `FUNCTION_ONLY`, 1 `IMPAIRMENT_THEN_FUNCTION`, and 19 `NEITHER_FOUND`; among `OTHER_ALL`, they comprise 2 `FUNCTION_ONLY` and 33 `NEITHER_FOUND`. Function and impairment are therefore retained as coexisting evidence where applicable.

No qualifying event is boundary-sensitive, so earliest/latest plausible-date sensitivity is identical by construction. For the different latent-event question, asymmetrically assigning every `NEITHER_FOUND` yields an Apollo-minus-`OTHER_ALL` any-event range from **-86.4 to 94.3 pp**. These are not observed-detection estimates and do not change the primary Aalen–Johansen result.

## Endpoint classifications

- **SURVIVAL: NOT_DETECTED / HIGHER.** The primary effect is below the materiality threshold, unstable, or not coherent across prespecified sensitivities.
- **PUBLIC FUNCTION: NOT_DETECTED / HIGHER.** The primary effect is below the materiality threshold, unstable, or not coherent across prespecified sensitivities.

## Limitations

Apollo membership is future-flight classification. Birth-origin comparisons therefore contain immortal-time and selection structure, and even the 1973 landmark does not remove healthy-selectee, mission-assignment, occupational, military, socioeconomic, or survivorship differences. The nested comparator sensitivities reuse many people and are not independent replications.

The public-function endpoint measures what the fixed search budget detected in public sources. Source availability, editorial choices, seclusion, physical disability, and identity/date resolution affect detection. No evidence remains unknown rather than impairment. Function and impairment can coexist. Small groups produce wide, discrete bootstrap and exact intervals.

The SSA benchmark is sex- and birth-era-matched but not occupation-, health-, or selection-matched; AS120 combines historical mortality with projections. Observed attained age for survivors is administratively censored and is not completed lifetime.

## Plain conclusions

**Survival:** no prespecified Apollo-versus-`OTHER_ALL` anomaly was detected. Apollo's primary RMST estimate is slightly higher, but small relative to the 5-year threshold, imprecise, and directionally inconsistent across the two nested composition sensitivities. Apollo and the comparison cohorts both outlive male birth-cohort expectations, especially Apollo, but that external contrast is strongly compatible with astronaut/test-pilot screening and healthy-selectee survival.

**Public function:** no prespecified anomaly was detected. Apollo's observed five-year detection estimate is slightly higher than `OTHER_ALL`, but the 1.7-point difference is below the 10-point threshold, imprecise, and reverses against `MILITARY_ONLY`. This conclusion is about detected public evidence, never clinical cognition.

Neither question supports a causal effect of Apollo flight.
