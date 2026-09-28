#!/usr/bin/env python3
"""
Digitize the period curves of Figure 2B (Antero et al. 2021): survival probability by AGE
for the whole US Olympian cohort split into six historical periods. We take p2, p3 and p4:

  p2  between the World Wars, 1920-1936
  p3  post-WWII and the beginning of the Cold War, 1948-1964   <- the Apollo-era comparator
  p4  Cold War and the Olympic boycotts, 1968-1984

p3 is the era-matched cohort for the Apollo astronauts (born 1923-1937, selected 1959-1966).

Panel B is the hardest of the four: six curves with pale CI bands that overlap heavily
between ages 60 and 95. Every column where two saturated hues sit within 4 px of each other
is recorded in _verify/fig2B_meta.json as an ambiguity, not silently smoothed away.
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

BOX = (734, 1279, 18, 295)
XI0, XI1 = 736, 1277
YI0, YI1 = 20, 294
LEGEND = (770, 850, 108, 268)      # swatch column + labels, measured from the swatch blobs


def in_legend(x, run):
    return LEGEND[0] <= x <= LEGEND[1] and not (run[1] < LEGEND[2] or run[0] > LEGEND[3])


def hue_mask(img, channel, sep, vmax=210):
    others = [i for i in range(3) if i != channel]
    lead = img[..., channel] - np.maximum(img[..., others[0]], img[..., others[1]])
    return (lead >= sep) & (img.max(2) <= vmax)


def main():
    img = D.load_rgb(SRC)
    xt, yt = D.measure_calibration(img, BOX)
    axes = D.Axes(xt, [0, 20, 40, 60, 80, 100], yt, [100, 75, 50, 25, 0])
    print(f"x ticks {xt} -> 0..100 age ({axes.px_per_x():.4f} px/yr, resid {axes.x_resid:.3f} yr)")
    print(f"y ticks {yt} -> 100..0 %      ({abs(axes.px_per_y()):.4f} px/%, resid {axes.y_resid:.3f} %)")

    masks = {
        "p2_1920_1936": hue_mask(img, 0, 45),
        "p3_1948_1964": hue_mask(img, 1, 30),
        "p4_1968_1984": hue_mask(img, 2, 45),
    }

    xs = list(range(XI0, XI1 + 1))
    tracks, coverage = {}, {}
    for name, m in masks.items():
        tr = {}
        for x in xs:
            rs = [r for r in D.column_runs(m, x, YI0, YI1) if not in_legend(x, r)]
            rs = [r for r in rs if (r[1] - r[0]) <= 8]        # a line, not a smeared blend
            if rs:
                a, b = max(rs, key=lambda r: r[1] - r[0])
                tr[x] = (a + b) / 2
        tracks[name] = tr
        coverage[name] = len(tr) / len(xs)
        print(f"{name:14s} columns={len(tr):4d} ({100*coverage[name]:.0f}% of the panel width)")

    # ---- record every column where two of the three hues coexist within 4 px ---------------
    ambiguous = []
    keys = list(tracks)
    for x in xs:
        vals = [(k, tracks[k][x]) for k in keys if x in tracks[k]]
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                if abs(vals[i][1] - vals[j][1]) <= 4:
                    ambiguous.append({"pixel_x": x, "age": round(float(axes.x(x)), 2),
                                      "curves": [vals[i][0], vals[j][0]]})
    print(f"columns where two curves sit within 4 px: {len(ambiguous)}")

    grid = np.arange(0, 106, 1.0)
    series = {}
    for name, tr in tracks.items():
        xd, yd = D.to_data(tr, axes)
        v = np.clip(D.resample(xd, yd, grid, monotone_dec=True), 0.0, 100.0)
        series[name] = v
        print(f"{name:14s} age span {xd.min():5.1f}-{xd.max():5.1f}")

    # ---- conditioning on survival to 30 ---------------------------------------------------
    # Apollo's curve is conditional on survival to 30 (all 29 were alive then; earliest death
    # age is 51). The panel-B curves are not. S(a | alive at 30) = S(a) / S(30) puts them on
    # the same footing, and it also removes the 1961 figure-skating air crash the supplementary
    # file flags for period 3 (those deaths were all under age 20).
    cond = {}
    for name, v in series.items():
        s30 = np.interp(30.0, grid, np.nan_to_num(v, nan=100.0))
        cond[name] = np.clip(v / s30 * 100.0, 0.0, 100.0) if s30 > 0 else v * np.nan
        print(f"{name:14s} S(30) = {s30:.2f}%  -> conditioning divisor")

    with open(HERE / "fig2B_periods_by_age.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age_years"]
                   + [f"{k}_survival_pct" for k in tracks]
                   + [f"{k}_survival_pct_given_alive_at_30" for k in tracks])
        for i, a in enumerate(grid):
            row = [f"{a:.0f}"]
            vals = [series[k][i] for k in tracks] + [cond[k][i] for k in tracks]
            if all(np.isnan(v) for v in vals):
                continue
            row += ["" if np.isnan(v) else f"{v:.2f}" for v in vals]
            w.writerow(row)

    (HERE / "_verify").mkdir(exist_ok=True)
    (HERE / "_verify" / "fig2B_meta.json").write_text(json.dumps({
        "plot_box_px": list(BOX), "x_ticks_px": xt, "x_tick_values": [0, 20, 40, 60, 80, 100],
        "y_ticks_px": yt, "y_tick_values": [100, 75, 50, 25, 0],
        "px_per_year": axes.px_per_x(), "px_per_pct": abs(axes.px_per_y()),
        "legend_exclusion_px": list(LEGEND),
        "coverage_fraction": coverage,
        "columns": {k: len(v) for k, v in tracks.items()},
        "ambiguous_columns_two_hues_within_4px": ambiguous,
        "S30_percent": {k: float(np.interp(30.0, grid, np.nan_to_num(v, nan=100.0)))
                        for k, v in series.items()},
    }, indent=2))
    np.save(HERE / "_verify" / "fig2B_series.npy",
            np.vstack([grid] + [series[k] for k in tracks] + [cond[k] for k in tracks]))
    print("wrote fig2B_periods_by_age.csv")


if __name__ == "__main__":
    main()
