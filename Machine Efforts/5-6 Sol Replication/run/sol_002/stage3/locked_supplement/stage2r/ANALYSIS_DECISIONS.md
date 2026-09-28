# Stage 2R Prospective Analysis Decisions

## Status and estimand

This document was fixed before any group outcome was calculated or revealed and before any group model was run. Stage 2R is a transparently labeled post-lock endpoint correction. It changes only the endpoint window: the stale age-80-to-85 restriction is superseded, and every locked qualifying achievement at age 80 or older through death or administrative censoring on 2026-06-01 is retained. Locked evidence definitions, adjudicated events, dates, source rules, and person-level states are not changed.

The corrected primary endpoint is a person-level indicator equal to one if the person has at least one locked `QUALIFYING_FUNCTION_EVENT` at any age 80 or older and no later than death or 2026-06-01, and zero otherwise. The target population is the locked cohort of people who reached age 80. This is public-evidence detection, not a clinical measure.

The primary contrast is the unrestricted detected-event risk in `APOLLO_FLEW` minus the unrestricted detected-event risk in `OTHER_ALL`. A negative effect is treated symmetrically with a positive effect. The unchanged practical-materiality threshold is an absolute risk difference of 0.10.

## Primary summaries and inference

For each primary group, the report will give the raw detected numerator and eligible denominator and a two-sided 95% Clopper-Pearson binomial interval.

The following two-by-two measures compare `APOLLO_FLEW` with `OTHER_ALL`:

- risk difference, Apollo minus Other, with a two-sided 95% Newcombe interval formed from the two independent Wilson score intervals without continuity correction (Newcombe method 10);
- risk ratio, Apollo divided by Other, with a two-sided 95% score interval obtained by inverting the constrained two-sample binomial score test for the risk-ratio parameter; boundary values are reported as zero or infinity when required;
- odds ratio, Apollo divided by Other, with a two-sided 95% conditional exact interval obtained by inverting equal-tail noncentral-hypergeometric tests conditional on the margins;
- a two-sided Fisher exact p-value, defined as the sum of central-hypergeometric table probabilities no greater than the probability of the observed table, with a small floating-point tolerance for equality.

In addition, a group-stratified person-level nonparametric bootstrap will independently resample people with replacement within `APOLLO_FLEW` and within `OTHER_ALL`, preserving both group sample sizes. The statistic is the Apollo-minus-Other risk difference. Exactly 50,000 replicates will be generated using the standard-library pseudorandom generator with seed `20260721`; the interval is the linearly interpolated 2.5th and 97.5th empirical percentiles.

No covariate-adjusted group model is primary.

## Unequal observable time

A complete Aalen-Johansen cumulative-incidence curve will be estimated from exact age 80. First locked qualifying function is the event of interest, death before such an event is the competing event, and administrative end on 2026-06-01 is right censoring. Every qualifying event at age 80 or older is retained; nobody is censored at age 85.

Analysis time is elapsed years from the date of the 80th birthday, using actual day differences divided by 365.2425. An event must occur no later than the locked death date and administrative end. Death after a first qualifying event does not alter event status. At a time with tied event-of-interest and competing-event counts, both increments use the common risk set immediately before that time and survival is then reduced by all failures at that time. Administrative censoring at a tied time occurs after failures for risk-set accounting.

The full step curve, including risk-set counts and event/censor counts at every observed time, will be retained in a generated CSV and figure. Readouts will be reported at 5, 10, and 15 years after age 80, using the last step at or before the requested time. “Under observation” is the event-free, death-free risk set immediately before the readout time among people whose follow-up reaches that time. Each readout will state that count. A tail-support warning will be explicit when fewer than 10 people in either comparison group remain under observation, or fewer than 20% of that group’s starting risk set remains; zero support will be labeled non-estimable rather than extrapolated.

These curves and milestone readouts are subordinate descriptions of observable time, not eligibility rules and not replacements for the unrestricted primary endpoint.

Potential post-80 follow-up will be summarized from age 80 to death or administrative end. Observed public-documentation features available in the locked inputs—death/censoring, documentation depth, substantive-source count, and independent-publisher count—will be described by group without conditioning, weighting, excluding, or redefining the endpoint on their basis.

