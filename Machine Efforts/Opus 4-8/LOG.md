# LOG — Opus 4-8 Referee Re-analysis (SuperAger estimand)

**Analyst:** research-statistician persona (Claude Opus 4.8, 1M ctx)
**Date:** 2026-06-04
**Folder:** `Machine Efforts/Opus 4-8/` — ALL outputs here. Everything else READ-ONLY.

This log records, in order: inputs read, scripts run, outputs produced, and key
decisions/assumptions. Goal: fully reconstructible from this folder alone.

---

## 0. Mandate change since prior referee report (2026-06-04, in project root)

The author  corrected the **estimand**. Definitional corrections I now treat as
the target, then test rigorously:

1. Co-occurrence of longevity + cognitive vitality is the PHENOMENON, not a confound.
   RETRACT prior "decouple the thresholds / nesting" framing. The phenotype IS
   "alive and cognitively intact past 80" = a **SuperAger** (Harrison/Weintraub et al.,
   JINS 2012).
2. The 80-year threshold is PRINCIPLED (borrowed from the SuperAging study), not post-hoc.
   RETRACT the "arbitrary cutpoint" critique for the 80 line specifically.
3. Estimand = **RATE of the SuperAger phenotype in the cohort vs reference base rates**
   (population SuperAger rate from literature + comparator groups). Primary anomaly is
   cohort-vs-population; Apollo-vs-rest secondary.

**Hard ethical constraints (author):**
- POSITIVE CLAIMS ONLY. Never assert/impute/compute disease or decline for any *named*
  individual. Assert only the observable *positive* signal (visible cognitive vitality)
  and its improbability.
- NO FALSE PRECISION. Vitality measure is a PUBLIC-EVIDENCE proxy (Space Grandpa), NOT a
  clinical assessment. Flag the construct asymmetry every time it is compared to a
  clinical/population rate. No spurious decimals; hedge where due.
- "Less charitable" (exclude fringe-belief astronauts) is OPTIONAL, NOT a decline marker;
  mention as a sensitivity only.

---

## 1. Inputs read (read-only source)

### 1a. Persona + prior report
- `<workspace>/.claude/agents/research-statistician.md` — re-adopted persona.
- `../../referee-report-2026-06-04.md` (project root) — my prior report. Central prior
  verdict ("not an anomaly; healthy-selectee effect; vitality ascertainment-confounded")
  is partly RETRACTED per the estimand correction; the *measurement-asymmetry* and
  *fragility* facts remain valid and must still be surfaced as honest uncertainty.

### 1b. House rules
- `Machine Efforts/AGENTS.md` — `Human Efforts/` is OFF-LIMITS (do not read/write/use).
  I have not touched `Human Efforts/`.

### 1c. Cohort data (enriched TSVs)
- `.../Final - Analysis - Enriched Datasets/07E-lunar-enriched.tsv` — 24 rows (Apollo lunar).
- `.../08E-non-lunar-apollo-enriched.tsv` — 5 rows (Apollo 7/9 non-lunar). Apollo total = 29.
- `.../03E-non-apollo-enriched.tsv` — 44 rows (core NASA non-Apollo; 31 flew / 13 never flew).
- `.../09-x15-pilots-enriched.tsv` — 13 rows (X-15/high-speed). 7 flagged "Went to Space"=Y
  (X-15 >80km wings): Adams, Dana, Knight, McKay, Rushworth, Walker, R.M.White.
- `.../10-dyna-soar-pilots-enriched.tsv` — 4 rows. None flew in space (program cancelled).
- `.../11-mol-full-enriched.tsv` — 8 rows (MOL-only, never transferred). None flew as MOL.
  (MOL men who flew transferred to NASA Group 7 and appear inside 03E.)
- Column schema (23 cols): Name, Astronaut Group, DoB, DoSel, AgeSel, **Went to Space(6)**,
  Moonwalker, Missions, NFlights, TimeInSpace, DoD, CurAge/AgeDeath(12), Status(13),
  **Accidental Death(14)**, Mort note(15), **Space Grandpa(16)**, SG Citation(17), ...

### 1d. GPT-5.5 processed person-level data
- `../GPT 5-5/outputs/.../2026-06-04/person_level_analysis.csv` — 98 people, 16 cols.
  Columns incl: endpoint_age, deceased, accidental_death, pre1970_accidental_death,
  included_in_apollo_vs_other_available, reached_80, reached_90, space_grandpa, cause_note.
  98 = 29 Apollo + 44 core-NASA-non-Apollo + 13 X-15 + 4 Dyna-Soar + 8 MOL. Reconciled.
  NOTE: this CSV has NO explicit flew-in-space flag — must merge from enriched `Went to Space`.
