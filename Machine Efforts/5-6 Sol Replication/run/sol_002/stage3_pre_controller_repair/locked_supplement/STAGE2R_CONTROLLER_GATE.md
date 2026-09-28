# sol_002r corrected Stage 2R controller gate

Gate time: 2026-07-23T06:56:28Z

## Result

Pass. The unrestricted public-function correction is complete and locked.

This is a post-lock endpoint correction, not a retroactively preregistered
result. The original Stage 2 remains preserved and hash-identical. A fresh
memory-disabled Sol thread received only byte-identical locked Stages 1–1C and
the corrected endpoint instructions; it did not receive the original Stage 2
directory, action log, response, estimate, direction, or conclusion.

## Why this branch exists

The frozen protocol mistakenly retained age `[80,85)` as the public-function
primary after the author had rejected that restriction. The evidence search
itself continued through death or 2026-06-01, so all later events were already
locked. Stage 2R changes only the analysis role:

- any qualifying function event at any age 80+ is primary;
- no event is discarded at age 85;
- the complete competing-risk curve and later event ages describe unequal
  opportunity and timing;
- the old five-year quantity is only a subordinate curve readout.

## Corrected result

| Group | Any age-80+ detection | Risk |
|---|---:|---:|
| `APOLLO_FLEW` | 3/22 | 13.6% |
| `OTHER_ALL` | 2/35 | 5.7% |

Apollo minus `OTHER_ALL`:

- unrestricted risk difference: `+7.92` percentage points;
- Newcombe method-10 95% interval: `-7.74` to `+28.05` points;
- stratified 50,000-replicate bootstrap interval: `-6.88` to `+24.42`
  points;
- risk ratio: `2.386`;
- odds ratio: `2.605`;
- Fisher two-sided p-value: `0.364`.

The corrected classification is:

- `PUBLIC FUNCTION: NOT_DETECTED / HIGHER`.

The estimate is positive but below the unchanged ten-point materiality
threshold, and both intervals include zero.

## Later achievement

All five detected event ages now count:

- Apollo: 81.98, 88.43, and 90.64;
- `OTHER_ALL`: 83.59 and 88.62.

Apollo has one detected event in each of `[80,85)`, `[85,90)`, and `[90,95)`.
The age-90.64 event is no longer removed from the primary.

The unrestricted Aalen–Johansen curve is also directionally higher at the
fixed readouts:

| Years after age 80 | Apollo | Other | Difference | Remaining support |
|---:|---:|---:|---:|---:|
| 5 | 4.55% | 2.86% | +1.69 pp | 18 vs 25 |
| 10 | 9.09% | 5.98% | +3.11 pp | 12 vs 11 |
| 15 | 14.09% | 5.98% | +8.11 pp | 2 vs 2 |

The 15-year value has severe tail-support warning and is not treated as strong
evidence.

## Sensitivity and ascertainment

- versus `CORE_NASA_NON_APOLLO`: `+6.49` points;
- versus `MILITARY_ONLY`: `+5.94` points;
- excluding R001: `+3.81` points.

The corrected composition estimates are directionally coherent, unlike the
stale five-year endpoint. But only five people have detected events, and the
R001 sensitivity attenuates the effect.

Apollo also had greater observation opportunity: median potential follow-up
after 80 was 10.62 versus 8.39 years, with somewhat higher documentation
depth. The unrestricted primary intentionally counts all available later
achievement; these differences are therefore disclosed as ascertainment
limitations rather than called adjustment.

## Validation

The fresh analyst:

- attested before data access that no prior project result or hypothesis was in
  context;
- wrote analysis decisions before revealing group outcomes;
- used no web or parent/sibling file;
- left all 86 locked input files unchanged;
- generated two byte-identical analytical passes;
- retained all requested tables, report, figure, decisions, validation,
  contamination assessment, conclusion, and real-clock action log.

The independent controller validator did not import the experimenter's code.
It exactly reproduced the unrestricted counts, point estimate, Newcombe and
bootstrap intervals, composition and R001 counts, six Aalen–Johansen
readouts/risk sets, all five event ages, all 86 hashes, and the classification.
It returned no problems.

## Additional audit correction

`DEV-20260723-12` records that the original stale Stage 2 secondary table
mislabeled subtraction of Wilson endpoints as a Newcombe interval. The
corrected method-10 interval is the one reported here. This changes no point
estimate, sign, or classification.

## Hashes

- corrected endpoint protocol:
  `42d23d1adeac5c44bed08f98a3e35243410dd1e3a902350a692db32921809861`
- fresh launch message:
  `4228a9d18a435ac96a9642027187f6658a544062c0678fb9be7c2ffc4dacaf01`
- complete Stage 2R manifest:
  `4f201770759a29ee3113c159b1a3f1de9f8523915d43c889031b22429c65e64e`
- independent controller audit:
  `e5bff9d1dc0f152e84dadf929927d9f49921b25508763448af2f44b7053fe63c`
- independent controller validator:
  `7443d38382c96bdb8238ffbf2a9de9b2edfe0cac4c13e9db2ae9226f79df7b13`
- corrected report:
  `a9e65fb4b472b186cd7d8f96750dc7b1935ba7f845fc12c261405f624690f415`
- corrected conclusion:
  `bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600`
- fresh final response:
  `e4c3634b37ab2b169f9ebeb13de4517534006fdd2a32f2b4d9087b8d2b678367`

## Runtime usage

The fresh Stage 2R thread used 1,217,669 input tokens, of which 1,121,280 were
cached, plus 40,518 output tokens and 11,514 reasoning-output tokens.

## Decision

Stage 2R passes and is locked. For the author’s intended public-function
question, cite Stage 2R rather than the stale five-year classification. Keep
the original Stage 2 only as the preserved audit trail. Do not begin
reference-dataset reconciliation without explicit authorization.
