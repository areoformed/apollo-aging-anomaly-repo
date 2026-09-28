#!/usr/bin/env python3
"""
figures.py — All figures for the Opus 4-8 SuperAger re-analysis.

G1  birth-year histogram (cohort ~1930 clustering)
G2  death/endpoint-age centrality by group (gen-pop-from-30 / non-Apollo / Apollo)
G5  SMR forest: Apollo vs pre-1970 flew-in-space non-Apollo (Byar CIs), + vs gen-pop
G10 KM Apollo vs pre-1970 flew non-Apollo (Greenwood CI, at-risk, censor ticks)
G12 4-way KM: Apollo / flew / never-flew / general population (Greenwood CI, at-risk, RMST note)
G3/G4 SMR visuals Apollo-vs-gen & non-Apollo-vs-gen (Byar)
HEAT  longevity x vitality probability heatmap (verify/extend run2)
SARATE SuperAger-rate forest: cohort conditional rates vs population anchors (cross-construct flagged)

All read from ../data/analysis_dataset.csv and ../outputs/*.csv (this folder only).
SVG + PNG to ../outputs/.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from lifelines import KaplanMeierFitter
from lifelines.utils import restricted_mean_survival_time

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
SRC = os.path.abspath(os.path.join(HERE, "..", "..",
        "Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))

plt.rcParams.update({"figure.dpi": 110, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False})
C = {"Apollo": "#c0392b", "flew": "#2471a3", "never": "#7d3c98",
     "genpop": "#566573", "pop": "#117a65"}

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))
d["birth_year"] = pd.to_datetime(d["date_of_birth"]).dt.year

def savefig(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {name}.svg/.png")

# ---- SSA life table for general-pop reference curve ----
lt = pd.read_csv(os.path.join(SRC, "data", "ssa-1930-male-cohort-lifetable.tsv"), sep="\t").sort_values("age")
l30 = lt.loc[lt.age == 30, "lx"].values[0]
lt["S30"] = np.where(lt.age >= 30, lt.lx/l30, np.nan)
ssa_ages = lt.loc[lt.age >= 30, "age"].values
ssa_S = lt.loc[lt.age >= 30, "S30"].values

# cohorts
apollo = d[d.cohort == "apollo"]
flew = d[(d.cohort == "nasa_nonapollo") & d.flew & ~d.pre1970_accidental_death]
never = d[(d.cohort == "nasa_nonapollo") & ~d.flew]

# ===================================================================== G1
fig, ax = plt.subplots(figsize=(8.5, 4.2))
bins = np.arange(1915, 1944) - 0.5
grp = {"Apollo": apollo, "NASA non-Apollo": d[d.cohort == "nasa_nonapollo"],
       "X-15/Dyna-Soar/MOL": d[d.cohort.isin(["x15", "dyna_soar", "mol"])]}
ax.hist([g.birth_year.values for g in grp.values()], bins=bins, stacked=True,
        label=list(grp.keys()), color=[C["Apollo"], C["flew"], C["genpop"]], edgecolor="white", lw=0.4)
ax.axvline(1930, color="k", ls="--", lw=1, alpha=0.6)
ax.text(1930.2, ax.get_ylim()[1]*0.92, "1930", fontsize=9)
ax.set_xlabel("Birth year"); ax.set_ylabel("Count")
ax.set_title("G1 — Birth-year distribution of the cohort (clustering near 1930)")
ax.legend(frameon=False, fontsize=9)
savefig(fig, "G1_birth_year_histogram")

# ===================================================================== G2
# Death/endpoint-age centrality: general-pop death-age dist (from SSA dx>=30), vs astronaut groups.
fig, ax = plt.subplots(figsize=(8.5, 4.6))
# general pop death-age density from dx (deaths at each age) conditioned on >=30
dx30 = lt.loc[lt.age >= 30, ["age", "dx"]].copy()
dens = dx30.dx / dx30.dx.sum()
ax.fill_between(dx30.age, dens*100, color=C["genpop"], alpha=0.25,
                label="US 1930 males (death-age dist | alive at 30)", step="mid")
# astronaut groups: show death ages (deceased only) as rug + violin-ish
for lbl, g, col in [("Apollo (deaths)", apollo, C["Apollo"]),
                    ("Non-Apollo flew (deaths)", flew, C["flew"])]:
    da = g.loc[g.deceased, "endpoint_age"].values
    ax.plot(da, np.full_like(da, -0.12 if "Apollo (d" in lbl else -0.24),
            "|", color=col, ms=14, label=f"{lbl}, median {np.median(da):.0f}")
    ax.axvline(np.median(da), color=col, ls=":", lw=1.2, alpha=0.7)
# living markers (Apollo)
liv = apollo.loc[~apollo.deceased, "endpoint_age"].values
ax.plot(liv, np.full_like(liv, -0.36), ">", color=C["Apollo"], ms=7,
        label=f"Apollo still-living (censored), {len(liv)} at {liv.min():.0f}-{liv.max():.0f}")
ax.set_xlim(30, 100); ax.set_ylim(-0.45, dens.max()*100*1.1)
ax.set_xlabel("Age"); ax.set_ylabel("US-male death-age density (%)")
ax.set_title("G2 — Death-age centrality by group vs general-population baseline")
ax.legend(frameon=False, fontsize=8, loc="upper left")
savefig(fig, "G2_death_age_centrality")

# ===================================================================== KM helpers
def fit(g, label):
    k = KaplanMeierFitter()
    k.fit(g.endpoint_age.values, g.deceased.astype(int).values,
          entry=np.full(len(g), 30.0), label=label)
    return k

def atrisk(g, ages):
    # delayed-entry risk set: entry=30 for all, at risk if 30<=t<=endpoint and not yet failed/censored before age a
    out = []
    for a in ages:
        n = int(((30.0 <= a) & (g.endpoint_age >= a)).sum())
        out.append(n)
    return out

def km_panel(groups, title, fname, rmst_t=None, rmst_pair=None):
    fig = plt.figure(figsize=(9, 6.4))
    gs = GridSpec(2, 1, height_ratios=[4, 1.1], hspace=0.08)
    ax = fig.add_subplot(gs[0]); axr = fig.add_subplot(gs[1], sharex=ax)
    ages_grid = np.arange(30, 101, 5)
    kms = {}
    for (lbl, g, col) in groups:
        k = fit(g, lbl); kms[lbl] = k
        k.plot_survival_function(ax=ax, color=col, ci_show=True, ci_alpha=0.12, lw=1.8)
        # censoring ticks (still living) at their ages
        cens = g.loc[~g.deceased, "endpoint_age"].values
        if len(cens):
            sf = k.survival_function_at_times(cens).values
            ax.plot(cens, sf, "+", color=col, ms=9, mew=1.6)
    ax.set_ylim(0, 1.02); ax.set_xlim(30, 100)
    ax.set_ylabel("Survival S(age) | alive at 30"); ax.set_title(title)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    # general pop overlay if present is handled by caller passing it as a group
    # at-risk table
    axr.axis("off")
    rows = []
    labels = [lbl for lbl, _, _ in groups]
    for i, (lbl, g, col) in enumerate(groups):
        ar = atrisk(g, ages_grid)
        for j, a in enumerate(ages_grid):
            axr.text(a, 0.8 - i*0.22, str(ar[j]), ha="center", va="center", fontsize=7.5, color=col)
        axr.text(28, 0.8 - i*0.22, lbl.split("(")[0].strip()[:18], ha="right", va="center",
                 fontsize=7.5, color=col)
    axr.text(28, 1.02, "At risk:", ha="right", va="center", fontsize=8, weight="bold")
    axr.set_xlim(30, 100); axr.set_ylim(0, 1.1)
    for a in ages_grid:
        axr.text(a, 1.02, str(a), ha="center", va="center", fontsize=7.5)
    if rmst_t and rmst_pair:
        a, b = rmst_pair
        ra = restricted_mean_survival_time(kms[a], t=rmst_t)
        rb = restricted_mean_survival_time(kms[b], t=rmst_t)
        ax.text(0.98, 0.97, f"RMST@{rmst_t}: {a.split('(')[0].strip()} {ra:.1f}y vs "
                f"{b.split('(')[0].strip()} {rb:.1f}y  (Δ={ra-rb:+.1f}y)",
                transform=ax.transAxes, ha="right", va="top", fontsize=8,
                bbox=dict(boxstyle="round", fc="#fbfcfc", ec="#aab"))
    savefig(fig, fname)

# G10 — Apollo vs flew
km_panel([("Apollo", apollo, C["Apollo"]),
          ("Non-Apollo flew (no pre1970 acc)", flew, C["flew"])],
         "G10 — Kaplan–Meier: Apollo vs pre-1970 flew-in-space non-Apollo\n"
         "(Greenwood CI shaded; + = still-living/censored)",
         "G10_km_apollo_vs_flew", rmst_t=90, rmst_pair=("Apollo", "Non-Apollo flew (no pre1970 acc)"))

# G12 — 4-way incl general population
fig = plt.figure(figsize=(9.2, 6.8))
gs = GridSpec(2, 1, height_ratios=[4, 1.3], hspace=0.08)
ax = fig.add_subplot(gs[0]); axr = fig.add_subplot(gs[1], sharex=ax)
groups4 = [("Apollo", apollo, C["Apollo"]),
           ("Non-Apollo flew", flew, C["flew"]),
           ("Non-Apollo never-flew", never, C["never"])]
kms = {}
for lbl, g, col in groups4:
    k = fit(g, lbl); kms[lbl] = k
    k.plot_survival_function(ax=ax, color=col, ci_show=True, ci_alpha=0.10, lw=1.8)
    cens = g.loc[~g.deceased, "endpoint_age"].values
    if len(cens):
        ax.plot(cens, k.survival_function_at_times(cens).values, "+", color=col, ms=9, mew=1.6)
ax.plot(ssa_ages, ssa_S, color=C["genpop"], ls="--", lw=1.8, label="US 1930 males (general pop)")
ax.set_ylim(0, 1.02); ax.set_xlim(30, 100)
ax.set_ylabel("Survival S(age) | alive at 30")
ax.set_title("G12 — 4-way Kaplan–Meier (Greenwood CI; + censored). Curves cross → RMST used, not log-rank.")
ax.legend(frameon=False, fontsize=9, loc="lower left")
# RMST annotations at t=90
rt = 90
note = "RMST@90 (from 30): " + ", ".join(
    f"{lbl.split('(')[0].strip()} {restricted_mean_survival_time(kms[lbl], t=rt):.1f}y"
    for lbl, _, _ in groups4)
ax.text(0.98, 0.97, note, transform=ax.transAxes, ha="right", va="top", fontsize=7.8,
        bbox=dict(boxstyle="round", fc="#fbfcfc", ec="#aab"))
axr.axis("off"); ages_grid = np.arange(30, 101, 5)
allg = groups4 + [("US 1930 males", None, C["genpop"])]
for i, (lbl, g, col) in enumerate(groups4):
    ar = atrisk(g, ages_grid)
    for j, a in enumerate(ages_grid):
        axr.text(a, 0.85 - i*0.2, str(ar[j]), ha="center", va="center", fontsize=7.3, color=col)
    axr.text(28, 0.85 - i*0.2, lbl[:16], ha="right", va="center", fontsize=7.3, color=col)
axr.text(28, 1.05, "At risk:", ha="right", va="center", fontsize=8, weight="bold")
for a in ages_grid:
    axr.text(a, 1.05, str(a), ha="center", va="center", fontsize=7.3)
axr.set_xlim(30, 100); axr.set_ylim(0, 1.15)
savefig(fig, "G12_km_4way")

# ===================================================================== G5 / G3 / G4 SMR forest
smr = pd.read_csv(os.path.join(OUT, "smr_results.csv"))
fig, ax = plt.subplots(figsize=(8.6, 3.6))
order = ["Apollo", "NASA non-Apollo flew (no pre1970 acc)", "GPT available non-Apollo (55)"]
sub = smr.set_index("cohort").loc[order].reset_index()
ypos = np.arange(len(sub))[::-1]
ax.errorbar(sub.SMR_rate, ypos,
            xerr=[sub.SMR_rate - sub.SMR_rate_lo_byar, sub.SMR_rate_hi_byar - sub.SMR_rate],
            fmt="o", color="#1f3b57", capsize=4, ms=7)
for y, (_, r) in zip(ypos, sub.iterrows()):
    ax.text(r.SMR_rate_hi_byar + 0.02, y, f"{r.SMR_rate:.2f} [{r.SMR_rate_lo_byar:.2f},{r.SMR_rate_hi_byar:.2f}]",
            va="center", fontsize=8)
ax.axvline(1.0, color="k", ls=":", lw=1)
ax.set_yticks(ypos); ax.set_yticklabels([s.replace(" (no pre1970 acc)", "\n(no pre1970 acc)") for s in sub.cohort], fontsize=8)
ax.set_xlabel("SMR (rate) vs US 1930 males, age-30 conditioned — Byar exact-Poisson 95% CI")
ax.set_title("G5/G3 — SMR forest: all selected-astronaut groups are protected (~0.4–0.55)\n"
             "= healthy-selectee effect, NOT Apollo-specific")
ax.set_xlim(0, 1.3)
savefig(fig, "G5_smr_forest")

# ===================================================================== SuperAger-rate forest (the headline)
sa = pd.read_csv(os.path.join(OUT, "superager_rates_by_cohort.csv"))
anchors = pd.read_csv(os.path.join(OUT, "superager_population_anchors.csv"))
fig, ax = plt.subplots(figsize=(9, 4.8))
rowdefs = [("Apollo", C["Apollo"]),
           ("NASA non-Apollo, flew (no pre1970 acc)", C["flew"]),
           ("NASA non-Apollo, never flew", C["never"]),
           ("GPT 'available' non-Apollo (55)", C["genpop"])]
y = len(rowdefs) + len(anchors) + 1
yt, ylab, ycol = [], [], []
for lbl, col in rowdefs:
    r = sa[sa.cohort == lbl].iloc[0]
    ax.errorbar(r.cond_rate, y, xerr=[[r.cond_rate - r.cond_lo], [r.cond_hi - r.cond_rate]],
                fmt="o", color=col, capsize=3, ms=7)
    ax.text(1.005, y, f"{r.superagers:.0f}/{r.reached_80:.0f}={r.cond_rate*100:.0f}%", va="center", fontsize=8, color=col)
    yt.append(y); ylab.append(lbl[:34] + " [vitality | 80+]"); ycol.append(col); y -= 1
y -= 0.6
# population anchors (vertical bands)
for _, a in anchors.iterrows():
    ax.scatter(a["rate"], y, marker="s", color=C["pop"], s=42)
    note = f'{a["rate"]*100:.0f}%  ({a["construct"][:24]})'
    ax.text(1.005, y, note, va="center", fontsize=7.5, color=C["pop"])
    yt.append(y); ylab.append("pop: " + a["key"][:26]); ycol.append(C["pop"]); y -= 1
ax.set_yticks(yt); ax.set_yticklabels(ylab, fontsize=7.6)
for t, c in zip(ax.get_yticklabels(), ycol): t.set_color(c)
ax.set_xlim(0, 1.0); ax.set_xlabel("SuperAger rate among 80+ survivors  (cohort: public-activity proxy; pop: clinical — CROSS-CONSTRUCT)")
ax.set_title("SuperAger-rate forest — Apollo 95% vs comparator astronauts (~67-70%) and population anchors\n"
             "Cohort rate = visible vitality (positive proxy); population = clinical dementia-free/cognition (different construct)")
savefig(fig, "SARATE_superager_rate_forest")

# ===================================================================== Heatmap (verify/extend run2)
# Joint exact P(N80>=22 AND N90>=13 AND vital_count>=21) over hazard-scale h x vitality-rate p.
from numpy import convolve
def ssa_S_at(age):
    a = int(np.floor(age))
    s = lt.set_index("age")["S30"]
    if a <= 30: return 1.0
    if a >= lt.age.max(): return max(s.get(int(lt.age.max()), 1e-9), 1e-12)
    s0 = s.get(a, np.nan); s1 = s.get(a+1, np.nan)
    if np.isnan(s0): return 1.0
    if np.isnan(s1): return s0
    return s0 + (s1-s0)*(age-a)
S80 = ssa_S_at(80); S90 = ssa_S_at(90); S95 = ssa_S_at(95)
def cat_probs(h):
    p80 = S80**h; p90 = S90**h; p95 = S95**h
    return np.array([1-p80, p80-p90, p90-p95, p95])  # <80, [80,90), [90,95), >=95
def joint_prob(h, p, n=29, n80=22, n90=13, vit=21):
    cp = cat_probs(h)
    # multinomial over 4 categories for n people; need N80>=n80 and N90>=n90 and vital>=vit
    # iterate counts (c0..c3) feasibly: enumerate c_ge90 (=c2+c3) and c_8089
    from math import comb
    tot = 0.0
    p_lt80, p_8090, p_9095, p_95 = cp
    p_ge90 = p_9095 + p_95
    p_ge80 = p_8090 + p_ge90
    for k80 in range(n80, n+1):           # survivors to 80
        # P(N80=k80)
        pk80 = comb(n, k80) * (p_ge80**k80) * (p_lt80**(n-k80))
        # among k80, split into [80,90) vs >=90, need >=n90 reach 90
        q90 = p_ge90 / p_ge80
        # vitality among k80 survivors: Binomial(k80,p) need >=vit
        # build vitality tail once
        vit_tail = sum(comb(k80, v)*(p**v)*((1-p)**(k80-v)) for v in range(vit, k80+1)) if k80>=vit else 0.0
        n90_prob = sum(comb(k80, j)*(q90**j)*((1-q90)**(k80-j)) for j in range(n90, k80+1))
        tot += pk80 * n90_prob * vit_tail
    return tot
hs = np.round(np.arange(1.0, 0.44, -0.05), 3)
ps = np.round(np.arange(0.30, 0.971, 0.05), 3)
Z = np.array([[joint_prob(h, p) for p in ps] for h in hs])
# For plotting with origin="lower", rows must run from LOW y (h=0.45) to HIGH y (h=1.0).
# hs is descending, so flip Z and hs for the image; keep Z/hs as-is for the CSV dump.
hs_asc = hs[::-1]
Z_asc = Z[::-1, :]
fig, ax = plt.subplots(figsize=(8.8, 5))
im = ax.imshow(np.log10(np.clip(Z_asc, 1e-30, 1)), aspect="auto", cmap="viridis",
               extent=[ps.min()*100, ps.max()*100, hs_asc.min(), hs_asc.max()], origin="lower")
cb = fig.colorbar(im, ax=ax); cb.set_label("log10  P(N80≥22 & N90≥13 & vital≥21)")
# mark key anchors on p-axis
for a, lab in [(0.866, "demfree80-84"), (0.697, "demfree90-94"), (0.68, "HCAP"), (0.955, "Apollo-obs")]:
    ax.axvline(a*100, color="white", ls=":", lw=0.8, alpha=0.6)
ax.axhline(0.457, color="white", ls="--", lw=0.9)
# Apollo observed operating point: SMR-like hazard 0.457, observed vitality 95.5%
ax.scatter(95.5, 0.457, marker="*", s=220, color="#ff2d55", edgecolor="white", lw=0.8, zorder=5)
ax.annotate("Apollo observed\n(h≈0.46, vitality 95.5%)", xy=(95.5, 0.457),
            xytext=(72, 0.52), color="white", fontsize=8,
            arrowprops=dict(arrowstyle="->", color="white", lw=0.9))
ax.set_xlabel("Vitality rate among 80+ survivors (%)  [population proxy]")
ax.set_ylabel("Hazard scale h  (1.0 = SSA general; 0.457 = Apollo-SMR-like)")
ax.set_title("HEAT — Joint probability of Apollo-like longevity+vitality under (hazard × vitality) grid\n"
             "Even at Apollo-SMR-like hazard, the observed vitality rate sits at the improbable edge")
savefig(fig, "HEAT_longevity_vitality_grid")
# also dump the grid
pd.DataFrame(Z, index=[f"h={h}" for h in hs], columns=[f"p={p}" for p in ps]).to_csv(
    os.path.join(OUT, "heatmap_joint_prob_grid.csv"))
print("[write] heatmap_joint_prob_grid.csv")
print("\nALL FIGURES DONE.")
