# Mental Vitality From Medical Documentation / Data

Analysis date: 2026-06-04

## Bottom Line

Yes, a population-level mental-vitality proxy can be inferred from medical and survey-health data, but not the same construct as the current `Space Grandpa` field.

`Space Grandpa` is an externally visible public-activity proxy: did the person show documented, notable late-life activity at 80+? Medical data can instead estimate clinical or functional cognitive vitality: no dementia, no MCI, preserved cognitive testing, independence in daily activities, absence of subjective cognitive decline with functional limitation, and/or continued participation in valued activities.

So the rigorous answer is:

- Do not use Medicare claims alone as the general-population mental-vitality denominator. They undercount or misclassify dementia and MCI.
- Do use HRS-HCAP and/or NHATS as the primary population comparator, with Medicare claims only as a linked secondary or sensitivity source.
- Do not claim that SSA life tables say anything about mental vitality. SSA supports survival only.
- Do not directly compare `Space Grandpa` to clinical normal cognition without labeling it as a cross-construct comparison.

## Construct Boundary

### Astronaut Dataset Construct

Current field: `Space Grandpa`.

Meaning in the current enriched astronaut data: source-backed public, professional, civic, creative, or aviation/space-related activity at age 80+, usually documented through biographical pages, news, institutional pages, speeches, books, interviews, or other public records.

This is not a clinical cognition measure. It is biased toward famous, publicly visible, institutionally celebrated people.

### Medical / Survey Construct

Potential measures:

1. Dementia-free survival at age 80+.
2. Cognitively normal, meaning neither dementia nor MCI.
3. No subjective cognitive decline with functional limitation.
4. Cognition plus function: no dementia/MCI, no ADL/IADL impairment, no need for proxy because of cognitive problems.
5. Participation-preserving vitality: cognition/function plus work, volunteering, social participation, technology use, driving, leaving home, or valued activities.

The most defensible comparator to `Space Grandpa` is not merely "not dementia." It is a composite that combines normal cognition, functional independence, and participation.

## Best Available Data Sources

### 1. HRS-HCAP

Use as primary cognitive-status source.

Evidence:

- The HRS-HCAP prevalence paper states that HRS is nationally representative and that HCAP was designed to update national estimates of MCI and dementia.
- HCAP sampled HRS participants age 65+ in 2016; 3,496 completed a comprehensive neuropsychological battery and informant interview.
- Dementia and MCI were classified by an algorithm based on standard diagnostic criteria and comparison with a robust normative sample.
- Published 2016 prevalence estimates: dementia 10% (95% CI 9-11) and MCI 22% (95% CI 20-24) among U.S. adults 65+; therefore broad normal-cognition prevalence is roughly 68% among 65+, before age-specific adjustment.
- Age was strongly associated with dementia and MCI, so age 80+/85+ rates must be estimated from age-stratified HCAP or HRS data rather than applying the overall 65+ rate.

Use case for this project:

- HCAP 2016 is well timed for the 1930 birth cohort: people born in 1930 were about 85-86 in 2016.
- The HRS-HCAP data release requires researcher registration and, for HCAP, sensitive-data access terms. This means raw person-level HCAP data should be pulled through the formal HRS route, not scraped.

### 2. NHATS

Use as primary functional and participation source, and secondary cognition source.

Evidence:

- NHATS is a nationally representative study of Medicare beneficiaries age 65+.
- It collects information on physical, cognitive, and sensory capacity; daily activities; social/technological environment; and participation in valued activities.
- It includes self and proxy cognitive assessments: memory, changes in thinking/memory, behavior, date orientation, 10-word recall, clock drawing, naming President/Vice President, delayed recall, and related measures.

Use case for this project:

- NHATS can support a "vitality" composite closer to the astronaut `Space Grandpa` idea because it includes participation and functioning, not only diagnosis.
- It is still not public eminence. It measures ordinary late-life function and participation.

### 3. Medicare Claims

Use only as a secondary medical-diagnosis source or sensitivity analysis.

Evidence:

- A 2026 HRS-linked Medicare claims evaluation of ICD-10 dementia case definitions reported 50% sensitivity and 97% specificity for a likely-or-higher Dementia DataHub definition relative to HRS classifications. It concluded that Medicare diagnoses are valuable for surveillance of diagnosed dementia but often miss cases.
- Zhu et al. 2019, comparing clinical dementia diagnosis with Medicare claims, reported sensitivity 0.51 and specificity 0.92.
- A Rush Alzheimer Disease Center validation using recent Medicare FFS claims found sensitivity 79%, specificity 88%, PPV 50%, NPV 97%, and accuracy 87% for a Bynum-standard algorithm.
- A 2025 ICD-10 Medicare claims validation found accuracy 87-90%, but most definitions favored specificity over sensitivity and performed differently by age, race, depressive symptoms, and stroke history.