- `.../kaplan_meier_points.csv`, `smr_summary.csv` (trusted as cross-checks; will reproduce).
- run2 grid (`.../_run2/`): the longevity×vitality probability machinery already exists
  (`run2_group29_report.md`, `simple_80plus_vitality_grid/`, `simple_80plus_mhas16_vitality_grid/`).
  I will VERIFY + extend + reframe (the run2 P(long+vital) bundles longevity & vitality at
  the cohort level; the corrected estimand wants person-level phenotype RATE vs base rate).

### 1e. Population SuperAger / vitality reference (the linchpin for the new estimand)
- `../GPT 5-5/research/mental-vitality-medical-data-2026-06-04/mental_vitality_medical_data_findings.md`
  Key population base rates extracted (with construct labels + uncertainty):
  - **GBD/Cao 2024 male dementia-FREE by age band (2020), eTable 4** (cleanest age-stratified):
    80-84: 86.6% (86.0-87.2) | 85-89: 79.1% (78.3-79.9) | 90-94: 69.7% (68.5-70.8) |
    95+: 50.7% (48.8-52.5). [dementia-free is PERMISSIVE: still includes MCI/functional loss]
  - **HRS-HCAP 2016**: dementia 10% (9-11), MCI 22% (20-24) among 65+ -> ~68% normal
    cognition at 65+. NOT age-80-specific; optimistic for 80+.
  - **Campos 2024 (ScienceDirect)**: 64.8% "no poor MMSE" among 80-94 (n=165; NOT
    US-representative, mostly female, low education).
  - **MHAS**: 54/334 = 16.17% "youthful cognition" 80+ — USER-SUPPLIED, strict lower bound,
    NOT reproduced from microdata.
  - Reference EXPLICITLY warns: Space Grandpa (public activity) != clinical cognition;
    proper age-80 rates need HRS-HCAP/NHATS person-level pulls (NOT done). MUST flag asymmetry.
  - `extracted/pmc11336039_cao2024_supplement_forecast_tables.csv` — GBD source for the above.

### 1f. SG (vitality proxy) audit
- `.../data/SG-audit-summary.md` — 73 NASA pre-1970 selected; 50 reached 80+ (40 Y / 10 N).
  Known asymmetry: 60% of Y rest on Wikipedia only; famous lunar astronauts well-documented;
  Phase-5 deep search applied ONLY to upgrade controls (favors controls, yet contrast still
  favors Apollo). Weak-evidence Y: Musgrave, Lind. Under-investigated living N: Holmquest,
  Parker. This asymmetry is the core honest-uncertainty caveat on the vitality proxy.

---

## 2. Reproduction environment
- Python 3.13.5; numpy 2.4.4; scipy 1.17.1; pandas 2.3.3; lifelines 0.30.3; matplotlib 3.10.8.
- Matches prior referee report environment. SSA life table verified clean (l(x+1)=l(x)-d(x)).

## 2b. Scripts run (in order) + key outputs

1. `scripts/build_dataset.py` -> `data/analysis_dataset.csv` (98 rows, 26 cols).
   Merged GPT-5.5 person-CSV with enriched "Went to Space" flag. INTEGRITY: 0 unmatched,
   0 SG disagreements between the two independent sources (cross-validation passes).
   Apollo: N=29, reached80=22, SuperAgers=21. Cohort counts reconcile to 29/44/13/8/4.

2. `scripts/superager_rates.py` -> superager_rates_by_cohort.csv, _population_anchors.csv,
   _rate_comparison.csv, g1_birth_year_data.csv.
   KEY: Apollo conditional SuperAger rate (SA among 80+ survivors) = 21/22 = 95.5%
   [Clopper-Pearson 77.2-99.9]; unconditional 21/29 = 72.4%.
   Comparators: NASA non-Apollo flew 16/23 = 69.6%; GPT available-others 24/36 = 66.7%.
   vs SINGLE population anchors (cross-construct): not sig vs 80-84 dementia-free (86.6%,
   p=0.19) but sig vs 85-89 (79.1%, p=0.039), 90-94 (69.7%, p=0.0038), HCAP-normal-cog
   (68%, p=0.0024). ANCHOR CHOICE IS LOAD-BEARING -> motivated age-matched anchor next.

3. `scripts/age_matched_anchor.py` -> age_matched_anchor_detail.csv, _summary.csv.
   THE FAIR COMPARISON. Each Apollo survivor assigned GBD male dementia-free prob at their
   OBSERVED age band; Poisson-binomial exact tail.
   APOLLO: 21 observed SuperAgers vs 15.83 expected (pop dementia-free), ratio 1.33,
   P(X>=21)=0.0058. SIGNIFICANT and survives age-matching (Apollo survivors concentrate in
   90-94 band where pop rate is only 69.7%, yet 10/10 are SuperAgers).
   NASA non-Apollo flew: 16 obs vs 17.44 exp, ratio 0.92, p=0.83 -> NULL.
   GPT available-others: 24 obs vs 27.45 exp, ratio 0.87, p=0.94 -> NULL.
   => SuperAger-rate anomaly is APOLLO-SPECIFIC, not a generic selection artifact.

