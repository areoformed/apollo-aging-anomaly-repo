#!/usr/bin/env python3
"""
Digitize panel C of Supplementary Figure S1 (Antero et al. 2021, supplementary material 1, p.3):
"Cumulative probability of death conditional to the age of first Olympic participation.
 ... C) From age 30 onwards."

This is the paper's OWN age-30-conditional figure, so it is the closest published comparator
for an Apollo curve that starts at age 30 - no baseline-age shift is needed on either side.
Two cautions, both stated in the README: its cohort is "athletes who had already been at the
Olympics by the age of 30" (a restriction on ENTRY age, not merely survival to 30), and the
panel is small - about 228 x 287 px for the whole plot, roughly a third of Figure 2C's scale.

Colour scheme is carried over from the main paper's Figure 2C caption ("Olympians (green area)
and the general population (black curve)"); the supplementary file does not restate it.

The source is the PNG embedded in the supplementary PDF at its native resolution (919x807),
extracted with PyMuPDF; re-rasterising the page at higher dpi would add pixels but no detail.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import digitize_lib as D

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src" / "figS1_native.png"

BOX = (664, 892, 51, 338)          # measured: panel C of the 3x2 grid
XI0, XI1 = 666, 890
FILL_MAX = 180          # grey wedge is 169,169,169; the dotted grid lines are 190,190,190


def main():
    img = D.load_rgb(SRC)
    xt, yt = D.measure_calibration(img, BOX, tick_side_px=6, min_hits=2)
    print(f"raw ticks x={xt}  y={yt}")
    assert len(xt) == 5 and len(yt) == 6, (xt, yt)
    axes = D.Axes(xt, [20, 40, 60, 80, 100], yt, [1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
    print(f"x -> 20..100 age ({axes.px_per_x():.4f} px/yr, resid {axes.x_resid:.3f} yr)")
    print(f"y -> 1.0..0.0    ({abs(axes.px_per_y()):.3f} px/unit, resid {axes.y_resid:.4f})")
    print(f"panel is {BOX[1]-BOX[0]} x {BOX[3]-BOX[2]} px  -> 1 px = "
          f"{1/axes.px_per_x():.3f} yr and {abs(1/axes.px_per_y()):.4f} probability units")

    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    # S1's teal is (0,104,139) - bluer than Figure 2C's (0,138,138); measured, not assumed
    teal = (b - r >= 60) & (g - r >= 45) & (b >= 100)
    filled = img.max(2) < FILL_MAX
    y_zero = int(round((0.0 - axes.yb) / axes.ya)) - 3

    oly, pop = {}, {}
    for x in range(XI0, XI1 + 1):
        y = y_zero
        while y > BOX[2] + 1 and filled[y, x]:
            y -= 1
        top = y + 1
        if top >= y_zero:
            continue
        pop[x] = float(top)
        ys = np.where(teal[top : y_zero + 1, x])[0]
        if len(ys):
            oly[x] = float(ys.min() + top)

    grid = np.arange(30, 106, 1.0)
    out = {}
    for name, tr in (("olympians", oly), ("population", pop)):
        xd, yd = D.to_data(tr, axes)
        v = np.clip(D.resample(xd, yd, grid), 0.0, 1.0)
        run = -np.inf
        for i in range(len(v)):
            if np.isnan(v[i]):
                continue
            run = max(run, v[i])
            v[i] = run
        out[name] = v
        print(f"{name:12s} columns={len(tr):4d}  age span {xd.min():5.1f}-{xd.max():5.1f}")

    with open(HERE / "figS1C_cumulative_death_from_age30.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age_years", "olympians_cum_death_prob", "population_cum_death_prob"])
        for i, a in enumerate(grid):
            o, p = out["olympians"][i], out["population"][i]
            if not (np.isnan(o) and np.isnan(p)):
                w.writerow([f"{a:.0f}",
                            "" if np.isnan(o) else f"{o:.4f}",
                            "" if np.isnan(p) else f"{p:.4f}"])

    m = ~(np.isnan(out["olympians"]) | np.isnan(out["population"]))
    lo, hi = grid[m][0], min(90, grid[m][-1])
    sel = m & (grid >= lo) & (grid <= hi)
    area = float(np.trapezoid(out["population"][sel] - out["olympians"][sel], grid[sel]))
    print(f"\nSANITY: area between the curves, age {lo:.0f}-{hi:.0f} = {area:.2f} yr "
          f"(paper's whole-cohort years-saved 5.1, 95% CI 4.3-6.0)")

    (HERE / "_verify").mkdir(exist_ok=True)
    (HERE / "_verify" / "figS1C_meta.json").write_text(json.dumps({
        "source": "supplementary material 1, page 3, Figure S1 panel C (embedded PNG, 919x807)",
        "plot_box_px": list(BOX), "x_ticks_px": xt, "x_tick_values": [20, 40, 60, 80, 100],
        "y_ticks_px": yt, "y_tick_values": [1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
        "px_per_year": axes.px_per_x(), "px_per_prob_unit": abs(axes.px_per_y()),
        "one_px_in_years": abs(1 / axes.px_per_x()),
        "one_px_in_prob_units": abs(1 / axes.px_per_y()),
        "columns": {"olympians": len(oly), "population": len(pop)},
        "area_between_curves_yr": area,
    }, indent=2))
    np.save(HERE / "_verify" / "figS1C_series.npy",
            np.vstack([grid, out["olympians"], out["population"]]))
    print("wrote figS1C_cumulative_death_from_age30.csv")


if __name__ == "__main__":
    main()