Implication:

Claims are better at identifying diagnosed dementia than at proving cognitive vitality. "No dementia claim" is not the same as "cognitively vital."

### 4. CDC BRFSS Subjective Cognitive Decline

Use as a public-health surveillance source, not a clinical comparator.

Evidence:

- CDC defines subjective cognitive decline as worsening or more frequent confusion or memory loss in the previous 12 months.
- The 2015-2016 MMWR found 11.2% of adults age 45+ reported subjective cognitive decline, and only 45.4% of those with SCD had discussed it with a health care professional.
- SCD prevalence increased to 14.3% among adults age 75+.

Implication:

BRFSS can support a broad "self-reported cognitive trouble" sensitivity analysis. It is not medical documentation and is not adequate for an astronaut comparison by itself.

### 5. Cao et al. 2024 / PMC11336039 / GBD Oldest-Old Dementia

Use as a secondary dementia-burden comparator, not as a primary mental-vitality source.

Evidence:

- Cao et al. 2024 is a GeroScience paper on U.S. adults age 80+ using Global Burden of Disease Study 2019 estimates for dementia prevalence, dementia mortality, and risk factors.
- The article reports that dementia cases and deaths among U.S. oldest-old adults rose substantially from 1990 to 2019, mainly because of population growth and aging.
- The Springer supplementary PDF contains extractable numeric tables: decomposition results for 1990-2019 changes and predicted dementia prevalent cases/rates and mortality counts/rates for 2020-2030.
- Extracted table files were generated locally:
  - `source_research/mental_vitality_medical_data_2026-06-04/extracted/pmc11336039_cao2024_supplement_forecast_tables.csv` with 528 rows from eTables 3-6.
  - `source_research/mental_vitality_medical_data_2026-06-04/extracted/pmc11336039_cao2024_supplement_decomposition_tables.csv` with 4 rows from eTables 1-2.

Usable columns:

- Age groups: 80-84, 85-89, 90-94, 95+.
- Sex: both, female, male.
- Years: 2020-2030 for forecast tables.
- Measures: dementia prevalent cases, dementia prevalence rate per 100,000, dementia mortality count, dementia mortality rate per 100,000.
- Uncertainty: 95% CI lower/upper values.

Implication for the Apollo project:

- This is usable for a broad U.S. oldest-old dementia-free bound:
  `dementia_free_rate = 1 - dementia_prevalence_rate_per_100k / 100000`.
- It is not enough to estimate `Space Grandpa` or mental vitality directly. It says nothing about MCI, normal cognition, ADL/IADL independence, public activity, work, volunteering, speeches, writing, or social participation.
- It is aggregate/modelled GBD output, not person-level cohort data. It cannot be standardized to astronaut-like health, education, military selection, or survival to age 30 without additional data.
- For the 1930 birth cohort specifically, the supplement's 2020-2030 tables cover roughly ages 90-100. Age 80/85 comparators for the 1930 cohort would require pulling 2010/2015 GBD values directly from the GBD Results tool or using HRS/NHATS/HCAP.

### 6. Campos et al. 2024 / ScienceDirect Cognitive Impairment Paper

Use as a cautionary clinical sensitivity anchor, not as a U.S. general-population comparator.

Evidence:

- The local ScienceDirect HTML copy reports a sample of 165 community-dwelling long-lived adults age 80-94, mean age 84.8 years.
- Poor Mini-Mental State Examination performance adjusted for education was found in 58 participants, or 35.2%.
- This gives a simple "no poor MMSE performance" anchor of 64.8% among that specific sample.
- The paper notes limitations: cross-sectional design, reduced sample size, and no comparisons among different ages and populations.

Implication:

- The paper is useful for bounding the idea that "dementia-free" is too permissive as a mental-vitality proxy.
- It should not be treated as the correct SSA-like rate for healthy U.S. men born in 1930. The sample is not U.S.-representative, is mostly female, and has very low mean education.

### 7. Murman 2015 / The Impact of Age on Cognition

Use as a construct-boundary source.

Evidence:

- The review distinguishes normal age-related cognitive change from disease-associated impairment.
- It emphasizes that speed of processing, working memory, and executive function tend to decline with normal aging, while cumulative knowledge and experiential skills are better maintained into advanced age.
- It also flags recruitment, misclassification, practice-effect, attrition, and survival biases in cognition-aging studies.

Implication:

- This supports keeping the astronaut `Space Grandpa` construct separate from clinical categories such as dementia-free or normal cognition.
- It also supports reporting ranges rather than a single mental-vitality denominator until HRS-HCAP/NHATS person-level age- and sex-specific estimates are extracted.

### 8. MHAS / Mexican Health and Aging Study

