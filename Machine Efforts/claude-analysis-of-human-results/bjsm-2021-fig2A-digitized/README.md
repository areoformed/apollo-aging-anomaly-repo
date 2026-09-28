# Antero et al. 2021, Figure 2 — digitized from scratch, and redrawn with Apollo

Built 2026-09-07 on [AUTHOR]'s ask: *"let's make a new sub-directory in the claude-analysis-of-human-results
folder and put an extrapolation of what the points are in there and then generate the values from
scratch… I think it would be interesting to do all 4 if we're getting the data."*

This replaces the earlier raster-overlay attempt
(`../apollo_on_bjsm_2021_figA.svg/.png`), which [AUTHOR] judged logically incorrect: it drew Apollo's
curve on top of a panel whose x-axis is *follow-up from the athlete's Games*, while Apollo's clock
started at *age 30*. Those two axes are not the same thing and the raster method could not be
corrected. Nothing here is traced by eye or built on that file; every number below comes out of a
colour mask and a measured calibration.

**Source figure.** `../../../Human Efforts/Graphs/Third Party/bjsports-2021-February-55-4-206-F2.large (1).jpg`
(1280 × 1021, JPEG). Antero J, Tanaka H, De Larochelambert Q, Pohar-Perme M, Toussaint J-F.
*Female and male US Olympic athletes live 5 years longer than their general population counterparts:
a study of 8124 former US Olympians.* Br J Sports Med 2021;55:206–212. doi:10.1136/bjsports-2019-101696.

**Supplementary source.** `../../../Human Efforts/Graphs/Third Party/bjsports-2021-February-55-4-206-inline-supplementary-material-1 (1).pdf`
— Supplementary material 1, page 3, Figure S1 panel C. The embedded PNG (919 × 807) was extracted at
its native resolution with PyMuPDF; re-rasterising the page at higher dpi would add pixels but no
detail. **The supplementary file contains no tabulated survival values** — it is three figures plus
prose — so digitization is the only route to the numbers, and there is nothing better to prefer over it.

---

## 1. What was digitized

| Panel | Curves | Axis | Output |
|---|---|---|---|
| **2A** | Male Olympians, Female Olympians, Male population, Female population | survival % vs follow-up years | `male_olympians.csv`, `female_olympians.csv`, `male_population.csv`, `female_population.csv` |
| **2B** | p2 (1920–36), p3 (1948–64), p4 (1968–84) | survival % vs attained age | `fig2B_periods_by_age.csv` |
| **2C** | US Olympians, US general population | cumulative death probability vs age | `fig2C_cumulative_death_by_age.csv` |
| **S1C** | US Olympians (at a Games by 30), US general population | cumulative death probability vs age, from 30 | `figS1C_cumulative_death_from_age30.csv` |

`points_raw.csv` holds the per-column pixel extraction for panel 2A before resampling
(curve, pixel_x, pixel_y, followup_years, survival_pct).

## 2. Method

1. **Find the plot box by measurement.** Scan for long runs of near-black pixels; the box borders fall
   out. No coordinates were assumed.
2. **Find the ticks by measurement.** Scan a thin band just *outside* each border — R draws ticks
   outward — and take the centre of each tick run. An affine pixel→data map is then least-squares
   fitted to the tick pixels, and its maximum residual is reported.
3. **Mask each curve by colour**, sampling the actual RGB from the figure's own legend swatches and
   from line cores, never from a guessed hex.
4. **Per pixel column, group masked rows into runs** and take each run's midpoint. Where two curves
   share a hue, they are separated structurally (§4).
5. **Resample to a 1-year grid** by linear interpolation across gaps — including the gaps in the
   dotted lines — and never extrapolate beyond the observed span. Survival curves are forced
   monotone non-increasing, cumulative-death curves monotone non-decreasing.

## 3. Calibration (all measured, not assumed)

**Figure 2A** — box x 99–626, y 18–355.

| | pixels | values | scale | max affine residual |
|---|---|---|---|---|
| x | 119, 237, 355, 473, 591 | 0, 20, 40, 60, 80 yr | 5.9000 px/yr | 0.000 yr |
| y | 31, 108, 187, 265, 342 | 100, 75, 50, 25, 0 % | 3.1161 px/% | 0.224 % |

