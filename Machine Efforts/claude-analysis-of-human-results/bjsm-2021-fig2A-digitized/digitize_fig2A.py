#!/usr/bin/env python3
"""
Digitize all four curves of Figure 2A, Antero et al. 2021 (Br J Sports Med 55:206-212):
Male Olympians, Female Olympians, Male population, Female population --- survival probability
against follow-up time since the athlete's first Olympic Games.

Method: colour masks -> per-column pixel runs -> continuity tracking -> calibrated data ->
1-year resample. Nothing is traced by eye. Outputs four CSVs plus points_raw.csv.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import digitize_lib as D

HERE = Path(__file__).resolve().parent
SRC = (
    HERE.parent.parent.parent
    / "Human Efforts"
    / "Graphs"
    / "Third Party"
    / "bjsports-2021-February-55-4-206-F2.large (1).jpg"
)

# Plot box border lines, measured (not assumed) by scanning for long dark runs.
BOX = (99, 626, 18, 355)          # x_left, x_right, y_top, y_bottom
XI0, XI1 = 100, 625               # interior columns
YI0, YI1 = 20, 354                # interior rows
# Legend ink bounding box, measured: x 140-328, y 214-328. Padded slightly.
LEGEND = (138, 336, 210, 332)


def in_legend(x, run):
    return LEGEND[0] <= x <= LEGEND[1] and not (run[1] < LEGEND[2] or run[0] > LEGEND[3])


def track(mask_core, mask_weak, xs, seeds, y0, y1, tol=9, exclude=None):
    """Follow one continuous curve across columns, preferring the core mask.

    `seeds` is {x: y} of columns where the curve's identity is already certain.
    Walks outward from the seeded span in both directions, predicting the next
    position by linear extrapolation of the last two accepted points.
    """
    out = dict(seeds)

    def candidates(mask, x):
        rs = D.column_runs(mask, x, y0, y1)
        if exclude is not None:
            rs = [r for r in rs if not exclude(x, r)]
        return [(a + b) / 2 for a, b in rs]

    def walk(order):
        hist = []
        for x in order:
            if x in out:
                hist.append((x, out[x]))
                hist = hist[-2:]
                continue
            if not hist:
                continue
            if len(hist) == 2 and hist[1][0] != hist[0][0]:
                slope = (hist[1][1] - hist[0][1]) / (hist[1][0] - hist[0][0])
            else:
                slope = 0.0
            pred = hist[-1][1] + slope * (x - hist[-1][0])
            best = None
            for m, t in ((mask_core, tol), (mask_weak, tol)):
                cands = candidates(m, x)
                if not cands:
                    continue
                c = min(cands, key=lambda v: abs(v - pred))
                if abs(c - pred) <= t:
                    best = c
                    break
            if best is not None:
                out[x] = best
                hist.append((x, best))
                hist = hist[-2:]
        return out

    walk(sorted(xs))
    walk(sorted(xs, reverse=True))
    return out


def main():
    img = D.load_rgb(SRC)

    # ---- calibration from tick pixels -------------------------------------------------
    xt, yt = D.measure_calibration(img, BOX)
    assert len(xt) == 5 and len(yt) == 5, (xt, yt)
    axes = D.Axes(xt, [0, 20, 40, 60, 80], yt, [100, 75, 50, 25, 0])
    print(f"x ticks {xt} -> 0..80 yr   ({axes.px_per_x():.4f} px/yr, max resid {axes.x_resid:.3f} yr)")
    print(f"y ticks {yt} -> 100..0 %   ({axes.px_per_y():.4f} px/%, max resid {axes.y_resid:.3f} %)")

    # ---- masks -------------------------------------------------------------------------
    blue_core = D.mask_blue(img, dark_max=155, sep=18)
    blue_weak = D.mask_blue(img, dark_max=225, sep=11)
    grn_core = D.mask_green_solid(img, dark_max=190, sep=18, rb_tol=20)
    grn_weak = D.mask_green_solid(img, dark_max=235, sep=12, rb_tol=30)
    cha_core = D.mask_chartreuse(img, gb=70, rb=45)
    cha_weak = D.mask_chartreuse(img, gb=48, rb=30)

    xs = list(range(XI0, XI1 + 1))

    # ---- blue pair: solid Male Olympians (upper) vs dotted Male population (lower) ------
    up, lo, amb = D.split_two_tracks(blue_core, xs, YI0, YI1, exclude=in_legend, max_jump=12)
    m_oly = track(blue_core, blue_weak, xs, up, YI0, YI1, tol=9, exclude=in_legend)
    # dotted: keep only core runs that are not the solid track, then interpolate its gaps
    m_pop = dict(lo)
    for x in xs:
        if x in m_pop:
            continue
        rs = [r for r in D.column_runs(blue_core, x, YI0, YI1) if not in_legend(x, r)]
        cands = [(a + b) / 2 for a, b in rs]
        s = m_oly.get(x)
        cands = [c for c in cands if s is None or c > s + 3]
        if cands:
            m_pop[x] = max(cands)

    # ---- green pair: solid Female Olympians, chartreuse dotted Female population --------
    f_seed = D.unique_run_only(grn_core, xs, YI0, YI1, exclude=in_legend)
    f_oly = track(grn_core, grn_weak, xs, f_seed, YI0, YI1, tol=9, exclude=in_legend)
    f_pop = D.extract_single(cha_core, xs, YI0, YI1, "largest", exclude=in_legend)
    for x in xs:                      # widen with the weak mask only where core found nothing
        if x not in f_pop:
            rs = [r for r in D.column_runs(cha_weak, x, YI0, YI1) if not in_legend(x, r)]
            if len(rs) == 1:
                a, b = rs[0]
                f_pop[x] = (a + b) / 2

    tracks = {
        "male_olympians": m_oly,
        "female_olympians": f_oly,
        "male_population": m_pop,
        "female_population": f_pop,
    }

    # ---- to data space, resample onto a 1-year grid -------------------------------------
    grid = np.arange(0, 84, 1.0)
    series, spans = {}, {}
    for name, tr in tracks.items():
        xd, yd = D.to_data(tr, axes)
        spans[name] = (float(xd.min()), float(xd.max()))
        v = D.resample(xd, yd, grid, monotone_dec=True)
        v = np.clip(v, 0.0, 100.0)
        series[name] = v
        print(f"{name:20s} columns={len(tr):4d}  span {xd.min():5.2f}-{xd.max():5.2f} yr")

    # Survival is 100% at t=0 by definition for KM and for the matched life-table curve.
    # Where the digitizer resolved nothing before its first point, join to (0, 100) linearly.
    anchored = {}
    for name in series:
        series[name], seg = D.anchor_at_zero(grid, series[name])
        if seg:
            anchored[name] = seg

    # ---- write CSVs ----------------------------------------------------------------------
    for name, v in series.items():
        with open(HERE / f"{name}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["followup_years", "survival_pct"])
            for t, s in zip(grid, v):
                if not np.isnan(s):
                    w.writerow([f"{t:.0f}", f"{s:.2f}"])

    with open(HERE / "points_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["curve", "pixel_x", "pixel_y", "followup_years", "survival_pct"])
        for name, tr in tracks.items():
            for x in sorted(tr):
                y = tr[x]
                w.writerow([name, x, f"{y:.1f}", f"{axes.x(x):.4f}", f"{axes.y(y):.4f}"])

    # ---- validation against numbers printed in the paper ---------------------------------
    def median_survival(v):
        ok = ~np.isnan(v)
        t, s = grid[ok], v[ok]
        below = np.where(s <= 50)[0]
        if len(below) == 0:
            return None
        i = below[0]
        if i == 0:
            return float(t[0])
        return float(np.interp(50.0, [s[i], s[i - 1]], [t[i], t[i - 1]]))

    checks = {
        "male_olympians_median_survival_yr": median_survival(series["male_olympians"]),
        "female_olympians_median_survival_yr": median_survival(series["female_olympians"]),
        "paper_male_median_yr": 56.7,
        "paper_male_ci": [55.8, 57.3],
        "paper_female_median_yr": 66.0,
        "paper_female_ci": [63.0, 67.6],
    }
    print("\nVALIDATION vs paper (Results, Overall survival):")
    print(f"  male   digitized {checks['male_olympians_median_survival_yr']:.2f} yr"
          f"   paper 56.7 (55.8-57.3)")
    print(f"  female digitized {checks['female_olympians_median_survival_yr']:.2f} yr"
          f"   paper 66.0 (63.0-67.6)")

    meta = {
        "source_image": str(SRC),
        "plot_box_px": {"x_left": BOX[0], "x_right": BOX[1], "y_top": BOX[2], "y_bottom": BOX[3]},
        "x_ticks_px": xt, "x_tick_values_yr": [0, 20, 40, 60, 80],
        "y_ticks_px": yt, "y_tick_values_pct": [100, 75, 50, 25, 0],
        "px_per_year": axes.px_per_x(), "px_per_pct": abs(axes.px_per_y()),
        "affine_max_residual": {"x_yr": axes.x_resid, "y_pct": axes.y_resid},
        "legend_ink_bbox_px": {"x0": 140, "x1": 328, "y0": 214, "y1": 328},
        "legend_exclusion_px": {"x0": LEGEND[0], "x1": LEGEND[1], "y0": LEGEND[2], "y1": LEGEND[3]},
        "columns_extracted": {k: len(v) for k, v in tracks.items()},
        "data_span_years": spans,
        "ambiguous_columns_blue_pair": [int(a) for a in amb],
        "anchored_to_t0_span_years": anchored,
        "validation": checks,
    }
    (HERE / "_verify" / "fig2A_meta.json").parent.mkdir(exist_ok=True)
    (HERE / "_verify" / "fig2A_meta.json").write_text(json.dumps(meta, indent=2))
    np.save(HERE / "_verify" / "fig2A_series.npy", np.vstack([grid] + [series[k] for k in
            ["male_olympians", "female_olympians", "male_population", "female_population"]]))
    print("\nwrote 4 CSVs + points_raw.csv + _verify/fig2A_meta.json")
    return axes, tracks, series, grid


if __name__ == "__main__":
    main()
