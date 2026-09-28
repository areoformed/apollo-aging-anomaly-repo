# Stage 3 Post-lock Reconciliation

This is a labeled reconciliation. It does not edit or replace any locked Stage 1, Stage 1B, Stage 1C, Stage 2, reference-bundle, or Stage 2R correction file. The operative Sol public-function endpoint is the corrected unrestricted any-age-80-plus endpoint; the rejected five-year quantity is retained only in locked audit history and is not recomputed here.

## Executive reconciliation

- **Identity/shared scope:** all 95 Sol people map conservatively to reference rows. The reference has three additional high-speed-pilot rows. There are no Sol-only rows.
- **Apollo:** both constructions contain the same 29 Apollo 7–17 flyers.
- **Primary survival estimand:** on the harmonized shared scope, the 1973-landmark 50-year RMST contrast is **+0.670 years** (95% percentile-bootstrap interval -5.088 to +6.099). This is effectively identical to the locked +0.670-year result and remains far below the fixed 5-year materiality threshold.
- **Operative Sol public-function rule:** 3/22 versus 2/35, risk difference **+7.9 percentage points** (95% Newcombe interval -7.7 to +28.0). This is identical to locked Stage 2R.
- **Reference Space Grandpa rule on the same people:** 21/22 versus 24/35, risk difference **+26.9 percentage points** (95% Newcombe interval +5.4 to +43.9; Fisher p=0.0193).
- **Endpoint cross-tab:** among 57 shared people who reached 80, Sol+/Space-Grandpa+ = 5, Sol+/Space-Grandpa− = 0, Sol−/Space-Grandpa+ = 40, and both negative = 12.

The reference comparison therefore **weakens the broad, endpoint-agnostic “no anomaly” reading but does not overturn either locked estimand-specific classification**. Survival remains `NOT_DETECTED / HIGHER`; the corrected unrestricted Sol public-detection endpoint remains `NOT_DETECTED / HIGHER`. The broader Space Grandpa field produces a materially larger contrast, demonstrating endpoint/ascertainment sensitivity rather than proving that one construct is the other.

## Pass 1 — Definition-level comparison

| Component | Sol locked definition | Reference construction | Reconciliation |
|---|---|---|---|
| Apollo | Physically launched prime crew on Apollo 7–17; Apollo 1, Skylab, and ASTP are not treatment flights. | Rows loaded from lunar and Apollo 7/9 non-lunar enriched files. | Exact same 29 people. |
| NASA boundary | Top-down NASA groups 1–7, including never-flew, resigned, medically disqualified, or preflight-death members; non-Apollo members are comparators. | File-defined `other_core_nasa` set of 44. | Row set agrees exactly, although the archived reference code delegates the boundary to its upstream file instead of restating it. |
| X-15 | Exactly 12 people who actually flew the X-15. | Mutually exclusive `X-15/high-speed pilots` source bucket; reference-wide scope also includes three other high-speed pilots. | Three reference-only rows are definition-only additions. Shared factual X-15 history agrees once overlap is reconstructed. |
| Dyna-Soar | Six selected-to-fly people; Armstrong and Dana excluded as support personnel. | Four rows have the exclusive Dyna-Soar source key; Knight and Thompson are stored under X-15. | Underlying six shared identities agree; exclusive source-key representation loses two overlap flags. |
| MOL | All 17 selected crewmembers, including seven NASA transfers. | Eight rows have the exclusive MOL source key; nine overlapping members are stored in NASA/X-15/Dyna-Soar buckets. | Underlying 17 shared identities agree; source-key representation loses nine overlap flags. |
| Deduplication | One person row with overlapping binary program flags. | One person row with one mutually exclusive primary/source key. | Both deduplicate people, but only Sol preserves all overlaps as flags. |
| `OTHER_ALL` | Non-Apollo union after person-level deduplication. | All rows with reference primary `other`. | 66 versus 69; the three-row difference is the broader high-speed scope. |
| Accidental deaths | External accidental death before 1970, retained in `OTHER_ALL` and flagged. | Same operational date/cause concept; 14 reference rows. | Twelve shared flags agree; two additional flags belong to reference-only Bridgeman and Kincheloe. |
| Backup crews | Recorded as rotations; never an untreated control. | No equivalent analytical field. | Not comparable; no reference contradiction. |
| Public function | Dated, attributable, substantive self-directed activity under frozen tiers/date rules; unrestricted endpoint uses any qualifying event at age 80+. | `Space Grandpa`: publicly documented late-life activity at 80+, assembled through heterogeneous narrative citations. | Related but non-equivalent. Neither field is a clinical cognitive diagnosis. |

