# Stage 2R corrected public-function endpoint protocol

Status: author-directed post-lock correction under `DEV-20260723-11`.

## Integrity status

The correction restores an author decision that predates launch but was not
encoded in the durable frozen protocol. Because the mismatch was recognized
after the original Stage 2 result was known to the controller, Stage 2R is not
described as preregistered. The original Stage 2 files and conclusion remain
locked and unchanged.

The Stage 2R analyst must be a fresh memory-disabled thread with no access to:

- the original `stage2/` directory or its result;
- a prior project result or reference dataset;
- parent or sibling project directories;
- this conversation, article, hypothesis, or prior numeric summary.

Its neutral workspace contains byte-identical copies of locked `stage1/`,
`stage1b/`, and `stage1c/` only. The stale analysis-role declarations inside
the Stage 1B codebook are superseded only as specified below; all evidence
definitions, event adjudications, dates, source rules, and person-level states
remain locked.

## Corrected question

Among people who reached age 80, does `APOLLO_FLEW` have a different
probability of at least one publicly detected qualifying function event at any
age 80 or older, through death or administrative censoring on 2026-06-01?

This remains a public-evidence detection endpoint, not a clinical measure.

## Primary estimand

The primary endpoint is a person-level indicator of at least one locked
`QUALIFYING_FUNCTION_EVENT` at any age 80+ through death or 2026-06-01.

The primary contrast is:

`risk(APOLLO_FLEW) - risk(OTHER_ALL)`.

Report raw numerator/denominator, Clopper-Pearson group intervals, the risk
difference with Newcombe interval, risk ratio with compatible interval, odds
ratio with conditional exact interval, and Fisher's exact two-sided p-value.
Also give a stratified person-level percentile-bootstrap interval for the risk
difference using 50,000 replicates, seed `20260721`, and the 2.5th/97.5th
percentiles.

Retain the ten-absolute-percentage-point practical threshold so the endpoint
correction does not opportunistically change the materiality bar.

## Unequal opportunity and death

The unrestricted binary endpoint intentionally counts achievements after age
85. It also gives people unequal observable time after age 80. Do not disguise
that limitation.

As a support-aware companion, estimate the complete Aalen-Johansen cumulative
incidence curve from the 80th birthday, using first qualifying function as the
event and death first as a competing event. Administrative end is right
censoring. Retain every event at every age 80+; do not censor at age 85.

Report curve readouts at 5, 10, and 15 years after age 80 with the numbers
still under observation and explicit tail-support warnings. These are
descriptive curve readouts, not eligibility restrictions or substitute
primaries. Retain the old five-year quantity only in this subordinate role.

Describe potential and observed follow-up time after age 80, death, censoring,
documentation depth, substantive-source counts, and independent-publisher
counts by group. Do not condition the endpoint on documentation depth or call
it adjustment.

## Later achievement

Retain a person-level table for every detected function event and report:

- first and latest qualifying-event age;
- latest-event-age distribution among detected people;
- the locked function/impairment temporal sequences;
- detection counts in age bands `[80,85)`, `[85,90)`, `[90,95)`, and `95+`.

Later detected achievement is not discarded. Do not invent an ordinal health
score for people with no detected evidence.

## Sensitivities

- Repeat the unrestricted primary contrast versus
  `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY`. These nested groups are not
  independent replications.
- Verify whether `OTHER_AVAILABLE` and `OTHER_ALL` are identical for the
  full-window eligible set; do not present duplicate results.
- Repeat the unrestricted `APOLLO_FLEW` versus `OTHER_ALL` primary contrast
  with R001 excluded, labeled technical-deviation sensitivity.
- Retain the separately labeled `NEITHER_FOUND` latent-event extremes as a
  different question from observed detection.
- Apply earliest/latest plausible dates for any boundary-sensitive age-80
  eligibility or event-order case. The age-85 boundary no longer determines
  eligibility.

## Classification

Classify corrected public function as `ROBUST`, `SUGGESTIVE`,
`NOT_DETECTED`, or `INDETERMINATE`, with direction `HIGHER`, `LOWER`, or
`UNCERTAIN`.

- `ROBUST`: absolute unrestricted primary risk difference at least 10
  percentage points, its primary 95% interval excludes zero, and neither
  composition sensitivity reverses direction.
- `SUGGESTIVE`: coherent direction and practically material magnitude but
  interval or ascertainment uncertainty remains.
- `NOT_DETECTED`: small, unstable, or sensitivity-explained.
- `INDETERMINATE`: data or provenance failure prevents judgment.

Assign direction from the sign of the unrestricted Apollo-minus-`OTHER_ALL`
primary estimate. Treat negative effects symmetrically.

## Required outputs

- `stage2r/CONTEXT_ATTESTATION.md`, written before any data read;
- `stage2r/ANALYSIS_DECISIONS.md`, written before group models;
- `stage2r/analysis.py`;
- `stage2r/ANALYSIS_REPORT.md`;
- `stage2r/RESULTS_SUMMARY.csv`;
- `stage2r/EVENT_AGE_TABLE.csv`;
- `stage2r/VALIDATION.md`;
- `stage2r/CONTAMINATION.md`;
- `stage2r/CORRECTED_CONCLUSION.md`;
- `stage2r/STAGE_COMPLETE.md`;
- `STAGE2R_ACTION_LOG.md`.

The analyst must use actual UTC clock calls for append-only logging and stop
after Stage 2R.
