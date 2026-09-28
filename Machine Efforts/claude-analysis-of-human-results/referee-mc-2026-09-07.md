# Referee report — Apollo Monte Carlo (`astro-game2.c`, 1,000,000 rounds)

**Commissioned:** 2026-09-07 ~01:15 PDT, by Claude on [AUTHOR]'s behalf — adversarial pass before any Monte Carlo number enters the Apollo aging-anomaly piece. **Referee:** research-statistician (Fable 5.1). **Written:** 2026-09-07 ~01:35 PDT (wording tightened ~01:45).

**Read (read-only, Human Efforts untouched — mtimes verified before and after):** `Human Efforts/scripts/Astronaut MC/` — `astro-game2.c`, `astroOnp.h`, `apolloData.h`, `nasaNonApolloAstroPre1970.h`, `1930CohortSSAData.h`, `nasaAstroStructDefv2.h`, both v2 generator scripts, `astronaut-monte-carlo-results.tsv` (all 1,000,000 rows); `Astronaut MR /smr.c`; her manual TSVs (`Manually Compiled Data/Apollo Astronaut Data/*.tsv`) for the Space-Grandpa and selection-year columns; the SSA source (`Actuarial Study 120/CohLifeTables_M_Alt2_TR2024.csv`); `03E-non-apollo-enriched.tsv` for astronaut groups; `apollo_mc_smr_histogram.py` and both SVGs.

**Run (everything under `claude-analysis-of-human-results/_referee_scratch/`):** `referee_check.py` — my own line-based parser of the .h files, recompute of the real-Apollo numbers, TSV percentiles with point masses, closed-form hypergeometric comparison, conditional vitality test, Byar/Garwood intervals, E-sensitivities against the TR2024 CSV (outputs in `check.out`, `extras.out`, `groups15.out`). `referee_mc.py` — an independent 1,000,000-round MC in numpy (PCG64, direct 29-subset sampling), four sensitivity variants (`mc.out`). `repro/` — her six source files copied verbatim, only the seed line and `runSize` edited, rebuilt with `cc -Wall` (Apple clang 17, macOS 15.7), run at the recorded seed and at two fresh seeds. The figure script was rerun in place and diffed against a snapshot (`svg_snapshot/`).

---

## Summary — most severe first

1. **Nothing in this Monte Carlo supports "Apollo aged unusually well."** All four statistics sit in the body of the null: SMR at the 42.6th percentile (two-sided p = 0.85); hit-80 count, P(≥ 22) = 0.69; space-grandpa count, P(≥ 19) = 0.22; median attained age, P(≥ 88) = 0.37. The MC's honest result is a null — and it is a useful one (item 4).
2. **[MUST-FIX — a wrong number in the deliverable]** The one figure that looked like evidence — *"9.9% of synthetic cohorts have more"* grandpas, i.e. "top 10%" — is a tail-convention error. 9.85% is P(X > 19). A permutation p-value includes the observed value: **P(X ≥ 19) = 21.8%** (exact hypergeometric: 21.72%). The same error makes median age look "top 7%": P(> 88) = 7.0%, but **P(≥ 88) = 36.9%** (30% of decks tie at 88). Both count statistics have closed forms; the MC only approximates them.
3. **[MUST-FIX — a claim in the piece, not a bug in this code]** Under her own hand-coded Space-Grandpa column (Apollo 19/22; Mitchell, Mattingly, Cunningham = X), the vitality-given-survival result is **not significant against the 65-pool comparator (19/28 = 68%; Fisher p = 0.117, MC conditional 11.7%) and vanishes against the like-for-like comparator** — non-Apollo survivors from the same selection groups as Apollo (Groups 1–5, 18 people): **13/15 = 86.7% vs Apollo 86.4%, p = 0.69.** The whole 65-pool gap is carried by Groups 6–7 (XS-11 scientists + MOL transfers: 6/13 = 46%) — a younger group, several of whom left NASA early or never flew, whose documentation depth varies widely. This is the documentation-depth confound the blind replication already found, now visible in her own data.
4. **The defensible reading of the SMR histogram is that low mortality belongs to the corps, not to Apollo.** Every one of the 1,000,000 synthetic cohorts has SMR < 1 (max 0.949); the whole 65-person pool sits at SMR 0.50 (Byar 95% CI 0.37–0.67). That is the healthy-selectee effect, and it is the sentence the piece can defend.
5. **The implementation is correct and reproducible.** Real-Apollo numbers reproduced exactly from the .h files by my own parser (O = 23, E = 46.895698, SMR = 0.490450, hit-80 = 22, grandpas = 19, median 88). The shuffle-and-skip samples a uniform 29-subset of the 65 non-accident astronauts (MC count distributions match the closed form bin-for-bin; χ² p = 0.34 and 0.47). Her binary rebuilt with the recorded seed regenerates the TSV rows byte-for-byte (checked on the first 3,000); at two fresh seeds it gives 42.53% / 42.47%; my numpy MC gives 42.48% / 42.54% — so 42.64% is a +2σ draw of that seed and **"≈ 42.5%" is the number.** Sensitivities (per-birth-cohort tables, immortal-time truncation, Groups 1–5 pool) move the percentile between 38.6% and 52.7%. Nothing changes.

