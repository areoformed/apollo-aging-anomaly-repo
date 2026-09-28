#!/usr/bin/env python3
"""
Shared digitizing machinery for Antero et al. 2021 (Br J Sports Med 55:206-212), Figure 2,
and Supplementary Figure S1.

Nothing here is eyeballed. Calibration comes from tick-mark pixels measured by
`measure_calibration()`; curve positions come from per-column colour masks.

[AUTHOR]'s ask, 2026-09-07: "generate the values from scratch ... do all 4 if we're getting the data."
"""
from __future__ import annotations

import numpy as np
from PIL import Image

# ----------------------------------------------------------------------------- geometry helpers


def load_rgb(path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB")).astype(int)


def _runs(idx, gap=3):
    """Group a sorted index array into (start, end) runs, splitting where the gap exceeds `gap`."""
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for v in idx[1:]:
        if v - p > gap:
            out.append((s, p))
            s = v
        p = v
    out.append((s, p))
    return out


def measure_calibration(img, box, tick_side_px=7, dark=170, min_hits=3):
    """Locate axis tick marks just outside a plot box and return their pixel centres.

    box = (x_left, x_right, y_top, y_bottom) of the plot rectangle's border lines.
    Ticks in R are drawn outside the box, so we scan a thin band beyond each border.
    """
    xl, xr, yt, yb = box
    d = img.max(2) < dark
    band = d[yb + 2 : yb + 2 + tick_side_px, :].sum(0)
    xs = np.where(band >= min_hits)[0]
    xs = xs[(xs >= xl - 10) & (xs <= xr + 10)]
    xticks = [(a + b) / 2 for a, b in _runs(xs, 3)]
    band = d[:, xl - 1 - tick_side_px : xl - 1].sum(1)
    ys = np.where(band >= min_hits)[0]
    ys = ys[(ys >= yt - 10) & (ys <= yb + 10)]
    yticks = [(a + b) / 2 for a, b in _runs(ys, 3)]
    return xticks, yticks


class Axes:
    """Affine pixel <-> data mapping, fitted by least squares to the measured tick pixels."""

    def __init__(self, xpix, xval, ypix, yval):
        self.xa, self.xb = np.polyfit(np.asarray(xpix, float), np.asarray(xval, float), 1)
        self.ya, self.yb = np.polyfit(np.asarray(ypix, float), np.asarray(yval, float), 1)
        self.x_resid = float(np.max(np.abs(np.polyval([self.xa, self.xb], xpix) - np.asarray(xval))))
        self.y_resid = float(np.max(np.abs(np.polyval([self.ya, self.yb], ypix) - np.asarray(yval))))

    def x(self, px):
        return self.xa * np.asarray(px, float) + self.xb

    def y(self, py):
        return self.ya * np.asarray(py, float) + self.yb

    def px_per_x(self):
        return 1.0 / self.xa

    def px_per_y(self):
        return 1.0 / self.ya


# ----------------------------------------------------------------------------- colour masks


def mask_blue(img, dark_max=155, sep=18):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (b - np.maximum(r, g) >= sep) & (img.max(2) <= dark_max)


def mask_green_solid(img, dark_max=210, sep=14, rb_tol=28):
    """Dark saturated green (the female-Olympian line): g dominant, r and b close together."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (g - np.maximum(r, b) >= sep) & (np.abs(r - b) <= rb_tol) & (img.max(2) <= dark_max)


def mask_chartreuse(img, gb=45, rb=28):
    """Yellow-green (the female-population dotted line): both r and g well above b."""
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (g - b >= gb) & (r - b >= rb)


def mask_rgb_near(img, target, tol=70, sep=25):
    """Pixels close to a saturated target colour, requiring the target's dominant channel to lead."""
    t = np.asarray(target, float)
    d = np.sqrt(((img - t) ** 2).sum(2))
    dom = int(np.argmax(t))
    others = [i for i in range(3) if i != dom]
    lead = img[..., dom] - np.maximum(img[..., others[0]], img[..., others[1]])
    return (d <= tol) & (lead >= sep)


def mask_dark_neutral(img, dark_max=110, sat_max=40):
    return (img.max(2) <= dark_max) & ((img.max(2) - img.min(2)) <= sat_max)


# ----------------------------------------------------------------------------- extraction


def column_runs(mask, x, y0, y1, gap=3, min_len=1):
    ys = np.where(mask[y0 : y1 + 1, x])[0]
    return [(a + y0, b + y0) for a, b in _runs(ys, gap) if (b - a + 1) >= min_len]


def extract_single(mask, xs, y0, y1, pick="largest", gap=3, min_len=1, exclude=None):
    """One curve per column.

    pick: 'largest' (the thickest run - the line core), 'top'/'bottom' run,
          'topmost_pixel', or 'median' of every masked row in the column.
    """
    out = {}
    for x in xs:
        rs = column_runs(mask, x, y0, y1, gap, min_len)
        if exclude is not None:
            rs = [r for r in rs if not exclude(x, r)]
        if not rs:
            continue
        if pick == "top":
            a, b = rs[0]
            out[x] = (a + b) / 2
        elif pick == "bottom":
            a, b = rs[-1]
            out[x] = (a + b) / 2
        elif pick == "topmost_pixel":
            out[x] = rs[0][0]
        elif pick == "largest":
            a, b = max(rs, key=lambda r: r[1] - r[0])
            out[x] = (a + b) / 2
        else:
            ys = np.concatenate([np.arange(a, b + 1) for a, b in rs])
            out[x] = float(np.median(ys))
    return out


def unique_run_only(mask, xs, y0, y1, gap=3, exclude=None):
    """Keep only columns where exactly one run survives - i.e. no ambiguity at all."""
    out = {}
    for x in xs:
        rs = column_runs(mask, x, y0, y1, gap)
        if exclude is not None:
            rs = [r for r in rs if not exclude(x, r)]
        if len(rs) == 1:
            a, b = rs[0]
            out[x] = (a + b) / 2
    return out


def anchor_at_zero(grid, values, x0=0.0, y0=100.0):
    """KM and life-table survival are 1.0 at entry by definition.

    Where the digitizer found nothing before its first resolved point (all four curves
    are bunched within a couple of percent of 100% there), join that first point to the
    definitional (x0, y0) with a straight line. Recorded as an assumption, not a measurement.
    """
    v = np.asarray(values, float).copy()
    ok = np.where(~np.isnan(v))[0]
    if len(ok) == 0:
        return v, None
    first = ok[0]
    if grid[first] <= x0:
        return v, None
    lo = np.where(grid >= x0)[0][0]
    seg = slice(lo, first + 1)
    v[seg] = np.interp(grid[seg], [x0, grid[first]], [y0, v[first]])
    return v, (float(x0), float(grid[first]))


def split_two_tracks(mask, xs, y0, y1, gap=3, min_len=1, exclude=None, max_jump=14):
    """Separate two same-hue curves that never cross (upper is always the higher-survival one).

    Pass 1: columns showing two or more runs give an unambiguous upper/lower pair.
    Pass 2: single-run columns are assigned by continuity to whichever track is nearer,
            interpolating the pass-1 tracks to that column first.
    Returns (upper, lower, ambiguous_columns).
    """
    runs_by_x = {}
    for x in xs:
        rs = column_runs(mask, x, y0, y1, gap, min_len)
        if exclude is not None:
            rs = [r for r in rs if not exclude(x, r)]
        if rs:
            runs_by_x[x] = rs

    upper, lower = {}, {}
    for x, rs in runs_by_x.items():
        if len(rs) >= 2:
            upper[x] = (rs[0][0] + rs[0][1]) / 2
            lower[x] = (rs[-1][0] + rs[-1][1]) / 2

    def interp(track, x):
        if not track:
            return None
        ks = np.array(sorted(track))
        vs = np.array([track[k] for k in ks], float)
        if x < ks[0] or x > ks[-1]:
            return None
        return float(np.interp(x, ks, vs))

    ambiguous = []
    for x, rs in sorted(runs_by_x.items()):
        if len(rs) >= 2:
            continue
        c = (rs[0][0] + rs[0][1]) / 2
        u, l = interp(upper, x), interp(lower, x)
        if u is None and l is None:
            ambiguous.append(x)
            continue
        du = abs(c - u) if u is not None else 1e9
        dl = abs(c - l) if l is not None else 1e9
        if min(du, dl) > max_jump:
            ambiguous.append(x)
            continue
        (upper if du <= dl else lower)[x] = c
    return upper, lower, ambiguous


def to_data(track, axes):
    """pixel dict {x_px: y_px} -> sorted arrays of (x_data, y_data)."""
    ks = np.array(sorted(track), float)
    vs = np.array([track[k] for k in sorted(track)], float)
    return axes.x(ks), axes.y(vs)


def resample(xd, yd, grid, monotone_dec=False):
    """Linear interpolation onto `grid`; NaN outside the observed span (never extrapolate)."""
    order = np.argsort(xd)
    xd, yd = xd[order], yd[order]
    # collapse duplicate x (a step riser gives several rows at one column)
    ux, uy = [], []
    i = 0
    while i < len(xd):
        j = i
        while j + 1 < len(xd) and xd[j + 1] == xd[i]:
            j += 1
        ux.append(xd[i])
        uy.append(np.median(yd[i : j + 1]))
        i = j + 1
    ux, uy = np.array(ux), np.array(uy)
    out = np.interp(grid, ux, uy, left=np.nan, right=np.nan)
    out[(grid < ux[0]) | (grid > ux[-1])] = np.nan
    if monotone_dec:
        v = out.copy()
        run = np.inf
        for i in range(len(v)):
            if np.isnan(v[i]):
                continue
            run = min(run, v[i])
            v[i] = run
        out = v
    return out
