# sol_002 Stage 2 controller gate

Gate time: 2026-07-23T06:30:29Z

## Result

Pass. Stage 2 and the blind conclusion are locked.

The same external `gpt-5.6-sol` thread used for Stages 1 through 1C ran with
memories disabled, user configuration and rules ignored, and a neutral actual
working directory. The thread received the cohort questions and labels only
after the ungrouped evidence files had passed the Stage 1C semantic gate. It
did not receive a prior estimate, conclusion, article, reference dataset, or
group-outcome hint.

## Blind conclusion

- `SURVIVAL: NOT_DETECTED / HIGHER`
- `PUBLIC FUNCTION: NOT_DETECTED / HIGHER`

The locked narrow answer is:

> No prespecified descriptive anomaly is detected.

## Primary estimates

| Endpoint | Apollo-minus-OTHER_ALL estimate | 95% interval | Locked materiality threshold |
|---|---:|---:|---:|
| 1973-landmark 50-year RMST | +0.670 years | -5.088 to +6.099 | 5.0 years |
| Five-year public-function detection | +1.688 percentage points | -8.571 to +13.636 | 10 percentage points |

Both point estimates are positive but below their materiality thresholds,
imprecise, and directionally reversed by one of the two prespecified nested
composition sensitivities.

The secondary any-age-80-plus public-detection counts are 3/22 for Apollo and
2/35 for `OTHER_ALL`. Excluding the technically nonuniform R001 record changes
the primary five-year contrast only from +1.688 to +1.905 percentage points.

## What the null classification does and does not mean

The raw selected-cohort descriptions are visibly favorable to Apollo: median
observed attained age is 88.1 versus 80.6, and 22/29 versus 35/66 reached age
80. The official male birth-cohort benchmark is also much lower, especially
for Apollo. Those are real descriptive patterns in this constructed dataset.

The protocol nevertheless classifies an Apollo-specific anomaly from the
common-landmark, same-era comparisons—not from the raw selected-cohort age
gap or the nonexchangeable general-population benchmark. Under that
prespecified test, the estimate is small and comparator-dependent. The result
does not show that the men were ordinary; it fails to isolate a stable
Apollo-specific excess from selection and comparator composition.

## Validation

The experimenter:

- retained all code, tables, reports, figures, source records, and decisions;
- ran 50,000 stratified bootstrap replicates per contrast with seed 20260721;
- completed the fixed Cox/Efron sensitivity and Schoenfeld-residual diagnostic;
- used Aalen–Johansen with death as competing event;
- produced exact/crude measures, boundary, latent-event, documentation-depth,
  composition, and R001 sensitivities;
- verified deterministic regeneration and locked-input immutability;
- returned `STAGE2_COMPLETE` with no blocking failure.

The independent controller audit separately reproduced all prespecified
bootstrap contrasts without importing the experimenter's analysis code,
checked the Cox score equations and standard errors, verified crude counts and
classification logic, and confirmed official SSA source values. It returned
no problems.

Every entry in all four stage manifests reverified. No Stage 1, Stage 1B, or
Stage 1C file changed during Stage 2.

## Declared qualifications

- `DEV-20260722-09`: the preferred complete SSA 2023 file was inaccessible.
  Before group models, the experimenter fixed a narrower official SSA AS120
  fallback. This affects only the external descriptive benchmark.
- `DEV-20260722-10`: two self-generated temporary aggregate-hash files were
  briefly written outside the neutral root and immediately deleted by exact
  pathname. They exposed no external data and have no analytic effect.
- The PH diagnostic is an explicitly labeled Schoenfeld-residual correlation
  and approximate global check. It is supplementary to the RMST primary.

## Hashes

- Stage 2 launch message:
  `628606bae2ec906dc00cb047457b57e524ec5e374ad7fe83aa57de7d3d37c567`
- Stage 2 manifest:
  `014ef8b64ef864b17d62857bce13feee8a8d0962aee488cbec815e4fbf355378`
- independent controller audit:
  `ce8bb16fbc3d2e423c1d9382a2422c770f5cf4d596e49f3a04d5d67eb261667e`
- independent controller validator:
  `d5bc3a574f6aba19e13d0152df457a5bfe2263ec4644c2c7c80fefad4fb4dd75`
- blind conclusion:
  `727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df`
- analysis report:
  `41b26e07f2aac5e48c8da9dac1f2588d08266ec0b2b03073de69f0b5b8931040`
- child final response:
  `0efb2c9d8c42c53bfa98999b58450a498825fc6470c0a18d629d274d865bb86a`

## Runtime usage

The persistent thread's cumulative usage was 68,579,545 input tokens,
67,161,600 cached input tokens, 267,594 output tokens, and 92,499 reasoning
output tokens. Stage 2 added 9,027,650 input, 8,851,712 cached input, 63,423
output, and 22,783 reasoning output tokens.

## Decision

The clean-context blind replication is complete through Stage 2. Do not begin
Stage 3 reconciliation until the author explicitly chooses to compare this
locked run with prior datasets or results.
