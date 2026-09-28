# Apollo Aging Anomaly: Methods, Findings, And Conclusion Trail

Generated: 2026-06-06

This dossier documents the Apollo 7-17 mortality, longevity, and late-life mental-vitality analysis performed in this workspace. It is meant to answer two questions:

1. What did the runs conclude?
2. How did the analysis get to those conclusions?

It also records which pieces are directly reproduced from the local data, which are sensitivity assumptions, and which are still provisional because the underlying microdata were not reproduced here.

## Bottom Line

The Apollo 7-17 group is unusually long-lived relative to the SSA 1930 U.S. male cohort conditional on reaching age 30. Apollo also has a very high observed public late-life activity proxy, `Space Grandpa`: 21 of 29 overall, and 21 of the 22 Apollo astronauts who reached age 80.

The rigorous probability question depends on what "healthy U.S. males selected at age 30" means. In this workflow, health selection is represented by post-age-30 hazard reduction against the SSA 1930 male life table.

For longevity alone, Apollo-like survival is rare under the general SSA baseline and much less rare under very strong health selection:

| Scenario | Hazard scale | P(N80 >= 22 and N90 >= 13) | Approx odds |
| --- | ---: | ---: | ---: |
| SSA general male, age-30 selected | 1.000 | 9.033e-07 | 1 in 1.1 million |
| Healthy, 30 pct lower hazard | 0.700 | 0.001496 | 1 in 669 |
| Very healthy, 45 pct lower hazard | 0.550 | 0.028877 | 1 in 35 |
| Apollo-SMR-like hazard scale | 0.457 | 0.123580 | 1 in 8 |

For longevity plus mental vitality, the result becomes much rarer because the Apollo target is not merely "many people live long"; it is "many people live long and at least 21 retain a high late-life vitality proxy."

Using the simple 80+ vitality grid requested later in the project:

| Scenario | Vitality rate | P(N80 >= 22, N90 >= 13, vitality >= 21) | Approx odds |
| --- | ---: | ---: | ---: |
| Healthy, 30 pct lower hazard | 16.17% | 2.872e-17 | 1 in 34.8 quadrillion |
| Healthy, 30 pct lower hazard | 68.00% | 1.521e-05 | 1 in 65,733 |
| Very healthy, 45 pct lower hazard | 16.17% | 1.026e-15 | 1 in 975 trillion |
| Very healthy, 45 pct lower hazard | 68.00% | 0.000390 | 1 in 2,562 |
| Apollo-SMR-like hazard scale | 16.17% | 7.324e-15 | 1 in 136.5 trillion |
| Apollo-SMR-like hazard scale | 68.00% | 0.002131 | 1 in 469 |

The Apollo-SMR-like row is not the clean answer for random healthy men. It is a backward-calibrated sensitivity scenario using the Apollo mortality advantage itself. It shows what happens if the comparison group is granted a mortality advantage similar to Apollo's observed SMR.

## What Was Compared

The analysis now uses local archived copies under:

`data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/`

Those archived files were copied from the original upstream processed-data folder:

`./Machine Efforts/Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data`

The cohort files used by the scripts were:

- `Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv`
- `Final - Analysis - Enriched Datasets/07E-lunar-enriched.tsv`
- `Final - Analysis - Enriched Datasets/08E-non-lunar-apollo-enriched.tsv`
- `Final - Analysis - Enriched Datasets/09-x15-pilots-enriched.tsv`
- `Final - Analysis - Enriched Datasets/10-dyna-soar-pilots-enriched.tsv`
- `Final - Analysis - Enriched Datasets/11-mol-full-enriched.tsv`

The general-population baseline was:

- `data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/data/ssa-1930-male-cohort-lifetable.tsv`

The main groups were:

