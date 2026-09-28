#!/usr/bin/env python3
"""
permutation.py — Vitality-rate permutation test on the 84-person pool.

Pool = GPT-5.5 'available' cohort (included_in_apollo_vs_other_available == True):
Apollo 29 + 55 non-accident-death others = 84. Under random Apollo-sized (n=29) draws
WITHOUT replacement from the pool, where does the OBSERVED Apollo SuperAger rate fall?

This is ASCERTAINMENT-HONEST in a specific sense: it asks whether Apollo's vitality outcome
is exchangeable with the rest of the SAME pool of selected astronauts (who share the same
public-documentation regime to first order). It does NOT compare to the general population;
it asks "is Apollo special WITHIN the astronaut pool". POSITIVE framing: statistic = count
of SuperAgers (visible vitality), higher = more vital, no decline imputed.

Two statistics, both reported:
  S1 = number of SuperAgers in the draw (unconditional, out of 29) -> confounds survival+vitality.
  S2 = conditional SuperAger rate among the draw's 80+ survivors -> isolates vitality-given-survival
       (the corrected estimand's core). Draws with <1 survivor excluded for S2.

Permutation p = P(stat_random >= stat_apollo).
Outputs: permutation_summary.csv, permutation_null_S1.csv, permutation_null_S2.csv
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))
pool = d[d.included_in_apollo_vs_other_available == True].copy().reset_index(drop=True)
assert len(pool) == 84, len(pool)
n_apollo = int((pool.cohort == "apollo").sum())
assert n_apollo == 29

reached80 = pool.reached_80.astype(bool).values
superager = pool.superager.astype(bool).values
N = len(pool)

# Observed Apollo
ap = pool[pool.cohort == "apollo"]
obs_S1 = int(ap.superager.sum())                       # 21
obs_surv = int(ap.reached_80.sum())                    # 22
obs_S2 = obs_S1 / obs_surv                              # 21/22

rng = np.random.default_rng(15170648)
B = 200_000
idx_all = np.arange(N)
S1 = np.empty(B, dtype=int)
S2 = np.full(B, np.nan)
for b in range(B):
    draw = rng.choice(idx_all, size=n_apollo, replace=False)
    sa = superager[draw].sum()
    surv = reached80[draw].sum()
    S1[b] = sa
    if surv > 0:
        S2[b] = sa / surv

p_S1 = (S1 >= obs_S1).mean()
valid = ~np.isnan(S2)
p_S2 = (S2[valid] >= obs_S2 - 1e-12).mean()

summ = pd.DataFrame([
    dict(statistic="S1_superager_count_of_29", observed=obs_S1,
         null_mean=S1.mean(), null_p95=np.percentile(S1, 95), perm_p_ge=p_S1, draws=B),
    dict(statistic="S2_conditional_rate_among_survivors", observed=obs_S2,
         null_mean=np.nanmean(S2), null_p95=np.nanpercentile(S2, 95), perm_p_ge=p_S2,
         draws=int(valid.sum())),
])
summ.to_csv(os.path.join(OUT, "permutation_summary.csv"), index=False)

# null distributions (binned)
s1tab = pd.Series(S1).value_counts().sort_index().rename("count").reset_index()
s1tab.columns = ["S1_value", "count"]
s1tab["frac"] = s1tab["count"] / B
s1tab.to_csv(os.path.join(OUT, "permutation_null_S1.csv"), index=False)

s2bins = np.linspace(0, 1, 21)
s2hist, edges = np.histogram(S2[valid], bins=s2bins)
pd.DataFrame({"bin_lo": edges[:-1], "bin_hi": edges[1:], "count": s2hist,
             "frac": s2hist/valid.sum()}).to_csv(
    os.path.join(OUT, "permutation_null_S2.csv"), index=False)

print("=" * 90)
print(f"PERMUTATION on 84-person pool (Apollo 29 + 55 others). {B:,} draws of size 29.")
print("  Positive-rate framing: statistic = SuperAger COUNT/RATE (visible vitality). No decline.")
print("=" * 90)
print(f"  S1 (SuperAger count of 29):   observed={obs_S1}  null mean={S1.mean():.2f}  "
      f"null p95={np.percentile(S1,95):.0f}  perm p(>= obs)={p_S1:.4f}")
print(f"  S2 (cond. rate among 80+):    observed={obs_S2:.3f} ({obs_S1}/{obs_surv})  "
      f"null mean={np.nanmean(S2):.3f}  null p95={np.nanpercentile(S2,95):.3f}  perm p(>= obs)={p_S2:.4f}")
print("\n  NOTE: S1 confounds survival+vitality (Apollo also survives slightly more);")
print("        S2 isolates the corrected estimand (vitality given survival).")
print("\n[write] outputs/permutation_summary.csv, permutation_null_S1.csv, permutation_null_S2.csv")
