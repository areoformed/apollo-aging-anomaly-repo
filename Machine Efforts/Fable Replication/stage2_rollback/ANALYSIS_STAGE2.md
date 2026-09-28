# STAGE 2 — Mortality & late-life cognition analysis

Input: `apollo_era_astronaut_cohort_v2.csv` (the dataset built in Stages 1/1b — nothing else
about the astronauts). Population reference for Q1(b): CDC/NCHS *United States Life Tables,
2021*, Table 2 (males). Scripts: `analysis_astronauts.py` (Q1a + Q2), `analysis_smr.py` (Q1b).
Run 2026-06-09; censoring 2026-06-01.

All 73 subjects are male (NASA Groups 1–7, 1959–69; the corps was all-male until Group 8 in
1978, excluded by the cohort bound). So "sex-matched" is automatic and exact.

---

## A. ANALYSIS DECISION LOG (judgment calls)

**A1 — Index date / start of time-at-risk = 1972-12-19 (Apollo 17 splashdown).** "Flew Apollo"
is an exposure that can only be confirmed by surviving to one's mission, so starting the clock
at birth gives Apollo flyers free survival time and produces immortal-time bias. I therefore
use a **landmark**: the moment the Apollo program ended and every subject's Apollo exposure is
fixed. Everyone alive on that date enters; exposure is already determined; no immortal time.
(Shown explicitly below: the naive from-birth HR is biased ~15% lower than the landmark HR.)

**A2 — Time scale = attained age, left-truncated (delayed entry) at age on the index date.**
Age is the overwhelming determinant of mortality here, so I use it as the analysis clock and
let each subject enter the risk set at his age on 1972-12-19. This auto-adjusts for the small
age differences between groups and is the natural scale for comparison to age-indexed life
tables in Q1(b).

**A3 — Who is excluded by the landmark.** 8 people died before 1972-12-19 and cannot enter:
the 3 Apollo 1 crew (1967 pad fire) and 5 comparison astronauts killed in training/accidents
(Bassett, Freeman, Givens, See, Williams, 1964–67). Excluding them is correct for a "does
flying Apollo change later mortality" question — these are pre-exposure deaths, not late-life
mortality, and counting the 5 accident deaths against the comparison arm would manufacture a
spurious Apollo advantage. (They are visible in the from-birth sensitivity.)

**A4 — Comparison group = all other Groups 1–7 astronauts alive at the landmark** (29
`COMP_FLEW_OTHER` + 7 surviving `COMP_NEVER_FLEW` = 36). Sensitivity restricting to
`COMP_FLEW_OTHER` only (n with Apollo = 58) is reported and changes nothing.

**A5 — Reference population for Q1(b) = CDC/NCHS 2021 US male life table**, applied by indirect
standardization over each subject's observed attained-age window from the index date. Using my
dataset only for the cohort/exposure/outcome; the population *reference* is the external
standard the prompt invites ("e.g., SSA cohort life tables"). I could not fetch ssa.gov or
web.archive (both 403/blocked), so I used the CDC 2021 male period table (NVSR 72-12 Table 2)
from a government mirror. **This is conservative:** 2021 period mortality is *lower* than the
mortality these 1921–42 birth cohorts actually met at older ages, so expected deaths are
understated and the SMR is biased *upward toward 1*. A true cohort table would push every SMR
*lower* — i.e., it can only strengthen, never create, a survival-advantage finding.

**A6 — SMR definition.** Per subject, expected deaths over [age at index, age at death/censor]
= cumulative-hazard difference `ln(l(a0)/l(a1))` from the reference table; `SMR = ΣO/ΣE` with
exact Poisson 95% CI. The `l(a0)` denominator conditions on survival to entry, so this is a
left-truncated, healthy-worker-appropriate SMR.

**A7 — Cognitive endpoint (Q2) = documented major cognitive impairment
(`IMPAIRED_DOCUMENTED`) by end of observation, among those who survived to an assessable late
life** (`cognitive_status ≠ DIED_EARLY`, i.e. attained age ≥ 70). Justification: late-life
cognition is undefined for someone who died at 56; `DIED_EARLY` is precisely "no observation
window," so those people are removed from the denominator rather than scored as non-impaired.
The endpoint is symmetric across groups and uses the coding already in the dataset.
`NO_EVIDENCE_EITHER_WAY` is treated as **missing/uncertain** and handled by bounds (A8), never
silently counted as "not impaired."