Primary roster anchors used for adjudication were already fetched in Stage 1: NASA Apollo missions and astronaut groups, NASA's 12 flown X-15 pilots, Smithsonian/USAF Dyna-Soar histories, and the NRO MOL roster. The reference bundle is approved comparison material, but approval was not treated as factual authority.

## Pass 2 — Row-level reconciliation

### Identity and membership

Exact birth date plus compatible identity mapped 95/95 Sol rows; only the Stafford/Mitchell shared-birthday collision required surname resolution. Name-only fuzzy matching was never used. `IDENTITY_MAPPING.csv` retains every original name and mapping basis.

The reference-only rows are:

1. William Barton Bridgeman — D-558-II high-speed pilot, not an X-15 flown pilot;
2. Alvin Swauger White — XB-70 high-speed pilot, not an X-15 flown pilot;
3. Iven Carl Kincheloe Jr. — selected for X-15 but died before flying it.

These are coherent under the reference's broader `X-15/high-speed` scope and excluded under Sol's fixed actual-X-15-flight rule. They are definition-only differences, not silent omissions. There are **zero factual Apollo/NASA/Dyna-Soar/MOL membership disagreements** after applying the primary rosters.

### Dates and status

Birth dates and 2026-06-01 vital status agree for every shared person. Three death dates differ by one day:

- Donn Eisele: Sol/NASA Fact Book `1987-12-02`; reference `1987-12-01`. Harmonized value: `1987-12-02`.
- Ronald Evans: Sol/NASA Fact Book `1990-04-07`; reference `1990-04-06`. Harmonized value: `1990-04-07`.
- Robert Rushworth: Sol and a NASA page say `1993-03-17`; the USAF personnel index and reference say `1993-03-18`. The more specific USAF personnel record controls, with the one-day official-source conflict retained as uncertainty.

Thus Rushworth's death date is a correction to Sol's prior row, reported only here. Eisele and Evans are corrections to reference rows. None changes landmark eligibility, age-80 eligibility, vital status, or substantive conclusions.

### Program flags

There are 13 shared flag/source-key differences: two X-15, two Dyna-Soar, and nine MOL. Every one arises because the reference assigns one mutually exclusive source key while Sol records overlapping factual history. The reference narrative itself identifies many overlaps. Harmonization retains agreed person membership and does not reinterpret an exclusive source key as a factual zero.

### Public-evidence rows

There are 40 indicator disagreements on the shared age-80 risk set. All five Sol detections are Space Grandpa positive. Forty additional people are Space Grandpa positive but Sol negative. The reference notes span substantive-looking interviews, testimony, piloting, authorship, and roles, but also awards, attendance, ceremonies, generic “active” descriptions, and other evidence that does not alone satisfy the frozen Sol event/date rules. Reference notes do not uniformly retain Sol's event date, precision bounds, directness, source tier, and contemporaneous-participation fields.

Accordingly:

- Space Grandpa positives were not automatically promoted into Sol events.
- Sol negatives were not interpreted as impairment.
- The discrepancy is classified as definition/public-evidence ascertainment unless a row has separately adjudicated factual conflict.
- No endpoint was collapsed into a synthetic consensus label.

`ROW_DIFFERENCES.csv` includes 103 auditable rows: explicit reference-only entries, zero-row sentinels for Sol-only and factual-membership disagreements, all date and flag conflicts, every endpoint disagreement, and exact-agreement rows.

## Pass 3 — Harmonized shared-scope analyses

### Survival

The harmonized rule requires a person to be present in both constructions and classified as Apollo by both or non-Apollo `OTHER_ALL` by both. It yields 29 Apollo and 66 other people before landmarking; 29 and 53 are alive on 1973-01-01. The 50-year RMSTs are 40.567 and 39.897 years.

The harmonized Apollo-minus-other effect is +0.670 years (95% interval -5.088, +6.099). The locked result was +0.670 years (−5.088, +6.099). The tiny numerical change is the Rushworth one-day adjudication. The reference-only Bridgeman and Kincheloe died before the landmark; Alvin White is excluded by shared-scope harmonization. No material survival conclusion changes.

