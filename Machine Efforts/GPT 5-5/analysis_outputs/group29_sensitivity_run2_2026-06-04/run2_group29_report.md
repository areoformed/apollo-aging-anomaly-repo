# Run 2: Group-of-29 Longevity and Mental-Vitality Sensitivity

Analysis date: 2026-06-04
Monte Carlo iterations per mortality scenario: 1,000,000
Seed base: 15170506
Runtime: 20.8 seconds

## Why This Is a Separate Run

Run1 is preserved as the astronaut-vs-astronaut and astronaut-vs-SSA analysis. This run asks a narrower probability question: if we draw 29 age-30-selected men from the 1930 male SSA cohort, under several healthier-than-average hazard assumptions and several mental-vitality proxy assumptions, how often do we see Apollo-like group outcomes?

The script writes exact probabilities alongside the Monte Carlo estimates. The exact probabilities are useful because Apollo-like outcomes can be rare under the unscreened SSA baseline, and simulation alone can under-resolve tails.

## Observed Apollo 7-17 Targets

- N: 29
- Reached age 80: 22
- Reached age 90: 13
- Reached age 95: 3 (Buzz Aldrin; Frank Borman; Jim Lovell)
- Space Grandpa count among all Apollo astronauts: 21
- Space Grandpa count among Apollo age-80 survivors: 21 / 22 = 95.5%

## Mortality Model

SSA survival is conditional on survival to age 30. Healthier-selection scenarios scale post-30 cumulative hazard by a constant factor h, equivalent to S_adjusted(age) = S_SSA(age) ** h. Lower h means better survival. These are sensitivity points, not claims that SSA has a health-screened table.

| Scenario | h | P80 | Exp N80 | P(N80 >= 22) | P(N80 >= 22,N90 >= 13) | P(+N95 >= obs) |
| --- | --- | --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | 1.000 | 0.412 | 11.96 | 0.000163 | 9.033e-07 | 7.632e-07 |
| Modestly healthy, 15 pct lower hazard | 0.850 | 0.471 | 13.66 | 0.001551 | 0.000045 | 0.000042 |
| Healthy, 30 pct lower hazard | 0.700 | 0.538 | 15.60 | 0.012392 | 0.001496 | 0.001463 |
| Very healthy, 45 pct lower hazard | 0.550 | 0.614 | 17.81 | 0.076925 | 0.028877 | 0.028771 |
| Apollo-SMR-like hazard scale | 0.457 | 0.667 | 19.34 | 0.199418 | 0.123580 | 0.123491 |

## Vitality Model

Vitality is modeled conditional on surviving to age 80. The Apollo target is 21 Space Grandpa positives, which is a public-activity construct. The population rates below are deliberately a range: dementia-free is permissive, normal cognition/no MCI is stricter, functional or public-activity rates are sensitivity placeholders pending HRS/NHATS extraction.

| Mortality scenario | Vitality scenario | Rate | Exp vital count | P(vital >= 21) | P(long+vital) |
| --- | --- | --- | --- | --- | --- |
| SSA general male, age-30 selected | Cao/GBD male 85-89 years dementia-free | 0.791 | 9.46 | 0.000013 | 6.839e-08 |
| SSA general male, age-30 selected | HRS-HCAP 65+ normal cognition overall | 0.680 | 8.13 | 9.039e-07 | 6.205e-09 |
| SSA general male, age-30 selected | ScienceDirect long-lived 80-94 no MMSE impairment | 0.648 | 7.75 | 3.813e-07 | 2.797e-09 |
| SSA general male, age-30 selected | Functional/participatory vitality sensitivity, 50 pct | 0.500 | 5.98 | 2.955e-09 | 2.799e-11 |
| SSA general male, age-30 selected | Apollo observed Space Grandpa among 80+ | 0.955 | 11.41 | 0.000317 | 7.223e-07 |
| Modestly healthy, 15 pct lower hazard | Cao/GBD male 85-89 years dementia-free | 0.791 | 10.80 | 0.000128 | 0.000004 |
| Modestly healthy, 15 pct lower hazard | HRS-HCAP 65+ normal cognition overall | 0.680 | 9.29 | 0.000010 | 3.659e-07 |
| Modestly healthy, 15 pct lower hazard | ScienceDirect long-lived 80-94 no MMSE impairment | 0.648 | 8.86 | 0.000004 | 1.679e-07 |
| Modestly healthy, 15 pct lower hazard | Functional/participatory vitality sensitivity, 50 pct | 0.500 | 6.83 | 3.632e-08 | 1.815e-09 |
| Modestly healthy, 15 pct lower hazard | Apollo observed Space Grandpa among 80+ | 0.955 | 13.04 | 0.002561 | 0.000036 |
| Healthy, 30 pct lower hazard | Cao/GBD male 85-89 years dementia-free | 0.791 | 12.34 | 0.001099 | 0.000145 |
| Healthy, 30 pct lower hazard | HRS-HCAP 65+ normal cognition overall | 0.680 | 10.61 | 0.000094 | 0.000015 |
| Healthy, 30 pct lower hazard | ScienceDirect long-lived 80-94 no MMSE impairment | 0.648 | 10.11 | 0.000042 | 0.000007 |
| Healthy, 30 pct lower hazard | Functional/participatory vitality sensitivity, 50 pct | 0.500 | 7.80 | 4.237e-07 | 8.438e-08 |
| Healthy, 30 pct lower hazard | Apollo observed Space Grandpa among 80+ | 0.955 | 14.89 | 0.017339 | 0.001233 |
| Very healthy, 45 pct lower hazard | Cao/GBD male 85-89 years dementia-free | 0.791 | 14.09 | 0.008058 | 0.003351 |
| Very healthy, 45 pct lower hazard | HRS-HCAP 65+ normal cognition overall | 0.680 | 12.11 | 0.000824 | 0.000390 |
| Very healthy, 45 pct lower hazard | ScienceDirect long-lived 80-94 no MMSE impairment | 0.648 | 11.55 | 0.000386 | 0.000188 |
| Very healthy, 45 pct lower hazard | Functional/participatory vitality sensitivity, 50 pct | 0.500 | 8.91 | 0.000005 | 0.000002 |
| Very healthy, 45 pct lower hazard | Apollo observed Space Grandpa among 80+ | 0.955 | 17.00 | 0.091828 | 0.024338 |
| Apollo-SMR-like hazard scale | Cao/GBD male 85-89 years dementia-free | 0.791 | 15.30 | 0.024964 | 0.016755 |
| Apollo-SMR-like hazard scale | HRS-HCAP 65+ normal cognition overall | 0.680 | 13.15 | 0.002930 | 0.002131 |
| Apollo-SMR-like hazard scale | ScienceDirect long-lived 80-94 no MMSE impairment | 0.648 | 12.54 | 0.001420 | 0.001050 |
| Apollo-SMR-like hazard scale | Functional/participatory vitality sensitivity, 50 pct | 0.500 | 9.67 | 0.000020 | 0.000015 |
| Apollo-SMR-like hazard scale | Apollo observed Space Grandpa among 80+ | 0.955 | 18.46 | 0.217988 | 0.106133 |

