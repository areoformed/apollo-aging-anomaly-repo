# Stage 2R Validation

Overall validation: **PASS**.

| Check | Result |
|---|---|
| Locked input hashes unchanged before versus after analysis | PASS |
| Independent in-memory regeneration byte-identical | PASS |
| No person-level structural or adjudication validation errors | PASS |
| OTHER_AVAILABLE and OTHER_ALL full-window eligible sets identical | PASS |
| CORE_NASA_NON_APOLLO nested within OTHER_ALL | PASS |
| MILITARY_ONLY nested within OTHER_ALL | PASS |
| Corrected endpoint includes every qualifying function event in the locked age-80-plus evidence window | PASS |
| No age-85 censor used in corrected competing-risk records | PASS |
| Bootstrap specification fixed at 50,000 replicates and seed 20260721 | PASS |
| Earliest/latest plausible-date scenarios do not use age 85 | PASS |

Locked input manifest contains 86 files. SHA-256 values are retained in `LOCKED_INPUT_HASHES.csv`; generated artifact hashes are retained in `OUTPUT_HASHES.csv`.

Eligible analytic population: 57; APOLLO_FLEW: 22; OTHER_ALL: 35.

Deterministic regeneration compares two complete independent analytical/rendering passes from the same locked inputs. Each pass resets the bootstrap generator to the fixed seed. The append-only action log and hand-authored prospective documents are outside that byte comparison.

Validation errors:
- None.
