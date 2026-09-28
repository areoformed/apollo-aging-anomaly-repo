# sol_002r corrected Stage 2R independent controller audit

Audit time: 2026-07-23

## Result

Pass. The corrected unrestricted public-function analysis is complete.

This branch is a transparently post-lock endpoint correction under
`DEV-20260723-11`. A fresh memory-disabled Sol thread analyzed byte-identical
locked Stages 1–1C without access to the original Stage 2 directory, response,
numbers, direction, or conclusion. That runtime isolation protects the
reanalysis from the earlier result; it does not retroactively make the
endpoint correction preregistered.

## Corrected primary

At least one locked qualifying function event at any age 80+ was detected for:

- 3 of 22 `APOLLO_FLEW` people: 13.6%;
- 2 of 35 `OTHER_ALL` people: 5.7%.

The unrestricted Apollo-minus-other risk difference is:

- point estimate: `+0.079220779`;
- Newcombe method-10 95% interval: `[-0.077370641, +0.280496015]`;
- 50,000-replicate stratified percentile-bootstrap interval:
  `[-0.068831169, +0.244155844]`;
- bootstrap seed: `20260721`.

The risk ratio is `2.3864`, the odds ratio is `2.6053`, and the Fisher
two-sided p-value is `0.3638`. These remain public-evidence-detection
quantities, not clinical or latent-health estimates.

## Later achievement and opportunity

The five detected people have qualifying event ages:

- Apollo: 81.98, 88.43, and 90.64;
- `OTHER_ALL`: 83.59 and 88.62.

The corrected primary counts all five. The age-90.64 piloting event is no
longer discarded by an age-85 analytic boundary.

The full age-80-origin Aalen–Johansen readouts are:

| Years after 80 | Apollo CIF | Other CIF | Apollo minus other | Under observation |
|---:|---:|---:|---:|---:|
| 5 | 4.55% | 2.86% | +1.69 pp | 18 vs 25 |
| 10 | 9.09% | 5.98% | +3.11 pp | 12 vs 11 |
| 15 | 14.09% | 5.98% | +8.11 pp | 2 vs 2 |

The 15-year readout is correctly marked as a severe tail-support warning, not
strong evidence. The unrestricted binary primary intentionally permits unequal
opportunity: median potential post-80 follow-up is 10.62 years for Apollo
versus 8.39 for `OTHER_ALL`, and Apollo also has somewhat greater public-source
depth. The report discloses these ascertainment advantages rather than
conditioning them away.

## Sensitivities

- versus `CORE_NASA_NON_APOLLO`: `+6.49` percentage points;
- versus `MILITARY_ONLY`: `+5.94` percentage points;
- excluding R001: `+3.81` percentage points.

Unlike the stale five-year endpoint, the two prespecified composition point
estimates do not reverse direction. The estimate nevertheless remains below
the unchanged ten-percentage-point materiality threshold, its intervals
include zero, and the R001 sensitivity attenuates it.

## Independent validation

`controller/sol_002r/validate_stage2r_controller.py` does not import the
experimenter's analysis. It independently:

- reconstructed all 57 age-80-eligible people and group membership;
- reproduced the 3/22 and 2/35 primary counts;
- reproduced the Newcombe interval algebra;
- reproduced the 50,000-replicate bootstrap interval exactly;
- reproduced both composition and R001 sensitivity counts;
- reconstructed the unrestricted competing-risk records and all six
  Aalen–Johansen readouts/risk sets;
- reproduced all five event ages;
- verified all 86 locked input hashes;
- verified the corrected classification and unrestricted conclusion.

It returned no problems. The experimenter's two independent generation passes
were also byte-identical.

## Additional interval correction

The audit found that the original stale Stage 2 secondary table labeled simple
subtraction of the two Wilson interval endpoints as a “Newcombe score
interval.” That is not Newcombe method 10 and produced the wider
`[-13.9, +31.8]` percentage-point interval previously summarized by the
controller. Stage 2R implements the Newcombe method-10 square-root combination
and independently reproduces `[-7.7, +28.0]`. This correction affects neither
the point estimate nor the `NOT_DETECTED` classification and is recorded as
`DEV-20260723-12`.

## Corrected conclusion

- `PUBLIC FUNCTION: NOT_DETECTED / HIGHER`

This is a weak-data conclusion, not evidence that nothing unusual exists. The
unrestricted point estimates are consistently higher across the three
comparators and include unusually late detected achievements, but only five
people have detected qualifying events, the uncertainty is large, the point
estimate misses the fixed materiality threshold, and ascertainment opportunity
is not equal.