| Group | N | Meaning |
| --- | ---: | --- |
| Apollo 7-17 | 29 | Astronauts who participated in Apollo 7 through Apollo 17. |
| Other same-era astronauts including military | 69 | NASA non-Apollo astronauts plus X-15/high-speed, Dyna-Soar, and MOL military comparison groups. |
| Other Apollo-available | 55 | The non-Apollo comparator after removing pre-1970 accidental deaths for the Apollo-vs-other availability comparison. |
| All same-era astronauts | 98 | Apollo plus all non-Apollo same-era/military comparison people. |

## Accident Handling

The accident rule is comparison-specific.

For astronaut-vs-general-population comparisons, accidental deaths were included because the SSA all-cause life table includes accidental deaths.

For Apollo-vs-other-astronaut comparisons, the analysis also created an `Other Apollo-available` comparator by removing non-Apollo accidental deaths before 1970. This follows the user's reasoning that those pre-1970 training or operational accidents effectively removed those people from the pool of astronauts who could have been available for later Apollo participation.

The exclusion rule used the available fields:

`Accidental Death = Y` and death date before 1970.

Those exclusions are listed in:

- `analysis_outputs/mortality_survival_run1_2026-06-04/pre1970_accident_exclusions.csv`

## Run 1: Mortality, SMR, Kaplan-Meier, And Astronaut Comparisons

Run1 is the broader astronaut-vs-astronaut and astronaut-vs-SSA analysis.

Script:

- `scripts/apollo_mortality_survival_analysis.py`

Main report:

- `analysis_outputs/mortality_survival_run1_2026-06-04/apollo_mortality_survival_report.md`

Key outputs:

- `analysis_outputs/mortality_survival_run1_2026-06-04/smr_summary.csv`
- `analysis_outputs/mortality_survival_run1_2026-06-04/kaplan_meier_points.csv`
- `analysis_outputs/mortality_survival_run1_2026-06-04/km_astronauts_vs_ssa.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/km_apollo_vs_other_available.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/mental_vitality_summary.csv`
- `analysis_outputs/mortality_survival_run1_2026-06-04/person_level_analysis.csv`

### SMR Method

The standardized mortality ratio was computed as:

`SMR = observed deaths / expected deaths`

Expected deaths were calculated from summed age-specific all-cause hazard exposure in the SSA 1930 male cohort life table, conditional on survival to age 30.

This is important: the expected-death denominator is not a simple sum of cumulative death probabilities. It is based on the life-table hazard contribution over each subject's observed risk window from age 30 to death or censoring.

SMR below 1.0 means the group had fewer deaths than expected under the SSA 1930 male age-30 baseline.

Run1 SMR results:

| Cohort | N | Observed deaths | Expected deaths | SMR | 95% low | 95% high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Apollo 7-17 | 29 | 23 | 50.31 | 0.46 | 0.30 | 0.69 |
| Other astronauts including military, all deaths | 69 | 56 | 77.03 | 0.73 | 0.56 | 0.94 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 42 | 76.72 | 0.55 | 0.40 | 0.74 |
| All same-era astronauts including Apollo and military | 98 | 79 | 127.34 | 0.62 | 0.50 | 0.77 |

### Kaplan-Meier Method

Kaplan-Meier curves used each astronaut's endpoint age:

- death age for deceased astronauts;
- current age at the analysis date for living astronauts, treated as censored.

The graphs compare astronaut survival curves against each other and against the SSA baseline conditional on survival to age 30.

Important caveat: for living Apollo astronauts, the observed endpoint is a lower bound. They have not "ended" their survival interval.

### Mental-Vitality Proxy In Run1

Run1 used only the dataset field `Space Grandpa` as the astronaut-side vitality proxy.

This field means publicly documented late-life activity at age 80+, not a clinical cognitive diagnosis.

Run1 observed:

