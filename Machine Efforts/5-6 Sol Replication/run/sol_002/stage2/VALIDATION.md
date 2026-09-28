# Stage 2 validation

## Locked-input and join checks

- Stage 1, Stage 1B, and Stage 1C were read only: PASS.
- Locked-file aggregate SHA-256 matches the pre-analysis value `cb4ed5df8f9e99656e06d5d980b46e37eb1fae5756eee0f623a934edd97146a4`: PASS.
- Cohort, worklist, and outcome person IDs join one-to-one: PASS.
- Every locked evidence row joins to a cohort person: PASS.
- APOLLO_FLEW and OTHER_ALL are disjoint: PASS.
- OTHER_ALL equals the frozen union rule restricted to non-Apollo: PASS.
- MILITARY_ONLY equals the union of the three military flags restricted to non-Apollo: PASS.
- OTHER_AVAILABLE and OTHER_ALL have identical post-1973 risk sets: PASS.
- OTHER_AVAILABLE and OTHER_ALL have identical age-80 risk sets: PASS.

## Survival checks

- Primary landmark is exactly 1973-01-01 and includes only people alive then: PASS.
- Death/censor dates do not exceed 2026-06-01: PASS.
- Primary horizon is exactly 50.0 analysis years: PASS.
- RMST uses Kaplan–Meier integration: PASS.
- Each RMST contrast uses stratified resampling within groups, 50000 replicates, seed 20260721, and percentile 2.5/97.5 limits: PASS.
- Cox model contains group plus linear age at landmark and uses Efron ties: PASS.
- Cox convergence flag: PASS.
- Schoenfeld-residual term and global diagnostics are retained: PASS.
- Birth-origin Kaplan–Meier is labeled retrospective and future-flight-selected: PASS.
- Nested composition groups are labeled sensitivities, not replications: PASS.

## Public-function checks

- Eligibility is reaching age 80 by death or censor: PASS.
- Every primary function event is in age [80,85): PASS.
- Death before detected function is competing; administrative/age-85 end is censoring: PASS.
- Every Aalen–Johansen contrast uses stratified resampling, 50000 replicates, seed 20260721, and percentile limits: PASS.
- The R001 exclusion appears only as a technical-deviation sensitivity: PASS.
- Secondary crude group intervals are Clopper–Pearson exact: PASS.
- Risk difference, risk ratio, odds ratio, compatible intervals, and Fisher test are retained: PASS.
- Documentation depth matches raw locked labels and raw source/publisher counts are retained: PASS.
- No analysis conditions on documentation depth: PASS.
- Latent-event bounds are separately labeled as a different question: PASS.
- Boundary-sensitive qualifying events found: 0. Earliest/latest sensitivity is identical by construction.
- Outcome states are mutually exclusive locked labels and temporal sequences are retained: PASS.

## External benchmark and interpretation

- Only official SSA life-table sources were used externally: PASS.
- Exact annual e0 values cover every represented birth year: PASS.
- S80 interpolation uses surrounding official decennial cohort values: PASS.
- External population expectations are labeled nonexchangeable descriptive benchmarks: PASS.
- No prior project result or parent/sibling project data was read: PASS.
- No causal or clinical-cognition claim is made: PASS.
