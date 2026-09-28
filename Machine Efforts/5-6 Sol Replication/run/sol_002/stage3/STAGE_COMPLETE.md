# Stage 3 Complete

Status: **COMPLETE**.

## Artifacts

- `stage3/RECONCILIATION.md`
- `stage3/ROW_DIFFERENCES.csv`
- `stage3/HARMONIZED_RESULTS.csv`
- `stage3/CONTAMINATION.md`
- `stage3/STAGE_COMPLETE.md`
- `stage3/SOURCE_LOG.csv`
- `stage3/analysis.py`
- `stage3/validate.py`
- `stage3/VALIDATION.md`
- `stage3/IDENTITY_MAPPING.csv`
- `stage3/PUBLIC_FUNCTION_CROSSTAB.csv`
- `stage3/LOCKED_INPUT_HASHES.csv`
- `stage3/REFERENCE_MANIFEST_VALIDATION.csv`
- `stage3/OTHER_AVAILABLE_CORRECTION.csv`

## Integrity

All locked Stage 1, Stage 1B, Stage 1C, Stage 2, approved reference, and locked Stage 2R trees match their pre-analysis aggregate hashes. `stage2/BLIND_CONCLUSION.md` remains `727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df`; `stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md` remains `bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600`.

## Narrow post-lock answer

The reference comparison **weakens, but does not overturn, the broad locked “no anomaly” conclusion**. The shared-scope 1973-landmark RMST result is effectively unchanged and remains non-material with a null-crossing interval. The operative corrected unrestricted Sol public-function result is also unchanged. However, the broader reference Space Grandpa rule produces a materially larger positive shared-set disparity, showing that the public-function answer is sensitive to endpoint breadth and ascertainment. That broader proxy is not the locked Sol qualifying-function endpoint and is not a clinical cognitive measure.

<!-- DEV-20260723-13 START -->
## Technical correction `DEV-20260723-13`

Locked Stage 2 incorrectly implemented `OTHER_AVAILABLE` as 66 usable non-Apollo people. The frozen secondary-only definition yields 54 people after excluding 12 prespecified pre-1970 accidental deaths. Corrected membership and birth-origin KM readouts are retained in `stage3/OTHER_AVAILABLE_CORRECTION.csv` and `stage3/HARMONIZED_RESULTS.csv`.

Exact person-ID checks show `OTHER_AVAILABLE` and `OTHER_ALL` are identical after the 1973 landmark (53 each) and in the age-80 risk set (35 each). The primary landmark RMST, age-80 public-function analyses, both locked conclusions, and the narrow endpoint-specific Stage 3 interpretation are unchanged. This repair did not browse or rerun a primary estimand.
<!-- DEV-20260723-13 END -->

No locked conclusion was rewritten. No blocking failure remains.