No fatal defect in the code. Both must-fix items are about what gets claimed.

---

## Findings, ranked

### F1 · [MUST-FIX] Tail convention on the count statistics — Q6, figure annotation
- **What's wrong.** `mc_grandpa_histogram.svg` annotates *"9.9% of synthetic cohorts have more."* Literally true, but it reads as a p-value and it is the wrong one. The permutation p-value for "Apollo has at least as many grandpas as observed" is P(X ≥ 19), which includes the 11.9% point mass at 19: **21.8%** (her TSV) / **21.72%** (exact). Median age: P(≥ 88) = 36.9%, not 7%. Hit-80: P(≥ 22) = 68.6%.
- **Why it matters.** "Top ~10%" and "top ~7%" are the only MC numbers that could be read as evidence for the anomaly, and both are artifacts of excluding the observed value. Any hostile reader with the TSV finds this in a minute.
- **Closed form (no MC needed).** Pool of 65 non-accident astronauts: 38 grandpas, 50 reached 80, 49 dead. Grandpa count ~ Hypergeometric(N=65, K=38, n=29): mean 16.95; P(≥19) = 0.2172, P(≥20) = 0.0983. Hit-80 ~ Hypergeometric(65, 50, 29): mean 22.31; P(≥22) = 0.6849. MC vs exact, bin by bin: grandpa χ² = 17.7 on 16 df (p = 0.34); hit-80 χ² = 13.7 on 14 df (p = 0.47) — the MC is a faithful sampler of the null.
- **Fix.** Annotate *"22% of synthetic cohorts have 19 or more"*; use ≥ throughout the writeup; cite the hypergeometric for the two counts and keep the MC for the SMR and median (which have no closed form).

### F2 · [MUST-FIX — for the piece's headline] Vitality-given-survival does not survive her own coding or the like-for-like comparator — Q6, Q8
- **Provenance first.** The `spaceGrandpa` flag comes from her manual TSV (`Lunar Astronauts-Apollo Astronauts.tsv`, `Non-Lunar…LEO-Only Apollo.tsv`, May 22 2026; column "Space Grandpa?": Y / X / NA). Apollo = **19 Y, 3 X (Mitchell, Mattingly, Cunningham), 7 NA (did not reach 80)**. Three coders, three sets (all checked at source): the V2 machine coding (`Opus 4-8/data/analysis_dataset.csv`, `space_grandpa`) has **21/22, Mattingly the single N**; hers has **19/22** (Mattingly plus Mitchell and Cunningham = X); the July blind run has **19/22** (Scott and Young dropped for lack of in-window evidence). The three agree only on Mattingly; a coding that honours every X any coder assigned gives 17/22. The non-Apollo flags come from the Opus/GPT enriched dataset, spot-checked by her — and her own generator comment rates that file's confidence as "low / lower than the other ones."
- **The numbers under her coding.**
  | comparator | grandpa / reached-80 | rate | one-sided Fisher p (Apollo ≥ 19 of 22) |
  |---|---|---|---|
  | Apollo 29 | 19 / 22 | 86.4% | — |
  | all other survivors in the 65 pool (Groups 1–7) | 19 / 28 | 67.9% | **0.117** (MC, conditional on h = 22: 11.7%) |
  | other survivors, **Groups 1–5 only** (like-for-like) | 13 / 15 | 86.7% | **0.688** (MC: 68.9%) |
  | Groups 6–7 alone (XS-11 + MOL transfers) | 6 / 13 | 46.2% | — |
