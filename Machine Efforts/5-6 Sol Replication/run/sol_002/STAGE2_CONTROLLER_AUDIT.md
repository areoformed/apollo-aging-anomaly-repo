# sol_002 Stage 2 independent controller audit

Audit time: 2026-07-23T06:28:50Z

## Result

Pass with the external-benchmark qualification in `DEV-20260722-09` and the
minor temporary-file qualification in `DEV-20260722-10`.

The blind classifications and conclusion were already written and returned by
the memory-disabled Sol thread before this audit began. The controller did not
alter any experimenter artifact.

## Independent numerical reproduction

`controller/sol_002/validate_stage2_controller.py` is a separate
standard-library implementation. It does not import the experimenter's
`stage2/analysis.py`. It independently rebuilt group membership and event
records from the locked CSV files and reproduced:

- all three 50,000-replicate landmark RMST bootstraps;
- all three 50,000-replicate five-year Aalen–Johansen bootstraps;
- the separately labeled R001-excluded Aalen–Johansen bootstrap;
- the primary crude function-detection counts;
- the Cox Efron score equations and model-based standard errors;
- the official-life-table year coverage and selected anchors;
- both endpoint classifications and the narrow conclusion.

The controller validator returned no problems. At the rounded published Cox
coefficients, the maximum absolute partial-likelihood score was
`0.0001101912`; the independently derived standard errors matched within
`0.000002`.

The experimenter's separate `stage2/validate.py` also passed. Its deterministic
rerun had already reproduced the same 30-artifact aggregate SHA-256,
`49720ae7dfac623d7e885500b5544195d7cab1f28bfb263f040519a80e6fd3d5`.

## Primary results

### Survival

The 1973 common-landmark Apollo-minus-`OTHER_ALL` 50-year RMST difference is
`+0.670080` years, with 50,000-replicate percentile interval
`[-5.088212, +6.098918]`.

The two nested composition sensitivities are:

- versus `CORE_NASA_NON_APOLLO`: `-2.972890` years;
- versus `MILITARY_ONLY`: `+4.651249` years.

The primary point estimate is below the locked absolute five-year materiality
threshold, its interval includes zero, and a prespecified composition
sensitivity reverses direction.

### Public-function detection

The age-80 risk set contains 22 Apollo and 35 `OTHER_ALL` people. There is one
first qualifying function detection before age 85 in each group. The
Apollo-minus-other five-year Aalen–Johansen difference is `+0.016883`, with
50,000-replicate percentile interval `[-0.085714, +0.136364]`.

The two nested composition sensitivities are `+0.009740` and `-0.031469`.
Excluding R001 changes the main technical-sensitivity difference only to
`+0.019048`. The primary estimate is below the locked ten-percentage-point
materiality threshold, its interval includes zero, and a prespecified
composition sensitivity reverses direction.

The secondary any-age-80-plus counts are 3/22 versus 2/35. Those counts do not
replace the five-year competing-risk primary.

## Official population benchmark

The preferred complete SSA 2023 male cohort file could not be downloaded in
the isolated runtime. Before any group outcome model, the experimenter fixed a
fallback to official SSA Actuarial Study 120:

- Table 11 for exact-year male cohort life expectancy at birth;
- Table 7 male survivor counts at age 80 for the 1920, 1930, 1940, and 1950
  birth cohorts, with linear interpolation for intervening birth years.

The controller opened the official SSA pages after the blind conclusion was
locked and verified every annual Table 11 value used for 1921–1942 and all
four age-80 anchors: `0.30437`, `0.36675`, `0.42355`, and `0.46735`.

The resulting population contrast is a descriptive healthy-selectee benchmark,
not an exchangeable control. The report correctly labels observed attained age
for living people as censored rather than completed lifetime.

## Method qualifications

- The isolated runtime had neither the scientific Python stack nor R. The
  experimenter therefore implemented the estimators in Python's standard
  library. Independent reproduction found no numerical discrepancy in a
  prespecified primary or composition contrast.
- The proportional-hazards check is a Schoenfeld-residual correlation with log
  event time plus an explicitly labeled approximate global statistic. It is
  supplementary, does not replace RMST, and found no signal that alters the
  endpoint classification.
- The two exact temporary hash files created outside the neutral root contained
  only self-generated aggregate hashes, were immediately deleted by exact
  pathname, and did not expose external data.

## Locked conclusion

- `SURVIVAL: NOT_DETECTED / HIGHER`
- `PUBLIC FUNCTION: NOT_DETECTED / HIGHER`

The narrow blind answer is: **No prespecified descriptive anomaly is
detected.**

This is not the statement that the raw Apollo attained ages look ordinary.
They do not: the selected cohort has much higher raw survival to age 80 than
the general U.S. male birth-cohort benchmark. It is the narrower statement
that the prespecified same-era cohort contrasts do not yield a material,
precise, composition-stable Apollo-specific anomaly.
