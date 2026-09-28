#!/usr/bin/env python3
"""Stage 2 analysis, part A: astronaut-vs-astronaut mortality + cognitive endpoint.
Uses ONLY apollo_era_astronaut_cohort_v2.csv. No external data here (SSA handled separately).
"""
import csv, math
from datetime import date
import numpy as np
from scipy import stats
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.utils import restricted_mean_survival_time

CSV = "apollo_era_astronaut_cohort_v2.csv"
CENSOR = date(2026, 6, 1)
INDEX = date(1972, 12, 19)          # Apollo 17 splashdown = end of crewed Apollo program
Y = 365.25

def d(s): return date.fromisoformat(s)
def age(b, t): return (t - b).days / Y

rows = list(csv.DictReader(open(CSV)))
for r in rows:
    r["b"] = d(r["birth_date"])
    r["dead"] = r["vital_status_20260601"] == "DEAD"
    r["exit"] = d(r["death_date"]) if r["dead"] else CENSOR
    r["age_exit"] = age(r["b"], r["exit"])
    r["grp"] = ("Apollo" if r["cohort"] == "APOLLO_FLEW"
                else "Apollo1" if r["cohort"] == "APOLLO1_CREW"
                else "Comparison")

def wilson(k, n):
    if n == 0: return (0.0, 0.0)
    z = 1.959964; p = k / n
    den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (max(0, c-h), min(1, c+h))

def pois_ci(k):  # exact Poisson 95% CI for a count
    lo = 0.0 if k == 0 else stats.chi2.ppf(0.025, 2*k)/2
    hi = stats.chi2.ppf(0.975, 2*k+2)/2
    return lo, hi

print("="*78)
print("PART 1  MORTALITY — astronaut vs astronaut")
print("="*78)

# ---- Primary: landmark cohort, attained-age time scale, left-truncated ----
land = [r for r in rows if r["grp"] in ("Apollo","Comparison")
        and (not r["dead"] or r["exit"] > INDEX)]   # alive at INDEX
for r in land:
    r["age_entry"] = age(r["b"], INDEX)
excluded = [r for r in rows if r["grp"] in ("Apollo","Comparison") and r["dead"] and r["exit"] <= INDEX]

print(f"\nIndex date (entry / start of time-at-risk): {INDEX}  (Apollo 17 splashdown)")
print(f"Time scale: attained age, left-truncated at age on index date.")
print(f"Censoring: {CENSOR}.  All subjects male (NASA Groups 1-7, 1959-69).")
print(f"\nExcluded from landmark cohort (died before index): {len(excluded)}")
for r in excluded:
    print(f"   - {r['full_name']:24s} {r['cohort']:16s} d.{r['death_date']} age {age(r['b'],r['exit']):.0f}")

for g in ("Apollo","Comparison"):
    sub = [r for r in land if r["grp"] == g]
    nd = sum(r["dead"] for r in sub)
    ages_entry = [r["age_entry"] for r in sub]
    py = sum(r["age_exit"] - r["age_entry"] for r in sub)
    dd = [r["age_exit"] for r in sub if r["dead"]]
    print(f"\n{g}: n={len(sub)}  deaths={nd}  alive={len(sub)-nd}  "
          f"entry-age mean={np.mean(ages_entry):.1f} (range {min(ages_entry):.0f}-{max(ages_entry):.0f})")
    if dd: print(f"   ages at death: mean {np.mean(dd):.1f}, median {np.median(dd):.1f}, "
                 f"range {min(dd):.0f}-{max(dd):.0f}")
    print(f"   person-years from index: {py:.0f}")

# KM with delayed entry; medians and survival at fixed ages
print("\nKaplan-Meier (attained age, delayed entry):")
kms = {}
for g in ("Apollo","Comparison"):
    sub = [r for r in land if r["grp"] == g]
    km = KaplanMeierFitter().fit(
        durations=[r["age_exit"] for r in sub],
        event_observed=[int(r["dead"]) for r in sub],
        entry=[r["age_entry"] for r in sub], label=g)
    kms[g] = km
    med = km.median_survival_time_
    print(f"   {g}: median age at death (KM) = {med:.1f}")
    for a in (80, 85, 90):
        try:
            s = float(km.predict(a)); print(f"      S({a}) = {s:.3f}", end="")
        except Exception: pass
    print()