- **Why the gap collapses — and the comparator's composition, stated plainly.** Groups 2 and 3 contribute *no* non-Apollo survivors (everyone from the New Nine and the Fourteen who survived the 1960s flew Apollo), so the 18 like-for-like comparators are Groups 1, 4 and 5: the Mercury Seven survivors (Carpenter, Glenn = Y; Cooper, Slayton < 80), the Group 4 scientists (Garriott, Gibson, Kerwin, Michel, Graveline — all Y; five of the 18, versus one scientist, Schmitt, among Apollo's 29), and the Group 5 pilots who flew Skylab/ASTP/Shuttle instead (Brand, Carr, Engle, Lind, Lousma, Pogue = Y; McCandless, Weitz = X; Bull < 80). These are well-documented careers. The Group 6–7 members (born 1926–1942; several left NASA early or never flew; documentation depth varies from Crippen and Truly to men with a paragraph) are where the X's cluster. Whether that is cognition or documentation, the data cannot say — which is precisely the point the blind replication made. Comparator-dependence *is* the finding.
- **Mortality is unaffected by the same restriction:** Apollo SMR 0.490 vs Groups 1–5 others 0.482 (ratio 1.02); MC percentile within the Groups 1–5 pool = 52.7%.
- **Fix.** If the piece keeps any vitality claim it must (a) print the 19/22, the 13/15 and the 19/28 side by side with their p-values, (b) say the comparator-dependence out loud, and (c) lead with "NASA holds the clinical records — someone should look," not "we measured an effect." The bare "p ≈ 0.006" from the 21/22 coding cannot appear without the coder-dependence stated. (The 72% population base rate used earlier is from the June referee record; I did not re-verify it tonight.)

### F3 · [SHOULD-FIX — framing] What the MC tests, and what it cannot — Q2
- **The null it samples.** A uniform random permutation of 73, restricted to the 65 with `trainAcc == false`, is a uniform random permutation of those 65; the first 29 of it is a uniform 29-subset. So the MC is a **permutation (randomization) test of the exchangeability hypothesis: "which 29 of the 65 survivors got Apollo seats is unrelated to their subsequent mortality."** Including the real 29 in the pool is not a bias — it is the null. A random deck shares Hypergeometric(65, 29, 29) members with the real one (mean 12.9); that overlap is the structure of every permutation test, and "draw from the 36 others only" would answer a different question (whose permutation null is, in any case, the same relabeling).
- **The right summary.** One-sided 42.6% (→ two-sided p = 2·min(0.426, 0.574) = 0.85). MC precision: SE = √(0.43·0.57/10⁶) = 0.05 percentage points; five independent million-round runs (three of her binary, two of mine) span 42.47–42.64%. A million rounds is far more than needed; C(65,29) ≈ 1.6×10¹⁸ is irrelevant because the MC estimates a tail probability, it does not enumerate.
- **Two questions, keep them apart in the text.** (1) *Is Apollo unusual within the corps?* — permutation; this MC; answer no. (2) *Is the corps' mortality below the general population's?* — a Poisson question on fixed O: Apollo 0.490, Byar 95% CI [0.311, 0.736] (exact Garwood identical to three decimals); non-Apollo-36 0.515 [0.336, 0.754]; pool-65 0.503 [0.372, 0.665]. The MC cannot speak to (2)'s uncertainty because under its null every death is fixed — the deck-to-deck SD of 0.070 is relabeling variance, not sampling variance, and must not be drawn as an error bar against 1.0. The support of the null is [0.197, 1.384] (all 16 living + 13 longest-lived dead; the 29 earliest deaths) — the MC sampled 0.252–0.949 because the extremes are astronomically improbable.
- **What (2) actually measures.** Reference = US **male, all races**, 1930 birth cohort, SSA Actuarial Study 120, 2024 Trustees Report Alternative 2 — cohort tables, historical through ~2022 and *projected* beyond — projection is by calendar year, so the last one to four years of reference hazard for the ~12 most recent Apollo exits (six deaths 2023–2025, six living) are model-based (Alternative 2). The cohort is white, college-educated, military officers; against a white-male or officer reference the SMR would be higher. SMR 0.49 is the healthy-selectee/SES gap. It says nothing about spaceflight.