The archived reference's age-30 analysis can be faithfully reproduced on the shared rows and is reported separately, never substituted for RMST:

- Apollo SMR versus the SSA 1930 male table: 0.457275515 (0.303871631, 0.688122468);
- shared Other SMR: 0.704228752 (0.538012330, 0.921796971);
- KM survival to age 80: 0.7586 versus 0.5303; to age 90: 0.4483 versus 0.2640;
- Apollo-versus-other age-origin log-rank p=0.0626.

These quantities show that both occupationally selected groups outlive a general-population table. They are retrospective, use a single 1930 male cohort table for people born across multiple years, and are vulnerable to healthy-selectee and future-membership selection. They do not establish a causal Apollo effect and do not replace the near-zero common-landmark RMST contrast.

### Publicly documented late-life functioning

The same shared age-80 risk set is used for both rules: 22 Apollo and 35 shared Other.

| Rule | Apollo | Shared Other | Apollo-minus-other RD | 95% Newcombe CI |
|---|---:|---:|---:|---:|
| Corrected unrestricted Sol qualifying-function detection | 3/22 | 2/35 | +7.9 pp | -7.7 to +28.0 pp |
| Reference Space Grandpa | 21/22 | 24/35 | +26.9 pp | +5.4 to +43.9 pp |

The full reference result was 21/22 versus 24/36 (+28.8 pp, Fisher p=0.0111). Restricting to shared scope removes Alvin White, a reference-only Space-Grandpa-negative comparator, so the comparator becomes 24/35 and the difference attenuates to +26.9 pp (Fisher p=0.0193). The corrected Sol result is unchanged because every Sol person is shared.

The contrast between +7.9 pp and +26.9 pp is evidence of construct and ascertainment sensitivity. It is not a validation of clinical cognition, and the larger reference quantity is not substituted for the locked Sol endpoint.

## Implementation and analysis differences

- Sol's primary survival estimand is a 1973 common-landmark 50-year RMST difference with stratified bootstrap uncertainty; the reference foregrounds age-origin KM/log-rank, SMR, and simulations.
- The reference analysis date is 2026-06-04; harmonization uses the fixed Sol censor 2026-06-01. No death lies in the three-day gap.
- The reference's primary source key is mutually exclusive; Sol program flags overlap.
- Reference `OTHER_AVAILABLE` removes pre-1970 accidental deaths. Sol's primary comparator is `OTHER_ALL`; after the 1973 landmark, those early accidental deaths are absent by construction.
- The reference age-30 SMR applies one 1930 cohort life table across the entire astronaut birth-year range and uses a log-approximate SMR interval. It is faithfully labeled as reference-style, not treated as Sol's prespecified effect.
- The reference's Fisher test for Space Grandpa and Sol's corrected Newcombe/bootstrap summaries answer different public-evidence questions.

## Corrections to prior constructions

- **Correction to Sol, reported only here:** Robert Rushworth's harmonized death date is 1993-03-18, with an official NASA/USAF one-day conflict retained.
- **Corrections to reference for harmonization:** Donn Eisele is 1987-12-02 and Ronald Evans is 1990-04-07, based on the official NASA Astronaut Fact Book.
- **No Sol membership correction:** the three reference-only people reflect the reference's broader high-speed-pilot definition.
- **No automatic Sol event correction:** Space Grandpa disagreements remain side-by-side endpoint/ascertainment differences.

## Narrow post-lock interpretation

The harmonized comparison leaves the survival classification unchanged and leaves the operative corrected Sol public-function classification unchanged. It weakens only the broad claim that there is no possible descriptive anomaly under any reasonable public-activity construct, because the broader Space Grandpa field shows a larger shared-set difference. The defensible statement is therefore endpoint-specific: **no anomaly is detected by the locked RMST or corrected Sol qualifying-function rules; a broader reference late-life-activity proxy does show a positive disparity that cannot be equated with the Sol endpoint or clinical cognition.**

<!-- DEV-20260723-13 START -->
## Technical post-lock correction — `DEV-20260723-13`

The controller supplied a frozen protocol fact that was unavailable in the neutral runtime: `OTHER_AVAILABLE` is `OTHER_ALL` excluding prespecified pre-1970 accidental deaths. It is a secondary birth-origin description only and is not an intrinsically superior control.

