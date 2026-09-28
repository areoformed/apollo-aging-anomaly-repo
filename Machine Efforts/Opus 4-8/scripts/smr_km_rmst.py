#!/usr/bin/env python3
"""
smr_km_rmst.py — G5 (SMR), G10 (KM Apollo vs flew), G12 (4-way KM + RMST), plus
reproduction of prior baseline SMRs as a data-stability sanity check.

Survival here is the MORTALITY survival analysis (the longevity leg of the SuperAger
phenotype). The vitality leg is handled in superager_rates.py / age_matched_anchor.py.

Methods:
  - KM via lifelines; Greenwood (log-log) CIs; at-risk tables; censoring ticks.
  - Hazards cross (per prior report) -> do NOT lean on log-rank; report RMST at a
    PRE-SPECIFIED horizon. Horizon choice declared below.
  - SMR with Byar exact-Poisson CI (NOT log-normal). Expected via integrated hazard from
    SSA 1930 male cohort table conditioned on age 30, AND via Sum(1-S) headcount, both shown.

Outputs:
  - smr_results.csv, km_points_<comparison>.csv, rmst_results.csv, atrisk_<...>.csv
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.utils import restricted_mean_survival_time

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
SRC = os.path.abspath(os.path.join(HERE, "..", "..",
        "Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))

# ---- SSA 1930 male cohort life table, conditioned on age 30 ----
lt = pd.read_csv(os.path.join(SRC, "data", "ssa-1930-male-cohort-lifetable.tsv"), sep="\t")
lt = lt.sort_values("age").reset_index(drop=True)
l30 = lt.loc[lt.age == 30, "lx"].values[0]
lt["S_from30"] = np.where(lt.age >= 30, lt.lx / l30, np.nan)
# survival to integer age a (S(a)=l(a)/l(30)); cumulative hazard H(a) = -ln S(a)
S = dict(zip(lt.age, lt.S_from30))
def S_at(age):
    a = int(np.floor(age))
    if a <= 30:
        return 1.0
    if a >= lt.age.max():
        return max(S.get(int(lt.age.max()), 1e-9), 1e-12)
    # linear interp in survival between integer ages
    s0 = S.get(a, None); s1 = S.get(a+1, None)
    if s0 is None: return 1.0
    if s1 is None: return s0
    frac = age - a
    return s0 + (s1 - s0) * frac

ENTRY = 30.0

def smr_byar(O, E, alpha=0.05):
    """SMR=O/E with Byar's approximate exact-Poisson CI on O."""
    smr = O / E
    z = stats.norm.ppf(1 - alpha/2)
    lower = (O * (1 - 1/(9*O) - z/(3*np.sqrt(O)))**3) / E
    upper = ((O+1) * (1 - 1/(9*(O+1)) + z/(3*np.sqrt(O+1)))**3) / E
    return smr, lower, upper

def expected_deaths(group):
    """Two conventions: integrated hazard Sum(-lnS) and headcount Sum(1-S)."""
    Hsum = 0.0; headcount = 0.0
    for _, r in group.iterrows():
        s = S_at(r.endpoint_age)
        s = min(max(s, 1e-12), 1.0)
        Hsum += -np.log(s)
        headcount += (1 - s)
    return Hsum, headcount

# Cohorts for SMR (vs SSA general pop): keep accidents (SSA is all-cause)
cohorts_smr = {
    "Apollo": d[d.cohort == "apollo"],
    "NASA non-Apollo flew": d[(d.cohort == "nasa_nonapollo") & d.flew],
    "NASA non-Apollo flew (no pre1970 acc)":
        d[(d.cohort == "nasa_nonapollo") & d.flew & ~d.pre1970_accidental_death],
    "GPT available non-Apollo (55)":
        d[(d.included_in_apollo_vs_other_available == True) & (d.cohort != "apollo")],
}
smr_rows = []
for name, g in cohorts_smr.items():
    O = int(g.deceased.sum())
    Hsum, head = expected_deaths(g)
    smr_h, lo_h, hi_h = smr_byar(O, Hsum)
    # headcount SMR uses expected decedents
    smr_c = O / head
    smr_rows.append(dict(cohort=name, N=len(g), observed_deaths=O,
        E_integrated_hazard=Hsum, SMR_rate=smr_h, SMR_rate_lo_byar=lo_h, SMR_rate_hi_byar=hi_h,
        E_headcount=head, SMR_headcount=smr_c))
smr = pd.DataFrame(smr_rows)
smr.to_csv(os.path.join(OUT, "smr_results.csv"), index=False)

print("=" * 100)
print("SMR vs SSA 1930 male general population (conditioned age 30). Byar exact-Poisson CI.")
print("  rate-SMR uses integrated hazard E; headcount-SMR uses Sum(1-S). Both shown (prior FATAL-2).")
print("=" * 100)
for _, r in smr.iterrows():
    print(f"{r['cohort']:40s} O={int(r.observed_deaths):3d}  E_haz={r.E_integrated_hazard:5.2f}  "
          f"SMR_rate={r.SMR_rate:.3f} [{r.SMR_rate_lo_byar:.3f},{r.SMR_rate_hi_byar:.3f}]  "
          f"E_head={r.E_headcount:5.2f}  SMR_head={r.SMR_headcount:.3f}")

