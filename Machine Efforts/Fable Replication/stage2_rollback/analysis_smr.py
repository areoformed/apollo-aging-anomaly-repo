#!/usr/bin/env python3
"""Stage 2 analysis, part B: Standardized Mortality Ratio vs US male population.

Reference: CDC/NCHS "United States Life Tables, 2021", Table 2 (males), radix 100,000.
Source NVSR Vol 72 No 12 (2023-11-07); transcribed from the CA-DIR mirror PDF
https://www.dir.ca.gov/osip/LifeExpectancyTables2021.pdf  (ssa.gov / web.archive blocked WebFetch).

Method: indirect standardization from the same index date as the astronaut comparison
(1972-12-19). For subject i, expected deaths over the observed attained-age window
[a0,a1] = cumulative-hazard difference under the reference table:
   E_i = ln( L(a0_i) / L(a1_i) ),  L = linearly-interpolated male l_x.
O = observed deaths. SMR = O/E, exact Poisson 95% CI. (E_i conditions on survival to a0
via the l(a0) denominator, so this is a left-truncated / healthy-worker-appropriate SMR.)

CONSERVATISM: a 2021 period table understates the mortality these 1921-42 birth cohorts
actually faced at older ages (mortality fell over time), so E is understated and SMR is
biased UP toward 1. A true cohort table would push every SMR below LOWER than reported.
"""
import csv, math
from datetime import date
from scipy import stats

CSV="apollo_era_astronaut_cohort_v2.csv"; CENSOR=date(2026,6,1); INDEX=date(1972,12,19); Y=365.25

# CDC/NCHS US MALE life table 2021, l_x by exact age (radix 100000)
LX={30:96811,31:96562,32:96303,33:96035,34:95757,35:95472,36:95178,37:94874,38:94560,
39:94234,40:93895,41:93541,42:93170,43:92783,44:92379,45:91958,46:91516,47:91051,
48:90556,49:90029,50:89467,51:88870,52:88234,53:87556,54:86828,55:86044,56:85205,
57:84309,58:83352,59:82328,60:81235,61:80070,62:78836,63:77541,64:76188,65:74780,
66:73316,67:71782,68:70181,69:68511,70:66772,71:64975,72:63110,73:61167,74:59126,
75:57001,76:54693,77:52283,78:49731,79:47087,80:44313,81:41479,82:38563,83:35595,
84:32576,85:29498,86:26421,87:23344,88:20319,89:17394,90:14623,91:12052,92:9722,
93:7661,94:5889,95:4407,96:3206,97:2263,98:1549,99:1026,100:657}

def L(a):
    if a<=30: return LX[30]
    if a>=100: return LX[100]
    lo=int(math.floor(a)); hi=lo+1; f=a-lo
    return LX[lo]*(1-f)+LX[hi]*f          # linear interpolation of survivors

def d(s): return date.fromisoformat(s)
def age(b,t): return (t-b).days/Y

rows=list(csv.DictReader(open(CSV)))
def grp(r): return "Apollo" if r["cohort"]=="APOLLO_FLEW" else ("Comparison" if r["cohort"] in ("COMP_FLEW_OTHER","COMP_NEVER_FLEW") else "Apollo1")

def pois_ci(O,E):  # exact Poisson CI on the rate O/E
    lo=0.0 if O==0 else stats.chi2.ppf(0.025,2*O)/2/E
    hi=stats.chi2.ppf(0.975,2*O+2)/2/E
    return lo,hi

print("="*78)
print("PART 1(b)  STANDARDIZED MORTALITY RATIO vs US MALE POPULATION (CDC 2021)")
print("Index date 1972-12-19; attained-age windows; left-truncated SMR.")
print("="*78)

res={}
for g in ("Apollo","Comparison"):
    sub=[r for r in rows if grp(r)==g]
    sub=[r for r in sub if not (r["vital_status_20260601"]=="DEAD" and d(r["death_date"])<=INDEX)]  # alive at index
    O=0; E=0.0
    for r in sub:
        b=d(r["birth_date"]); a0=age(b,INDEX)
        dead=r["vital_status_20260601"]=="DEAD"
        a1=age(b, d(r["death_date"]) if dead else CENSOR)
        O+=int(dead); E+=math.log(L(a0)/L(a1))
    smr=O/E; lo,hi=pois_ci(O,E)
    res[g]=(O,E,smr,lo,hi,len(sub))
    print(f"\n{g}: n={len(sub)}  observed deaths O={O}  expected E={E:.1f}")
    print(f"   SMR = {smr:.3f}   95% CI [{lo:.3f}, {hi:.3f}]   (SMR<1 => fewer deaths than US male pop)")
    print(f"   => observed/expected deaths {O}/{E:.1f}; population would predict ~{E:.0f} deaths in this person-time")

# ratio of SMRs (Apollo vs Comparison) ; var(ln) = 1/O_A + 1/O_C
OA,EA=res["Apollo"][0],res["Apollo"][1]; OC,EC=res["Comparison"][0],res["Comparison"][1]
rsmr=(OA/EA)/(OC/EC); se=math.sqrt(1/OA+1/OC)
print(f"\nSMR ratio Apollo/Comparison = {rsmr:.3f}  95% CI [{math.exp(math.log(rsmr)-1.96*se):.3f}, {math.exp(math.log(rsmr)+1.96*se):.3f}]")
print("   (CI spans 1 => no detectable Apollo-vs-comparison difference, consistent with the Cox HR)")

# intuitive complement: expected survivors to censoring among those still alive-eligible
print("\nComplement — expected vs observed survival to 2026-06-01 (population reference):")
for g in ("Apollo","Comparison"):
    sub=[r for r in rows if grp(r)==g]
    sub=[r for r in sub if not (r["vital_status_20260601"]=="DEAD" and d(r["death_date"])<=INDEX)]
    exp_surv=0.0; obs_alive=0
    for r in sub:
        b=d(r["birth_date"]); a0=age(b,INDEX); aN=age(b,CENSOR)
        exp_surv+=L(aN)/L(a0)          # P(survive index->censoring age) under pop rates
        obs_alive+=int(r["vital_status_20260601"]=="ALIVE")
    print(f"   {g}: expected still-alive at 2026-06-01 under US male rates ~ {exp_surv:.1f} of {len(sub)}; observed {obs_alive}")
