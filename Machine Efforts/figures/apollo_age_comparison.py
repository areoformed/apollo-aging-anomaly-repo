#!/usr/bin/env python3
"""
Apollo aging anomaly — COMPARISON cohort histogram ("Apollo removed").

The control group for the aging analysis: astronaut-selected/-trained people who did
NOT fly Apollo deep-space missions — X-20 Dyna-Soar, MOL, X-15 / high-speed pilots,
and the core NASA non-Apollo selectees. 69 people: deceased (age at death) stacked
with the living (current age, CURRENT_YEAR).

STYLE: laid out to match the author's refined 29-cohort chart ("Apollo Astronauts Age
Distribution") so the two read as a pair — centered serif title, two-line mono
subtitle (incl. her "computed by hand / graphed via Claude script + Sketch" line),
"# count" y-axis label, a CONTINUOUS age x-axis (30-120) with numeric labels at every
5-year tick (longer at the decades), "age" label beneath, DECEASED/LIVING legend
top-right, and the bin total printed above each bar. Fonts + exact colours are rough
stand-ins — the author finishes those in Sketch.

Source = cohort_comparison_bins.csv (bin_start,total,mort,alive). The tool re-checks
mort + alive == total per bin (and the grand totals) before it will draw.

Run:  python3 apollo_age_comparison.py   ->  writes age_comparison_with_living.svg
"""

import csv
import sys
from pathlib import Path

AGE_BIN = 5
CURRENT_YEAR = 2026
Y_AXIS_MAX = 18              # headroom above this cohort's data max (=16, the 85-89 bin)
DECEASED_FILL = "#4f5d73"   # slate-navy stand-in (match the author's in Sketch)
LIVING_FILL   = "#cfc6bf"   # warm-taupe stand-in (match the author's in Sketch)

SERIF = "Georgia, 'Times New Roman', serif"        # title / axis labels (stand-in)
MONO  = "'SF Mono', Menlo, Consolas, monospace"    # subtitle / numbers / legend (stand-in)

HERE = Path(__file__).resolve().parent
CSV  = HERE / "cohort_comparison_bins.csv"
OUT  = HERE / "age_comparison_with_living.svg"


def load_bins(path):
    """Read the binned figures and re-check the arithmetic before trusting them."""
    rows = list(csv.DictReader(path.open()))
    bins = []
    for r in rows:
        st    = int(r["bin_start"])
        total = int(r["total"]); mort = int(r["mort"]); alive = int(r["alive"])
        if mort + alive != total:                       # the two parts must rebuild the whole
            sys.exit(f"BIN {st}: mort+alive ({mort}+{alive}) != total ({total}).")
        bins.append({"start": st, "alive": alive, "mort": mort, "total": total})
    return bins


def bin_label(start, width=AGE_BIN):
    return f"{start}-{start + width - 1}"