### F4 · [SHOULD-FIX — sensitivity, small] The expected-deaths construction — Q1
- **What it is.** E = Σᵢ −ln(l(aᵢ)/l(30)) = Σᵢ ∫₃₀^{aᵢ} h_ref(t) dt: each person's cumulative reference hazard over their at-risk window [30, exit). O/E is the indirectly standardized SMR on person-time. Valid. E > n is expected once survivors are followed past the age where reference cumulative hazard exceeds 1.
- **Living members.** Handled correctly: administrative censoring at the 2026 epoch; they contribute ∫₃₀^{2026−b} h dt and no event. Non-informative censoring holds (a calendar date).
- **Ages by year difference.** For a death, (d − b) is *unbiased* for exact age at death (the birthday/death-day offsets u_d − u_b have mean zero); there is no systematic off-by-one. For the six living Apollo, 2026 − b overstates exact age at a June-1 epoch by ~0.08 y (understates at Sep 7 by ~0.18 y); one full year of hazard at their ages sums to 1.38, so the epoch convention moves E by ~0.2 of 46.9 — third decimal. State the epoch.
- **Single 1930 table for births 1923–1936 (Apollo) / 1921–1942 (pool).** Cumulative hazard 30→80 by cohort: 1921 0.991 · 1923 0.963 · 1930 0.843 · 1935 0.760 · 1942 0.698. Apollo's mean birth year is 1930.9 (median 1930), so the errors nearly cancel: per-birth-cohort tables give E = 46.54, **SMR 0.494 (+0.8%)**. The non-Apollo comparator is more spread and younger: SMR 0.515 → 0.533 (+3.5%). MC percentile under per-cohort tables: **38.6%.**
- **Immortal time.** The window starts at 30, but the pool is conditioned on surviving to be selected (1959–69) and on surviving the 1960s (the `trainAcc` exclusion). Expected deaths accumulated before that conditioning date can have no observed counterpart → E inflated, SMR biased low. Truncating each window at the later of age 30 and 1 Jan 1970: Apollo E = 46.21, **SMR 0.498 (+1.5%)**; at selection year: 0.492 (+0.3%); per-cohort + 1970 truncation: **0.502 (+2.3%)**. MC percentile: 42.8% / 38.9%. Symmetric across decks, so the permutation result is unaffected; the absolute SMR moves in the third decimal.
- **Fix.** One methods sentence acknowledging both (or adopt per-cohort + 1970-truncated E as primary — it is the more defensible construction). Either way, report SMR as 0.49–0.50.