## Assumption Inventory

| Key | Rate | Construct | Denominator | Source |
| --- | --- | --- | --- | --- |
| cao_gbd_2020_male_80_84_dementia_free | 0.866 | Dementia-free only | Men in age band 80-84 years | Cao et al. 2024 supplement eTable 4, GBD 2019 forecast, U.S. male 2020 |
| cao_gbd_2020_male_85_89_dementia_free | 0.791 | Dementia-free only | Men in age band 85-89 years | Cao et al. 2024 supplement eTable 4, GBD 2019 forecast, U.S. male 2020 |
| cao_gbd_2020_male_90_94_dementia_free | 0.697 | Dementia-free only | Men in age band 90-94 years | Cao et al. 2024 supplement eTable 4, GBD 2019 forecast, U.S. male 2020 |
| cao_gbd_2020_male_95_plus_dementia_free | 0.507 | Dementia-free only | Men in age band 95+ years | Cao et al. 2024 supplement eTable 4, GBD 2019 forecast, U.S. male 2020 |
| hcap_65plus_normal_cognition_overall | 0.680 | No dementia and no MCI | U.S. adults 65+, not age-80 male survivors | HRS-HCAP prevalence paper: 10 pct dementia and 22 pct MCI among U.S. adults 65+ in 2016 |
| sciencedirect_80_94_no_mmse_impairment | 0.648 | No poor MMSE performance | Community-dwelling long-lived adults age 80-94 | Campos et al. 2024, Journal of Affective Disorders, n=165 age 80-94; 58 poor MMSE adjusted for education |
| functional_vitality_sensitivity_50pct | 0.500 | Normal cognition plus functional/participatory reserve | Age-80 survivors | Sensitivity assumption, not a single-source estimate |
| public_activity_sensitivity_35pct | 0.350 | Visible late-life activity | Age-80 survivors | Sensitivity assumption, not a single-source estimate |
| apollo_observed_space_grandpa_among80 | 0.955 | Publicly documented late-life activity | Apollo age-80 survivors | Run1 astronaut dataset Space Grandpa field |

## Interpretation Guardrails

- SSA mortality can answer longevity only; it cannot infer mental vitality.
- Dementia-free rates are upper-bound vitality proxies because they do not exclude MCI, functional dependence, or low participation.
- The ScienceDirect 80-94 MMSE anchor is useful as a clinical caution but is not a U.S. high-education male population baseline.
- The age/cognition review supports the construct boundary: normal aging can preserve knowledge and speech while reducing speed, working memory, and executive function, so public late-life activity is not reducible to 'no dementia'.

## Output Files

- `run2_survival_scenario_summary.csv`
- `run2_survival_count_distributions.csv`
- `run2_observed_apollo_targets.csv`
- `run2_vitality_assumptions.csv`
- `run2_vitality_scenario_summary.csv`
- `run2_vitality_count_distributions.csv`
- `run2_method_notes.md`
- `run2_group29_report.md`