Locked Stage 2 instead implemented `OTHER_AVAILABLE` as every non-Apollo person with usable birth and end-of-follow-up fields (`stage2/analysis.py`, locked line 716). Because all 66 non-Apollo rows were usable, it incorrectly made `OTHER_AVAILABLE` identical to the 66-person `OTHER_ALL` even at birth origin. The frozen rule yields **54 people**, excluding **12** flagged pre-1970 accidental deaths.

The locked secondary files affected by the wrong membership are:

- `stage2/survival_group_summary.csv` (`OTHER_AVAILABLE` group count and dependent summaries);
- `stage2/km_birth_selected_ages.csv` (all six `OTHER_AVAILABLE` readouts);
- `stage2/survival_birth_km.svg` (the `OTHER_AVAILABLE` birth-origin curve);
- `stage2/population_expectation.csv` and the `OTHER_AVAILABLE` population-benchmark row in `stage2/RESULTS_SUMMARY.csv` (both were composed from the wrong 66-person set);
- the corresponding Stage 2 report/code statements that treated the birth-origin set as 66.

Per the controller's narrow repair instruction, Stage 3 recomputed only the corrected group count and retrospective birth-origin KM readouts. The locked Stage 2 files remain unchanged.

| Attained age | Corrected KM | 95% log-log Greenwood CI |
|---:|---:|---:|
| 60 | 0.944444 | 0.837570 to 0.981737 |
| 70 | 0.833333 | 0.704178 to 0.909574 |
| 80 | 0.648148 | 0.505483 to 0.759100 |
| 85 | 0.498084 | 0.358862 to 0.622491 |
| 90 | 0.322646 | 0.201680 to 0.449678 |
| 95 | 0.225852 | 0.113618 to 0.361365 |

`stage3/OTHER_AVAILABLE_CORRECTION.csv` contains all 66 `OTHER_ALL` people, the 12 exclusions, and person-level landmark/age-80 membership checks.

The corrected 54-person `OTHER_AVAILABLE` set and 66-person `OTHER_ALL` set are **not** identical at birth origin. They become exactly identical after the 1973 landmark: both contain the same 53 person IDs because all 12 prespecified accidental exclusions died before 1970. They are also exactly identical in the non-Apollo age-80 risk set: both contain the same 35 person IDs because none of the 12 exclusions reached age 80.

Therefore the locked 1973-landmark Apollo-versus-`OTHER_ALL` RMST and all age-80 public-function analyses are unchanged. No primary estimand was recomputed in this repair; their existing Stage 3 rows were read, hash-protected, and preserved. The endpoint-specific narrow Stage 3 interpretation and both locked conclusions remain verbatim and unchanged.
<!-- DEV-20260723-13 END -->

## Locked conclusions preserved verbatim

`stage2/BLIND_CONCLUSION.md` — SHA-256 `727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df`:

```text
# Blind conclusion

- SURVIVAL: **NOT_DETECTED / HIGHER**
- PUBLIC FUNCTION: **NOT_DETECTED / HIGHER**

**Is there an anomaly?** No prespecified descriptive anomaly is detected.

This conclusion uses the locked 5.0-year survival RMST and 10-percentage-point public-function thresholds. It describes future-selected cohorts and public-evidence detection; it is neither causal nor a clinical cognitive conclusion.
```

`stage3/locked_supplement/stage2r/CORRECTED_CONCLUSION.md` — SHA-256 `bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600`:

```text
# Corrected Stage 2R Conclusion

Corrected `PUBLIC FUNCTION` strength: **NOT_DETECTED**. Direction: **HIGHER**.

Using every locked qualifying event at age 80 or older through death or 2026-06-01, APOLLO_FLEW had 3 detections among 22 eligible people (13.6%), and OTHER_ALL had 2 among 35 (5.7%). The unrestricted Apollo-minus-Other risk difference was 7.9% (95% Newcombe CI -7.7% to 28.0%).

The classification applies the fixed 10-absolute-percentage-point threshold, primary interval rule, and the two explicitly nested composition checks. It describes public-evidence detection, not a clinical measure, latent health state, or survival. `NEITHER_FOUND` is not assigned a health ordering. No event was excluded at age 85, and no original Stage 2 estimate was consulted or used for comparison.
```
