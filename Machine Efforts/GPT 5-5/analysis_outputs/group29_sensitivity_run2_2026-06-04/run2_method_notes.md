# Run 2 Method Notes

Analysis date: 2026-06-04

## Inputs

- Run1 parser/script: `scripts/apollo_mortality_survival_analysis.py`
- Astronaut source data: run1 `load_people()` over the enriched Apollo/non-Apollo TSVs.
- Mortality source: local SSA 1930 male cohort life table from the processed-data folder, conditional on age 30.
- Cao/GBD extracted supplement table: `source_research/mental_vitality_medical_data_2026-06-04/extracted/pmc11336039_cao2024_supplement_forecast_tables.csv`
- ScienceDirect local HTML: `source_research/mental_vitality_medical_data_2026-06-04/references/sciencedirect_2024_prevalence_cognitive_impairment_older_people.html`
- Murman local HTML: `source_research/mental_vitality_medical_data_2026-06-04/references/pmc4906299_impact_of_age_on_cognition.html`

## Apollo Targets

- Group size: 29
- Reached age 80: 22
- Reached age 90: 13
- Reached age 95: 3
- Space Grandpa positives among all 29: 21
- Space Grandpa positives among age-80 survivors: 21

## Mortality Sensitivity

SSA survival from age 30 to age A is S_SSA(A). A health-selection scenario uses a hazard scale h:

```text
S_adjusted(A) = S_SSA(A) ** h
```

The Monte Carlo draw for each simulated person uses one uniform random number and the nested probabilities for reaching ages 80, 90, and 95. This is enough for the run2 question because the requested endpoint is count of people reaching Apollo-like age thresholds, not full death-age curves.

Exact probabilities are computed from the multinomial distribution over four mutually exclusive categories: death before 80, reached 80 but not 90, reached 90 but not 95, and reached 95. This prevents rare-tail conclusions from depending only on Monte Carlo resolution.

## Vitality Sensitivity

Vitality is modeled conditional on being an age-80 survivor. If k people in the simulated group reach age 80, and p is a chosen vitality proxy probability, the vitality count is Binomial(k, p). The final distribution is a mixture over the survival-count distribution.

```text
P(V = v) = sum_k P(N80 = k) * BinomialPMF(v | k, p)
```

The core output probabilities include:

- `P(vitality >= 21)` regardless of the exact age-threshold profile.
- `P(N80 >= 22 and vitality >= 21)`.
- `P(N80 >= 22 and N90 >= 13 and vitality >= 21)`.
- `P(N80 >= 22 and N90 >= 13 and N95 >= 3 and vitality >= 21)`.

## Construct Boundary

The astronaut `Space Grandpa` field is public late-life activity. Cao/GBD dementia-free rates, HRS-HCAP normal cognition, and the ScienceDirect MMSE anchor are clinical or survey-health proxies. They should be read as sensitivity bounds, not a direct substitution for public activity.

## Reproducibility

- Monte Carlo iterations per mortality scenario: 1,000,000
- Seed base: 15170506
- Exact probabilities are deterministic and do not depend on the seed.
