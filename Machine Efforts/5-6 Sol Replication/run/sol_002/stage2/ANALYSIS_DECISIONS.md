# Stage 2 analysis decisions

## Freeze point and scope

These decisions were recorded before reading cohort flags, revealing group labels, or running group models. Stage 2 will read but never modify the locked Stage 1, Stage 1B, and Stage 1C artifacts. Astronaut comparisons use only the locked person-level data. The only external data permitted are official U.S. male cohort life tables. All estimates are descriptive and noncausal.

The censoring date is 2026-06-01. Two-sided 95% intervals are reported throughout. Effect signs are always APOLLO_FLEW minus or relative to the named comparator.

## Groups

- `APOLLO_FLEW`: `apollo_flew=1`.
- `OTHER_ALL`: `other_all=1`.
- `CORE_NASA_NON_APOLLO`: `core_nasa_non_apollo=1`.
- `MILITARY_ONLY`: the union of `military_x15`, `military_dyna_soar`, and `military_mol`, restricted to `apollo_flew=0`.
- `OTHER_AVAILABLE`: every `apollo_flew=0` person with usable locked birth and end-of-follow-up data. It is used only for the retrospective birth-origin description. Its post-1973 and age-80 risk-set identity with `OTHER_ALL` will be checked mechanically; an identical set will be reported as such, not presented as sensitivity evidence.

Comparator groups are nested and reuse people. Composition sensitivities are not independent replications.

## Survival estimands and uncertainty

For each group, report people, deaths, administrative censoring, observed attained age at death/censor, median and interquartile range, range, and an exact distribution-free 95% confidence interval for the median based on binomial order statistics. Death proportions receive Clopper–Pearson exact intervals.

The primary survival analysis uses the common landmark 1973-01-01 and includes people alive on that date. Follow-up is from the landmark to death or 2026-06-01. The primary effect is the difference in Kaplan–Meier restricted mean survival time through 50 years:

`RMST(APOLLO_FLEW) - RMST(comparator)`.

The primary interval uses a stratified nonparametric percentile bootstrap that resamples people within each group, 50,000 replicates, seed 20260721, and the 2.5th and 97.5th percentiles. The same algorithm and seed are used separately for prespecified composition contrasts. Kaplan–Meier pointwise intervals use Greenwood variance with the log–log transformation.

The fixed adjustment sensitivity is a Cox proportional-hazards model from the landmark with APOLLO_FLEW indicator and age at landmark in years as a linear covariate, Efron ties, and conventional two-sided Wald intervals. Report the group hazard ratio and p-value as supplementary. Test proportional hazards using Schoenfeld residuals against transformed event time for each covariate and globally. This model does not replace the RMST primary.

Kaplan–Meier from birth is a secondary retrospective, future-flight-selected cohort description. Composition descriptions compare APOLLO_FLEW with `OTHER_ALL`, `CORE_NASA_NON_APOLLO`, and `MILITARY_ONLY`; `OTHER_AVAILABLE` appears only here.

## U.S. population expectation

Use an official Social Security Administration male cohort life table matched to exact birth year. Record the official URL and local fetched copy. Derive exact-birth-year survival probabilities and expected remaining lifetime. For the landmark risk sets, calculate each person's expected 50-year RMST conditional on survival to their 1973 age, then average within group. Also compare birth-origin Kaplan–Meier survival at selected attained ages with birth-year-standardized male cohort expectations. Population comparisons are descriptive benchmarks, not exchangeable controls, and receive no causal interpretation.

## Public-evidence detection estimands

Eligibility is reaching age 80 by death or 2026-06-01. The primary public-function analysis begins on the 80th birthday. First qualifying function before age 85 is the event of interest; death first is a competing event; the 85th birthday or 2026-06-01 is censoring. Estimate five-year cumulative incidence with Aalen–Johansen.

The primary effect is:

`five-year CIF(APOLLO_FLEW) - five-year CIF(OTHER_ALL)`.

Its interval uses stratified nonparametric percentile bootstrap resampling people within groups, 50,000 replicates, seed 20260721, with the 2.5th and 97.5th percentiles. Apply the same algorithm separately to the two composition sensitivities. Verify whether `OTHER_AVAILABLE` and `OTHER_ALL` have the same age-80 risk set; if identical, do not duplicate the estimate.

The precommitted R001 technical-deviation sensitivity repeats, without changing any primary analysis, (1) APOLLO_FLEW versus OTHER_ALL five-year detection and (2) the secondary crude any-age-80-plus detection after excluding R001. It is neither primary nor an independent confirmation.

The secondary crude endpoint is any qualifying function event at any age 80+. Report numerator/denominator and Clopper–Pearson exact intervals by group; risk difference with a Newcombe score interval; risk ratio with a compatible score/log interval; odds ratio with a conditional exact interval; and Fisher's exact two-sided p-value. Zero cells, if any, will be retained and handled by the stated interval method rather than silently corrected.

Describe documentation depth and raw substantive-source/publisher counts by group. Do not condition an endpoint analysis on documentation depth and do not call MEDIUM/HIGH restriction adjustment or complete-case correction.

For `NEITHER_FOUND`, report separately labeled worst/best latent-event bounds by assigning all such people in one group versus the other an unobserved event. These bounds answer a different latent-event question, not observed public-evidence detection, and do not change the primary estimate.

For every qualifying boundary-sensitive event, repeat the primary coding at its earliest and latest defensible dates. If there are no such rows, record that the sensitivity is identical by construction. Summarize latest qualifying-function ages and the locked function/impairment temporal states.

## Classification

Classify survival and public function separately as ROBUST, SUGGESTIVE, NOT_DETECTED, or INDETERMINATE, and direction as HIGHER, LOWER, or UNCERTAIN.

- Survival practical materiality: absolute primary RMST difference at least 5.0 years.
- Public-function practical materiality: absolute primary five-year risk difference at least 0.10.
- ROBUST requires practical materiality, a primary 95% interval excluding the null, and no direction reversal in either prespecified composition sensitivity.
- SUGGESTIVE permits interval or ascertainment uncertainty but requires coherent direction and practical magnitude.
- NOT_DETECTED means the effect is small, unstable, or sensitivity-explained.
- INDETERMINATE is reserved for data or provenance failure that prevents judgment.
- Direction is the sign of the primary Apollo-minus-OTHER_ALL estimate; exactly zero is UNCERTAIN. A large precise negative effect is treated symmetrically.

The narrow conclusion will answer only whether either prespecified endpoint shows a descriptive anomaly under these rules. Future-flight classification, immortal-time/selection, healthy-selectee effects, nested comparator reuse, public-source availability, and noncausal interpretation will be explicit.

## External-source access deviation recorded before models

The preferred 2023 Trustees Report Alternative II male cohort CSV was identified on the official SSA site, but the web connector exposed only a truncated preview and the local sandbox could not resolve the SSA host. No model had been run when this access failure occurred.

The direction-neutral fallback is official SSA Actuarial Study No. 120:

- Table 11 provides exact annual male cohort life expectancy at birth for every locally represented birth year.
- Table 7 provides the male cohort survivor function at exact age 80 for 1920, 1930, 1940, and 1950. Exact-birth-year S80 will be linearly interpolated between the two surrounding official decennial rows.

Accordingly, the population benchmark is limited to exact-year expected lifetime at birth and birth-year-standardized survival to age 80. A population 50-year landmark RMST will not be synthesized from unavailable ages. This changes only the external descriptive benchmark, not any astronaut contrast, primary estimand, interval, sensitivity, or classification rule.