| Cohort | N | Reached 80 | SG=Y among 80+ | SG=Y among 80+ % | SG=Y all | SG=Y all % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Apollo 7-17 | 29 | 22 | 21 | 95.5 | 21 | 72.4 |
| Other astronauts including military, all deaths | 69 | 36 | 24 | 66.7 | 24 | 34.8 |
| Other Apollo-available, excl. pre-1970 accidents | 55 | 36 | 24 | 66.7 | 24 | 43.6 |
| All same-era astronauts including Apollo and military | 98 | 58 | 45 | 77.6 | 45 | 45.9 |

The direct Apollo-vs-other comparison among 80+ astronauts had Fisher p = 0.0111, but this is a comparison of a public-evidence proxy, not clinical cognition.

## Mental Vitality: What Can And Cannot Be Inferred

The research memo is:

- `mental_vitality_medical_data_findings.md`

The source archive is:

- `source_research/mental_vitality_medical_data_2026-06-04/references/`
- `source_research/mental_vitality_medical_data_2026-06-04/source_log.csv`
- `source_research/mental_vitality_medical_data_2026-06-04/source_manifest_sha256.txt`

The conclusion was:

1. SSA can support mortality and survival only. It cannot infer mental vitality.
2. Medical and survey data can support a population-level cognitive or functional vitality proxy.
3. That proxy is related to, but not identical with, `Space Grandpa`.

The cleanest possible population endpoints would be:

- clinical cognitive vitality: normal cognition, no MCI, no dementia;
- functional cognitive vitality: normal cognition plus no ADL/IADL dependency or cognitive-functional proxy impairment;
- participatory vitality: functional vitality plus ordinary participation indicators such as working, volunteering, social activity, driving, leaving home, or technology/finance use.

HRS-HCAP and NHATS are the strongest candidate data sources for those endpoints. Medicare claims alone are not adequate for proving vitality because claims are better at identifying diagnosed dementia than at proving normal cognition or preserved function.

## Source Anchors For The Vitality Sensitivity Range

The user asked for a simple 80+ rate rather than age-bucket precision. That was the right methodological move because the available sources do not support clean rates for 80-84, 85-89, 90-94, 95-99, 100-104, and 105-110 in the same construct.

The final simple grid used four blanket 80+ rates:

| Rate | Label | Status |
| ---: | --- | --- |
| 16.17% | MHAS 54/334 youthful-cognition lower anchor | User-supplied or derived lower anchor; not reproduced from MHAS microdata here. |
| 33.45% | Interior point | Sensitivity value evenly spaced between lower and upper anchors. |
| 50.72% | Interior point | Sensitivity value evenly spaced between lower and upper anchors. |
| 68.00% | HRS-HCAP broad normal-cognition upper anchor | HRS-HCAP 65+ dementia 10% and MCI 22%, so broad normal cognition about 68%; optimistic for 80+. |

The MHAS 54/334 figure must be labeled carefully. The local MHAS documentation verifies the MHAS cohort and cognitive-status machinery, including categories like Normal, Normal with Instrumental Impairment, CIND, and Dementia. But this workspace did not reproduce the exact `54 / 334` numerator and denominator from MHAS microdata. Therefore the number is useful as a strict sensitivity anchor, not as a fully reproduced published statistic.

The HRS-HCAP 68% figure is also not a perfect 80+ rate. It is a broad U.S. adult 65+ normal-cognition anchor. Because cognitive impairment rises with age, 68% is probably optimistic for an 80+ denominator.

Cao et al. 2024 / PMC11336039 was usable for dementia-free context, but not for mental vitality. It provides age-banded dementia prevalence and mortality forecasts for U.S. oldest-old adults, including 80-84, 85-89, 90-94, and 95+. From that, dementia-free rates can be computed. But dementia-free is too permissive because it does not exclude MCI, functional dependence, or lack of participation.

The extracted Cao/GBD supplement tables are:

- `source_research/mental_vitality_medical_data_2026-06-04/extracted/pmc11336039_cao2024_supplement_forecast_tables.csv`
- `source_research/mental_vitality_medical_data_2026-06-04/extracted/pmc11336039_cao2024_supplement_decomposition_tables.csv`