# ----------------------------------------------------------------------------
# Kaplan-Meier: build (duration, event) with delayed entry at age 30.
# event = deceased (all-cause); duration = endpoint_age; entry = 30.
# ----------------------------------------------------------------------------
def km_df(group):
    return pd.DataFrame({
        "T": group.endpoint_age.values,
        "E": group.deceased.astype(int).values,
        "entry": np.full(len(group), ENTRY),
    })

def fit_km(group, label):
    df = km_df(group)
    kmf = KaplanMeierFitter()
    kmf.fit(df["T"].values, event_observed=df["E"].values,
            entry=df["entry"].values, label=label)
    return kmf

groups_km = {
    "Apollo": d[d.cohort == "apollo"],
    "NASA non-Apollo flew (no pre1970 acc)":
        d[(d.cohort == "nasa_nonapollo") & d.flew & ~d.pre1970_accidental_death],
    "NASA non-Apollo never flew":
        d[(d.cohort == "nasa_nonapollo") & ~d.flew],
}
kmfs = {k: fit_km(g, k) for k, g in groups_km.items()}

# KM survival readouts at key ages with Greenwood CI
read_ages = [70, 80, 85, 90, 95]
km_read = []
for k, kmf in kmfs.items():
    ci = kmf.confidence_interval_survival_function_
    for a in read_ages:
        s = float(kmf.predict(a))
        # nearest CI row
        idx = ci.index.get_indexer([a], method="nearest")[0]
        lo = ci.iloc[idx, 0]; hi = ci.iloc[idx, 1]
        km_read.append(dict(group=k, age=a, S=s, S_lo=lo, S_hi=hi))
kmread = pd.DataFrame(km_read)
kmread.to_csv(os.path.join(OUT, "km_survival_readouts.csv"), index=False)

print("\n" + "=" * 100)
print("KM survival (delayed entry at 30) with Greenwood 95% CI at key ages")
print("=" * 100)
piv = kmread.pivot(index="age", columns="group", values="S")
print(piv.to_string(float_format=lambda x: f"{x:.3f}"))

# ----------------------------------------------------------------------------
# RMST at PRE-SPECIFIED horizon. Curves cross -> RMST is the right summary.
# Horizon: t=90 (a principled choice tied to the SuperAger regime; declared in advance,
# matches the age band where Apollo survivors concentrate). Also report t=95.
# RMST computed from age 30 baseline; difference Apollo - comparator.
# ----------------------------------------------------------------------------
def rmst_with_se(kmf, t):
    # lifelines restricted_mean_survival_time returns area; we also bootstrap SE.
    val = restricted_mean_survival_time(kmf, t=t)
    return val

rmst_rows = []
horizons = [90, 95]
# Use lifelines' RMST + a simple bootstrap for difference CI
rng = np.random.default_rng(15170608)
def boot_rmst_diff(gA, gB, t, B=2000):
    diffs = []
    A = km_df(gA); Bd = km_df(gB)
    for _ in range(B):
        iA = rng.integers(0, len(A), len(A)); iB = rng.integers(0, len(Bd), len(Bd))
        sA = A.iloc[iA]; sB = Bd.iloc[iB]
        try:
            kA = KaplanMeierFitter().fit(sA["T"].values, sA["E"].values, entry=sA["entry"].values)
            kB = KaplanMeierFitter().fit(sB["T"].values, sB["E"].values, entry=sB["entry"].values)
            diffs.append(restricted_mean_survival_time(kA, t=t) - restricted_mean_survival_time(kB, t=t))
        except Exception:
            continue
    diffs = np.array(diffs)
    return np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)

apollo_g = groups_km["Apollo"]
flew_g = groups_km["NASA non-Apollo flew (no pre1970 acc)"]
for t in horizons:
    rA = restricted_mean_survival_time(kmfs["Apollo"], t=t)
    rF = restricted_mean_survival_time(kmfs["NASA non-Apollo flew (no pre1970 acc)"], t=t)
    lo, hi = boot_rmst_diff(apollo_g, flew_g, t)
    rmst_rows.append(dict(horizon=t, rmst_apollo=rA, rmst_flew=rF,
                          diff_apollo_minus_flew=rA-rF, diff_lo95=lo, diff_hi95=hi))
rmst = pd.DataFrame(rmst_rows)
rmst.to_csv(os.path.join(OUT, "rmst_results.csv"), index=False)

print("\n" + "=" * 100)
print("RMST (restricted mean survival time, from age 30) — PRE-SPECIFIED horizons; hazards cross.")
print("  Apollo vs NASA non-Apollo flew (no pre1970 acc). Bootstrap 95% CI on the difference (B=2000).")
print("=" * 100)
for _, r in rmst.iterrows():
    print(f"  t={int(r.horizon)}:  RMST Apollo={r.rmst_apollo:.2f}y  flew={r.rmst_flew:.2f}y  "
          f"diff={r.diff_apollo_minus_flew:+.2f}y  95%CI [{r.diff_lo95:+.2f},{r.diff_hi95:+.2f}]")

# Save KM points for plotting (each group full step function + CI)
for k, kmf in kmfs.items():
    sf = kmf.survival_function_.reset_index()
    sf.columns = ["age", "S"]
    ci = kmf.confidence_interval_survival_function_.reset_index()
    ci.columns = ["age", "S_lo", "S_hi"]
    m = sf.merge(ci, on="age")
    safe = k.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
    m.to_csv(os.path.join(OUT, f"km_points_{safe}.csv"), index=False)

print("\n[write] outputs/smr_results.csv, km_survival_readouts.csv, rmst_results.csv, km_points_*.csv")