**Figure 2B** — box x 734–1279, y 18–295. x: 755, 849, 943.5, 1037.5, 1132, 1226 → 0–100 yr
(4.7114 px/yr, resid 0.033 yr). y: 29, 92.5, 157, 220.5, 285.5 → 100–0 % (2.5640 px/%, resid 0.195 %).

**Figure 2C** — box x 54–626, y 556–956. x: 141, 273.5, 405.5, 538 → 20, 40, 60, 80 yr
(6.6150 px/yr, resid 0.023 yr). y: 571, 645, 719, 793.5, 867.5, 941.5 → 1.0…0.0 (370.6 px/unit).

**Figure S1C** — box x 664–892, y 51–338 in the 919×807 PNG. x: 673, 725, 778, 831, 883 → 20–100 yr
(2.6300 px/yr, resid 0.152 yr). y: 62, 115, 168, 221, 275, 328 → 1.0…0.0 (266.1 px/unit).

## 4. Colour thresholds

Sampled from the figure. Legend swatches: Male Olympians **(12, 4, 116)**, Female Olympians
**(0, 98, 0)**; panel B's p2 **(253, 6, 0)**, p3 **(6, 203, 9)**, p4 **(0, 2, 249)**; panel 2C's fill
**(0, 138, 138)**; Figure S1C's fill **(0, 104, 139)** — S1's teal is measurably *bluer* than 2C's, so
the two panels need different masks.

| curve | rule |
|---|---|
| blue lines (2A) | `b − max(r,g) ≥ 18` and `max channel ≤ 155`; fallback `≥ 11`, `≤ 225` used only where the core mask is empty |
| green solid (2A) | `g − max(r,b) ≥ 18`, `\|r − b\| ≤ 20`, `max ≤ 190` |
| chartreuse dotted (2A) | `g − b ≥ 70` and `r − b ≥ 45` |
| p2 / p3 / p4 (2B) | dominant channel leads the other two by ≥ 45 / 30 / 45, `max ≤ 210`, run height ≤ 8 px |
| teal fill (2C) | `\|g − b\| ≤ 14`, `g ≥ 95`, `r ≤ 70` |
| teal fill (S1C) | `b − r ≥ 60`, `g − r ≥ 45`, `b ≥ 100` |

**The CI bands are excluded by brightness, not by hue.** A band pixel and a line pixel can have the
same blueness — panel 2A's blue band runs around (192,192,240) with `b − max(r,g)` up to 56, the same
as the line core — but the band is *bright* (max channel 190–255) and the line core is dark
(≤ 155). The brightness cap is doing that work; the hue rule alone would fail.

**Panels 2C and S1C are not line charts and were not read as ones.** They are stacked areas: teal fill
from 0 up to the Olympians' curve, then a grey wedge up to the population's curve, which carries a
black outline. For each column the reader walks *up from the axis* through the contiguous non-white
fill (`max channel < 195` for 2C, `< 180` for S1C, chosen to sit between the grey wedge at 169 and the
dotted grid lines at 190–230). The top of that run is the population; the top of its teal part is the
Olympians. Anchoring at the axis makes the reading immune to floating ink: the panel letter "C" and
the whole "Early mortality" inset are not connected to the fill and are never picked up. No hand-drawn
exclusion rectangle is used for them.

## 5. Accuracy

**Reading uncertainty is ±1 px.** On Figure 2A that is **±0.32 % survival and ±0.17 years**.
Panel S1C is about three times coarser — its whole plot is 228 × 287 px, so 1 px = **0.38 yr and
0.0038 probability units**. Panel 2C: 1 px = 0.15 yr and 0.0027 units. Panel 2B: 1 px = 0.21 yr and
0.39 % survival.

**Loss from resampling to a 1-year grid** (deliverable CSV vs the raw per-column extraction, Figure 2A):

