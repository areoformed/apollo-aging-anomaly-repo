# Referee Report (Re-analysis) — "Apollo Aging Anomaly" under the SuperAger estimand

**Referee:** research-statistician (adversarial pre-publication review, second pass)
**Date:** 2026-06-04
**Mandate change:** The author corrected the estimand. The phenotype is the **SuperAger**
(alive AND cognitively/publicly vital past 80; Harrison/Weintraub et al., JINS 2012), the
80-year line is **principled** (borrowed from that study), and the target is the **RATE of
the SuperAger phenotype in the cohort vs population base rates** (cohort-vs-population
PRIMARY; Apollo-vs-rest SECONDARY). My prior report's "decouple the thresholds / arbitrary
cutpoint / vitality is just ascertainment-confounded longevity" framings are **retracted on
those specific points** and replaced below. The *measurement-asymmetry* and *fragility*
findings from the prior report remain valid and are carried forward as honest uncertainty.
**All work reproducible under `Machine Efforts/Opus 4-8/` (scripts/, outputs/, data/, LOG.md).**

**Hard constraints honored:** POSITIVE claims only — I assert only *observed* vitality
(Space Grandpa = Y) and its improbability; I never impute decline or disease to any named
person (SG=N is treated strictly as "no public evidence," never as "declined"). No false
precision — the vitality measure is flagged as a PUBLIC-EVIDENCE proxy, not a clinical
assessment, every time it meets a clinical/population rate.

---

## VERDICT (one line)

**Supported as a POSITIVE, moderate-strength anomaly — but it lives in COGNITIVE VITALITY
AMONG SURVIVORS, not in survival.** Apollo astronauts who reach old age show visible
cognitive/public vitality at ~95% (21 of 22 survivors-to-80), which exceeds the age-matched
population dementia-free rate (~72% expected; p ≈ 0.006) and exceeds comparable same-era
astronaut cohorts (~67–70%; within-pool permutation p ≈ 0.004). The pure-longevity claim is
**null** between Apollo and same-era flyers and is the generic healthy-selectee effect.

This is **defensible as a positive "NASA should investigate" claim**, stated with the
construct caveat. It is **not** defensible as a precise clinical effect, and it is fragile to
~2 vitality recodings, so it must be presented with its uncertainty visible.

---

## WHAT'S SOLID (load-bearing and correct)

1. **Data integrity / cross-validation.** I rebuilt a clean person-level dataset
   (`data/analysis_dataset.csv`, 98 people) by merging the GPT-5.5 endpoints with the
   enriched "Went to Space" flag. The two independent sources agree perfectly: **0 unmatched
   rows, 0 Space-Grandpa disagreements**. Cohort counts reconcile exactly (Apollo 29 = 24
   lunar + 5 non-lunar; NASA non-Apollo 44 = 31 flew + 13 never; X-15 13 / Dyna-Soar 4 / MOL 8).

2. **Reproduction of the prior baseline.** Every survival number reproduces to 3 decimals
   (Apollo SMR_rate 0.457, integrated-hazard E 50.31, headcount E 20.35, headcount-SMR 1.130).
   The data has not shifted since the prior report.

3. **The corrected estimand is well-posed and the headline phenotype rate is correct.**
   Apollo SuperAgers (reached 80 AND SG=Y) = **21/29 = 72.4% unconditional**, **21/22 = 95.5%
   conditional** on reaching 80 (Clopper-Pearson exact 77.2–99.9%). Confirmed two ways.

4. **The anomaly is APOLLO-SPECIFIC, which is the key positive result.** Under the fair
   age-matched population model, the comparator astronaut groups are *null*
   (NASA-non-Apollo-flew ratio 0.92, p=0.83; GPT available-others ratio 0.87, p=0.94) while
   Apollo is elevated (ratio 1.33, p=0.006). A generic "elite-selection" or "healthy-worker"
   explanation would lift the comparators too — and it does not. This directly answers the
   strongest objection to the prior longevity framing.

5. **Three independent statistical framings converge.** Age-matched population
   Poisson-binomial p=0.0058; within-84-pool permutation (conditional vitality rate) p=0.0037;
   single-anchor exact binomial vs GBD male 90–94 dementia-free p=0.0038. A parametric model,
   a nonparametric permutation, and a fixed-anchor binomial all land at p ≈ 0.004–0.006.