def render(bins, out_path, n_dead, n_alive):
    n = len(bins)
    y_max = max(Y_AXIS_MAX, max((b["total"] for b in bins), default=1))

    ml, mr, mt, mb = 80, 40, 110, 90
    w, h = 1180, 745
    pw, ph = w - ml - mr, h - mt - mb
    bottom = mt + ph
    cx = ml + pw / 2

    age_lo = bins[0]["start"]
    age_hi = bins[-1]["start"] + AGE_BIN      # continuous axis 30 .. 120
    span = age_hi - age_lo

    def x_age(a): return ml + (a - age_lo) / span * pw
    def y_at(v):  return bottom - (v / y_max) * ph
    def seg_h(c): return (c / y_max) * ph

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">')
    s.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>')

    # title + two-line subtitle (centered), mirroring the 29-cohort chart
    s.append(f'<text x="{cx:.1f}" y="46" text-anchor="middle" font-family="{SERIF}" '
             f'font-size="30" fill="#222">Non-Apollo Astronauts Age Distribution</text>')
    s.append(f'<text x="{cx:.1f}" y="70" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#9a9a9a">'
             f'69-astronaut comparison cohort (Apollo removed) &#183; Dyna-Soar &#183; MOL &#183; X-15 &#183; core NASA non-Apollo</text>')
    s.append(f'<text x="{cx:.1f}" y="84" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#9a9a9a">'
             f'data collected + computed by hand &#8212; graphed via Claude-generated script + Sketch App (current age, {CURRENT_YEAR})</text>')

    # y gridlines + integer labels
    s.append(f'<g font-family="{MONO}" font-size="11" fill="#9a9a9a" text-anchor="end">')
    for t in range(0, y_max + 1):
        yy = y_at(t)
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw:.1f}" y2="{yy:.1f}" stroke="#ededed" stroke-width="1"/>')
        s.append(f'<text x="{ml - 12}" y="{yy + 4:.1f}">{t}</text>')
    s.append('</g>')

    # y-axis title
    ymid = mt + ph / 2
    s.append(f'<text x="26" y="{ymid:.1f}" text-anchor="middle" font-family="{SERIF}" font-size="14" '
             f'fill="#9a9a9a" transform="rotate(-90 26 {ymid:.1f})"># count</text>')

    # stacked bars on the continuous axis: deceased (bottom) + living (top)
    for b in bins:
        if b["total"] == 0:
            continue
        x0, x1 = x_age(b["start"]), x_age(b["start"] + AGE_BIN)
        bw = (x1 - x0) * 0.82
        bx = x0 + (x1 - x0 - bw) / 2
        if b["mort"]:
            s.append(f'<rect x="{bx:.1f}" y="{y_at(b["mort"]):.1f}" width="{bw:.1f}" '
                     f'height="{seg_h(b["mort"]):.1f}" fill="{DECEASED_FILL}"/>')
        if b["alive"]:
            top = b["mort"] + b["alive"]
            s.append(f'<rect x="{bx:.1f}" y="{y_at(top):.1f}" width="{bw:.1f}" '
                     f'height="{seg_h(b["alive"]):.1f}" fill="{LIVING_FILL}"/>')
        s.append(f'<text x="{bx + bw / 2:.1f}" y="{y_at(b["total"]) - 7:.1f}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="11" fill="#555">{b["total"]}</text>')

    # x-axis baseline
    s.append(f'<line x1="{ml}" y1="{bottom}" x2="{ml + pw:.1f}" y2="{bottom}" stroke="#333" stroke-width="1.2"/>')

    # x ticks + numeric labels every 5 years (longer + thicker at the decades)
    s.append(f'<g font-family="{MONO}" font-size="11" fill="#9a9a9a" text-anchor="middle">')
    a = age_lo
    while a <= age_hi:
        xx = x_age(a)
        major = (a % 10 == 0)
        tlen = 9 if major else 5
        s.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + tlen}" '
                 f'stroke="#333" stroke-width="{1.2 if major else 0.8}"/>')
        s.append(f'<text x="{xx:.1f}" y="{bottom + 24:.1f}">{a}</text>')
        a += AGE_BIN
    s.append('</g>')

    # x-axis title
    s.append(f'<text x="{cx:.1f}" y="{h - 26:.1f}" text-anchor="middle" font-family="{SERIF}" '
             f'font-size="14" fill="#9a9a9a">age</text>')

    # legend, top-right
    lx, ly = ml + pw - 150, mt + 6
    s.append(f'<g font-family="{MONO}" font-size="12" fill="#555">')
    s.append(f'<rect x="{lx}" y="{ly}" width="14" height="14" fill="{DECEASED_FILL}"/>')
    s.append(f'<text x="{lx + 20}" y="{ly + 12}">DECEASED</text>')
    s.append(f'<rect x="{lx}" y="{ly + 22}" width="14" height="14" fill="{LIVING_FILL}"/>')
    s.append(f'<text x="{lx + 20}" y="{ly + 34}">LIVING</text>')
    s.append('</g>')

    s.append('</svg>')
    out_path.write_text("\n".join(s), encoding="utf-8")
    return w, h, y_max


def main():
    bins = load_bins(CSV)
    n_dead  = sum(b["mort"] for b in bins)
    n_alive = sum(b["alive"] for b in bins)
    n_total = sum(b["total"] for b in bins)

    print(f"Comparison cohort: {n_total} -> {n_dead} deceased, {n_alive} living.")
    print(f"\n{'bin':>8} {'mort':>5} {'alive':>6} {'tot':>4}")
    for b in bins:
        if b["total"]:
            print(f"{bin_label(b['start']):>8} {b['mort']:>5} {b['alive']:>6} {b['total']:>4}")

    w, h, ymax = render(bins, OUT, n_dead, n_alive)
    print(f"\nWrote {OUT.name}  ({w}x{h}, y_max={ymax}) — open in Sketch.")


if __name__ == "__main__":
    main()
