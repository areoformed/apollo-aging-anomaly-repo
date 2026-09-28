"""
Independent statistical analysis of the Apollo-era astronaut cohort.

Q1 MORTALITY
  (a) Apollo flyers vs comparison astronauts in the dataset.
  (b) Apollo flyers vs era/sex-matched US-population expectation (SMR vs CDC/NCHS 2021 male life table).
Q2 COGNITION
  Late-life cognitive impairment endpoint; ascertainment (documentation_depth) bounding.

KEY JUDGMENT CALLS (see comments at each stage):
  - Index/landmark date = 1973-01-01 (day after Apollo 17, Dec 1972 -> all Apollo exposure complete).
    Conditioning on survival to a single common post-program date removes immortal-time bias
    symmetrically (flying Apollo required surviving to one's 1968-72 mission).
  - Time scale = attained age (left-truncated at age on the index date) for the longevity read-out;
    a parallel time-since-index Cox (age-at-index adjusted) gives the test / hazard ratio.
  - Comparison group = COMP_FLEW_OTHER + COMP_NEVER_FLEW, restricted to those alive at the index date.
    APOLLO1_CREW (3 pad-fire deaths, 1967) are excluded from the Apollo-vs-comparison contrast:
    they died pre-index and loading 3 Apollo-program deaths into the "never flew Apollo" arm would
    bias it. The 5 pre-1973 accident deaths in COMP_NEVER_FLEW are likewise pre-index.
  - Reference population (Q1b) = supplied CDC/NCHS 2021 male period life table (radix 100000).
  - Cognitive endpoint (Q2) = documented late-life cognitive impairment among subjects with a
    late-life observation window (exclude DIED_EARLY, i.e. died <70, and APOLLO1_CREW).
"""

import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
from lifelines.utils import median_survival_times

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)

CSV = "apollo_era_astronaut_cohort_v2.csv"
INDEX = pd.Timestamp("1973-01-01")     # landmark: day after Apollo program ended
CENSOR = pd.Timestamp("2026-06-01")    # dataset censoring date
DAYS_YR = 365.25

# ----------------------------------------------------------------------------
# CDC/NCHS 2021 US male period life table, survivors l_x (radix 100000)
# ----------------------------------------------------------------------------
LX = {30:96811,31:96562,32:96303,33:96035,34:95757,35:95472,36:95178,37:94874,38:94560,
39:94234,40:93895,41:93541,42:93170,43:92783,44:92379,45:91958,46:91516,47:91051,48:90556,
49:90029,50:89467,51:88870,52:88234,53:87556,54:86828,55:86044,56:85205,57:84309,58:83352,
59:82328,60:81235,61:80070,62:78836,63:77541,64:76188,65:74780,66:73316,67:71782,68:70181,
69:68511,70:66772,71:64975,72:63110,73:61167,74:59126,75:57001,76:54693,77:52283,78:49731,
79:47087,80:44313,81:41479,82:38563,83:35595,84:32576,85:29498,86:26421,87:23344,88:20319,
89:17394,90:14623,91:12052,92:9722,93:7661,94:5889,95:4407,96:3206,97:2263,98:1549,99:1026,100:657}
_AMIN, _AMAX = min(LX), max(LX)

def ln_l(age):
    """log of interpolated life-table survivors at (possibly fractional) age (constant-hazard within year)."""
    if age <= _AMIN: return np.log(LX[_AMIN])
    if age >= _AMAX: return np.log(LX[_AMAX])
    lo = int(np.floor(age)); frac = age - lo
    return np.log(LX[lo]) + frac * (np.log(LX[lo + 1]) - np.log(LX[lo]))

def expected_deaths(entry_age, exit_age):
    """Expected cumulative hazard (=expected deaths) over [entry,exit] under population rates,
    conditional on survival to entry_age:  H(exit)-H(entry) = ln(l(entry)) - ln(l(exit))."""
    return ln_l(entry_age) - ln_l(exit_age)

# ----------------------------------------------------------------------------
# Load + derive time-at-risk fields
# ----------------------------------------------------------------------------
df = pd.read_csv(CSV)
df["birth"] = pd.to_datetime(df["birth_date"])
df["dead"] = (df["vital_status_20260601"] == "DEAD").astype(int)
df["death"] = pd.to_datetime(df["death_date"])
df["exit_date"] = df["death"].where(df["dead"] == 1, CENSOR)