4. `scripts/smr_km_rmst.py` -> smr_results.csv, km_survival_readouts.csv, rmst_results.csv,
   km_points_*.csv. REPRODUCES prior baseline exactly (Apollo SMR_rate 0.457, E_haz 50.31,
   E_head 20.35, SMR_head 1.130 -> data stable).
   LONGEVITY LEG IS NULL between Apollo and same-era flyers: KM curves overlap
   (Apollo S80=0.759 vs flew 0.793; S90=0.448 vs 0.434); RMST diff at t=90 = -2.38y
   [-7.81,+2.91] (Apollo slightly lower, CI incl 0). SMR_rate ~0.42-0.55 for ALL selected
   groups (healthy-selectee effect, NOT Apollo-specific). Hazards cross -> used RMST not log-rank.
   CONCLUSION: the anomaly is NOT in survival; it is in VITALITY-AMONG-SURVIVORS.

## 2c. Decisions added during analysis
- **D5 The anomaly is cognitive-vitality-conditional-on-survival, NOT a survival anomaly.**
  Pure-mortality comparison Apollo vs same-era flyers is null (RMST CI includes 0; KM overlap).
  This CONFIRMS prior report's FATAL-1 (longevity vs general pop = selectee effect) and is
  consistent with the corrected estimand: the SuperAger signal is the vitality rate among
  those who reach old age, where Apollo (95.5%) exceeds both population (age-matched p=0.006)
  and comparator astronauts (null). Reframe accordingly. POSITIVE claim only.
- **D6 Anchor choice is load-bearing -> age-matched Poisson-binomial is the primary fair test;**
  single-anchor table retained as sensitivity showing the range.

5. `scripts/fragility.py` -> fragility_age_matched.csv, fragility_apollo_vs_comparator.csv.
   (A) Apollo vs age-matched pop: survives removing 1 vitality assertion (p=0.029), NOT 2
   (p=0.091). (B) Apollo vs comparator astronauts (secondary): baseline p=0.027 but breaks
   under any single hostile perturbation (comparator +2 -> p=0.10; Apollo -1 -> p=0.077).
   => PRIMARY (pop) test moderately robust; SECONDARY (astro-v-astro) test fragile.
   Apollo's Y-codings are STRONG/specific (dated 80+ events); the weak-evidence Y's
   (Musgrave, Lind) are in the COMPARATOR, so comparator vitality is if anything OVERstated
   -> the gap is conservative. Apollo's one borderline 80+ case (Mattingly) is already coded N.

6. `scripts/permutation.py` -> permutation_summary.csv, permutation_null_S1/S2.csv.
   84-pool, 200k draws of size 29. S1 (SuperAger count of 29): obs 21, null mean 15.5,
   perm p=0.0106. S2 (cond vitality rate among 80+ survivors = corrected estimand): obs
   95.5%, null mean 77.6%, perm p=0.0037. Within-pool framing partially neutralizes the
   ascertainment-bias objection (comparator also contains famous figures: Glenn, Carpenter...).

7. `scripts/selection_strata.py` -> selection_strata_all_nasa.csv, selection_strata_apollo.csv.
   SAMPLE-STABILITY: vitality signal is NOT driven by one subgroup. Apollo by selection group
   (conditional SuperAger rate): New Nine 6/6=100%, The Fourteen 9/9=100%, Group 5 4/5=80%,
   Mercury 1/1, Scientists 1/1. Strictest/earliest groups (which supplied the lunar crews)
   show PERFECT vitality among survivors. The obscure latest group (MOL Transfer, all-NASA
   table) shows 20% = ascertainment-bias prediction. DATA NOTE: "Group 5" and "The Original
   Nineteen" are the SAME NASA Group 5 (lunar file labels it "Group 5"; non-Apollo file
   labels it "Group 5 — The Original Nineteen"); combined N=19 = real group size. Cosmetic
   label split only; no effect on conclusions.

8. `scripts/figures.py` -> G1,G2,G5,G10,G12,SARATE,HEAT (.svg+.png) + heatmap_joint_prob_grid.csv,
   km_points_*.csv, km_survival_readouts.csv. All KMs: Greenwood CI + at-risk tables +
   censoring ticks + delayed entry at 30. G12 hazards cross -> RMST annotated, NOT log-rank.
   HEAT independently reimplements run2's joint-probability machinery and REPRODUCES it
   (my h=1.0/p=0.95 -> 6.94e-07 vs run2 h=1.0/p=0.955 -> 7.22e-07; my h=0.45/p=0.95 -> 0.114
   vs run2 h=0.457/p=0.955 -> 0.106). [FIXED a y-axis orientation bug in the heatmap: hs runs
   descending, needed Z flipped for origin="lower"; corrected, Apollo star now at bottom-right.]