| curve | columns | mean deviation | max deviation |
|---|---|---|---|
| male_olympians | 420 | 0.94 px (0.30 %) | 5.70 px (1.83 %) |
| female_olympians | 487 | 1.13 px (0.36 %) | 5.18 px (1.66 %) |
| male_population | 218 | 0.52 px (0.17 %) | 2.91 px (0.93 %) |
| female_population | 304 | 0.88 px (0.28 %) | 5.46 px (1.75 %) |

The maxima land on Kaplan–Meier step risers, where a 1-year grid cannot represent a vertical jump.

## 6. Verification

**Visual.** `_verify/fig2A_overlay.png`, `fig2B_overlay.png`, `fig2C_overlay.png`,
`figS1C_overlay.png` re-plot the resampled 1-year series back into the original pixel grid, on top of
the source panel. `_verify/crossrender_matplotlib.png` re-plots every series independently in
matplotlib as a check on the hand-rolled SVG geometry. `_verify/svg_render/` holds PNG rasterisations
of the six delivered SVGs.

**Against numbers printed in the paper** — this is the discriminating check, and all three pass:

| quantity | digitized here | printed in the paper |
|---|---|---|
| median survival after the Games, male Olympians | **56.47 yr** | 56.7 (95% CI 55.8–57.3) |
| median survival after the Games, female Olympians | **65.81 yr** | 66.0 (95% CI 63.0–67.6) |
| area between the Figure 2C curves, ages 25–90 | **5.28 yr** | years-saved 5.1 (95% CI 4.3–6.0) |

The third is corroboration, not reproduction: the paper computes years-saved per individual over each
person's own follow-up, not as the area between two published curves. The same area on Figure S1C,
ages 43–90, comes to 5.73 yr.

## 7. The at-risk table under panel A

Printed values, read directly: **Male Olympians** 5823 5338 4721 3921 3126 2549 1645 833 238 34 0;
**Female Olympians** 2301 1899 1466 1018 654 498 324 176 68 14 1. The two first entries sum to 8124,
matching the cohort size stated in the paper.

**Which x positions those columns correspond to.** The digit-group centres measure at pixel x =
118, 167, 214.5, 263.5, 313.5, 362, 410.5, 458.5, 508, 556.5, 605, i.e. follow-up
**−0.2, 8.1, 16.2, 24.5, 33.0, 41.2, 49.4, 57.5, 65.9, 74.2, 82.4 years** — eleven equally spaced
times with a step of ≈ 8.25 yr, spanning 0 to ≈ 82.4 yr. **They are not at 0, 8, 16 … 80**, and not at
round numbers at all. Independent support for reading the last column as ≈82.4: R pads a plot range by
4 % each side, and the box interior (x 100–625) maps to −3.2 … 85.8 yr, so 1.08·D = 89.0 → D = 82.4 yr,
the maximum follow-up in the data. The table is `seq(0, 82.4, length.out = 11)`.

Panel B's at-risk columns behave the same way: centres at ages −0.2, 10.6, 21.2, 31.9, 42.6, 53.5,
64.0, 74.7, 85.4, 96.2, **106.8** — eleven points to the maximum attained age, not to 100.

## 8. Every ambiguity, flagged

1. **Follow-up 0–20 yr on panel 2A is where the digitization is weakest.** All four curves sit within
   about 3.5 % of one another there and JPEG blending destroys hue separation — 110 of the 526 panel
   columns returned no blue pixel at all under the core mask. The blue pair could not be split before t ≈ 9. The male Olympian track is
   resolved from **t = 9.15 yr** and the male population track from **t = 4.75 yr**; each is joined to
   the definitional point (0, 100 %) by a straight line. Those two spans are recorded in
   `_verify/fig2A_meta.json` under `anchored_to_t0_span_years`. It is an assumption, not a measurement
   — but survival *is* 1 at entry by definition, and every curve is above 96 % across the joined span.
2. **Male Olympians and Male population share a hue.** They cannot be told apart by colour. They are
   separated structurally: in the 190 columns (of 526) showing two blue runs the upper run is the Olympian
   curve and the lower is the population curve (the paper's finding is that Olympians survive better
   throughout, so the two never cross); single-run columns are then assigned by continuity from the
   two-run tracks. 45 columns remained ambiguous under that rule and are listed in
   `_verify/fig2A_meta.json` as `ambiguous_columns_blue_pair`.