6. **GPT-5.5's run2 longevity×vitality machinery is correct.** My independent
   reimplementation of the joint exact probability reproduces it (e.g., h=1.0/p≈0.95 →
   6.9e-07 vs run2 7.2e-07; h≈0.46/p≈0.95 → 0.114 vs run2 0.106).

7. **The vitality signal is sample-stable across selection groups.** It is *not* an artifact
   of one anomalous subgroup; the strictest, earliest NASA groups — which supplied the lunar
   crews — show the highest conditional vitality (New Nine 6/6, The Fourteen 9/9, both 100%).

---

## THE CORE REFRAME (this replaces the prior "no anomaly" verdict)

The prior report asked "do Apollo astronauts **die less** than expected" and correctly found
that null (count-based, p=0.125; survival indistinguishable from other selected astronauts).
**That finding still holds and is reaffirmed here** (`outputs/rmst_results.csv`,
`G10`/`G12`): RMST(t=90) Apollo − same-era-flyers = **−2.38 y, 95% CI [−7.81, +2.91]** — the
point estimate is even slightly *negative* (Apollo lost Conrad at 69, Swigert 51, Irwin 61,
Roosa 61, Evans 56 early), and the KM curves overlap and cross. The SMR ≈ 0.46 is shared by
*every* selected-astronaut group (`G5`) — the textbook healthy-selectee signature.

**But the SuperAger estimand is a different question:** among those who *do* reach old age,
are they cognitively/publicly vital at an improbable rate? Here Apollo separates sharply from
both the population and the comparator astronauts. **The anomaly is real; it was simply in
the wrong leg in the prior analysis.** Survival is the floor (necessary to be observed at 80);
the surprise is the vitality-given-survival.

---

## FINDINGS (severity-ranked; "severity" here = threat to the POSITIVE claim)

### [STRENGTH-1] The age-matched population comparison is the right primary test and it holds.
A single population anchor is misleading because Apollo's 22 survivors are not all 80–84 —
they span 82–97, concentrated in the 90–94 band (10 of 22), where the population male
dementia-free rate is only **69.7%**. The fair test assigns each survivor the GBD dementia-free
probability for their *observed* age band and sums to an expected SuperAger count
(`scripts/age_matched_anchor.py`): **21 observed vs 15.83 expected, Poisson-binomial
P(X≥21)=0.0058.** Crucially, all 10 of Apollo's 90–94 survivors are SuperAgers against a 70%
population rate, and all 3 of its 95+ survivors against a 51% rate. **Confidence: high that
this is the correct framing; the result is significant.**

### [MAJOR-2] The signal rests entirely on the Space-Grandpa PUBLIC-EVIDENCE proxy; two biases of opposite sign, net unsigned.
Space Grandpa is *visible* late-life activity, not a clinical cognitive assessment. Two biases
operate and must both be stated:
- **Ascertainment bias inflates Apollo:** famous Moon-crews are far more documented than
  obscure pilots. The project's own SG audit says 60% of Y-codings rest on Wikipedia alone,
  and the deep-search effort was applied *only* to upgrade controls — yet the contrast still
  favors Apollo. This pushes the Apollo rate *up*.
- **Construct mismatch deflates Apollo:** the population anchor is *dementia-free* (permissive
  — counts MCI and functional decline as "fine"), whereas SG=Y requires *demonstrated activity*,
  which is arguably a *higher* bar than merely not-demented. Comparing a stricter cohort
  numerator to a looser population denominator makes the test *conservative*.

I cannot sign the net of these. **This is the single most important caveat and it must be in
the prose**: the number is a *public-evidence* anomaly, honestly uncertain in magnitude, which
is exactly why the right ask is "NASA holds the clinical records — they should look,"
**not** "we have measured a clinical effect." **Confidence: certain this asymmetry exists;
the strategic positive framing handles it correctly.**

### [MAJOR-3] Fragility: robust to the age-matching critique and within-pool ascertainment, but breaks at ~2 vitality recodings; the SECONDARY astronaut-vs-astronaut test is fragile.
(`scripts/fragility.py`)
- **Primary (Apollo vs age-matched population):** survives removing **1** vitality assertion
  (p=0.029) but **not 2** (p=0.091). Apollo's Y-codings are mostly strong and specific (dated
  80+ events: Aldrin at the South Pole at 86, Lovell speaking at 89, Stafford's Russian eulogy
  at 88, Haise's autobiography at 88), and its one borderline 80+ case (Mattingly) is already
  coded N — so "remove 2 genuine ones" is fairly hostile. Still, the result is *moderately*,
  not *highly*, robust. Report this.