df["age_index"] = (INDEX - df["birth"]).dt.days / DAYS_YR
df["age_exit"]  = (df["exit_date"] - df["birth"]).dt.days / DAYS_YR
df["age_death"] = (df["death"] - df["birth"]).dt.days / DAYS_YR
# alive at the landmark = did not die before the index date
df["alive_at_index"] = (df["dead"] == 0) | (df["death"] >= INDEX)
df["t_index"] = (df["exit_date"] - INDEX).dt.days / DAYS_YR  # years from landmark to exit

df["apollo"] = (df["cohort"] == "APOLLO_FLEW").astype(int)
df["is_comp"] = df["cohort"].isin(["COMP_FLEW_OTHER", "COMP_NEVER_FLEW"])

print("=" * 90)
print("COHORT OVERVIEW (n=%d)" % len(df))
print("=" * 90)
print(df.groupby("cohort").agg(n=("full_name", "size"),
                               dead=("dead", "sum"),
                               alive_at_1973=("alive_at_index", "sum")).to_string())
print("\nPre-index deaths excluded from the landmark contrast:")
print(df.loc[~df["alive_at_index"], ["full_name", "cohort", "death_date"]].to_string(index=False))

# ============================================================================
# Q1a  APOLLO vs COMPARISON ASTRONAUTS
# ============================================================================
print("\n" + "=" * 90)
print("Q1a  MORTALITY: Apollo flyers vs comparison astronauts")
print("Landmark = 1973-01-01; subjects alive at landmark; immortal time removed.")
print("=" * 90)

lm = df[df["alive_at_index"]].copy()           # landmark cohort
ap = lm[lm["apollo"] == 1]
cp = lm[lm["is_comp"]]
print(f"Landmark cohort: Apollo n={len(ap)} (deaths {ap.dead.sum()}), "
      f"Comparison n={len(cp)} (deaths {cp.dead.sum()})")
print(f"Mean age at landmark: Apollo {ap.age_index.mean():.1f}, Comparison {cp.age_index.mean():.1f}")
print(f"Mean age at death (decedents): Apollo {ap.loc[ap.dead==1,'age_death'].mean():.1f}, "
      f"Comparison {cp.loc[cp.dead==1,'age_death'].mean():.1f}")

# --- Median age at death, age time scale w/ left truncation at landmark age ---
print("\n[Attained-age scale, left-truncated at landmark age] Kaplan-Meier median age at death:")
for name, g in [("Apollo", ap), ("Comparison", cp)]:
    kmf = KaplanMeierFitter()
    kmf.fit(durations=g["age_exit"], event_observed=g["dead"], entry=g["age_index"], label=name)
    med = kmf.median_survival_time_
    ci = median_survival_times(kmf.confidence_interval_).values.flatten()
    print(f"  {name:11s} median age at death = {med:.1f}  (95% CI {ci[0]:.1f}-{ci[1]:.1f})")

# also subgroups
for sub in ["COMP_FLEW_OTHER", "COMP_NEVER_FLEW"]:
    g = lm[lm["cohort"] == sub]
    kmf = KaplanMeierFitter().fit(g["age_exit"], g["dead"], entry=g["age_index"], label=sub)
    print(f"  {sub:15s} median age at death = {kmf.median_survival_time_:.1f}  (n={len(g)}, deaths {g.dead.sum()})")

# --- Log-rank test on time-since-landmark (common start; no truncation needed) ---
lr = logrank_test(ap["t_index"], cp["t_index"], ap["dead"], cp["dead"])
print(f"\nLog-rank (time since landmark), Apollo vs Comparison: chi2={lr.test_statistic:.3f}, p={lr.p_value:.3f}")

# --- Cox hazard ratios ---
def cox_hr(data, covariates, duration, event, entry=None, label=""):
    cph = CoxPHFitter()
    cols = covariates + [duration, event] + ([entry] if entry else [])
    if entry:
        cph.fit(data[cols], duration_col=duration, event_col=event, entry_col=entry)
    else:
        cph.fit(data[cols], duration_col=duration, event_col=event)
    s = cph.summary
    hr = float(s.loc["apollo", "exp(coef)"])
    lo = float(s.loc["apollo", "exp(coef) lower 95%"])
    hi = float(s.loc["apollo", "exp(coef) upper 95%"])
    p  = float(s.loc["apollo", "p"])
    print(f"  {label:48s} HR(Apollo)={hr:.2f} (95% CI {lo:.2f}-{hi:.2f}), p={p:.3f}")
    return hr, lo, hi, p

print("\nCox proportional-hazards (event=death):")
cox_hr(lm, ["apollo"], "t_index", "dead", label="time-since-landmark, unadjusted:")
cox_hr(lm, ["apollo", "age_index"], "t_index", "dead", label="time-since-landmark, adj. age-at-landmark:")
# age time scale w/ left truncation (entry=age at landmark, duration=age at exit)
lm_age = lm.copy()
cox_hr(lm_age, ["apollo"], "age_exit", "dead", entry="age_index",
       label="attained-age scale, left-truncated:")