Use as a potential strict lower-bound anchor if the supplied 54/334 calculation is accepted, but do not treat the cohort-profile citation alone as the source of that numerator and denominator.

Evidence saved locally:

- The official MHAS study-description page describes MHAS as a national longitudinal study of adults age 50+ in Mexico.
- The Wong, Michaels-Obregon, and Palloni cohort-profile metadata was saved from PubMed; the Oxford PDF endpoint returned a Cloudflare challenge page, which is retained as a failed PDF attempt.
- The official MHAS constructed-data page says the cognitive-function constructed files include scores, normative standards, z-scores, and cognitive classifications.
- The 2018/2021 MHAS cognitive scoring document defines direct-interview cognitive status as:
  - normal;
  - normal with instrumental impairment;
  - CIND;
  - dementia.
- The same scoring document combines cognitive task impairment, IQCODE proxy classification, and IADL difficulty; for example, 2021 dementia includes proxy impairment or 2+ impaired cognitive tasks plus at least one IADL difficulty.
- The created-variable descriptive document did not, by itself, verify the supplied 54/334 figure. One visible `334` hit in that document is `aivd_medicina_21`, difficulty taking medications, not an age-80+ cognitive denominator.

Current implication:

- The supplied estimate `54 / 334 = 16.17%` is useful as a strict lower-bound sensitivity point only if treated as a user-supplied MHAS-derived calculation.
- It should be labelled separately from the official cohort-profile citation until the exact analytic subset and variable definition are reproduced from MHAS microdata.
- A new run2 sub-output uses this lower anchor, paired with the HRS-HCAP broad 68% normal-cognition upper anchor:
  `analysis_outputs/group29_sensitivity_run2_2026-06-04/simple_80plus_mhas16_vitality_grid/`.

## Recommended Operational Endpoints

### Primary Endpoint: Clinical Cognitive Vitality at 80+

Among people who survive to age 80:

`cognitive_vitality_80 = normal cognition, no MCI, no dementia`

Source: HRS-HCAP/HRS cognition algorithms.

This is the cleanest medical/survey endpoint, but it is stricter than "not dementia."

### Secondary Endpoint: Functional Cognitive Vitality at 80+

Among people who survive to age 80:

`functional_vitality_80 = normal cognition AND no ADL/IADL dependency AND no proxy/cognitive-functional limitation`

Source: HRS or NHATS.

This better matches "retention of mental vitality" than diagnosis alone.

### Tertiary Endpoint: Participatory Vitality at 80+

Among people who survive to age 80:

`participatory_vitality_80 = functional_vitality_80 AND evidence of participation`

Possible participation indicators:

- Working, volunteering, caregiving, organized activities, or frequent social engagement.
- Drives or independently leaves home.
- Uses technology/handles bills/communications.
- Reports valued activity participation.

Source: NHATS is likely stronger than HRS for this endpoint.

This is the closest population comparator to `Space Grandpa`, but still not equivalent to public biographical visibility.

## How to Estimate for a 1930-Birth-Cohort Comparator

1. Pull HRS public cognition and HCAP sensitive data through HRS registration.
2. Restrict to U.S. respondents born around 1930, or use birth-year/age cells that put respondents at age 80, 85, and 90.
3. Condition on survival to age 30 conceptually, then on observed survival to the age being evaluated. For cognitive vitality at 80+, the immediate denominator should be survivors to 80, not the entire birth cohort, unless explicitly modeling survival and cognition jointly.
4. Weight estimates with HRS/HCAP sampling weights.
5. Stratify or standardize by:
   - sex,
   - education,
   - race/ethnicity,
   - veteran/military status if available,
   - birth-year band,
   - survival age.
6. For the astronaut comparison, report at least two baselines:
   - general U.S. male baseline;
   - high-education / healthier survivor sensitivity baseline.
7. Do a Medicare-claims-only sensitivity analysis, then correct/qualify it using published sensitivity and specificity ranges.

## Current Evidence-Based Conclusion

The current astronaut `Space Grandpa` rate should not be described as comparable to a "mental vitality rate" inferred from medical documentation without redefinition.

But it is scientifically feasible to build a rigorous general-population comparator if the endpoint is renamed and operationalized. The strongest defensible language is:

> "We compare astronaut public-activity retention to population cognitive/functional vitality proxies from HRS-HCAP/NHATS. These are related but non-identical measures; the population estimate is not a public-visibility rate."

## Local Archive Notes

Most source pages/documents were saved under `source_research/mental_vitality_medical_data_2026-06-04/references/`. Several HRS, DeepBlue, and PMC pages returned security-challenge HTML when fetched by shell, even though they are viewable in a browser or searchable. Those failed copies are retained in the archive and documented in `source_research/mental_vitality_medical_data_2026-06-04/source_log.csv` rather than discarded.