## Run 2: Group-Of-29 Probability Model

Run2 asks a narrower question:

If we draw a group of 29 U.S. males from the 1930 birth cohort who are alive at age 30, how often do they show Apollo-like longevity and vitality?

Script:

- `scripts/apollo_mortality_survival_analysis_run2.py`

Main report:

- `analysis_outputs/group29_sensitivity_run2_2026-06-04/run2_group29_report.md`

### Observed Apollo Targets

The target values were:

| Target | Apollo observed value |
| --- | ---: |
| Group size | 29 |
| Reached age 80 | 22 |
| Reached age 90 | 13 |
| Reached age 95 | 3 |
| Space Grandpa count overall | 21 |
| Space Grandpa among age-80 survivors | 21 / 22 = 95.5% |

The combined Apollo-like event used in the later vitality grid was:

`N80 >= 22, N90 >= 13, and vitality count >= 21`

### Health Selection Model

The SSA 1930 male life table is not health-screened. To approximate different degrees of healthy selection, Run2 scaled cumulative post-age-30 hazard with:

`S_adjusted(age) = S_SSA(age) ** h`

where:

- `h = 1.000` is the unmodified SSA general male age-30 baseline;
- lower `h` means reduced hazard and better survival;
- `h = 0.700` represents 30% lower post-age-30 hazard;
- `h = 0.550` represents 45% lower post-age-30 hazard;
- `h = 0.457` is the Apollo-SMR-like sensitivity, calibrated to Apollo's observed SMR.

These are sensitivity points, not a claim that the SSA contains a ready-made "healthy astronaut-like men" table.

## Final MHAS16 80+ Vitality Grid

Script:

- `scripts/apollo_mortality_survival_analysis_run2_mhas16_vitality_grid.py`

Output directory:

- `analysis_outputs/group29_sensitivity_run2_2026-06-04/simple_80plus_mhas16_vitality_grid/`

Key outputs:

- `mhas16_rate_grid_report.md`
- `mhas16_rate_grid_summary.csv`
- `mhas16_rate_grid_assumptions.csv`
- `mhas16_age_bucket_context.csv`
- `mhas16_probability_heatmap.svg`
- `mhas16_expected_vital_count.svg`

This run used exact probabilities for the rare-tail event. That matters because Monte Carlo alone can miss very small probabilities.

### How The Probability Conclusion Follows

The conclusion comes from multiplying two linked ideas:

1. How often does a 29-person group have at least 22 people reach 80 and at least 13 reach 90 under the chosen mortality scenario?
2. Among people who reach 80, how often do at least 21 total people in the group retain the vitality proxy under the chosen 80+ vitality rate?

The survival component is generated from the SSA 1930 male life table, conditional on age 30, after optional hazard scaling.

The vitality component is conditional on reaching age 80: each age-80 survivor has an independent probability `p` of meeting the mental-vitality proxy. The four `p` values are the 16.17%, 33.45%, 50.72%, and 68.00% sensitivity rates.

That is why the same mortality scenario can produce very different combined probabilities depending on the mental-vitality assumption.

For a "healthy" group with 30% lower hazard:

| Vitality rate | P(long+vital) | Approx odds |
| ---: | ---: | ---: |
| 16.17% | 2.872e-17 | 1 in 34.8 quadrillion |
| 33.45% | 4.903e-11 | 1 in 20.4 billion |
| 50.72% | 1.089e-07 | 1 in 9.2 million |
| 68.00% | 1.521e-05 | 1 in 65,733 |

For a "very healthy" group with 45% lower hazard:

| Vitality rate | P(long+vital) | Approx odds |
| ---: | ---: | ---: |
| 16.17% | 1.026e-15 | 1 in 975 trillion |
| 33.45% | 1.605e-09 | 1 in 623 million |
| 50.72% | 3.199e-06 | 1 in 312,602 |
| 68.00% | 0.000390 | 1 in 2,562 |