## Later achievement

A person-level event-age table will be retained for every eligible person. It will include the person identifier, group/set membership, endpoint indicator, all locked qualifying event ages at 80 or older in chronological order, the number of such events, and the first and latest event ages where detected. Event age uses elapsed days from the locked birth date divided by 365.2425; date-only precision and plausible-date alternatives are addressed in the date sensitivity.

Among detected people, the report will provide first-event and latest-event age summaries and the complete latest-age distribution. It will report locked function/impairment sequences without imposing an order on the substantive states. `NEITHER_FOUND` will remain a public-evidence state; no health ordering will be invented for it.

Qualifying detected events—not people—will be counted in the mutually exclusive age bands `[80,85)`, `[85,90)`, `[90,95)`, and `95+`. Events after age 85 remain part of the corrected primary endpoint.

## Fixed sensitivities

Composition sensitivities compare the unrestricted `APOLLO_FLEW` risk separately with `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY`. These comparator sets are explicitly nested and are not independent analyses; their person-ID nesting and overlap will be validated and reported.

The full-window eligible person-ID sets labeled `OTHER_AVAILABLE` and `OTHER_ALL` will be compared directly. If identical, the report will state the verified equality and will not duplicate the numerical result. Any inequality is a validation failure requiring explanation.

A technical-deviation sensitivity will recompute the unrestricted primary Apollo-minus-`OTHER_ALL` contrast after excluding person `R001`, regardless of that person’s group or endpoint state. It will not be presented as the corrected primary.

Separately labeled `NEITHER_FOUND` worst/best latent-event bounds answer a different question from public detection. Detected qualifying-function cases remain one. Among people whose locked sequence/state is `NEITHER_FOUND`, the lower Apollo-minus-Other bound assigns no latent event to Apollo and a latent event to Other; the upper bound assigns a latent event to Apollo and none to Other. Other locked non-detected states remain zero. These extreme assignments are not clinical estimates and do not change the public-detection endpoint.

An earliest/latest plausible-date sensitivity will use the locked date precision/bounds, where available, to evaluate whether a person reached age 80 by death/administrative end and whether a qualifying event is at age 80 or older and precedes death/administrative end. The two coherent extremes will be labeled according to their earliest or latest plausible dates, and any changed person/event classification will be listed. Age 85 is not a boundary in either scenario. If the locked inputs provide no date range beyond a single adjudicated date for a required field, the scenarios coincide and that fact will be reported.

## Classification rule

The corrected `PUBLIC FUNCTION` strength is one of `ROBUST`, `SUGGESTIVE`, `NOT_DETECTED`, or `INDETERMINATE`; direction is one of `HIGHER`, `LOWER`, or `UNCERTAIN`.

- `ROBUST` requires an absolute unrestricted primary risk difference of at least 0.10, the primary 95% Newcombe interval excluding zero, and no direction reversal in either composition sensitivity.
- `SUGGESTIVE` requires a coherent unrestricted direction and a practically material absolute magnitude of at least 0.10, but may have interval or ascertainment uncertainty.
- `NOT_DETECTED` applies when the contrast is small, unstable, or explained by sensitivity.
- `INDETERMINATE` applies only when a data or provenance failure prevents judgment.

Direction is assigned from the sign of the unrestricted Apollo-minus-`OTHER_ALL` primary risk difference: positive is `HIGHER`, negative is `LOWER`, and exactly zero or an unavailable estimand is `UNCERTAIN`. The classification will not use survival outcomes and will not consult, reconstruct, or compare against an original Stage 2 result.

## Reproducibility and retained artifacts

`stage2r/analysis.py` will use only the Python standard library. It will verify locked input hashes before and after analysis, reject out-of-window or internally inconsistent records, generate every result table and figure deterministically, and preserve the fixed bootstrap seed and replicate count. All machine-readable tables used for the report, the Aalen-Johansen curves/readouts, sensitivity results, validation checks, and a source-input hash manifest will be retained under `stage2r/`.

The script will never write to `stage1/`, `stage1b/`, or `stage1c/`. Deterministic regeneration will be checked by hashing generated analytical outputs from two clean output builds while excluding the append-only action log and the hand-authored attestation/decision documents.
