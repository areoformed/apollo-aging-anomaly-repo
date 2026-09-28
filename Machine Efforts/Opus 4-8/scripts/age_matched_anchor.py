#!/usr/bin/env python3
"""
age_matched_anchor.py — The FAIR population comparison for the SuperAger rate.

Problem with a single anchor: Apollo's 22 survivors-to-80 are NOT all 80-84. Their
current/at-death ages span ~82-97 (median ~90). The age-appropriate population
dementia-free rate for a man at 90 (~70%) is much lower than at 82 (~87%). So the
honest population comparator is an AGE-MATCHED expected SuperAger count: assign each
Apollo survivor the GBD male dementia-free rate for the age band they are observed at,
then sum to an expected count under the population model, and test observed vs expected.

This is a Poisson-binomial expectation (each survivor i has population vitality prob p_i
set by their age band). We then test the observed SuperAger count against that.

CONSTRUCT ASYMMETRY (stated, not hidden): Apollo numerator = Space Grandpa (public
activity); the p_i are clinical dementia-free rates (permissive). dementia-free is an
UPPER bound on cognitive vitality, so using it makes the population look MORE vital and
the test CONSERVATIVE for the anomaly. Conversely, ascertainment bias (famous Apollo
crews better documented) inflates the Apollo numerator. The two biases offset in unknown
proportion; net sign not asserted.

We use the age band at OBSERVED endpoint (current age if living, age at death if dead).
This is a positive-direction definition: a man documented active at 88 who later died at
90 was a SuperAger; we evaluate the population dementia-free prob at his observed age.

Outputs:
  - age_matched_anchor_detail.csv  (per Apollo survivor: age band, pop p_i)
  - age_matched_anchor_summary.csv (expected vs observed, Poisson-binomial tail p)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
OUT = os.path.abspath(os.path.join(HERE, "..", "outputs"))

d = pd.read_csv(os.path.join(DATA, "analysis_dataset.csv"))

# GBD male dementia-free by age band (2020), from Cao 2024 eTable4. 95+ aggregated.
GBD = [
    (80, 85, 0.866),
    (85, 90, 0.791),
    (90, 95, 0.697),
    (95, 200, 0.507),
]
def gbd_demfree(age):
    for lo, hi, r in GBD:
        if lo <= age < hi:
            return r, f"{lo}-{hi-1 if hi<200 else '+'}"
    return np.nan, "NA"

def poisson_binomial_pmf(probs):
    """Exact PMF of sum of independent Bernoulli(p_i) via DP."""
    pmf = np.array([1.0])
    for p in probs:
        pmf = np.convolve(pmf, [1-p, p])
    return pmf

def analyze(label, survivors):
    rows = []
    for _, r in survivors.iterrows():
        age = r.endpoint_age
        p, band = gbd_demfree(age)
        rows.append(dict(name=r["name"], endpoint_age=round(age, 1), deceased=bool(r.deceased),
                         age_band=band, pop_demfree_p=p, observed_superager=bool(r.superager)))
    det = pd.DataFrame(rows)
    probs = det.pop_demfree_p.values
    obs = int(det.observed_superager.sum())
    exp = probs.sum()
    pmf = poisson_binomial_pmf(probs)
    # one-sided upper tail P(X >= obs)
    p_ge = pmf[obs:].sum()
    return det, dict(cohort=label, n_survivors=len(det), observed_superagers=obs,
                     expected_superagers_pop=exp, ratio=obs/exp,
                     p_poisbin_ge=p_ge)

results = []
details = []
for label, mask in [
    ("Apollo", d.cohort == "apollo"),
    ("NASA non-Apollo flew (no pre1970 acc)",
     (d.cohort == "nasa_nonapollo") & d.flew & ~d.pre1970_accidental_death),
    ("GPT available non-Apollo (55)",
     (d.included_in_apollo_vs_other_available == True) & (d.cohort != "apollo")),
]:
    surv = d[mask & d.reached_80]
    det, summ = analyze(label, surv)
    det.insert(0, "cohort", label)
    details.append(det)
    results.append(summ)

det_all = pd.concat(details, ignore_index=True)
summ_all = pd.DataFrame(results)
det_all.to_csv(os.path.join(OUT, "age_matched_anchor_detail.csv"), index=False)
summ_all.to_csv(os.path.join(OUT, "age_matched_anchor_summary.csv"), index=False)

print("=" * 96)
print("AGE-MATCHED population SuperAger anchor (GBD male dementia-free at OBSERVED age band)")
print("  Population p_i = dementia-free (PERMISSIVE upper bound). Apollo numerator = public-activity.")
print("  Poisson-binomial exact tail. Cross-construct; conservative for the anomaly on the clinical axis.")
print("=" * 96)
for _, r in summ_all.iterrows():
    print(f"{r['cohort']:40s}  survivors={int(r.n_survivors):3d}  "
          f"observed SA={int(r.observed_superagers):3d}  expected(pop)={r.expected_superagers_pop:5.2f}  "
          f"ratio={r.ratio:.2f}  P(X>={int(r.observed_superagers)})={r.p_poisbin_ge:.3e}")

print("\n--- Apollo survivor age-band breakdown ---")
ap = det_all[det_all.cohort == "Apollo"]
print(ap.groupby("age_band").agg(n=("name", "size"),
      pop_p=("pop_demfree_p", "first"),
      observed_SA=("observed_superager", "sum")).to_string())
print("\n[write] outputs/age_matched_anchor_detail.csv, age_matched_anchor_summary.csv")
