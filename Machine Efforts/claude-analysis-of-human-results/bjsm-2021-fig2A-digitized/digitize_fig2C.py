#!/usr/bin/env python3
"""
Digitize Figure 2C (Antero et al. 2021, Br J Sports Med 55:206-212):
cumulative probability of death per age, US Olympians vs the US general population.

Caption, verbatim: "(C) Cumulative probability of death per age among former US Olympians
(green area) and the general population (black curve)."

Method. The panel is a stacked area chart: teal fill from 0 up to the Olympians' curve,
then a grey wedge up to the general population's curve, which carries a black outline.
So for each pixel column we walk UP from the axis through the contiguous non-white fill:
  - the top of that run       = the general population's cumulative death probability
  - the top of its teal part  = the Olympians' cumulative death probability
Anchoring the walk at the axis makes the reading immune to floating ink elsewhere in the
panel - the "C" panel letter and the inset ("Early mortality", a separate box in the upper
left) are not connected to the fill and are therefore never picked up.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import digitize_lib as D

HERE = Path(__file__).resolve().parent
SRC = (HERE.parent.parent.parent / "Human Efforts" / "Graphs" / "Third Party"
       / "bjsports-2021-February-55-4-206-F2.large (1).jpg")

BOX = (54, 626, 556, 956)          # measured plot-box border lines
XI0, XI1 = 56, 624       # skip the box border columns themselves
Y_ZERO_SCAN = 938                  # a row just above the F = 0 baseline (the tick sits at 941.5)
FILL_MAX = 195                     # max channel below this counts as fill; the dotted grid lines
                                   # in the white region measure 194-230, the grey wedge 155-185


def main():
    img = D.load_rgb(SRC)
    xt, yt = D.measure_calibration(img, BOX)
    xt = [t for t in xt if 130 <= t <= 560]
    axes = D.Axes(xt, [20, 40, 60, 80], yt, [1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
    print(f"x ticks {xt} -> 20,40,60,80 yr  ({axes.px_per_x():.4f} px/yr, resid {axes.x_resid:.3f} yr)")
    print(f"y ticks {yt} -> 1.0..0.0        ({abs(axes.px_per_y()):.2f} px/unit, resid {axes.y_resid:.4f})")

    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    teal = (np.abs(g - b) <= 14) & (g >= 95) & (r <= 70)
    filled = img.max(2) < FILL_MAX

    oly, pop, empty = {}, {}, []
    for x in range(XI0, XI1 + 1):
        y = Y_ZERO_SCAN
        while y > BOX[2] + 1 and filled[y, x]:
            y -= 1
        top = y + 1
        if top >= Y_ZERO_SCAN:          # no fill in this column: outside the data range
            empty.append(x)
            continue
        pop[x] = float(top)
        ys = np.where(teal[top : Y_ZERO_SCAN + 1, x])[0]
        if len(ys):
            oly[x] = float(ys.min() + top)

    grid = np.arange(13, 95, 1.0)
    out = {}
    for name, tr in (("olympians", oly), ("population", pop)):
        xd, yd = D.to_data(tr, axes)
        v = np.clip(D.resample(xd, yd, grid), 0.0, 1.0)
        run = -np.inf                    # cumulative death probability is non-decreasing
        for i in range(len(v)):
            if np.isnan(v[i]):
                continue
            run = max(run, v[i])
            v[i] = run
        out[name] = v
        print(f"{name:12s} columns={len(tr):4d}  age span {xd.min():5.1f}-{xd.max():5.1f}")

    with open(HERE / "fig2C_cumulative_death_by_age.csv", "w", newline="") as fh:
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
    print(f"\nSANITY: area between the two curves, age {lo:.0f}-{hi:.0f} = {area:.2f} yr.")
    print("        The paper's headline years-saved is 5.1 (95% CI 4.3-6.0). The paper computes")
    print("        that per individual over their own follow-up, so this is an order-of-magnitude")
    print("        check on curve identity only, not a reproduction of the estimate.")

    (HERE / "_verify").mkdir(exist_ok=True)
    (HERE / "_verify" / "fig2C_meta.json").write_text(json.dumps({
        "plot_box_px": list(BOX), "x_ticks_px": xt, "x_tick_values": [20, 40, 60, 80],
        "y_ticks_px": yt, "y_tick_values": [1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
        "px_per_year": axes.px_per_x(), "px_per_prob_unit": abs(axes.px_per_y()),
        "fill_threshold_max_channel": FILL_MAX,
        "columns": {"olympians": len(oly), "population": len(pop)},
        "columns_with_no_fill": len(empty),
        "area_between_curves_yr": area,
    }, indent=2))
    np.save(HERE / "_verify" / "fig2C_series.npy",
            np.vstack([grid, out["olympians"], out["population"]]))
    print("wrote fig2C_cumulative_death_by_age.csv")


if __name__ == "__main__":
    main()
