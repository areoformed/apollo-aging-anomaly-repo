#!/usr/bin/env python3
"""
selection_strata.py — Selection-group stratification (sample-stability robustness).

Does the SuperAger signal hold across NASA selection groups despite selection criteria
loosening over time (Mercury 7 hardest -> later groups looser)? If the vitality signal is
an artifact of one anomalous subgroup, stratification will reveal it. POSITIVE framing.

We tabulate, per selection group (across the WHOLE NASA pool, Apollo + non-Apollo, since
groups span both): N, reached-80, SuperAgers, conditional rate. Then specifically within
Apollo, by selection group.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))
d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))

def cp_ci(k, n, alpha=0.05):
    if n == 0: return (np.nan, np.nan)
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha/2, k, n-k+1)
    hi = 1.0 if k == n else stats.beta.ppf(1-alpha/2, k+1, n-k)
    return lo, hi

# NASA selection groups only (exclude X-15/DynaSoar/MOL-only military programs)
nasa = d[d.cohort.isin(["apollo", "nasa_nonapollo"])].copy()

def strat(df, by):
    rows = []
    for g, m in df.groupby(by):
        n = len(m); r80 = int(m.reached_80.sum()); sa = int(m.superager.sum())
        lo, hi = cp_ci(sa, r80) if r80 else (np.nan, np.nan)
        rows.append(dict(group=g, N=n, reached_80=r80, superagers=sa,
                         cond_rate=sa/r80 if r80 else np.nan, cond_lo=lo, cond_hi=hi,
                         uncond_rate=sa/n))
    return pd.DataFrame(rows).sort_values("group")

# order selection groups chronologically
order = ["Mercury Seven", "The New Nine", "The Fourteen", "The Original Nineteen",
         "The Scientists", "The Excess Eleven", "MOL Transfer"]
allgrp = strat(nasa, "selection_group_short")
allgrp["ord"] = allgrp.group.map({g: i for i, g in enumerate(order)}).fillna(99)
allgrp = allgrp.sort_values("ord").drop(columns="ord")
allgrp.to_csv(os.path.join(OUT, "selection_strata_all_nasa.csv"), index=False)

apollo = nasa[nasa.cohort == "apollo"]
apgrp = strat(apollo, "selection_group_short")
apgrp["ord"] = apgrp.group.map({g: i for i, g in enumerate(order)}).fillna(99)
apgrp = apgrp.sort_values("ord").drop(columns="ord")
apgrp.to_csv(os.path.join(OUT, "selection_strata_apollo.csv"), index=False)

print("=" * 92)
print("SELECTION-GROUP STRATIFICATION — ALL NASA (Apollo + non-Apollo), chronological")
print("  Criteria loosened over time (Mercury 7 strictest). Does vitality signal persist?")
print("=" * 92)
for _, r in allgrp.iterrows():
    cr = f"{r.cond_rate*100:.0f}% [{r.cond_lo*100:.0f},{r.cond_hi*100:.0f}]" if r.reached_80 else "—"
    print(f"  {r.group:22s} N={int(r.N):2d}  80+={int(r.reached_80):2d}  SA={int(r.superagers):2d}  cond={cr}")

print("\n--- Apollo only, by selection group ---")
for _, r in apgrp.iterrows():
    cr = f"{r.cond_rate*100:.0f}%" if r.reached_80 else "—"
    print(f"  {r.group:22s} N={int(r.N):2d}  80+={int(r.reached_80):2d}  SA={int(r.superagers):2d}  cond={cr}")

print("\n[write] outputs/selection_strata_all_nasa.csv, selection_strata_apollo.csv")