3. **Dotted lines have gaps by construction.** Of 526 columns, the male population curve was resolved
   in 218 and the female population curve in 304. The gaps are interpolated, which is exactly what a
   dotted line asks for, but the CSVs are denser than the ink.
4. **`p4_1968_1984_survival_pct_given_alive_at_30` is identical to the unconditioned column.**
   p4's track is only resolved from age 31.6, so S(30) defaulted to 100 % and the divisor did nothing.
   The p4 conditioned column carries no extra information; p2's divisor is 98.3 % and p3's is 94.4 %.
5. **Panel 2B is the least accurate of the four.** Six curves with pale CI bands overlap heavily above
   age 60. Coverage: **p3 73 %, p2 65 %, p4 53 %** of the panel width. 16 columns have two saturated
   hues within 4 px of each other — ages 27, 32, 43, 48, and 100–103 — and each is listed in
   `_verify/fig2B_meta.json`. p4's cohort (Games 1968–84) is still young, so its curve is short and
   its published CI band is very wide; treat p4 as context, not evidence.
6. **S1C loses the Olympian curve below age ~42**, where the teal layer is thinner than one pixel. The
   population curve is resolved from age 34.1, the Olympian curve from 42.5. Both are near zero there.
7. **The legend.** The brief estimated it at x 300–650, y 430–650; that region is in fact the at-risk
   table. The legend's measured ink bounding box is **x 140–328, y 214–328** (swatches at x 157–171,
   y 216–227 and y 242–253). It is excluded as x 138–336, y 210–332. **No curve passes behind it**:
   over that x-span (follow-up 3.2–36.8 yr) the lowest of the four curves is at 78.3 % survival, while
   the legend's top edge is at 42.4 %. Nothing had to be reconstructed behind text.
8. **Panel 2C's inset** ("Early mortality", its own box plus axis labels) sits inside the panel. It is
   handled by the axis-anchored fill walk described in §4 rather than by masking a rectangle, so no
   real data is discarded.
9. **Colour identity in 2C and S1C** comes from the main paper's Figure 2 caption ("Olympians (green
   area) and the general population (black curve)"). The supplementary file does not restate the
   scheme for S1; it is carried over.

## 9. What was fetched from the paper