### F5 · [FINE, one documentation item] The `trainAcc` exclusion — Q3
- Defensible and necessary: the real 29 are conditioned on surviving to fly (1968–72), so the comparator must be too. Including the eight would make every synthetic deck look worse than Apollo by construction (this is exactly what `smr.c`'s "dirty ratio" shows).
- Verified on all 73: `trainAcc ⇔ death ≤ 1970` holds in both directions; none of the 29 is `trainAcc`; the eight are Bassett, Chaffee, Freeman, Givens, Grissom, See, White, Williams — all accidental. The two generators encode *different* rules (Apollo: pre-1970 AND accidental; non-Apollo: any death ≤ 1970) that happen to coincide in the data. No exit age is < 30 (which would have produced a negative E term). No one in the 73 died between 1970 and 1981 (Swigert, 1982, is the first), so the boundary is insensitive.
- The hostile version of Q3 is not the eight; it is the **18 Groups 6–7 members who were realistically never Apollo candidates**. For mortality the restriction changes nothing (percentile 52.7%); for vitality it is decisive (F2). Report both pools.

### F6 · [FINE] RNG, shuffle, reproducibility — Q4
- `rand() % (i+1)` with RAND_MAX = 2³¹−1: modulo bias ≤ 73/2³¹ ≈ 3.4×10⁻⁸ per draw. Negligible.
- On this libc, `rand()` is the Park–Miller minimal-standard LCG (verified: 16807 × 1788768027 mod (2³¹−1) = 1200655436 = the first output after `srand`). The man page calls it "bad"; for this use the closed-form comparison in F1 is the real test and it passes.
- Fisher–Yates (lines 125–132): Durstenfeld form, j ∈ [0, i], self-swap allowed — correct. Not resetting the deck between rounds is fine (a uniform permutation composed with any permutation is uniform).
- Seed: recorded in the TSV; rebuilt binary reproduces the first 3,000 rows byte-for-byte; two fresh seeds give 42.53% and 42.47%. **Reproducibility is libc-dependent** — say "macOS libc `rand()`, seed 1788768027", or switch to a self-contained generator (e.g. `random()`/`srandom`, or a short xorshift) so the seed claim is portable.

### F7 · [COSMETIC] Code and labels — Q5, Q8
- `sorted[14]` of 29 is the median (the 15th value). Correct; for the real 29, positions 13–15 are all 88.
- Line 205 hard-codes `2026`; `astroOnp.h` defines `studyYear`. Use the constant. Likewise the literal `29` (three places) vs `apolloAstrosCount`.
- The `while` walk (lines 143–168) has no bound on `shuffleIterate`; safe because only 8 of 73 are excluded, latent otherwise.
- TSV header says "SMR v US Census" — the reference is SSA Actuarial Study 120 (TR2024, Alt 2, male, 1930 cohort). Cite it exactly.
- C comment "no deaths post 1970" means no *training-accident* deaths post 1970.
- "Median Group Age" is a median **attained** age as of 2026 (ages at death mixed with current ages of the living) — label it so; it is a fine permutation statistic but not a "median lifespan," and it is coarse (9 of the 29 were born in 1930).
- `calculateSMR` still prints four lines per astronaut per deck (~10⁸ lines per run). Not a correctness issue.
- Her manual TSV marks Armstrong "Accidental? = Y" (died 2012 of post-surgical complications). Not load-bearing (pre-1970 = N) but check before the data ships.
- Figure: `apollo_mc_smr_histogram.py` (as updated 01:14) reproduces both SVGs byte-identically; the SMR rule is at the exact continuous position of 0.4905, the grandpa rule at the centre of bin 19; annotation percentages match the TSV. Only the F1 wording needs to change.

---

## What the writeup may say
- "Within the 65 NASA astronauts selected before 1970 who survived the decade, the 29 who flew Apollo have a standardized mortality ratio of 0.49 (95% CI 0.31–0.74) against the US male 1930 birth cohort (SSA Actuarial Study 120); about 43% of one million random 29-person subsets of the same pool have an SMR at or below it. **The low mortality belongs to the corps, not to Apollo.**" ← the headline sentence I would let stand.
- "No random 29-subset of that pool reached an SMR of 1; the corps as a whole sits at 0.50 (0.37–0.67)."
- "Apollo's 22 astronauts who reached 80, and the 19 of them who meet the piece's space-grandpa criterion, are what a random 29-person subset of the corps produces (one-sided p = 0.69 and 0.22)."
- "The simulation is seeded (1788768027, macOS libc `rand()`) and was independently re-implemented; both give ≈ 42.5%."

## What it may not say
- "Apollo astronauts lived longer" / "aged unusually well" / "outlived their peers."
- "Top 10% for space grandpas" / "top 7% on median age."
- "Half the mortality of ordinary Americans" without saying that every astronaut subgroup shows it and that the reference is all-races US males.
- "The Monte Carlo confirms the vitality result." Under her coding it does the opposite (F2).
- "One million simulations" as a precision claim; the count statistics have closed forms, and the SMR percentile is ±0.05 points either way.

## What I could not verify
- The Space-Grandpa codings themselves (criteria are not in the files I read; I took the flags as given and traced them to her manual TSV).
- Birth/death years against primary sources (the July blind-replication diff audited 14 rows; not repeated tonight). Lovell 2025 taken as given.
- The 72% population vitality base rate from the June record.
- A white-male or officer reference table (not in the folder) — direction stated, magnitude not.
- Whether Groups 6–7 "could have flown Apollo" is a historical argument; I report the sensitivity, not a ruling.

## Reproduction log
- `.h` parse (mine, line-based) → Apollo 29 / other 44 / pool 65; `1930CohortSSAData.h` identical to the TR2024 CSV row 1930 at every age 0–119.
- Real Apollo: O 23, E 46.895698, SMR 0.490450, hit-80 22, grandpa 19, median 88 — matches the figure tool and `smr.c`.
- TSV: 1,000,000 rows, contiguous indices, seed 1788768027. SMR min 0.2516, p5 0.401, median 0.5032, mean 0.5078, SD 0.0698, p95 0.630, max 0.9490; zero decks ≥ 1. P(SMR ≤ 0.490450) = 42.64%, no ties.
- Grandpa 19: P(≥) 21.76% / P(>) 9.85% / P(=) 11.90%. Hit-80 22: P(≥) 68.58% / P(≤) 54.17%. Median 88: P(≥) 36.95% / P(>) 7.03% / P(=) 29.92%.
- Exact hypergeometric: grandpa P(≥19) 21.72%; hit-80 P(≥22) 68.49%. χ² vs MC: 17.7/16 df, 13.7/14 df.
- Vitality: P(g ≥ 19 | h = 22) = 11.72% (227,522 such decks); Fisher 0.1167; Groups 1–5 like-for-like Fisher 0.688.
- E variants (Apollo): 0.4905 → per-cohort 0.4942 → trunc-1970 0.4978 → selection 0.4921 → cohort+trunc 0.5018.
- Independent numpy MC (1M, PCG64): 42.48% / 42.54% (two seeds); per-cohort 38.62%; trunc-1970 42.83%; cohort+trunc 38.91%; Groups 1–5 pool 52.74%.
- Her binary, verbatim copy, seed 1788768027: first 3,000 rows identical. Seeds 20260907 / 424242 at 1M: 42.53% / 42.47%; P(g≥19) 21.78% / 21.72%.
- Figure script rerun in place: SVGs byte-identical to the on-disk files.