# Apollo vs each comparison subgroup (age-adjusted, time-since-landmark)
for sub in ["COMP_FLEW_OTHER", "COMP_NEVER_FLEW"]:
    d = lm[(lm["apollo"] == 1) | (lm["cohort"] == sub)]
    cox_hr(d, ["apollo", "age_index"], "t_index", "dead", label=f"Apollo vs {sub} (adj age):")

# ============================================================================
# Q1b  SMR vs US 2021 MALE LIFE TABLE
# ============================================================================
print("\n" + "=" * 90)
print("Q1b  MORTALITY: Standardized Mortality Ratio vs CDC/NCHS 2021 US male life table")
print("Follow-up from landmark 1973-01-01 to death/censor; expected from age interval.")
print("=" * 90)

def smr(group):
    O = int(group["dead"].sum())
    E = float(np.sum([expected_deaths(r.age_index, r.age_exit) for r in group.itertuples()]))
    s = O / E
    lo = 0.0 if O == 0 else stats.chi2.ppf(0.025, 2 * O) / 2 / E
    hi = stats.chi2.ppf(0.975, 2 * O + 2) / 2 / E
    return O, E, s, lo, hi

print(f"{'cohort':22s} {'N':>3s} {'Obs':>4s} {'Exp':>7s} {'SMR':>6s}  95% CI")
groups = [("APOLLO_FLEW", ap),
          ("COMP_FLEW_OTHER", lm[lm.cohort == "COMP_FLEW_OTHER"]),
          ("COMP_NEVER_FLEW", lm[lm.cohort == "COMP_NEVER_FLEW"]),
          ("COMPARISON (pooled)", cp)]
smr_results = {}
for nm, g in groups:
    O, E, s, lo, hi = smr(g)
    smr_results[nm] = (O, E, s, lo, hi)
    print(f"{nm:22s} {len(g):3d} {O:4d} {E:7.2f} {s:6.2f}  ({lo:.2f}-{hi:.2f})")

# Apollo vs comparison as a ratio of SMRs (relative mortality), via Cox already done.
oA, eA = smr_results["APOLLO_FLEW"][0], smr_results["APOLLO_FLEW"][1]
oC, eC = smr_results["COMPARISON (pooled)"][0], smr_results["COMPARISON (pooled)"][1]
# ratio of two SMRs with Poisson/Wald log CI
rr = (oA / eA) / (oC / eC)
se_log = np.sqrt(1 / oA + 1 / oC)
print(f"\nSMR ratio Apollo/Comparison = {rr:.2f} "
      f"(95% CI {rr*np.exp(-1.96*se_log):.2f}-{rr*np.exp(1.96*se_log):.2f})  [standardized to same life table]")

# ============================================================================
# Q2  COGNITION
# ============================================================================
print("\n" + "=" * 90)
print("Q2  COGNITION: late-life cognitive impairment, Apollo vs comparison")
print("=" * 90)

# Endpoint window: must have a late-life observation window -> exclude DIED_EARLY (died <70)
# and APOLLO1_CREW (all died 1967). Group = Apollo vs pooled comparison.
cog = df[(df["cognitive_status_20260601"] != "DIED_EARLY") &
         (df["cohort"] != "APOLLO1_CREW")].copy()
cog["grp"] = np.where(cog["apollo"] == 1, "Apollo", "Comparison")

print("\nCohort x cognitive status (full dataset):")
print(pd.crosstab(df["cohort"], df["cognitive_status_20260601"]).to_string())
print("\nCohort x documentation_depth (full dataset):")
print(pd.crosstab(df["cohort"], df["documentation_depth"]).to_string())
print("\ndocumentation_depth x cognitive status (full dataset):")
print(pd.crosstab(df["documentation_depth"], df["cognitive_status_20260601"]).to_string())

print("\n--- Endpoint cohort (survived to a late-life window; DIED_EARLY & Apollo1 excluded) ---")
ct = pd.crosstab(cog["grp"], cog["cognitive_status_20260601"])
print(ct.to_string())

def clopper(x, n):
    lo = 0.0 if x == 0 else stats.beta.ppf(0.025, x, n - x + 1)
    hi = 1.0 if x == n else stats.beta.ppf(0.975, x + 1, n - x)
    return lo, hi

def wilson(x, n, z=1.96):
    if n == 0: return (0, 0)
    p = x / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (c - h) / d, (c + h) / d