BMJ's own site returns HTTP 403. The full text was obtained as the publisher PDF hosted by INSEP
(the first author's institute) and saved to `_src/antero2021_bjsm_insep.pdf` with its text at
`_src/antero2021.txt`. All quotations below are `[fetched, verbatim]` from that PDF.

- **Population comparator** — `[fetched]` *"Data on the US general population mortality were obtained
  trough the national life tables, available by the Berkeley Mortality database … and the Human
  Mortality database"*, and *"for each individual in our study, the general population mortality
  values of individuals of the same sex and calendar year were considered and their values taken for
  all ages from the time of Olympic game participation until the end of follow-up. In this way, all
  the comparisons with the general population were adjusted by sex, birth date and periods of
  follow-up."* So: **US life tables, matched per individual on sex, birth date and calendar period** —
  not a single national curve.
- **Follow-up definition** — `[fetched]` *"The athletes' follow-up started at their first Olympic Games
  participation and ended at their date of death or at the study's end point: 1 January 2016."*
  (An age-90 cap applies to the years-saved computation only, not to the survival curves.)
- **Cohort** — `[fetched]` 8124 US Olympians (2301 women, 5823 men), Games 1912–2012, 2309 deaths.
  Mean age at death, among those who died, 72.4 ± 16.1 yr; mean follow-up for those alive in 2016,
  28.6 ± 16.8 yr.
- **Licence** — `[fetched, verbatim]` **"© Author(s) (or their employer(s)) 2020. No commercial
  re-use. See rights and permissions. Published by BMJ."** There is **no Creative Commons statement
  anywhere in the article**; it is not open access. This is reported, not interpreted — it is not
  legal advice. Every figure here is redrawn from extracted values; **no pixel of the original is
  reproduced in any deliverable**, and each SVG carries the citation and the rights line.
- **Baseline age at first Games — NOT REPORTED IN THIS PAPER.** The BJSM paper has no
  cohort-characteristics table and states no mean or median age at first Olympic participation; the
  supplementary file does not either. Both were grepped. The value used here comes from **a different
  paper by the same authors on the same US Olympian cohort**: Antero J et al., *"Heads-Up:
  Risk-Specific Neurodegenerative Mortality and Years-Saved Analysis on the US Olympian Cohort"*,
  Front Physiol 2021;12:705616 (open access, CC BY), **Table 2, "Description of the Olympians cohort
  characteristics"**. `[fetched, verbatim from the primary full text — Europe PMC JATS XML, saved at
  `_src/frontiers2021_PMC8458956.xml`; not from a summary]`:

  | Mean age at the first OG in years (SD) | N | Female | Male |
  |---|---|---|---|
  | Games **1948–1972** | 24 (5.16) | 21 (4.41) | 24 (4.98) |
  | Games **1912–1972** | 24 (5.05) | 21 (4.41) | **25 (4.87)** |

  The same table gives mean follow-up 52 yr (SD 12.78) and mean age at leaving the cohort 76 yr
  (SD 12.86, male) for 1912–1972, and it footnotes that *"Age in years, proportion, and IQR are
  rounded up."* — so 25 and 21 are rounded, not exact.
  ⚠️ **The Games window differs from the BJSM paper's 1912–2012.** Treat male 25 / female 21 as a
  well-sourced proxy for the BJSM cohort's entry age, not as that cohort's own published statistic.
  Every SVG that uses it says so on its face.

## 10. Apollo's Kaplan–Meier

From `../../../Human Efforts/scripts/Astronaut MC/apolloData.h` (read-only; nothing under
`Human Efforts/` was modified). Age at death = deathYear − birthYear; living astronauts censored at
2026 − birthYear; ties broken with events before censorings.

**n = 29, 23 deaths, 6 censored** at ages 91, 91, 91, 93, 94, 96. Earliest death age **51**
(Swigert), latest **97** (Lovell). Median survival age **88**. Roster and steps:
`apollo_roster.csv`, `apollo_km_by_age.csv`.

Two things to hold onto. **All 29 were alive at 30** — indeed all were alive at 50 — so starting
Apollo's clock at 30 (or at 25) discards nobody and costs no information. And **only birth and death
years are recorded**, so every Apollo age carries ±1 year of quantisation, which is larger than the
digitization error on the Olympian curves. The curve's final drop to zero at 97 is the Kaplan–Meier
convention when the last observation is a death; it does not mean the estimator is confident there.

## 11. The five redrawn figures

Hand-rolled SVG, named `<g>` layers, white ground, no embedded raster. Each carries its citation, the
rights line, and its alignment assumptions as text inside the file.

| file | what it is |
|---|---|
| `fig2A_redrawn_followup.svg` | the four digitized curves on the original follow-up axis, faithfully |
| `fig2A_with_apollo_followup.svg` | the same, plus Apollo as a step curve with censoring ticks, its clock started at **age 25** (male mean age at first Games) |
| `fig2A_with_apollo_age.svg` | everything on an **age** axis: Olympian and population curves shifted by the sex-specific mean entry age (men +25, women +21), Apollo by attained age |
| `fig2B_p3_with_apollo_age.svg` | **the era-matched comparison.** p2/p3/p4 by age, rescaled to S(age)/S(30), with Apollo |
| `fig2C_with_apollo_age.svg` | cumulative death probability by age, published and rescaled-from-30 versions, with Apollo |
| `figS1C_with_apollo_age.svg` | the paper's **own** age-30 analysis with Apollo — no shift and no rescaling needed on either side |

### The alignment problem, and what was done about it

[AUTHOR]'s objection to the first attempt was right and it governs everything here. Panel 2A's x-axis is
follow-up from each athlete's *first Games*, at a mean age of about 25. Apollo's clock started at 30.
Two curves on those axes are not comparable. There are three honest fixes and all three are shipped:

- **Shift the Olympians onto an age axis** (`fig2A_with_apollo_age.svg`). Caveat that does not cancel:
  entry ages are a *distribution* (SD ≈ 5 yr), so adding a single mean translates each curve without
  reshaping it. The true age-scale curve is slightly flatter than the one drawn.
- **Use panels that are already on an age axis** (2B, 2C). Here the mismatch is the other way: those
  curves start at cohort entry, Apollo's at 30. ⚠️ **The paper never states how panel B handles
  delayed entry.** Its at-risk row for p3 (1, 1, 467, 1373, 1470, 1441, …) shows the risk set still
  *growing* past age 30, so athletes are clearly entering after 30, but no left-truncation method is
  described. Conditioning on S(30) is the right move given a survival-by-age curve; it is an
  assumption about the estimator the authors used, and it is named here rather than buried. Both are rescaled by conditioning on survival to 30 —
  S(a | alive at 30) = S(a)/S(30), and F(a | 30) = (F(a) − F(30))/(1 − F(30)). **This is my
  transformation, not the paper's**; the unconditioned values are kept in the CSVs alongside, and the
  published p3 is drawn faintly on the panel-B figure so the size of the correction is visible.
  For p3 the divisor is S(30) = 94.4 % — that 5.6 % is the **1961 air crash that killed the US
  figure-skating team**, which the supplementary file flags for period 3 specifically; conditioning on
  age 30 removes it, since those deaths were all under age 20.
- **Use the paper's own age-30 figure** (S1C). No shift, no rescaling, nothing assumed. It is the
  cleanest published comparator for an Apollo curve that begins at 30 — at the cost of a coarser panel
  and a narrower cohort ("athletes who had already been at Olympics by the age of 30", a restriction
  on *entry age*, not merely on survival).

### Confounds that could not be corrected, only stated

- **p3 pools both sexes; Apollo is all male.** Panel 2A shows female Olympians outliving male
  Olympians by about 9 years of median follow-up. So p3 sits *higher* than an all-male p3 would, and
  the confound works **against** Apollo, not for it.
- **No confidence band is drawn for Apollo.** With n = 29 it would be wide. The Olympian curves'
  published CI bands are also not digitized — only the point estimates are.
- **The Olympians are a selected cohort**, as the authors themselves say: at inclusion they were
  *"probably free of chronic diseases … amplifying, therefore, the difference in mortality"*. The
  astronauts were selected harder still. Neither curve is the general population.

## 12. What the comparison shows

Stated as arithmetic, with the caveats above standing. On the cleanest figure — S1C, the paper's own
age-30 analysis, no shifting and no rescaling — the Apollo astronauts' cumulative death probability
runs **below** the Olympians' from roughly age 62 to age 90, and both run well below the US general
population's. On the age-axis version of panel 2A the Apollo curve sits above the male Olympians for
most of the range and close to the female Olympians. On panel 2B, conditioned at 30, Apollo tracks
between p3 (its own era) and p4 (a later, longer-lived era) into the eighties.

n is 29. No interval is computed here, the age data are year-quantised, and the direction of the one
correctable confound (sex mixing in p3) already runs against Apollo. Read it as a well-founded
direction, not as an effect size.

## 13. Files

**Code** — `digitize_lib.py` (shared machinery), `digitize_fig2A.py`, `digitize_fig2B.py`,
`digitize_fig2C.py`, `digitize_figS1C.py`, `apollo_km.py`, `svg_lib.py`, `make_svgs.py`,
`verify.py`, `verify_crossrender.py`. Run in that order; each is standalone and prints its own
calibration and validation.

**Data** — `male_olympians.csv`, `female_olympians.csv`, `male_population.csv`,
`female_population.csv`, `points_raw.csv`, `fig2B_periods_by_age.csv`,
`fig2C_cumulative_death_by_age.csv`, `figS1C_cumulative_death_from_age30.csv`,
`apollo_km_by_age.csv`, `apollo_roster.csv`.

**Figures** — the six SVGs listed in §11.

**`_verify/`** — overlays, the matplotlib cross-render, SVG rasterisations, and a `*_meta.json` per
panel holding the full calibration, thresholds, coverage counts and the ambiguity lists.

**`_src/`** — the extracted supplementary figure PNGs and the fetched article PDF plus its text.
Read-only inputs; nothing under `Human Efforts/` was written to.
