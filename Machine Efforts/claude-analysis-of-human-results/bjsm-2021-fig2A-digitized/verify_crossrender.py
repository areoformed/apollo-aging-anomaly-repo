#!/usr/bin/env python3
"""Independent matplotlib re-plot of every digitized series, purely as a cross-check on the
hand-rolled SVG geometry. Nothing here is a deliverable; the SVGs are."""
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import apollo_km

HERE = Path(__file__).resolve().parent
V = HERE / "_verify"
BASE_M, BASE_F = 25, 21

rows = apollo_km.load()
t, s = apollo_km.km([(r[3], r[4]) for r in rows])
a_age = np.concatenate([[30.0], t]); a_surv = np.concatenate([[1.0], s]) * 100

A = np.load(V / "fig2A_series.npy"); B = np.load(V / "fig2B_series.npy")
C = np.load(V / "fig2C_series.npy"); S1 = np.load(V / "figS1C_series.npy")

fig, ax = plt.subplots(2, 3, figsize=(19, 10), dpi=110)
names = ["male_olympians", "female_olympians", "male_population", "female_population"]

a = ax[0, 0]
for i, n in enumerate(names):
    a.plot(A[0], A[1 + i], lw=1.6, ls="--" if "population" in n else "-", label=n)
a.set_title("2A - follow-up axis"); a.set_xlabel("follow-up (yr)"); a.legend(fontsize=7)

a = ax[0, 1]
for i, n in enumerate(names):
    a.plot(A[0] + (BASE_M if "male_" in n and not n.startswith("female") else BASE_F),
           A[1 + i], lw=1.4, ls="--" if "population" in n else "-", label=n)
a.step(a_age, a_surv, where="post", lw=2.2, color="#d64500", label="Apollo")
a.set_title("2A - age axis + Apollo"); a.set_xlabel("age (yr)"); a.legend(fontsize=7)

a = ax[0, 2]
for i, n in enumerate(["p2", "p3", "p4"]):
    a.plot(B[0], B[1 + i], lw=1.0, ls=":", label=f"{n} published")
    a.plot(B[0], B[4 + i], lw=1.8, label=f"{n} | alive at 30")
a.step(a_age, a_surv, where="post", lw=2.2, color="#d64500", label="Apollo")
a.set_xlim(30, 106); a.set_title("2B - periods + Apollo"); a.legend(fontsize=6)

a = ax[1, 0]
a.plot(C[0], C[1], lw=1.8, label="Olympians"); a.plot(C[0], C[2], lw=1.8, color="k", label="population")
a.step(a_age, 1 - a_surv / 100, where="post", lw=2.2, color="#d64500", label="Apollo")
a.set_title("2C - cumulative death by age"); a.legend(fontsize=7)

a = ax[1, 1]
a.plot(S1[0], S1[1], lw=1.8, label="Olympians (at a Games by 30)")
a.plot(S1[0], S1[2], lw=1.8, color="k", label="population")
a.step(a_age, 1 - a_surv / 100, where="post", lw=2.2, color="#d64500", label="Apollo")
a.set_title("S1C - cumulative death from age 30"); a.legend(fontsize=7)

a = ax[1, 2]
a.step(a_age, a_surv, where="post", lw=2.2, color="#d64500")
cens = sorted(r[3] for r in rows if r[4] == 0)
a.plot(cens, [apollo_km.step_at(t, s, c)[0] * 100 for c in cens], "|", ms=14, color="#d64500")
a.set_title(f"Apollo KM alone (n=29, {sum(r[4] for r in rows)} deaths, 6 censored)")
a.set_xlabel("age (yr)")

for r_ in ax:
    for a_ in r_:
        a_.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(V / "crossrender_matplotlib.png")
print("wrote _verify/crossrender_matplotlib.png")
