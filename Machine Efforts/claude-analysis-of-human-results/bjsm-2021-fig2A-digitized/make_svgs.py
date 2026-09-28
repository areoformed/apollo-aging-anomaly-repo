#!/usr/bin/env python3
"""Redraw the digitized values as hand-rolled SVGs, and overlay the Apollo astronauts' KM."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import apollo_km
import svg_lib as S

HERE = Path(__file__).resolve().parent

# Baseline age at first Olympic Games. NOT reported in the BJSM paper or its supplement;
# taken from the same group's open-access companion study on the SAME US Olympian cohort:
# Antero J et al., "Heads-Up: Risk-Specific Neurodegenerative Mortality and Years-Saved
# Analysis on the US Olympian Cohort", Front Physiol 2021;12:705616, Table 2 (Games 1912-1972).
# Confirmed against the primary full text (Europe PMC PMC8458956 XML, _src/frontiers2021_PMC8458956.xml):
#   "Mean age at the first OG in years (SD)" | 1948-1972: N 24 (5.16), Female 21 (4.41), Male 24 (4.98)
#                                            | 1912-1972: N 24 (5.05), Female 21 (4.41), Male 25 (4.87)
BASE_M, BASE_M_SD = 25, 4.87
BASE_F, BASE_F_SD = 21, 4.41

CIT = ("Redrawn from digitized values of Figure 2A in Antero et al., Br J Sports Med "
       "2021;55:206-212; digitization accuracy ±1 px (≈±0.3 % survival, ±0.2 yr).")
RIGHTS = ("Source figure © Author(s) (or their employer(s)) 2020, published by BMJ; "
          "\"No commercial re-use.\" No raster from the original is reproduced here.")

COL = {
    "male_olympians": "#1f3a93",
    "female_olympians": "#14622f",
    "male_population": "#5f7fd0",
    "female_population": "#8aa628",
    "apollo": "#d64500",
    "p2": "#b03060", "p3": "#14622f", "p4": "#1f3a93",
    "population": "#111111", "olympians": "#0f7f80",
}


# ---------------------------------------------------------------- SSA 1930 male birth cohort (TR2024 Alt2)
# Added 2026-09-15 at [AUTHOR]'s ask ("Can we do it now?") so the draft's sentence "alongside social security
# data" is true of THIS figure. Source: her own generated header, Human Efforts/scripts/Astronaut MR /
# 1930CohortSSAData.h, built by "ssa 1930 cohort c-lib gen.py" from CohLifeTables_M_Alt2_TR2024.csv
# (SSA Actuarial Study 120, cohort life table, MALE, alternative 2, 1930 birth year). Same table smr.c uses.
SSA_H = (HERE.parent.parent.parent / "Human Efforts" / "scripts" / "Astronaut MR " / "1930CohortSSAData.h")
SSA_LABEL = "US general population, SSA 1930 male birth cohort, from age 30 (TR2024 Alt2)"
COL["ssa1930"] = "#552a1e"


def ssa1930_cond30():
    """Cumulative death probability conditional on survival to 30 from the SSA cohort table:
    F(x|30) = 1 - l(x)/l(30). Returns (ages, F) on the integer ages 30..100, plus l(x) for the CSV."""
    import re
    lx = {}
    for m in re.finditer(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}", SSA_H.read_text()):
        lx[int(m.group(1))] = int(m.group(2))
    l30 = lx[30]
    ages = np.arange(30, 101, dtype=float)
    F = np.array([1.0 - lx[int(a)] / l30 for a in ages])
    return ages, F, lx


def load_2A():
    a = np.load(HERE / "_verify" / "fig2A_series.npy")
    return a[0], dict(zip(["male_olympians", "female_olympians",
                           "male_population", "female_population"], a[1:]))


def apollo():
    rows = apollo_km.load()
    t, s = apollo_km.km([(r[3], r[4]) for r in rows])
    ages = np.concatenate([[30.0], t])
    surv = np.concatenate([[1.0], s]) * 100.0
    cens = sorted(r[3] for r in rows if r[4] == 0)
    cens_s = [float(apollo_km.step_at(t, s, c)[0] * 100) for c in cens]
    return rows, ages, surv, cens, cens_s


def write(name, svg):
    (HERE / name).write_text(svg)
    print("wrote", name)


def main():
    grid, S2A = load_2A()
    rows, a_age, a_surv, cens, cens_s = apollo()
    n_d = sum(1 for r in rows if r[4] == 1)

    # ------------------------------------------------------------------ (a) 2A redrawn
    c = S.Chart((0, 84), (0, 100), "Follow-up time since first Olympic Games (years)",
                "Survival probability", "US Olympians vs their general-population referents",
                [0, 10, 20, 30, 40, 50, 60, 70, 80], [0, 25, 50, 75, 100])
    for k, dash in (("female_olympians", None), ("male_olympians", None),
                    ("female_population", "3 4"), ("male_population", "3 4")):
        c.path(f"curve-{k.replace('_','-')}", grid, S2A[k], COL[k], 2.2, dash)
    for k, lbl, dash in (("male_olympians", "Male Olympians", None),
                         ("female_olympians", "Female Olympians", None),
                         ("male_population", "Male population (US life tables)", "3 4"),
                         ("female_population", "Female population (US life tables)", "3 4")):
        c.add_legend(lbl, COL[k], dash)
    write("fig2A_redrawn_followup.svg", c.render([
        "**" + CIT,
        RIGHTS,
        "Four curves digitized by colour mask from the published panel, resampled to a 1-year grid.",
        "Validation against numbers printed in the paper's Results: median survival after the Games,",
        "male 56.5 yr digitized vs 56.7 reported (95% CI 55.8-57.3); female 65.8 vs 66.0 (63.0-67.6).",
        "Cohort: 8124 US Olympians (5823 men, 2301 women), Games 1912-2012, followed to 1 January 2016.",
    ], legend_x=S.L + 30, legend_y=S.T + 190))

    # ------------------------------------------------------------------ (b) 2A + Apollo, follow-up
    c = S.Chart((0, 84), (0, 100), "Follow-up time (years since cohort entry)",
                "Survival probability",
                "Apollo astronauts on the Olympians' follow-up clock",
                [0, 10, 20, 30, 40, 50, 60, 70, 80], [0, 25, 50, 75, 100])
    for k, dash in (("female_olympians", None), ("male_olympians", None),
                    ("female_population", "3 4"), ("male_population", "3 4")):
        c.path(f"curve-{k.replace('_','-')}", grid, S2A[k], COL[k], 2.0, dash, opacity=0.85)
    # start the drawn path at follow-up 0 (age 25): all 29 were alive then, S = 1 by definition
    a_age_fu = np.concatenate([[float(BASE_M)], a_age])
    a_surv_fu = np.concatenate([[100.0], a_surv])
    c.path("apollo-km", a_age_fu - BASE_M, a_surv_fu, COL["apollo"], 2.8, step=True)
    c.ticks_marks("apollo-censoring-ticks", np.array(cens) - BASE_M, cens_s, COL["apollo"])
    for k, lbl, dash in (("male_olympians", "Male Olympians", None),
                         ("female_olympians", "Female Olympians", None),
                         ("male_population", "Male population", "3 4"),
                         ("female_population", "Female population", "3 4")):
        c.add_legend(lbl, COL[k], dash, 2.0)
    c.add_legend(f"Apollo astronauts (n=29, {n_d} deaths), from age {BASE_M}", COL["apollo"], None, 2.8)
    write("fig2A_with_apollo_followup.svg", c.render([
        "**ALIGNMENT ASSUMPTION: Apollo's follow-up clock is started at age " + str(BASE_M) +
        ", the reported mean age at first Games for male US Olympians",
        f"({BASE_M} yr, SD {BASE_M_SD}) - Antero et al., Front Physiol 2021;12:705616, Table 2, "
        "Games 1912-1972. That value is NOT in the BJSM paper;",
        "it comes from the same authors' companion study on the same cohort over a shorter Games window. "
        "All 29 Apollo astronauts were",
        "alive at 25 and at 30 (earliest death age 51), so the shift loses no one. Ticks mark the 6 living, "
        "censored at 2026 minus birth year.",
        "The Olympians entered at a SPREAD of ages (SD ~5 yr), so shifting by a single mean is an "
        "approximation: it translates the curve, it does not reshape it.",
        CIT, RIGHTS,
    ], legend_x=S.L + 30, legend_y=S.T + 168))

    # ------------------------------------------------------------------ (c) 2A + Apollo, age axis
    c = S.Chart((20, 106), (0, 100), "Attained age (years)", "Survival probability",
                "The logically aligned version: everything on an age axis",
                [20, 30, 40, 50, 60, 70, 80, 90, 100], [0, 25, 50, 75, 100])
    for k, base, dash in (("female_olympians", BASE_F, None), ("male_olympians", BASE_M, None),
                          ("female_population", BASE_F, "3 4"), ("male_population", BASE_M, "3 4")):
        c.path(f"curve-{k.replace('_','-')}", grid + base, S2A[k], COL[k], 2.0, dash, opacity=0.85)
    c.path("apollo-km", a_age, a_surv, COL["apollo"], 2.8, step=True)
    c.ticks_marks("apollo-censoring-ticks", cens, cens_s, COL["apollo"])
    for k, lbl, base, dash in (("male_olympians", f"Male Olympians (shifted +{BASE_M} yr)", BASE_M, None),
                               ("female_olympians", f"Female Olympians (shifted +{BASE_F} yr)", BASE_F, None),
                               ("male_population", "Male population", BASE_M, "3 4"),
                               ("female_population", "Female population", BASE_F, "3 4")):
        c.add_legend(lbl, COL[k], dash, 2.0)
    c.add_legend(f"Apollo astronauts (n=29), attained age", COL["apollo"], None, 2.8)
    write("fig2A_with_apollo_age.svg", c.render([
        "**Every curve on one age axis. Olympian and population curves are shifted by the mean age at "
        "first Games: men +25 yr (SD 4.87), women +21 (SD 4.41)",
        "(Antero et al., Front Physiol 2021;12:705616, Table 2, Games 1912-1972 - the BJSM paper itself "
        "reports no baseline age).",
        "Two caveats that do not cancel. (1) Entry ages are a distribution, not a point: shifting by the "
        "mean translates each curve without reshaping it,",
        "so the true age-scale curve is slightly flatter than the one drawn here. (2) The Olympian curves "
        "start at survival = 1 at entry; the Apollo curve",
        "starts at survival = 1 at age 30 and is therefore conditional on survival to 30 - which costs "
        "nothing, since all 29 were alive then.",
        CIT, RIGHTS,
    ], legend_x=S.L + 30, legend_y=S.T + 160))

    # ------------------------------------------------------------------ (d) 2B p3 + Apollo  [PRIMARY]
    mb = json.loads((HERE / "_verify" / "fig2B_meta.json").read_text())
    ab = np.load(HERE / "_verify" / "fig2B_series.npy")
    gb = ab[0]
    raw = {"p2": ab[1], "p3": ab[2], "p4": ab[3]}
    cond = {"p2": ab[4], "p3": ab[5], "p4": ab[6]}
    c = S.Chart((30, 106), (0, 100), "Attained age (years)",
                "Survival probability, conditional on being alive at 30",
                "Apollo astronauts against the era-matched Olympian cohort (Figure 2B, p3)",
                [30, 40, 50, 60, 70, 80, 90, 100], [0, 25, 50, 75, 100])
    c.path("curve-p3-unconditioned", gb, raw["p3"], COL["p3"], 1.4, "2 4", opacity=0.55)
    for k, lbl in (("p2", "p2  Olympians 1920-1936"), ("p3", "p3  Olympians 1948-1964"),
                   ("p4", "p4  Olympians 1968-1984")):
        c.path(f"curve-{k}", gb, cond[k], COL[k], 2.4 if k == "p3" else 1.9,
               None, opacity=1.0 if k == "p3" else 0.75)
    c.path("apollo-km", a_age, a_surv, COL["apollo"], 2.8, step=True)
    c.ticks_marks("apollo-censoring-ticks", cens, cens_s, COL["apollo"])
    c.add_legend("p3  Olympians 1948-1964 (Apollo's era)", COL["p3"], None, 2.4)
    c.add_legend("p3 unconditioned (as published)", COL["p3"], "2 4", 1.4)
    c.add_legend("p2  Olympians 1920-1936", COL["p2"], None, 1.9)
    c.add_legend("p4  Olympians 1968-1984", COL["p4"], None, 1.9)
    c.add_legend(f"Apollo astronauts (n=29, {n_d} deaths)", COL["apollo"], None, 2.8)
    write("fig2B_p3_with_apollo_age.svg", c.render([
        "**Panel B is already on an age axis, so no baseline shift is needed. p3 is the era-matched "
        "cohort: Olympians who competed 1948-1964,",
        "**against Apollo astronauts born 1923-1937 and selected 1959-1966.",
        "The Olympian curves are rescaled to S(age)/S(30) so that both sides start from 'alive at 30', "
        "which is where Apollo's curve begins.",
        f"For p3 the divisor is S(30) = {mb['S30_percent']['p3_1948_1964']:.1f} % - the drop is the "
        "1961 air crash that killed the US figure-skating team,",
        "flagged in the paper's supplementary file; conditioning on age 30 removes it. The published, "
        "unconditioned p3 is drawn faintly for comparison.",
        "Two confounds, both stated rather than corrected: p3 pools both sexes while Apollo is all male "
        "(women outlived men by ~9 yr of median follow-up",
        "in panel A, so this biases p3 upward, against Apollo); and panel B's curves carry CI bands that "
        "overlap heavily above age 60 - p3 was resolved in",
        "73 % of pixel columns, p2 in 65 %, p4 in 53 %, with gaps interpolated. Redrawn from digitized "
        "values of Figure 2B; " + RIGHTS,
    ], legend_x=S.L + 30, legend_y=S.T + 30))

    # ------------------------------------------------------------------ (e) 2C + Apollo
    ac = np.load(HERE / "_verify" / "fig2C_series.npy")
    gc, oly, pop = ac[0], ac[1], ac[2]

    def cond_F(F, g):
        F30 = np.interp(30.0, g, np.nan_to_num(F))
        out = (F - F30) / (1 - F30)
        out[g < 30] = np.nan
        return np.clip(out, 0, 1)

    c = S.Chart((30, 100), (0, 1), "Attained age (years)",
                "Cumulative probability of death", "Cumulative death probability from age 30",
                [30, 40, 50, 60, 70, 80, 90, 100], [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                ytickfmt=lambda v: f"{v:g}")
    c.path("curve-population-published", gc, pop, COL["population"], 1.3, "2 4", opacity=0.5)
    c.path("curve-olympians-published", gc, oly, COL["olympians"], 1.3, "2 4", opacity=0.5)
    c.path("curve-population-cond30", gc, cond_F(pop, gc), COL["population"], 2.2)
    c.path("curve-olympians-cond30", gc, cond_F(oly, gc), COL["olympians"], 2.2)
    ssa_age, ssa_F, ssa_lx = ssa1930_cond30()
    c.path("curve-ssa1930-cond30", ssa_age, ssa_F, COL["ssa1930"], 2.2, "6 3")
    c.path("apollo-cumulative-death", a_age, 1 - a_surv / 100, COL["apollo"], 2.8, step=True)
    c.ticks_marks("apollo-censoring-ticks", cens, [1 - s / 100 for s in cens_s], COL["apollo"])
    c.add_legend("US general population, from age 30", COL["population"], None, 2.2)
    c.add_legend("US Olympians, from age 30", COL["olympians"], None, 2.2)
    c.add_legend("as published (from cohort entry)", "#777777", "2 4", 1.3)
    c.add_legend(SSA_LABEL, COL["ssa1930"], "6 3", 2.2)
    c.add_legend(f"Apollo astronauts (n=29, {n_d} deaths)", COL["apollo"], None, 2.8)
    with open(HERE / "ssa1930_cumulative_death_from_age30.csv", "w") as fh:
        fh.write("age_years,l_x_ssa1930_male_alt2,cum_death_prob_from_30\n")
        for a, F in zip(ssa_age, ssa_F):
            fh.write(f"{int(a)},{ssa_lx[int(a)]},{F:.5f}\n")
    print("wrote ssa1930_cumulative_death_from_age30.csv")
    write("fig2C_with_apollo_age.svg", c.render([
        "**Brown dashed: SSA 1930 male birth-cohort table (Actuarial Study 120, TR2024 Alt2), the table smr.c uses, "
        "as 1 - l(age)/l(30).",
        "**It is a COHORT table for one birth year; the paper's black referent is a PERIOD table matched to each "
        "Olympian's sex and calendar year. Built differently,",
        "**they nonetheless agree: over ages 30-88 the mean gap is 0.013 in probability, the largest 0.062 "
        "(at 69, a digitization step), mean signed difference 0.001.",
        "**Figure 2C digitized as a stacked area: teal fill = Olympians, black curve on top of the grey "
        "wedge = the US general population.",
        "Solid lines are rescaled to start from age 30, F(age|30) = (F(age) - F(30)) / (1 - F(30)), so "
        "they begin where Apollo's curve begins;",
        "the published curves, which run from cohort entry, are drawn faintly behind them.",
        "Independent check on this digitization: the area between the two published curves from age 25 "
        "to 90 comes to 5.28 years, against the",
        "paper's headline years-saved of 5.1 (95% CI 4.3 to 6.0). The paper computes that per individual, "
        "so agreement this close is corroboration,",
        "not reproduction. Redrawn from digitized values of Figure 2C in Antero et al., "
        "Br J Sports Med 2021;55:206-212. " + RIGHTS,
    ], legend_x=S.L + 30, legend_y=S.T + 30))

    # ------------------------------------------------------------------ (f) S1C + Apollo
    asr = np.load(HERE / "_verify" / "figS1C_series.npy")
    gs, olys, pops = asr[0], asr[1], asr[2]
    c = S.Chart((30, 100), (0, 1), "Attained age (years)",
                "Cumulative probability of death",
                "The paper's own age-30 figure (Supplementary Figure S1C) with Apollo",
                [30, 40, 50, 60, 70, 80, 90, 100], [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                ytickfmt=lambda v: f"{v:g}")
    c.path("curve-population", gs, pops, COL["population"], 2.2)
    c.path("curve-olympians", gs, olys, COL["olympians"], 2.2)
    c.path("curve-ssa1930-cond30", ssa_age, ssa_F, COL["ssa1930"], 2.2, "6 3")
    c.path("apollo-cumulative-death", a_age, 1 - a_surv / 100, COL["apollo"], 2.8, step=True)
    c.ticks_marks("apollo-censoring-ticks", cens, [1 - s / 100 for s in cens_s], COL["apollo"])
    c.add_legend("US general population", COL["population"], None, 2.2)
    c.add_legend("US Olympians at a Games by age 30", COL["olympians"], None, 2.2)
    c.add_legend(SSA_LABEL, COL["ssa1930"], "6 3", 2.2)
    c.add_legend(f"Apollo astronauts (n=29, {n_d} deaths)", COL["apollo"], None, 2.8)
    write("figS1C_with_apollo_age.svg", c.render([
        "**Supplementary Figure S1C is the authors' OWN age-30 analysis - \"Cumulative probability of "
        "death conditional to the age of first Olympic",
        "**participation ... C) From age 30 onwards\" - so no baseline shift and no rescaling are needed "
        "on either side. It is the cleanest published",
        "**comparator for an Apollo curve that starts at 30.",
        "Its cohort is narrower than Figure 2C's: athletes who had ALREADY been to a Games by age 30, "
        "a restriction on entry age, not merely on",
        "survival. The panel is also small - 228 x 287 px for the whole plot, so 1 px = 0.38 yr and "
        "0.0038 probability units, roughly three times",
        "coarser than Figure 2A. Area between the two curves, ages 43-90: 5.73 yr (paper's whole-cohort "
        "years-saved 5.1, 95% CI 4.3-6.0).",
        "Redrawn from digitized values of Supplementary material 1, page 3, Figure S1 panel C, "
        "Antero et al., Br J Sports Med 2021;55:206-212. " + RIGHTS,
    ], legend_x=S.L + 30, legend_y=S.T + 30))


if __name__ == "__main__":
    main()
