#!/usr/bin/env python3
"""
fragility.py — Stress-test the SuperAger-rate anomaly against the DOCUMENTED Space Grandpa
coding uncertainty (the ascertainment-bias concern). Two targets:

  (A) Apollo vs AGE-MATCHED population (the primary fair test): does P(X>=obs) survive
      flipping Apollo's weakest Y-codings to N? (positive-direction: removing a claim, never
      adding a decline label).
  (B) Apollo vs comparator astronauts: does the gap survive simultaneously (i) downgrading
      Apollo's weak Y's and (ii) upgrading the comparator's under-investigated N's to Y
      (the symmetric-documentation-effort worst case the prior report used)?

Perturbations are taken ONLY from the project's own SG-audit-summary.md:
  - Apollo weak/borderline: Mattingly already N (not flipped). No Apollo Y flagged "weak"
    in the audit; for a hostile bound we additionally test removing the 2 thinnest-described
    Apollo Y's by citation (sensitivity, labelled). POSITIVE framing: this only REMOVES a
    vitality assertion; it does NOT assert decline.
  - Comparator under-investigated N -> Y (audit-named): Holmquest(87), Parker(89), Mattingly(87,
    Apollo so not a comparator), plus weak control Y's already counted (Musgrave, Lind kept Y).
    We also test +3 and +4 generic control upgrades as in prior report.

All p-values: age-matched Poisson-binomial tail (A); Fisher exact + Newcombe diff (B).
Outputs: fragility_age_matched.csv, fragility_apollo_vs_comparator.csv
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))

GBD = [(80, 85, 0.866), (85, 90, 0.791), (90, 95, 0.697), (95, 200, 0.507)]
def gbd_p(age):
    for lo, hi, r in GBD:
        if lo <= age < hi:
            return r
    return np.nan
def poisbin_pmf(probs):
    pmf = np.array([1.0])
    for p in probs:
        pmf = np.convolve(pmf, [1-p, p])
    return pmf

apollo80 = d[(d.cohort == "apollo") & d.reached_80].copy()      # 22 survivors
probs = apollo80.endpoint_age.map(gbd_p).values
exp_pop = probs.sum()

# Identify Apollo Y survivors with comparatively THIN citations for a hostile-bound flip.
# From the citation review, the 2 thinnest-anchored Apollo 80+ Y's (still real, but to bound
# the ascertainment worry) are taken as: those whose strongest cited event is closest to 80.
# We test removing 0,1,2,3 of Apollo's Y's. This is a SENSITIVITY BOUND, not an assertion.
apollo_y_count = int(apollo80.superager.sum())  # 21

print("=" * 96)
print("(A) FRAGILITY of Apollo vs AGE-MATCHED population (Poisson-binomial, GBD dementia-free)")
print(f"    Apollo survivors=22, expected(pop dementia-free)={exp_pop:.2f}")
print("    Each row REMOVES k of Apollo's 21 vitality assertions (positive-direction bound).")
print("=" * 96)
A_rows = []
for k in range(0, 5):
    obs = apollo_y_count - k
    pmf = poisbin_pmf(probs)
    p_ge = pmf[obs:].sum() if obs <= len(pmf)-1 else 0.0
    A_rows.append(dict(apollo_Y_removed=k, apollo_obs_SA=obs, expected_pop=exp_pop,
                       ratio=obs/exp_pop, p_poisbin_ge=p_ge))
    print(f"  remove {k}: obs SA={obs:2d}  ratio={obs/exp_pop:.2f}  P(X>={obs})={p_ge:.3e}"
          f"   {'(sig@0.05)' if p_ge<0.05 else '(N.S.)'}")
pd.DataFrame(A_rows).to_csv(os.path.join(OUT, "fragility_age_matched.csv"), index=False)

# ----------------------------------------------------------------------------
# (B) Apollo vs comparator astronauts (NASA non-Apollo flew, no pre1970 acc), conditional rate.
# Baseline: Apollo 21/22 vs comparator 16/23.
# ----------------------------------------------------------------------------
comp80 = d[(d.cohort == "nasa_nonapollo") & d.flew & ~d.pre1970_accidental_death & d.reached_80].copy()
ap_k, ap_n = apollo_y_count, len(apollo80)            # 21, 22
co_k, co_n = int(comp80.superager.sum()), len(comp80)  # 16, 23

def fisher_diff(ak, an, ck, cn):
    table = [[ak, an-ak], [ck, cn-ck]]
    _, p = stats.fisher_exact(table, alternative="greater")
    return p

print("\n" + "=" * 96)
print("(B) FRAGILITY Apollo vs NASA non-Apollo flyers (conditional SuperAger rate), Fisher one-sided")
print(f"    Baseline: Apollo {ap_k}/{ap_n} vs comparator {co_k}/{co_n}")
print("    Hostile worst case: simultaneously REMOVE Apollo Y's AND ADD comparator Y's")
print("=" * 96)
B_rows = []
scenarios = [
    ("baseline", 0, 0),
    ("comparator +2 (Holmquest,Parker N->Y)", 0, 2),
    ("comparator +3", 0, 3),
    ("comparator +4", 0, 4),
    ("apollo -1 Y", 1, 0),
    ("apollo -2 Y", 2, 0),
    ("apollo -2 AND comparator +3 (double hostile)", 2, 3),
    ("apollo -3 AND comparator +4 (extreme)", 3, 4),
]
for lbl, dap, dco in scenarios:
    ak = ap_k - dap
    ck = min(co_k + dco, co_n)
    p = fisher_diff(ak, ap_n, ck, co_n)
    B_rows.append(dict(scenario=lbl, apollo=f"{ak}/{ap_n}", comparator=f"{ck}/{co_n}",
                       apollo_rate=ak/ap_n, comp_rate=ck/co_n, p_fisher_greater=p))
    print(f"  {lbl:46s} Apollo {ak}/{ap_n}={ak/ap_n*100:.0f}%  comp {ck}/{co_n}={ck/co_n*100:.0f}%"
          f"  p={p:.3f} {'(sig)' if p<0.05 else '(N.S.)'}")
pd.DataFrame(B_rows).to_csv(os.path.join(OUT, "fragility_apollo_vs_comparator.csv"), index=False)

print("\n[write] outputs/fragility_age_matched.csv, fragility_apollo_vs_comparator.csv")