## 2d. Sensitivities (author-decision items, NOT decline markers)
- `outputs/sensitivity_less_charitable.csv`: removing Edgar Mitchell (the one Apollo 80+
  astronaut with LIFELONG fringe ESP/noetic beliefs — NOT late-life change) from the
  vitality numerator gives 20/22=90.9%, age-matched p=0.029 — still significant. This is the
  OPTIONAL "less charitable" version; presented as a robustness point only. Explicitly NOT a
  decline imputation. O'Leary (other fringe case) died at 71, not in the 80+ set.
- `outputs/olympian_comparator_SCOPED_NOT_RUN.md`: Olympian fitness-control DEFERRED. No
  browser tools; no local Olympian mortality data (searched). Did NOT fabricate. Scoped:
  Olympian data could bound the LONGEVITY leg only (and would reinforce "survival advantage
  is ordinary for elite-selected"), and structurally CANNOT speak to the cognitive-vitality
  leg where the anomaly lives.

## 3b. CONVERGENCE (three independent framings of the Apollo SuperAger anomaly)
- Age-matched population Poisson-binomial (GBD dementia-free):  p = 0.0058
- Within-84-pool permutation, conditional vitality rate (S2):   p = 0.0037
- Single-anchor exact binomial vs GBD male 90-94 dementia-free:  p = 0.0038
All land at p ~ 0.004-0.006. The convergence across a parametric population model, a
nonparametric within-pool permutation, and a single fixed-anchor binomial is reassuring.

## 4. Bottom line recorded here for reconstructibility
- The anomaly is NOT in survival (Apollo vs same-era flyers RMST diff includes 0; KM overlap;
  SMR ~0.46 is the generic healthy-selectee effect shared by ALL selected groups).
- The anomaly IS in COGNITIVE/PUBLIC VITALITY AMONG SURVIVORS: Apollo 95.5% (21/22) vs
  age-matched population ~72% expected (p~0.006) and vs comparator astronauts ~67-70% (p~0.004
  within-pool). Apollo-specific (comparators are null vs population).
- Strength: MODERATE positive signal. Robust to the age-matching critique, multiplicity
  (primary estimand pre-specifiable), and within-pool ascertainment (permutation). FRAGILE to
  ~2 vitality recodings and weak on the secondary astro-v-astro test. The vitality proxy is
  PUBLIC-EVIDENCE, not clinical: ascertainment bias (fame->documentation) inflates; construct
  mismatch (visible-activity is arguably STRICTER than dementia-free) deflates; net sign of
  these two biases is UNSIGNED. State honestly. Defensible as a positive, NASA-should-look
  claim; NOT defensible as a precise clinical effect.

---

## 3. Decisions / assumptions (key)

- **D1 SuperAger phenotype operationalization.** SuperAger = reached age 80 AND Space Grandpa=Y
  (visible cognitive/public vitality at 80+). SG is the only available person-level vitality
  proxy in the data. It is a PUBLIC-EVIDENCE proxy, not clinical — every cohort-vs-population
  comparison flags this asymmetry explicitly. POSITIVE direction only: SG=Y asserts *observed*
  vitality; SG=N asserts only *absence of public evidence*, NOT decline.

- **D2 Two denominators reported, never conflated.**
  (i) CONDITIONAL rate = SuperAgers / survivors-to-80 (comparable to dementia-free-at-80
      population rates).
  (ii) UNCONDITIONAL rate = SuperAgers / cohort-at-selection (compounds survival x vitality;
      this is the joint improbability the run2 grid targets).

- **D3 "flew-in-space" definition fork (G5/G10/G12).** Orchestrator's named comparators
  (McCandless, Crippen, Truly, Young) are NASA Group-5/7 Shuttle flyers -> intended comparator
  is NASA astronauts who flew. X-15 pilots who earned >80km wings are a *separate* fork.
  PRIMARY flew-restricted cohort = NASA pre-1970 non-Apollo who went to space (03E Went=Y).
  SENSITIVITY: add X-15 "flew" pilots. Document both; do not silently pick one.
  Accidents EXCLUDED astronaut-vs-astronaut UNLESS post-Apollo (per mandate); operationalized
  via pre1970_accidental_death flag (= exclude) but KEEP post-Apollo accidents (Anders 2024,
  Overmyer 1996, etc.).

- **D4 GBD dementia-free as the primary population anchor** for the SuperAger rate, because
  it is the only source with male + age-80+-stratified granularity. Treated as an UPPER bound
  on true cognitive vitality (permissive). Report the range across all four anchors; never a
  single false-precision number.
