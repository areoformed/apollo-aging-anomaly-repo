#!/usr/bin/env python3
"""
Kaplan-Meier survival for the 29 Apollo-programme astronauts, computed from
`Human Efforts/scripts/Astronaut MC/apolloData.h` (read-only source of truth).

Rows are {"name", birthYear, deathYear, ...} with deathYear 0 meaning still living.
Age at death = deathYear - birthYear. Living astronauts are censored at 2026 - birthYear.
Ties are broken with events before censorings, the standard convention.

Only birth and death YEARS are recorded, so every age carries +/- 1 year of quantisation.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent.parent / "Human Efforts" / "scripts" / "Astronaut MC" / "apolloData.h"
STUDY_END_YEAR = 2026
ROW = re.compile(r'\{\s*"((?:[^"\\]|\\.)+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,')


def load():
    rows = []
    for m in ROW.finditer(DATA.read_text()):
        name, birth, death = m.group(1), int(m.group(2)), int(m.group(3))
        if death:
            rows.append((name, birth, death, death - birth, 1))
        else:
            rows.append((name, birth, None, STUDY_END_YEAR - birth, 0))
    assert len(rows) == 29, len(rows)
    return rows


def km(observations):
    """observations: list of (time, event). Returns (times, survival) as a step function."""
    obs = sorted(observations, key=lambda o: (o[0], -o[1]))
    n_at_risk = len(obs)
    s = 1.0
    times, surv = [], []
    i = 0
    while i < len(obs):
        t = obs[i][0]
        d = 0
        c = 0
        j = i
        while j < len(obs) and obs[j][0] == t:
            if obs[j][1]:
                d += 1
            else:
                c += 1
            j += 1
        if d:
            s *= 1 - d / n_at_risk
            times.append(t)
            surv.append(s)
        n_at_risk -= d + c
        i = j
    return np.array(times, float), np.array(surv, float)


def step_at(times, surv, x, s0=1.0):
    """Right-continuous step evaluation: S(x) = last surv value at a time <= x."""
    x = np.atleast_1d(np.asarray(x, float))
    out = np.full(x.shape, s0)
    for i, xi in enumerate(x):
        m = times <= xi
        if m.any():
            out[i] = surv[m][-1]
    return out


def main():
    rows = load()
    deaths = [r for r in rows if r[4] == 1]
    alive = [r for r in rows if r[4] == 0]
    ages = [r[3] for r in rows]
    print(f"n={len(rows)}  deaths={len(deaths)}  censored(alive at {STUDY_END_YEAR})={len(alive)}")
    print(f"age at death: min {min(r[3] for r in deaths)}  max {max(r[3] for r in deaths)}")
    print(f"censoring ages: {sorted(r[3] for r in alive)}")
    print(f"all 29 alive at 30? {min(ages) >= 30}  (earliest death age {min(r[3] for r in deaths)})")

    obs_age = [(r[3], r[4]) for r in rows]
    t, s = km(obs_age)

    with open(HERE / "apollo_km_by_age.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age_years", "survival_pct", "n_deaths_at_age", "n_at_risk_before"])
        n = len(rows)
        prev = 0
        for age in sorted({r[3] for r in rows}):
            d = sum(1 for r in rows if r[3] == age and r[4] == 1)
            c = sum(1 for r in rows if r[3] == age and r[4] == 0)
            sv = step_at(t, s, age)[0] * 100
            if d:
                w.writerow([age, f"{sv:.4f}", d, n])
            n -= d + c
            prev = sv

    with open(HERE / "apollo_roster.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "birth_year", "death_year", "age_years", "event_1_death_0_censored"])
        for r in rows:
            w.writerow([r[0], r[1], r[2] if r[2] else "", r[3], r[4]])

    print("\nKM steps (age, S%):")
    print("  " + "  ".join(f"{int(a)}:{v*100:.1f}" for a, v in zip(t, s)))
    print(f"\nmedian survival age = {t[s <= 0.5][0] if (s <= 0.5).any() else 'n/a'}")
    print("wrote apollo_km_by_age.csv, apollo_roster.csv")
    return rows, t, s


if __name__ == "__main__":
    main()
