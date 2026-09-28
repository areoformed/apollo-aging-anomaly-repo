#!/usr/bin/env python3
"""
Overlay an SSA expected-deaths-by-age curve onto the author's refined "Apollo Astronauts
Age Distribution" Sketch SVG.

WHAT IT DRAWS
-------------
The bars are the 29-astronaut cohort: deaths at age-at-death (navy) + the living at
current age (taupe). The overlaid dashed curve answers: "if these 29 men were just
average Americans of their birth years, where would actuarial science expect their
deaths to fall by age?" If the navy bars sit RIGHT of the curve, the astronauts
out-lived the baseline — the aging-anomaly read.

METHOD (v1 — every choice here is a flag for the author / the research-statistician)
-----------------------------------------------------------------------------
Source: SSA Cohort Life Tables, Males, Alternative-2 (intermediate) mortality,
2024 Trustees Report — l(x), d(x) by single year of age, by birth cohort.
  expected deaths in [a, a+5) = N * ( l(a) - l(a+5) ) / l(CONDITION_AGE)
1. COHORT_YEAR     — one representative birth year stands in for all 29.
                     FLAG: the rigorous version weights each astronaut's OWN birth-year cohort.
2. CONDITION_AGE   — we only compare among males who survived to this age, because the
                     astronaut sample, by construction, contains no childhood / young-adult
                     deaths. Conditioning removes that immortal-time bias. FLAG: 30 is a
                     defensible default (~selection era); the value moves the curve + scaling.
3. N_COHORT = 29   — scales the SS distribution to the cohort. The curve sums to ~29 over a
                     full lifetime; the navy bars sum to fewer because 6 are still alive
                     (right-censored) — so compare SHAPE / central tendency, not bar-for-bar.

Coordinates are read straight off the Sketch file (grid-aligned), so the curve lands
on the same axes as the bars. Writes a NEW svg; the input is never overwritten.

Run:  python3 apollo_ssa_overlay.py
"""

import csv
from pathlib import Path

BASE = Path(".")
SS_CSV  = BASE / "Human Efforts/Manually Compiled Data/Third Party/US Social Security/Actuarial Study 120/CohLifeTables_M_Alt2_TR2024.csv"
SVG_IN  = BASE / "Human Efforts/Graphs/For Claude Mutation/For Claude SSA overlay — Apollo Astronauts Age.svg"
SVG_OUT = SVG_IN.parent / "Apollo Astronauts Age — SSA overlay (v1).svg"

# --- the three methodological knobs (see docstring) ---
COHORT_YEAR   = 1928
CONDITION_AGE = 30
N_COHORT      = 29
BIN_LO, BIN_HI, BIN = 30, 120, 5

# --- coordinate mapping, read off the Sketch SVG (grid frame) ---
X0, X_PER_BIN   = 0.89164278, 71.331361     # x of the age-30 tick; px per 5-year bin
Y0, Y_PER_COUNT = 670.584976, 55.807869     # y of count 0; px per count unit
GRID_TX, GRID_TY = 123.9384, 113.1          # grid origin inside the chart's group
LINE = "#B3543F"                            # stand-in colour for the curve (the author restyles)

def x_at(age):   return X0 + (age - 30) / BIN * X_PER_BIN
def y_at(count): return Y0 - count * Y_PER_COUNT


def read_cohort(path, year):
    """Pull l(x) for one birth-year cohort from the SSA table."""
    lx = {}
    with path.open() as f:
        for row in csv.reader(f):
            if len(row) < 4 or not row[0].strip().isdigit():
                continue
            if int(row[0]) != year:
                continue
            try:
                lx[int(row[1])] = float(row[3])
            except ValueError:
                continue
    if CONDITION_AGE not in lx:
        raise SystemExit(f"cohort {year}: no l({CONDITION_AGE}) found.")
    return lx


def main():
    lx = read_cohort(SS_CSV, COHORT_YEAR)
    l_cond = lx[CONDITION_AGE]
    bins = list(range(BIN_LO, BIN_HI, BIN))
    exp = {a: N_COHORT * (lx.get(a, 0.0) - lx.get(a + BIN, 0.0)) / l_cond for a in bins}

    pts = " ".join(f"{x_at(a + BIN/2):.2f},{y_at(exp[a]):.2f}" for a in bins)
    dots = "\n".join(
        f'                    <circle cx="{x_at(a + BIN/2):.2f}" cy="{y_at(exp[a]):.2f}" r="3" fill="{LINE}"/>'
        for a in bins if exp[a] > 0.02)

    overlay = (
        f'                <g id="ssa-overlay" transform="translate({GRID_TX}, {GRID_TY})">\n'
        f'                    <polyline points="{pts}" fill="none" stroke="{LINE}" '
        f'stroke-width="2.5" stroke-dasharray="6,4" stroke-linejoin="round" stroke-linecap="round"/>\n'
        f'{dots}\n'
        f'                    <line x1="1092" y1="78" x2="1115" y2="78" stroke="{LINE}" '
        f'stroke-width="2.5" stroke-dasharray="6,4"/>\n'
        f'                    <text x="1126" y="83" fill="#555555" '
        f'font-family="SFMono-Light, SF Mono" font-size="16" font-weight="300">SSA EXPECTED</text>\n'
        f'                </g>\n'
    )

    svg = SVG_IN.read_text(encoding="utf-8")
    marker = '<g id="legend"'
    if marker not in svg:
        raise SystemExit("could not find the legend group to inject before.")
    # inject before the legend so the dashed curve sits on top of the bars
    svg = svg.replace('                ' + marker, overlay + '                ' + marker, 1)
    SVG_OUT.write_text(svg, encoding="utf-8")

    print(f"SSA cohort {COHORT_YEAR}, Males, Alt-2 (2024 TR); conditioned on survival to age {CONDITION_AGE}; scaled to N={N_COHORT}.")
    print(f"l({CONDITION_AGE}) = {l_cond:.0f}   (of 100,000 born)")
    print(f"\n{'bin':>7} {'exp deaths':>11}")
    tot = 0.0
    for a in bins:
        if exp[a] > 0.005:
            print(f"  {a:>3}-{a+4:<3} {exp[a]:>9.2f}")
            tot += exp[a]
    print(f"  total expected deaths (alive at {CONDITION_AGE} → eventual): {tot:.2f} of {N_COHORT}")
    print(f"\nWrote: {SVG_OUT.name}")


if __name__ == "__main__":
    main()