For the Apollo-SMR-like sensitivity:

| Vitality rate | P(long+vital) | Approx odds |
| ---: | ---: | ---: |
| 16.17% | 7.324e-15 | 1 in 136.5 trillion |
| 33.45% | 1.070e-08 | 1 in 93.5 million |
| 50.72% | 1.954e-05 | 1 in 51,165 |
| 68.00% | 0.002131 | 1 in 469 |

Therefore:

- If the question is longevity only, Apollo-like longevity is rare under the general population, but can become plausible under very strong health selection.
- If the question is longevity plus 21 people retaining a high late-life vitality proxy, Apollo-like outcomes remain rare even under strong health selection unless the population vitality rate is set very high.
- If the model is granted Apollo-like mortality advantage in advance, the result is less rare, but that scenario is partly circular and should be labeled as a sensitivity check rather than a neutral prior.

## User-Requested Run-Level Distributions

The later graphing request asked to show where the runs themselves fell:

- y-axis = number of simulated 29-person groups;
- x-axis = age statistic, for longevity plots;
- x-axis = number of people with mental vitality, for vitality plots.

Script:

- `scripts/apollo_mortality_survival_analysis_run2_user_requested_distributions.py`

Output directory:

- `analysis_outputs/group29_sensitivity_run2_2026-06-04/user_requested_run_distributions_censored/`

Key outputs:

- `age_22nd_longest_lived_distribution.svg`
- `age_13th_longest_lived_distribution.svg`
- `mental_vitality_count_distribution.svg`
- `run_distribution_summary.csv`
- `observed_apollo_censored_markers.csv`
- `user_requested_run_distribution_report.md`

The age statistics are order statistics:

- `age_22nd_longest_lived`: the age of the 22nd-longest-lived person in the simulated 29-person group. This corresponds to the age through which the group still has 22 survivors.
- `age_13th_longest_lived`: the age of the 13th-longest-lived person in the simulated 29-person group. This corresponds to the age through which the group still has 13 survivors.

The observed Apollo markers were treated as censored lower bounds because several Apollo astronauts were still living at the analysis date. The simulation did not impose an arbitrary upper age cap. It sampled within the SSA life-table support.

Observed Apollo markers:

| Marker | Value | Interpretation |
| --- | ---: | --- |
| 22nd-longest-lived age | >= 82.06 | Lower-bound marker; living Apollo astronauts affect the rank set. |
| 13th-longest-lived age | >= 90.49 | Lower-bound marker; living Apollo astronauts affect the rank set. |
| Mental vitality count | 21 | Observed Space Grandpa count. |

Distribution highlights:

| Scenario | Age22 p50 | Age13 p50 |
| --- | ---: | ---: |
| SSA general male, age-30 selected | 65 | 79 |
| Modestly healthy, 15 pct lower hazard | 67 | 81 |
| Healthy, 30 pct lower hazard | 70 | 83 |
| Very healthy, 45 pct lower hazard | 73 | 86 |
| Apollo-SMR-like hazard scale | 76 | 88 |

At the upper 68% vitality rate, the simulated probability that vitality count alone reaches at least 21 was:

| Scenario | P(vitality count >= 21) |
| --- | ---: |
| SSA general male, age-30 selected | 0.000001 |
| Modestly healthy, 15 pct lower hazard | 0.000005 |
| Healthy, 30 pct lower hazard | 0.000096 |
| Very healthy, 45 pct lower hazard | 0.000878 |
| Apollo-SMR-like hazard scale | 0.003049 |

## Graph Inventory

Run1 graphs:

- `analysis_outputs/mortality_survival_run1_2026-06-04/km_astronauts_vs_ssa.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/km_apollo_vs_other_available.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/smr_summary.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/mental_vitality_sg80.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/monte_carlo_deaths_apollo.svg`
- `analysis_outputs/mortality_survival_run1_2026-06-04/monte_carlo_deaths_other_all.svg`