def newcombe_rd(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1); l2, u2 = wilson(x2, n2)
    rd = p1 - p2
    lo = rd - np.sqrt((p1 - l1)**2 + (u2 - p2)**2)
    hi = rd + np.sqrt((u1 - p1)**2 + (p2 - l2)**2)
    return rd, lo, hi

def counts(g, status):
    sub = cog[cog["grp"] == g]
    return int((sub["cognitive_status_20260601"] == status).sum()), len(sub)

imp_A, nA = counts("Apollo", "IMPAIRED_DOCUMENTED")
imp_C, nC = counts("Comparison", "IMPAIRED_DOCUMENTED")
ne_A = int((cog[cog.grp=="Apollo"]["cognitive_status_20260601"] == "NO_EVIDENCE_EITHER_WAY").sum())
ne_C = int((cog[cog.grp=="Comparison"]["cognitive_status_20260601"] == "NO_EVIDENCE_EITHER_WAY").sum())

print(f"\nNaive endpoint = IMPAIRED_DOCUMENTED (NO_EVIDENCE treated as not-impaired):")
for g, x, n in [("Apollo", imp_A, nA), ("Comparison", imp_C, nC)]:
    lo, hi = clopper(x, n)
    print(f"  {g:11s} {x}/{n} = {x/n*100:.1f}%  (95% CI {lo*100:.1f}-{hi*100:.1f}%)")
rd, lo, hi = newcombe_rd(imp_A, nA, imp_C, nC)
print(f"  Risk difference (Apollo - Comparison) = {rd*100:+.1f}%  (95% Newcombe CI {lo*100:+.1f} to {hi*100:+.1f}%)")
OR, pf = stats.fisher_exact([[imp_A, nA - imp_A], [imp_C, nC - imp_C]])
print(f"  Fisher exact p = {pf:.3f}  (odds ratio {OR:.2f}; 0 impaired in Apollo arm)")

print(f"\nUnobserved (NO_EVIDENCE) cases that drive ascertainment: Apollo {ne_A}, Comparison {ne_C}")
print("Bounds on impairment rate / risk difference over the 4 extreme NO_EVIDENCE assignments:")
corners = []
for aA in (0, ne_A):              # impaired among Apollo NO_EVIDENCE
    for aC in (0, ne_C):          # impaired among Comparison NO_EVIDENCE
        rA = (imp_A + aA) / nA
        rC = (imp_C + aC) / nC
        corners.append((aA, aC, rA, rC, rA - rC))
        print(f"  Apollo NE->imp={aA}, Comp NE->imp={aC}: "
              f"Apollo {rA*100:4.1f}%, Comparison {rC*100:4.1f}%, diff {(rA-rC)*100:+5.1f}%")
diffs = [c[4] for c in corners]
print(f"  => Risk difference (Apollo-Comparison) bounded in [{min(diffs)*100:+.1f}%, {max(diffs)*100:+.1f}%]"
      f"  (sign {'flips' if min(diffs)<0<max(diffs) else 'stable'})")

print("\nDepth-stratified (best ascertainment = HIGH documentation_depth):")
for depth in ["HIGH", "MEDIUM", "LOW"]:
    sub = cog[cog["documentation_depth"] == depth]
    for g in ["Apollo", "Comparison"]:
        s = sub[sub.grp == g]
        imp = int((s["cognitive_status_20260601"] == "IMPAIRED_DOCUMENTED").sum())
        ne  = int((s["cognitive_status_20260601"] == "NO_EVIDENCE_EITHER_WAY").sum())
        print(f"  depth={depth:6s} {g:11s} impaired {imp}/{len(s)}, NO_EVIDENCE {ne}/{len(s)}")
print("Where the documented impairments fall:")
print(df.loc[df.cognitive_status_20260601=="IMPAIRED_DOCUMENTED",
             ["full_name","cohort","documentation_depth"]].to_string(index=False))

print("\nConditional-on-documented endpoint (among IMPAIRED+INTACT only; removes NO_EVIDENCE):")
for g in ["Apollo", "Comparison"]:
    s = cog[cog.grp == g]
    imp = int((s.cognitive_status_20260601 == "IMPAIRED_DOCUMENTED").sum())
    intact_n = int((s.cognitive_status_20260601 == "INTACT_DOCUMENTED").sum())
    n = imp + intact_n
    lo, hi = clopper(imp, n)
    print(f"  {g:11s} impaired/documented = {imp}/{n} = {imp/n*100:.1f}%  (95% CI {lo*100:.1f}-{hi*100:.1f}%)")

print("\nDONE.")