# Cox PH with delayed entry -> hazard ratio Apollo vs Comparison (ref=Comparison)
import pandas as pd
df = pd.DataFrame({
    "entry":[r["age_entry"] for r in land],
    "exit":[r["age_exit"] for r in land],
    "event":[int(r["dead"]) for r in land],
    "apollo":[1 if r["grp"]=="Apollo" else 0 for r in land],
})
cph = CoxPHFitter().fit(df, duration_col="exit", event_col="event", entry_col="entry", formula="apollo")
hr = math.exp(cph.params_["apollo"]); lo, hi = np.exp(cph.confidence_intervals_.loc["apollo"].values)
p = cph.summary.loc["apollo","p"]
print(f"\nCox PH (ref = Comparison; +ve coef = higher mortality for Apollo):")
print(f"   HR Apollo vs Comparison = {hr:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  p = {p:.3f}")

# exponential rate ratio (robustness)
dA=sum(r['dead'] for r in land if r['grp']=='Apollo'); pyA=sum(r['age_exit']-r['age_entry'] for r in land if r['grp']=='Apollo')
dC=sum(r['dead'] for r in land if r['grp']=='Comparison'); pyC=sum(r['age_exit']-r['age_entry'] for r in land if r['grp']=='Comparison')
rr=(dA/pyA)/(dC/pyC); se=math.sqrt(1/dA+1/dC)
print(f"   Exponential rate ratio = {rr:.3f}  95% CI [{math.exp(math.log(rr)-1.96*se):.3f}, {math.exp(math.log(rr)+1.96*se):.3f}]")

# sensitivity: comparison = flew-other only
df2 = df.copy()
mask = [r["grp"]=="Apollo" or r["cohort"]=="COMP_FLEW_OTHER" for r in land]
sub2 = df[mask]
cph2 = CoxPHFitter().fit(sub2, duration_col="exit", event_col="event", entry_col="entry", formula="apollo")
hr2=math.exp(cph2.params_["apollo"]); lo2,hi2=np.exp(cph2.confidence_intervals_.loc["apollo"].values)
print(f"   [sensitivity] vs COMP_FLEW_OTHER only (n={int(sum(mask))}): HR={hr2:.3f} CI[{lo2:.3f},{hi2:.3f}] p={cph2.summary.loc['apollo','p']:.3f}")

# sensitivity: naive from-birth (shows immortal-time inflation; includes all 73)
dfb = pd.DataFrame({
    "exit":[r["age_exit"] for r in rows],
    "event":[int(r["dead"]) for r in rows],
    "apollo":[1 if r["grp"]=="Apollo" else 0 for r in rows],
    "incl":[r["grp"] in ("Apollo","Comparison") for r in rows]})
dfb = dfb[dfb["incl"]].drop(columns="incl")
cphb = CoxPHFitter().fit(dfb, duration_col="exit", event_col="event", formula="apollo")
hrb=math.exp(cphb.params_["apollo"]); lob,hib=np.exp(cphb.confidence_intervals_.loc["apollo"].values)
print(f"   [sensitivity] NAIVE from-birth (immortal-time-biased): HR={hrb:.3f} CI[{lob:.3f},{hib:.3f}] p={cphb.summary.loc['apollo','p']:.3f}")

print("\n" + "="*78)
print("PART 2  COGNITIVE ENDPOINT — Apollo vs comparison astronauts")
print("="*78)
print("""Endpoint: documented major cognitive impairment (IMPAIRED_DOCUMENTED) by end of
observation, among astronauts who survived to an assessable late life
(cognitive_status != DIED_EARLY, i.e. attained age >= 70). DIED_EARLY excluded from
denominator (no observation window). NO_EVIDENCE handled explicitly via bounds.""")

def grp2(r): return "Apollo" if r["grp"]=="Apollo" else "Comparison"  # Apollo1 are all DIED_EARLY anyway
cells = {}
for g in ("Apollo","Comparison"):
    sub=[r for r in rows if grp2(r)==g and r["grp"] in ("Apollo","Comparison")]
    by={k:0 for k in ("IMPAIRED_DOCUMENTED","INTACT_DOCUMENTED","NO_EVIDENCE_EITHER_WAY","DIED_EARLY")}
    for r in sub: by[r["cognitive_status_20260601"]]+=1
    cells[g]=by
    assess=by["IMPAIRED_DOCUMENTED"]+by["INTACT_DOCUMENTED"]+by["NO_EVIDENCE_EITHER_WAY"]
    print(f"\n{g}: total={len(sub)}  DIED_EARLY={by['DIED_EARLY']}  assessable={assess}")
    print(f"   IMPAIRED={by['IMPAIRED_DOCUMENTED']}  INTACT={by['INTACT_DOCUMENTED']}  NO_EVIDENCE={by['NO_EVIDENCE_EITHER_WAY']}")

