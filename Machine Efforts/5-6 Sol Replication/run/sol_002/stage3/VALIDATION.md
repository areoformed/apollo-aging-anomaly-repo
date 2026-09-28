# Stage 3 Validation

Overall: **PASS**.

| Check | Result |
|---|---|
| All six locked tree aggregates match pre-analysis baselines | PASS |
| Both locked conclusion hashes match | PASS |
| Every approved reference-manifest file matches | PASS |
| All 95 Sol rows map uniquely | PASS |
| Reference-only rows equal three and Sol-only rows equal zero | PASS |
| Shared Apollo classifications agree | PASS |
| Harmonized shared Other scope equals 66 | PASS |
| 1973 landmark risk sets equal 29 and 53 | PASS |
| Bootstrap uses 50,000 replicates and seed 20260721 | PASS |
| Death-date disagreements equal three | PASS |
| Program representation disagreements equal thirteen | PASS |
| No factual membership disagreement remains | PASS |
| Shared age-80 risk set equals 22 Apollo plus 35 Other | PASS |
| Corrected Sol unrestricted counts equal locked Stage 2R | PASS |
| Every Sol detection is Space Grandpa positive | PASS |
| Public-function crosstab sums to 57 | PASS |
| No stale five-year endpoint appears in harmonized results | PASS |
| Results keep Sol and Space Grandpa endpoint labels separate | PASS |
| No locked file was written by this script | PASS |

The original blind conclusion and corrected conclusion were read and quoted verbatim; neither was regenerated. No rejected five-year public-function estimate was recomputed or presented as primary.

<!-- DEV-20260723-13 START -->
## `DEV-20260723-13` repair checks

| Check | Result |
|---|---|
| Locked Stage 2 erroneous implementation reproduced as 66 usable non-Apollo rows | PASS |
| Frozen `OTHER_AVAILABLE` definition implemented as `other_all == 1` and `pre1970_accidental_death == 0` | PASS |
| Corrected `OTHER_AVAILABLE` count is 54; excluded count is 12 | PASS |
| Corrected and `OTHER_ALL` post-1973 person-ID sets are exactly identical (53 each) | PASS |
| Corrected and `OTHER_ALL` age-80 person-ID sets are exactly identical (35 each) | PASS |
| Corrected birth-origin KM readouts retained at ages 60, 70, 80, 85, 90, and 95 | PASS |
| Existing primary RMST result row preserved at +0.670028147 years | PASS |
| Existing corrected unrestricted Sol public-function result row preserved at +0.079220779 | PASS |
| No primary estimand recomputed by `repair_main` | PASS |
| Both locked conclusions remain hash-identical and verbatim | PASS |
| No browsing occurred during this repair | PASS |

The 1973-landmark RMST is unchanged because the corrected and `OTHER_ALL`
post-landmark person-ID sets are identical. The age-80 public-function analyses
are unchanged because the corresponding age-80 person-ID sets are identical.
<!-- DEV-20260723-13 END -->