**A8 — Ascertainment handled by bounds + a depth-matched stratum, not by assertion.** (i)
Manski worst-case bounds: let every `NO_EVIDENCE` be intact (lower bound) then impaired (upper
bound). (ii) Least-biased stratum: restrict to `documentation_depth = HIGH`, where a major
dementia would almost certainly have surfaced, so HIGH + `NO_EVIDENCE` ≈ truly not impaired.
(iii) Direction check: compare `documentation_depth` between groups, because the more-documented
group is the one in which impairment is *more* likely to be detected.

---

## B. QUESTION 1 — MORTALITY

### B1. Apollo flyers vs comparison astronauts  *(no detectable difference)*

Landmark cohort from 1972-12-19, attained age, left-truncated.

| | Apollo | Comparison |
|---|---|---|
| n at risk (alive at index) | 29 | 36 |
| deaths / still alive 2026-06-01 | 23 / 6 | 26 / 10 |
| mean age at entry (index) | 41.6 | 39.3 |
| KM median age at death | **88.1** | **86.1** |
| KM survival S(80) / S(85) / S(90) | .76 / .66 / .45 | .78 / .61 / .37 |

- **Cox proportional-hazards HR (Apollo vs Comparison) = 0.83, 95% CI [0.46, 1.48], p = 0.53.**
- Exponential rate ratio = 1.18, 95% CI [0.67, 2.07] (constant-hazard robustness check).
- Sensitivity vs `COMP_FLEW_OTHER` only: HR = 0.95 [0.51, 1.76], p = 0.87.
- Naive from-birth (immortal-time-biased, for contrast only): HR = 0.71 [0.41, 1.24] — i.e.,
  ignoring the landmark inflates an apparent Apollo advantage, as predicted by A1.

**Conclusion B1: no detectable difference in all-cause mortality between Apollo-flown and
comparison astronauts.** Median age at death differs by ~2 years (88 vs 86) with a HR CI that
comfortably spans 1. With 23 and 26 deaths the study can only resolve large effects (roughly
HR ≤ 0.5 or ≥ 1.9); a modest ±25% difference would be undetectable here, so this is "no
*detectable* difference," not proof of identity.

### B2. Apollo flyers vs era/sex-matched US male population  *(large survival advantage)*

Indirect standardization to the CDC 2021 US male table from the same index date.

| Group | Observed deaths | Expected (US male) | **SMR (95% CI)** |
|---|---|---|---|
| Apollo | 23 | 45.5 | **0.51 [0.32, 0.76]** |
| Comparison | 26 | 48.5 | **0.54 [0.35, 0.79]** |

- Intuitive complement: under US male population rates ~1.7 of the 29 Apollo flyers would still
  be alive at 2026-06-01; **6 are.** For comparison astronauts, expected ~4.1 of 36 alive;
  **10 are.**
- SMR ratio Apollo / Comparison = 0.94, 95% CI [0.54, 1.65] — astronaut groups indistinguishable.

**Conclusion B2: both astronaut groups die at about half the rate the era/sex-matched US male
population would predict (SMR ≈ 0.50–0.54, CIs exclude 1), and Apollo flyers are no different
from comparison astronauts in this respect.** This is the expected healthy-worker / healthy-
survivor selection effect (elite test pilots and scientists who passed rigorous medicals and
had already survived to ~40). Because the 2021 reference table is conservative (A5), the true
advantage versus the cohorts' contemporaneous population is *larger* than shown. The
population-level difference is real and large; the *Apollo-specific* difference is absent.

---

## C. QUESTION 2 — LATE-LIFE COGNITIVE OUTCOMES

Endpoint per A7; ascertainment per A8. Comparison = `COMP_FLEW_OTHER` + `COMP_NEVER_FLEW`.

### C1. Counts

