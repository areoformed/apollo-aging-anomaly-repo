#!/usr/bin/env python3
"""
superager_rates.py — Core SuperAger-phenotype RATE analysis (the corrected estimand).

Estimand: rate of the SuperAger phenotype (reached 80 AND visibly cognitively vital,
proxied by Space Grandpa=Y) in the cohort vs reference base rates.

CONSTRUCT HONESTY: Space Grandpa is a PUBLIC-EVIDENCE proxy, NOT a clinical assessment.
SG=Y asserts observed vitality (positive); SG=N asserts only absence of public evidence,
NOT decline. Every cohort-vs-population comparison flags this asymmetry. The population
anchors (GBD dementia-free etc.) are CLINICAL/permissive and on a different construct;
they are upper bounds and the comparison is cross-construct. No false precision.

Outputs (to ../outputs/):
  - superager_rates_by_cohort.csv     (rates + exact-binomial Clopper-Pearson CIs)
  - superager_population_anchors.csv  (population base rates, conditional-at-80)
  - superager_rate_comparison.csv     (cohort conditional rate vs each anchor: ratio, exact test)
  - g1_birth_year_data.csv            (birth-year histogram data)
Console: full reproduction of prior baseline (sanity), plus all rate tables.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))
os.makedirs(OUT, exist_ok=True)

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))
d["birth_year"] = pd.to_datetime(d["date_of_birth"]).dt.year

# ----------------------------------------------------------------------------
# Clopper-Pearson exact binomial CI
# ----------------------------------------------------------------------------
def cp_ci(k, n, alpha=0.05):
    if n == 0:
        return (np.nan, np.nan)
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha/2, k, n-k+1)
    hi = 1.0 if k == n else stats.beta.ppf(1-alpha/2, k+1, n-k)
    return (lo, hi)

def rate_row(label, m):
    n = len(m)
    r80 = int(m.reached_80.sum())
    sa = int(m.superager.sum())
    # conditional: SuperAgers among survivors-to-80
    cond_lo, cond_hi = cp_ci(sa, r80)
    # unconditional: SuperAgers among all
    unc_lo, unc_hi = cp_ci(sa, n)
    return {
        "cohort": label, "N": n, "reached_80": r80, "superagers": sa,
        "cond_rate": sa/r80 if r80 else np.nan, "cond_lo": cond_lo, "cond_hi": cond_hi,
        "uncond_rate": sa/n if n else np.nan, "uncond_lo": unc_lo, "uncond_hi": unc_hi,
    }

# ----------------------------------------------------------------------------
# Cohort definitions
# ----------------------------------------------------------------------------
apollo = d[d.cohort == "apollo"]
nasa_all = d[d.cohort == "nasa_nonapollo"]
nasa_flew = d[(d.cohort == "nasa_nonapollo") & d.flew]
nasa_never = d[(d.cohort == "nasa_nonapollo") & ~d.flew]
avail = d[d.included_in_apollo_vs_other_available == True]
avail_other = avail[avail.cohort != "apollo"]
# flew-restricted same-era comparator, PRIMARY = NASA non-Apollo who flew (exclude pre1970 accidents)
nasa_flew_noacc = nasa_flew[~nasa_flew.pre1970_accidental_death]
# SENSITIVITY: add X-15 wings flyers (non pre1970-accident)
x15_flew_noacc = d[(d.cohort == "x15") & d.flew & ~d.pre1970_accidental_death]
flew_plus_x15 = pd.concat([nasa_flew_noacc, x15_flew_noacc])

rows = [
    rate_row("Apollo", apollo),
    rate_row("NASA non-Apollo (all)", nasa_all),
    rate_row("NASA non-Apollo, flew", nasa_flew),
    rate_row("NASA non-Apollo, flew (no pre1970 acc)", nasa_flew_noacc),
    rate_row("NASA non-Apollo, never flew", nasa_never),
    rate_row("flew NASA + X-15 wings (no pre1970 acc)", flew_plus_x15),
    rate_row("GPT 'available' pool (84)", avail),
    rate_row("GPT 'available' non-Apollo (55)", avail_other),
]
rates = pd.DataFrame(rows)
rates.to_csv(os.path.join(OUT, "superager_rates_by_cohort.csv"), index=False)

print("=" * 100)
print("SUPERAGER PHENOTYPE RATES BY COHORT  (SuperAger = reached 80 AND Space Grandpa=Y)")
print("  SG = PUBLIC-EVIDENCE proxy, not clinical. Clopper-Pearson exact 95% CIs.")
print("=" * 100)
for _, r in rates.iterrows():
    print(f"{r['cohort']:42s}  N={int(r.N):3d}  80+={int(r.reached_80):3d}  SA={int(r.superagers):3d}"
          f"  cond={r.cond_rate*100:5.1f}% [{r.cond_lo*100:4.1f},{r.cond_hi*100:5.1f}]"
          f"  uncond={r.uncond_rate*100:5.1f}% [{r.uncond_lo*100:4.1f},{r.uncond_hi*100:5.1f}]")

# ----------------------------------------------------------------------------
# Population anchors (CONDITIONAL on survival to 80), from the reference doc.
# All flagged by construct + asymmetry. dementia-free is PERMISSIVE (upper bound on vitality).
# ----------------------------------------------------------------------------
anchors = pd.DataFrame([
    # key, label, rate, lo, hi, construct, denom, source, note
    dict(key="gbd_male_80_84_demfree", rate=0.866, lo=0.860, hi=0.872,
         construct="dementia-free (permissive)", denom="men 80-84",
         source="Cao 2024 GBD eTable4 male 2020", note="UPPER BOUND on vitality; still incl MCI"),
    dict(key="gbd_male_85_89_demfree", rate=0.791, lo=0.783, hi=0.799,
         construct="dementia-free (permissive)", denom="men 85-89",
         source="Cao 2024 GBD eTable4 male 2020", note="UPPER BOUND on vitality"),
    dict(key="gbd_male_90_94_demfree", rate=0.697, lo=0.685, hi=0.708,
         construct="dementia-free (permissive)", denom="men 90-94",
         source="Cao 2024 GBD eTable4 male 2020", note="UPPER BOUND on vitality"),
    dict(key="gbd_male_95plus_demfree", rate=0.507, lo=0.488, hi=0.525,
         construct="dementia-free (permissive)", denom="men 95+",
         source="Cao 2024 GBD eTable4 male 2020", note="UPPER BOUND on vitality"),
    dict(key="hcap_65plus_normalcog", rate=0.680, lo=np.nan, hi=np.nan,
         construct="normal cognition (no dem,no MCI)", denom="US adults 65+ (NOT 80+)",
         source="HRS-HCAP 2016 (10% dem,22% MCI)", note="age-65+ overall; OPTIMISTIC for 80+"),
    dict(key="campos_80_94_no_mmse_imp", rate=0.648, lo=np.nan, hi=np.nan,
         construct="no poor MMSE", denom="long-lived 80-94 (n=165)",
         source="Campos 2024 ScienceDirect", note="NOT US-rep; mostly female; low education"),
    dict(key="mhas_80plus_youthful", rate=0.1617, lo=np.nan, hi=np.nan,
         construct="youthful cognition (strict)", denom="MHAS 80+ (54/334)",
         source="MHAS user-supplied (NOT reproduced)", note="STRICT LOWER anchor; unverified"),
])
anchors.to_csv(os.path.join(OUT, "superager_population_anchors.csv"), index=False)

# ----------------------------------------------------------------------------
# CONDITIONAL comparison: Apollo SuperAger-among-survivors vs each population anchor.
# This is the cleanest like-with-like (both conditional on reaching ~80).
# Exact binomial test: P(observe >= Apollo's SA count | n=22, p=anchor).
# NOTE asymmetry: Apollo numerator is public-activity; anchor is clinical. Cross-construct.
# ----------------------------------------------------------------------------
apollo_sa = int(apollo.superager.sum())          # 21
apollo_80 = int(apollo.reached_80.sum())          # 22
comp_rows = []
for _, a in anchors.iterrows():
    p = a["rate"]
    # one-sided exact: P(X >= apollo_sa) under Binom(apollo_80, p)
    pval = stats.binomtest(apollo_sa, apollo_80, p, alternative="greater").pvalue
    obs = apollo_sa/apollo_80
    comp_rows.append(dict(
        anchor=a["key"], anchor_rate=p, construct=a["construct"], denom=a["denom"],
        apollo_cond_rate=obs, rate_ratio=obs/p,
        excess_pp=(obs - p)*100,
        p_exact_ge=pval, source=a["source"], note=a["note"],
    ))
comp = pd.DataFrame(comp_rows)
comp.to_csv(os.path.join(OUT, "superager_rate_comparison.csv"), index=False)

print("\n" + "=" * 100)
print(f"APOLLO conditional SuperAger rate = {apollo_sa}/{apollo_80} = {apollo_sa/apollo_80*100:.1f}%")
print("  vs population anchors (CROSS-CONSTRUCT: Apollo=public-activity, anchor=clinical).")
print("  p_exact = P(X >= 21 | Binom(22, anchor_rate)), one-sided.")
print("=" * 100)
for _, r in comp.iterrows():
    print(f"  vs {r['anchor']:28s} ({r['anchor_rate']*100:4.1f}% {r['construct'][:22]:22s})"
          f"  RR={r['rate_ratio']:.2f}  +{r['excess_pp']:5.1f}pp  p={r['p_exact_ge']:.2e}")

# ----------------------------------------------------------------------------
# G1 birth-year histogram data
# ----------------------------------------------------------------------------
by = d.copy()
by["grp"] = np.where(by.cohort == "apollo", "Apollo",
             np.where(by.cohort == "nasa_nonapollo", "NASA non-Apollo", "X-15/DynaSoar/MOL"))
g1 = (by.groupby(["birth_year", "grp"]).size().rename("count").reset_index())
g1.to_csv(os.path.join(OUT, "g1_birth_year_data.csv"), index=False)
print("\n[G1] birth-year range:", int(d.birth_year.min()), "-", int(d.birth_year.max()))
print("[G1] Apollo birth-year quartiles:",
      apollo.assign(by=pd.to_datetime(apollo.date_of_birth).dt.year).by.quantile([0,.25,.5,.75,1]).astype(int).tolist())

print("\n[write] outputs/superager_rates_by_cohort.csv, superager_population_anchors.csv,")
print("        superager_rate_comparison.csv, g1_birth_year_data.csv")