- **Secondary (Apollo 21/22 vs same-era flyers 16/23, Fisher one-sided):** baseline p=0.027
  but collapses under *any* single plausible perturbation (comparator +2 under-investigated
  controls → p=0.10; Apollo −1 → p=0.077). The weak-evidence Y's the audit flags (Musgrave,
  Lind) are in the *comparator*, so the comparator rate is if anything overstated and the gap
  is conservative — but the astro-vs-astro contrast is not on its own publishable as
  significant. This matches the prior report's fragility finding and is correctly **secondary**.
**Confidence: high. Lead with the population test; present astro-vs-astro as directional support.**

### [MAJOR-4] Multiplicity — pre-specify ONE primary estimand.
The package still contains many researcher degrees of freedom (cohort definitions, anchors,
hazard grids, two runs, SG recoding history). For the corrected claim, **pre-register the
age-matched SuperAger-rate Poisson-binomial test against the GBD male dementia-free anchor as
the single primary estimand**, with the within-pool permutation as the confirmatory robustness
check and everything else (single-anchor table, hazard×vitality grid, astro-vs-astro) as
declared sensitivities. With the primary fixed, the multiplicity objection is contained, and
the primary p ≈ 0.006 (and permutation 0.004) is not the product of cherry-picking — the three
framings agree. **Confidence: high; this is a presentation requirement, not a data problem.**

### [STRENGTH-5] Longevity-leg honesty is a feature, not a bug.
By openly reporting that survival is *not* the anomaly (RMST CI includes 0; SMR is the generic
selectee effect), the piece pre-empts the epidemiologist's strongest attack and isolates the
genuinely novel claim. This is the correct, defensible posture and it is the opposite of the
flattering-framing trap the prior report warned about. Keep it.

### [MINOR-6] Denominator must be stated every time.
Conditional (95.5%, among survivors-to-80) and unconditional (72.4%, among all 29) are *both*
legitimate but answer different questions. The conditional rate is the like-for-like
comparator to population dementia-free-at-80 rates and should be the headline; the unconditional
rate is the joint survival×vitality improbability and belongs in the heatmap framing. Never let
prose slide between them. (`outputs/superager_rates_by_cohort.csv` carries both with CIs.)

### [MINOR-7] Within-pool permutation is the cleanest ascertainment-robust statistic — feature it.
(`scripts/permutation.py`) Because the 84-person comparator pool *also* contains highly
documented figures (Glenn, Carpenter, Cooper, Schirra), the within-pool permutation partially
neutralizes the "fame → documentation" objection: even against other famous astronauts,
Apollo's conditional vitality rate sits above the 99.6th percentile of random draws (p=0.0037).
This is arguably more persuasive to a hostile reader than the population comparison.

### [MINOR-8] Cosmetic data-label split (no effect).
The lunar enriched file labels Apollo Group 5 simply "Group 5" while the non-Apollo file labels
the same men "Group 5 — The Original Nineteen." Combined N = 19 = the true group size. This is a
display artifact in the stratification table only; conclusions unaffected. Worth a one-line clean
before publication for tidiness.

---

## THE FIVE MANDATED BUILDS + EXTENSIONS (all in `outputs/`)

| Build | File(s) | Result |
|---|---|---|
| **G1** birth-year histogram | `G1_birth_year_histogram.*` | Cohort clusters ~1930 (Apollo birth-year IQR 1930–1933). |
| **G2** death-age centrality | `G2_death_age_centrality.*` | Apollo deaths median 86, flyers 85, both right of pop mode ~85 and far right of pop *mean* ~74; 6 Apollo censored at 91–96. |
| **G5** SMR Apollo vs flew (Byar) | `G5_smr_forest.*`, `smr_results.csv` | ALL selected groups SMR ~0.42–0.55 vs gen pop — selectee effect, not Apollo-specific. Byar exact-Poisson CIs. |
| **G10** KM Apollo vs flew | `G10_km_apollo_vs_flew.*` | Curves overlap; Greenwood CIs, at-risk table, censor ticks, RMST@90 Δ=−2.4y. |
| **G12** 4-way KM + RMST | `G12_km_4way.*` | Apollo/flew/never-flew/gen-pop; hazards cross → RMST not log-rank; CIs + at-risk. |
| Vitality permutation | `permutation_*.csv` | S2 cond-rate p=0.0037; S1 count p=0.0106. Positive-rate framing. |
| Hazard×vitality heatmap | `HEAT_*.*`, `heatmap_joint_prob_grid.csv` | Reproduces+extends run2; Apollo observed at the improbable bright edge. |
| SMR visuals G3/G4 | `G5_smr_forest.*` (combined) | Byar CIs; Apollo and non-Apollo both protected vs gen pop. |
| Selection-group strata | `selection_strata_*.csv` | Signal holds across groups; strictest early groups 100%. |
| Olympian comparator | `olympian_comparator_SCOPED_NOT_RUN.md` | DEFERRED — no local data, no web tools; scoped, **not fabricated**. |
| Less-charitable sensitivity | `sensitivity_less_charitable.csv` | Remove Mitchell (lifelong belief, NOT decline) → 20/22, p=0.029, holds. |