Run2 simple-grid graphs:

- `analysis_outputs/group29_sensitivity_run2_2026-06-04/simple_80plus_mhas16_vitality_grid/mhas16_probability_heatmap.svg`
- `analysis_outputs/group29_sensitivity_run2_2026-06-04/simple_80plus_mhas16_vitality_grid/mhas16_expected_vital_count.svg`

User-requested distribution graphs:

- `analysis_outputs/group29_sensitivity_run2_2026-06-04/user_requested_run_distributions_censored/age_22nd_longest_lived_distribution.svg`
- `analysis_outputs/group29_sensitivity_run2_2026-06-04/user_requested_run_distributions_censored/age_13th_longest_lived_distribution.svg`
- `analysis_outputs/group29_sensitivity_run2_2026-06-04/user_requested_run_distributions_censored/mental_vitality_count_distribution.svg`

## Reproduction Commands

From this workspace root:

```bash
python3 "scripts/apollo_mortality_survival_analysis.py"
python3 "scripts/extract_cao2024_supplement_tables.py" source_research/mental_vitality_medical_data_2026-06-04/references/springer_11357_2024_1180_MOESM1_ESM.txt source_research/mental_vitality_medical_data_2026-06-04/extracted
python3 "scripts/apollo_mortality_survival_analysis_run2.py"
python3 "scripts/apollo_mortality_survival_analysis_run2_simple_vitality_grid.py"
python3 "scripts/apollo_mortality_survival_analysis_run2_mhas16_vitality_grid.py"
python3 "scripts/apollo_mortality_survival_analysis_run2_user_requested_distributions.py"
```

Notes:

- The later scripts write separate output directories and preserve older runs.
- The plotting scripts use pure Python/SVG output because the local NumPy/matplotlib stack was not reliable in this workspace.
- The run-level distribution script uses 1,000,000 iterations per mortality scenario.

## What Is Verified Versus Provisional

Directly reproduced in this workspace:

- Apollo and comparator cohort counts from the processed TSVs.
- Accident-handling rules and pre-1970 exclusion list.
- SSA age-30 conditional survival baseline from the local SSA life table.
- SMR, Kaplan-Meier points, Monte Carlo summaries, and SVG graphs.
- Cao/GBD supplement tables extracted into local CSVs.
- HRS-HCAP broad 65+ dementia/MCI anchor from archived source material.
- MHAS documentation showing cognitive-status machinery.

Provisional or sensitivity-only:

- The MHAS `54 / 334 = 16.17%` lower anchor. It is labeled user-supplied/MHAS-derived because the exact numerator and denominator were not reproduced from MHAS microdata here.
- The 33.45% and 50.72% interior points. These are sensitivity values, not source claims.
- The 68% HRS-HCAP upper anchor as an 80+ rate. It is a broad 65+ normal-cognition anchor and likely optimistic for age 80+.
- `Space Grandpa` as a mental-vitality construct. It is a public-activity proxy, not clinical cognition.
- Apollo-SMR-like hazard scaling as a random-healthy comparison. It is useful for sensitivity but partly backward-calibrated to Apollo's observed mortality.

## Next Steps For More Rigor

The strongest next improvement would be a person-level HRS-HCAP or NHATS extraction:

1. Obtain HRS-HCAP/NHATS data through proper access channels.
2. Define an age-80+ denominator and apply survey weights.
3. Estimate U.S. male age-specific rates for normal cognition, functional cognitive vitality, and participatory vitality.
4. Run the same 29-person simulation using those weighted rates instead of broad sensitivity anchors.
5. If using MHAS as a strict lower-bound comparator, reproduce the exact `54 / 334` analytic subset from MHAS microdata and document the variable logic.

Until then, the most honest conclusion is a bounded one: Apollo's longevity is unusual, and Apollo's public late-life vitality rate is extraordinarily high, but the exact population rarity of the combined outcome depends strongly on the chosen mental-vitality denominator.
