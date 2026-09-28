# sol_002 Stage 3 independent controller audit

Audit time: 2026-07-23T09:04:03Z

## Result

Pass after the narrow `DEV-20260723-13` repair.

The same memory-disabled external Sol thread performed the labeled post-lock
reconciliation only after the blind Stage 2 conclusion and fresh-context
corrected Stage 2R conclusion were locked. The initial Stage 3 is preserved at
`stage3_pre_controller_repair/`; the canonical repaired result is `stage3/`.

## Independent reconstruction

`controller/sol_002/validate_stage3_controller.py` does not import the
experimenter's Stage 2, Stage 2R, or Stage 3 analysis modules. It independently
verified the archive/reference manifests and rebuilt the key estimands from
the locked person-level CSV/TSV inputs.

It reproduced:

| Quantity | Independent result |
|---|---:|
| Sol people mapped to reference | 95 / 95 |
| Reference-only people | 3 |
| Apollo membership disagreements | 0 |
| Harmonized Apollo / Other 1973 risk sets | 29 / 53 |
| 50-year RMST difference | +0.670028147 years |
| RMST bootstrap 95% interval | -5.088314852 to +6.098816053 |
| Corrected Sol age-80+ detections | 3/22 vs 2/35 |
| Corrected Sol risk difference | +0.079220779 |
| Corrected Sol Newcombe 95% interval | -0.077370641 to +0.280496015 |
| Corrected Sol bootstrap 95% interval | -0.068831169 to +0.244155844 |
| Shared-scope Space Grandpa | 21/22 vs 24/35 |
| Space Grandpa risk difference | +0.268831169 |
| Space Grandpa Newcombe 95% interval | +0.053543512 to +0.438512763 |
| Space Grandpa bootstrap 95% interval | +0.092207792 to +0.440259740 |
| Corrected `OTHER_AVAILABLE` | 54, excluding 12 |
| Post-1973 set identity | 53 vs 53, exact |
| Age-80 set identity | 35 vs 35, exact |

The controller independently reran all three 50,000-replicate stratified
bootstraps with seed 20260721 using only the Python standard library. This
avoids the workspace's architecture-broken NumPy installation.

## Row and definition reconciliation

- The three reference-only people are Alvin S. White, Iven Kincheloe, and
  William Bridgeman. They belong to the reference's broader high-speed-pilot
  scope but did not actually fly the X-15, which Sol required.
- Both constructions contain the same 29 Apollo 7–17 flyers and the same 44
  core NASA non-Apollo people.
- Thirteen apparent program-flag disagreements arise from the reference's
  mutually exclusive source key versus Sol's overlapping X-15, Dyna-Soar, and
  MOL history flags.
- Donn Eisele and Ronald Evans have one-day reference errors resolved by the
  official NASA Astronaut Fact Book. Robert Rushworth has a genuine one-day
  NASA/USAF conflict; the harmonized analysis uses the more specific USAF
  personnel-index date, 1993-03-18.
- Every one of the five strict Sol detections is Space Grandpa positive. Forty
  additional shared age-80 people are positive only under Space Grandpa.
  This is principally a construct/evidence-policy difference, not opposing
  factual evidence.

## `DEV-20260723-13`

The independent audit confirmed that locked Stage 2 violated the frozen
secondary `OTHER_AVAILABLE` definition:

- frozen: `OTHER_ALL` excluding pre-1970 accidental deaths;
- implemented: every usable non-Apollo row.

The locked output therefore used 66 people instead of 54 for the secondary
birth-origin descriptions. Stage 3 now retains all 66 rows in
`OTHER_AVAILABLE_CORRECTION.csv`, explicitly marks the 12 exclusions, and
recomputes KM survival at ages 60, 70, 80, 85, 90, and 95.

All 12 exclusions died before 1970. The corrected set is exactly identical to
`OTHER_ALL` after the 1973 landmark and in the age-80 risk set. No primary
RMST, public-function result, interval, or conclusion changes.

## Integrity and procedural qualifications

- The repaired Stage 3 archive manifest verifies.
- The initial Stage 3 archive and its exact initial action-log state are
  separately preserved and verify.
- Every approved reference source/copy pair matches across all 63 manifest
  rows.
- The blind and corrected conclusion hashes remain
  `727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df`
  and
  `bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600`.
- `DEV-20260723-14` records one transient reference-tree bytecode cache,
  removed by exact path with the reference aggregate restored.
- `DEV-20260723-15` records that the experimenter validator's hard-coded
  neutral-runtime aggregate is not portable across the permanent archive's
  separately manifested generated Stage 2 bytecode. Source/data/results are
  unchanged; the controller validator explicitly handles and independently
  checks both contexts.

## Interpretation

The locked estimand-specific classifications remain:

- survival: `NOT_DETECTED / HIGHER`;
- corrected unrestricted Sol public function: `NOT_DETECTED / HIGHER`.

The reference comparison does, however, reject an endpoint-agnostic reading of
"nothing unusual." Under the broader Space Grandpa proxy on the exact shared
age-80 risk set, Apollo's positive disparity is +26.9 percentage points and
its Newcombe interval excludes zero. That is evidence that the public-vitality
answer is highly sensitive to what counts and how evidence is accepted. Space
Grandpa is not interchangeable with Sol's stricter event rule and neither is
a clinical cognitive measure.

