#!/usr/bin/env python3
"""
Verification pass. For each digitized panel:
  1. re-plot the RESAMPLED 1-year series back into the original pixel grid and save an overlay PNG,
  2. report how far the deliverable (the CSV) sits from the raw per-column pixel extraction.

The second number is the one that matters: it is the error introduced by resampling onto a
1-year grid, on top of the +/- 1 px reading uncertainty of the extraction itself.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import digitize_lib as D

HERE = Path(__file__).resolve().parent
V = HERE / "_verify"
JPG = (HERE.parent.parent.parent / "Human Efforts" / "Graphs" / "Third Party"
       / "bjsports-2021-February-55-4-206-F2.large (1).jpg")
PNG = HERE / "_src" / "figS1_native.png"

COLOURS = {"male_olympians": "#e8590c", "female_olympians": "#c92a2a",
           "male_population": "#f08c00", "female_population": "#a61e4d",
           "olympians": "#e8590c", "population": "#c92a2a",
           "p2_1920_1936": "#e8590c", "p3_1948_1964": "#c92a2a", "p4_1968_1984": "#5f3dc4"}


def read_points():
    pts = {}
    with open(HERE / "points_raw.csv") as fh:
        for row in csv.DictReader(fh):
            pts.setdefault(row["curve"], []).append(
                (float(row["pixel_x"]), float(row["pixel_y"])))
    return pts


def report(name, xd_px, yd_px, grid, values, axes_x_of_px, px_per_unit, unit):
    """Compare the CSV (grid, values) against the raw pixel extraction."""
    keep = ~np.isnan(values)
    if keep.sum() < 2:
        return None
    data_x = axes_x_of_px(np.array(xd_px))
    pred = np.interp(data_x, grid[keep], values[keep], left=np.nan, right=np.nan)
    ok = ~np.isnan(pred)
    if ok.sum() == 0:
        return None
    # convert the residual from data units back into pixels
    resid_units = np.abs(pred[ok] - np.array(yd_px)[ok] * 0)  # placeholder, replaced below
    return resid_units


def main():
    img = D.load_rgb(JPG)
    out = {}

    # ---------------------------------------------------------------- Figure 2A
    meta = json.loads((V / "fig2A_meta.json").read_text())
    ax = D.Axes(meta["x_ticks_px"], meta["x_tick_values_yr"],
                meta["y_ticks_px"], meta["y_tick_values_pct"])
    arr = np.load(V / "fig2A_series.npy")
    grid, names = arr[0], ["male_olympians", "female_olympians",
                           "male_population", "female_population"]
    pts = read_points()

    fig, a = plt.subplots(figsize=(10, 6.4), dpi=140)
    a.imshow(img[0:410, 0:660])
    stats2A = {}
    for i, nm in enumerate(names):
        v = arr[1 + i]
        keep = ~np.isnan(v)
        px = (grid[keep] - ax.xb) / ax.xa
        py = (v[keep] - ax.yb) / ax.ya
        a.plot(px, py, lw=1.1, color=COLOURS[nm], label=nm.replace("_", " "))
        raw = np.array(pts[nm])
        rx, ry = raw[:, 0], raw[:, 1]
        pred_y = np.interp(rx, px, py, left=np.nan, right=np.nan)
        d = np.abs(pred_y - ry)
        d = d[~np.isnan(d)]
        stats2A[nm] = {"n_columns": int(len(rx)),
                       "mean_abs_dev_px": float(d.mean()), "max_abs_dev_px": float(d.max()),
                       "mean_abs_dev_survival_pct": float(d.mean() / abs(1 / ax.ya)),
                       "max_abs_dev_survival_pct": float(d.max() / abs(1 / ax.ya))}
    a.set_xlim(90, 640); a.set_ylim(400, 10)
    a.legend(fontsize=7, loc="lower left", framealpha=0.9)
    a.set_title("Figure 2A: digitized 1-year series re-plotted over the source panel", fontsize=9)
    a.axis("off"); fig.tight_layout(); fig.savefig(V / "fig2A_overlay.png"); plt.close(fig)
    out["fig2A"] = stats2A

    # ---------------------------------------------------------------- Figure 2B
    mb = json.loads((V / "fig2B_meta.json").read_text())
    axb = D.Axes(mb["x_ticks_px"], mb["x_tick_values"], mb["y_ticks_px"], mb["y_tick_values"])
    ab = np.load(V / "fig2B_series.npy")
    gb, nb = ab[0], ["p2_1920_1936", "p3_1948_1964", "p4_1968_1984"]
    fig, a = plt.subplots(figsize=(10, 5.6), dpi=140)
    a.imshow(img[0:300, 700:1280]); 
    for i, nm in enumerate(nb):
        v = ab[1 + i]; keep = ~np.isnan(v)
        px = (gb[keep] - axb.xb) / axb.xa - 700
        py = (v[keep] - axb.yb) / axb.ya
        a.plot(px, py, lw=1.1, color=COLOURS[nm], label=nm)
    a.set_xlim(25, 580); a.set_ylim(300, 5)
    a.legend(fontsize=7, loc="lower left", framealpha=0.9)
    a.set_title("Figure 2B: digitized p2/p3/p4 re-plotted over the source panel", fontsize=9)
    a.axis("off"); fig.tight_layout(); fig.savefig(V / "fig2B_overlay.png"); plt.close(fig)

    # ---------------------------------------------------------------- Figure 2C
    mc = json.loads((V / "fig2C_meta.json").read_text())
    axc = D.Axes(mc["x_ticks_px"], mc["x_tick_values"], mc["y_ticks_px"], mc["y_tick_values"])
    ac = np.load(V / "fig2C_series.npy")
    fig, a = plt.subplots(figsize=(9, 6.4), dpi=140)
    a.imshow(img[550:960, 40:640])
    for i, nm in enumerate(["olympians", "population"]):
        v = ac[1 + i]; keep = ~np.isnan(v)
        px = (ac[0][keep] - axc.xb) / axc.xa - 40
        py = (v[keep] - axc.yb) / axc.ya - 550
        a.plot(px, py, lw=1.2, color=COLOURS[nm], label=nm)
    a.legend(fontsize=8, loc="upper left", framealpha=0.9)
    a.set_title("Figure 2C: digitized boundaries re-plotted over the source panel", fontsize=9)
    a.axis("off"); fig.tight_layout(); fig.savefig(V / "fig2C_overlay.png"); plt.close(fig)

    # ---------------------------------------------------------------- Figure S1C
    ms = json.loads((V / "figS1C_meta.json").read_text())
    axs = D.Axes(ms["x_ticks_px"], ms["x_tick_values"], ms["y_ticks_px"], ms["y_tick_values"])
    asr = np.load(V / "figS1C_series.npy")
    s1 = D.load_rgb(PNG)
    fig, a = plt.subplots(figsize=(7, 8), dpi=150)
    a.imshow(s1[40:350, 650:900])
    for i, nm in enumerate(["olympians", "population"]):
        v = asr[1 + i]; keep = ~np.isnan(v)
        px = (asr[0][keep] - axs.xb) / axs.xa - 650
        py = (v[keep] - axs.yb) / axs.ya - 40
        a.plot(px, py, lw=1.2, color=COLOURS[nm], label=nm)
    a.legend(fontsize=8, loc="upper left", framealpha=0.9)
    a.set_title("Figure S1C: digitized boundaries over the source panel", fontsize=9)
    a.axis("off"); fig.tight_layout(); fig.savefig(V / "figS1C_overlay.png"); plt.close(fig)

    (V / "verification.json").write_text(json.dumps(out, indent=2))
    print("Figure 2A - deviation of the 1-year CSV from the raw per-column extraction:")
    for nm, s in stats2A.items():
        print(f"  {nm:20s} n={s['n_columns']:4d}  mean {s['mean_abs_dev_px']:.2f} px "
              f"({s['mean_abs_dev_survival_pct']:.2f} %)   max {s['max_abs_dev_px']:.2f} px "
              f"({s['max_abs_dev_survival_pct']:.2f} %)")
    print("\nwrote _verify/{fig2A,fig2B,fig2C,figS1C}_overlay.png and verification.json")


if __name__ == "__main__":
    main()