# naive prevalence among assessable
def assess_n(g): b=cells[g]; return b["IMPAIRED_DOCUMENTED"]+b["INTACT_DOCUMENTED"]+b["NO_EVIDENCE_EITHER_WAY"]
iA,nA=cells["Apollo"]["IMPAIRED_DOCUMENTED"],assess_n("Apollo")
iC,nC=cells["Comparison"]["IMPAIRED_DOCUMENTED"],assess_n("Comparison")
print(f"\nNaive impairment prevalence (assessable denominator):")
print(f"   Apollo     {iA}/{nA} = {iA/nA*100:.1f}%  95% CI [{wilson(iA,nA)[0]*100:.1f}, {wilson(iA,nA)[1]*100:.1f}]")
print(f"   Comparison {iC}/{nC} = {iC/nC*100:.1f}%  95% CI [{wilson(iC,nC)[0]*100:.1f}, {wilson(iC,nC)[1]*100:.1f}]")
OR,pf = stats.fisher_exact([[iA,nA-iA],[iC,nC-iC]])
print(f"   Fisher exact two-sided p = {pf:.3f}   (risk difference {iA/nA*100-iC/nC*100:+.1f} pp)")

# Manski worst-case bounds: NO_EVIDENCE could be all-intact or all-impaired
neA=cells["Apollo"]["NO_EVIDENCE_EITHER_WAY"]; neC=cells["Comparison"]["NO_EVIDENCE_EITHER_WAY"]
print(f"\nManski bounds on impairment prevalence (NO_EVIDENCE ranges intact<->impaired):")
print(f"   Apollo     [{iA}/{nA}, {(iA+neA)}/{nA}] = [{iA/nA*100:.1f}%, {(iA+neA)/nA*100:.1f}%]")
print(f"   Comparison [{iC}/{nC}, {(iC+neC)}/{nC}] = [{iC/nC*100:.1f}%, {(iC+neC)/nC*100:.1f}%]")
rd_lo = iA/nA - (iC+neC)/nC; rd_hi=(iA+neA)/nA - iC/nC
print(f"   Risk difference (Apollo-Comp) bound: [{rd_lo*100:+.1f} pp, {rd_hi*100:+.1f} pp]  (straddles 0 => sign unidentified)")

# Depth-informed least-biased stratum: HIGH documentation, assessable
print(f"\nLeast-ascertainment-biased stratum (documentation_depth=HIGH, assessable):")
print(f"   (assumption: a major dementia in a HIGH-coverage person would surface, so HIGH+NO_EVIDENCE ~ not impaired)")
for g in ("Apollo","Comparison"):
    sub=[r for r in rows if grp2(r)==g and r["grp"] in ("Apollo","Comparison")
         and r["cognitive_status_20260601"]!="DIED_EARLY" and r["documentation_depth"]=="HIGH"]
    imp=sum(r["cognitive_status_20260601"]=="IMPAIRED_DOCUMENTED" for r in sub)
    ne =sum(r["cognitive_status_20260601"]=="NO_EVIDENCE_EITHER_WAY" for r in sub)
    print(f"   {g}: IMPAIRED {imp}/{len(sub)} = {imp/len(sub)*100:.1f}%  (NO_EVIDENCE among them: {ne}; Wilson CI [{wilson(imp,len(sub))[0]*100:.1f},{wilson(imp,len(sub))[1]*100:.1f}])")

# Ascertainment direction: documentation depth by group among assessable
print(f"\nAscertainment check — documentation_depth among assessable survivors:")
for g in ("Apollo","Comparison"):
    sub=[r for r in rows if grp2(r)==g and r["grp"] in ("Apollo","Comparison") and r["cognitive_status_20260601"]!="DIED_EARLY"]
    from collections import Counter
    c=Counter(r["documentation_depth"] for r in sub)
    print(f"   {g}: HIGH={c['HIGH']} MEDIUM={c['MEDIUM']} LOW={c['LOW']}  (better-documented => impairment MORE likely to be detected)")