| | Apollo | Comparison |
|---|---|---|
| total | 29 | 41 |
| DIED_EARLY (excluded, age <70) | 6 | 8 |
| **assessable denominator** | **23** | **33** |
| IMPAIRED_DOCUMENTED | **0** | **2** (Peterson, Fullerton) |
| INTACT_DOCUMENTED | 20 | 20 |
| NO_EVIDENCE_EITHER_WAY | 3 | 11 |

### C2. Naive impairment prevalence
- Apollo 0/23 = **0.0%** (95% CI 0.0–14.3%); Comparison 2/33 = **6.1%** (95% CI 1.7–19.6%).
- Risk difference −6.1 pp; **Fisher exact p = 0.51** — not significant. Only **2 events** exist
  in the entire dataset, so the impairment endpoint has essentially no statistical power.

### C3. Ascertainment bounds (the honest width of the uncertainty)
Manski bounds, ranging `NO_EVIDENCE` from all-intact to all-impaired:
- Apollo impairment ∈ **[0.0%, 13.0%]**; Comparison ∈ **[6.1%, 39.4%]**.
- Risk-difference bound **[−39.4 pp, +7.0 pp]** — **straddles zero, so the sign of any
  difference is not identified** from counts alone. This is the quantified ascertainment
  problem: the unknown cognitive status of the 3 Apollo + 11 comparison `NO_EVIDENCE` people is
  wider than any plausible true effect.

### C4. Least-ascertainment-biased stratum (documentation_depth = HIGH)
Where a major dementia would almost certainly be public:
- Apollo **0/22** impaired (incl. 3 HIGH-coverage `NO_EVIDENCE`: Scott, Young, Mattingly).
- Comparison **0/12** impaired (incl. 2 HIGH-coverage `NO_EVIDENCE`: Engle, Truly).
- **Both strata are event-free.** The two impairment cases (Peterson, Fullerton) are *both*
  MEDIUM-depth comparison subjects — i.e., the entire "signal" sits where ascertainment is
  weakest and the comparison group simply has more such people.

### C5. Direction of the ascertainment bias, and the documentation artifact
- Among assessable survivors, Apollo is far better documented (HIGH/MED/LOW = 22/1/0) than the
  comparison group (12/18/3). So impairment is *more* likely to be detected in Apollo — yet none
  was. That makes Apollo's 0/23 a *conservative* reading for "Apollo not worse," but it cannot
  manufacture a positive finding from 2 events.
- The flip side is a trap to avoid: the **`INTACT_DOCUMENTED` rate** looks higher in Apollo
  (20/23 = 87%) than comparison (20/33 = 61%). That gap is **documentation, not cognition** —
  restricting to HIGH-depth subjects collapses it to **86% (19/22) vs 83% (10/12)**. Matching on
  `documentation_depth` erases the apparent difference, confirming the raw INTACT gap is an
  ascertainment artifact.

**Conclusion C: no detectable difference in late-life cognitive impairment between Apollo-flown
and comparison astronauts.** With only 2 documented impairment events total, the endpoint is
unpowered; worst-case bounds do not even identify the sign of a difference; and the cleanest,
least-biased view (HIGH-documentation survivors) shows zero impairment in *both* groups. The
dataset cannot support any claim of a cognitive difference in either direction. The strength of
this null is explicitly limited by ascertainment, which I have bounded (C3) rather than assumed
away — and which, where it does bite, runs slightly *against* an "Apollo is healthier" reading
(C5), not for it.

---

## D. LIMITATIONS

- **Power.** n≈29 vs 36, ~23–26 deaths/arm, 2 cognitive events. Adequate to detect only large
  mortality effects; near-zero power for the cognitive endpoint. Nulls are "not detectable,"
  not "absent."
- **Cognitive endpoint is documentation-defined**, not clinically adjudicated; `IMPAIRED` rests
  on public reports (one of the two, Fullerton, is an explicit judgment call; Peterson's WaPo
  obituary 403'd and was corroborated indirectly). C3–C5 bound the resulting uncertainty.
- **Reference table** is period-2021, not a true cohort table (A5) — conservative for B2.
- **Selection.** Both astronaut groups are elite survivors; the population comparison (B2)
  measures that selection, not spaceflight. The within-astronaut comparison (B1) is the cleaner
  test of an Apollo-specific effect, and it is null.
- No multiplicity adjustment is needed — two pre-specified questions, reported individually.