---

## DEFERRED / FLAGGED FOR [AUTHOR]'S DECISION

1. **Olympian fitness control — needs primary-source numbers.** No local data and no web
   access here; I refused to transcribe specific SMR/HR figures from memory into a
   publication-gating artifact. If wanted, pull Sarna 1993 / Antero-Jacquemin 2015 directly and
   use them to bound the **longevity** leg only (they reinforce "survival advantage is ordinary
   for elite cohorts"); they **cannot** address the cognitive-vitality leg where the anomaly is.

2. **The vitality proxy.** The honest ceiling on this analysis is the Space-Grandpa proxy.
   If a stronger claim is wanted later, the path is blinded, symmetric re-coding of late-life
   activity with inter-rater reliability — or, better, the strategic ask that NASA examine the
   actual clinical records. I recommend the latter as the frame; the former only tightens the
   public-evidence number, it cannot make it clinical.

3. **Less-charitable version (author's call).** Excluding the one lifelong-fringe-belief
   survivor (Mitchell) leaves the result significant (p=0.029). Presented as a sensitivity, NOT
   a decline marker. Recommend mentioning it pre-emptively so a hostile reader can't wield it.

4. **Pre-registration of the single primary estimand** (age-matched SuperAger-rate
   Poisson-binomial vs GBD dementia-free) before release, to neutralize the multiplicity attack.

---

## WHAT I COULD NOT VERIFY (and what would close it)
- **Underlying biographical facts** (birth/death dates, living status, accident classes): trusted
  the enriched TSVs + the project's fact-audit; not re-sourced against primary records. The
  two independent in-project sources agree perfectly, which is reassuring but not external
  validation.
- **The true clinical cognitive status** of any survivor: deliberately NOT assessed (ethical
  constraint). The claim is, and must remain, about *observable* vitality and its improbability.
- **Age-80-specific US-male SuperAger base rate from HRS-HCAP/NHATS person-level data:** not
  pulled (requires HRS registration; flagged in the reference doc). I used the GBD dementia-free
  age-banded male rates as the best available age-stratified anchor, labeled as a *permissive
  upper bound*. A proper HCAP pull would sharpen — and, because HCAP normal-cognition is
  *stricter* than dementia-free, would likely *strengthen* — the anomaly.

---

## ONE-PARAGRAPH BOTTOM LINE
Under the corrected SuperAger estimand, the anomaly is real but it is not where the prior
analysis looked. Apollo astronauts do **not** outlive other elite same-era astronauts (RMST
difference includes zero; the SMR ≈ 0.46 is the ordinary healthy-selectee effect shared by
every selected group). What is genuinely improbable is that **of the Apollo men who reach old
age, ~95% (21 of 22) remain visibly cognitively and publicly vital** — against an age-matched
population dementia-free expectation near 72% (p ≈ 0.006), against comparable astronaut cohorts
near 67–70% (within-pool permutation p ≈ 0.004), with three independent statistical framings
converging at p ≈ 0.004–0.006 and the signal holding across the strictest selection groups.
The measure is a *public-evidence* proxy, not a clinical one, and it is fragile to about two
re-codings — so the right, defensible posture is exactly the one the author has chosen: a
**positive** claim of improbable observed vitality, stated with its uncertainty, intended to
prompt the one party who holds the actual medical records — NASA — to investigate. Do not
overstate it as a clinical effect; do not bury that it rests on documentation. Framed that way,
it survives a hostile read.
