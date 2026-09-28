#!/usr/bin/env python3
"""
Apollo aging anomaly — BIRTH-YEAR distribution histograms (the "long span" view).

Two charts, drawn on a SHARED birth-year axis (1910-1945) so they read as a pair and
you can see both cohorts were born into the same window:

  apollo_birth_years.svg     - the 29 Apollo-era astronauts by birth year, stacked
                               LLO (flew to lunar orbit / deep space) over LEO (stayed
                               in low Earth orbit only).  24 LLO + 5 LEO = 29.
  nonapollo_birth_years.svg  - the 69-person comparison cohort (Apollo removed) by
                               birth year, single series.

Both use 3-year birth-year bins on a continuous 1910-1945 axis (ticks every 5 years,
decades drawn longer/thicker). Style mirrors the age-distribution charts: centered
serif title, two-line mono subtitle (incl. the "computed by hand / Claude script +
Sketch" line), "# count" y-axis, bin total printed above each bar, legend top-right.
Fonts + exact colours are rough stand-ins -- the author finishes those in Sketch.

Data (edit these, not the code):
  apollo_birth_years.csv     bin_start,llo,leo
  nonapollo_birth_years.csv  bin_start,count
The tool re-checks the grand totals (24 LLO + 5 LEO = 29 ; 69) before it will draw.

NOTE (flag for the author): the two charts use SEPARATE y-maxes (Apollo 14, non-Apollo 18)
because the cohorts differ in size (29 vs 69). Set Y_MAX_APOLLO = Y_MAX_NONAPOLLO if
you'd rather share one vertical scale for a strict bar-height comparison.

Run:  python3 apollo_birth_years.py
"""

import csv
import sys
from pathlib import Path

BIN = 3                          # 3-year birth-year bins
AXIS_LO, AXIS_HI = 1910, 1945    # shared "long span" x-axis for both charts
Y_MAX_APOLLO    = 14             # headroom over Apollo's tallest bin (12, the 1929-31 bin)
Y_MAX_NONAPOLLO = 18             # headroom over non-Apollo's tallest bin (16, the 1929-31 bin)

# stand-in colours (the author finishes in Sketch) -- kept in the age-charts' palette
LLO_FILL  = "#4f5d73"    # slate-navy: lunar-orbit / deep-space astronauts
LEO_FILL  = "#cfc6bf"    # warm-taupe: low-Earth-orbit only
SOLO_FILL = "#4f5d73"    # single-series comparison cohort

SERIF = "Georgia, 'Times New Roman', serif"        # title / axis labels (stand-in)
MONO  = "'SF Mono', Menlo, Consolas, monospace"    # subtitle / numbers / legend (stand-in)

HERE = Path(__file__).resolve().parent


def load(path, value_cols):
    """Read bin_start + the named integer value columns; preserve row order."""
    bins = []
    for r in csv.DictReader(path.open()):
        vals = [int(r[c]) for c in value_cols]
        bins.append({"start": int(r["bin_start"]), "vals": vals, "total": sum(vals)})
    return bins


def render(bins, segments, out_path, title, sub1, sub2, y_max, legend, n_label):
    """
    bins     : [{start, vals:[...], total}]   vals aligned to `segments` order
    segments : [(index_into_vals, fill)]      bottom-to-top stack order
    legend   : [(label, fill)]                may be empty (single series)
    """
    ml, mr, mt, mb = 80, 40, 110, 90
    w, h = 1180, 745
    pw, ph = w - ml - mr, h - mt - mb
    bottom = mt + ph
    cx = ml + pw / 2
    span = AXIS_HI - AXIS_LO

    def x_yr(y): return ml + (y - AXIS_LO) / span * pw
    def y_at(v): return bottom - (v / y_max) * ph
    def seg_h(c): return (c / y_max) * ph

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>']

    # title + two-line subtitle (centered), mirroring the age charts
    s.append(f'<text x="{cx:.1f}" y="46" text-anchor="middle" font-family="{SERIF}" font-size="30" fill="#222">{title}</text>')
    s.append(f'<text x="{cx:.1f}" y="70" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#9a9a9a">{sub1}</text>')
    s.append(f'<text x="{cx:.1f}" y="84" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#9a9a9a">{sub2}</text>')

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

    # stacked bars on the continuous birth-year axis
    for b in bins:
        if b["total"] == 0 or b["start"] >= AXIS_HI:
            continue
        x0, x1 = x_yr(b["start"]), x_yr(b["start"] + BIN)
        bw = (x1 - x0) * 0.82
        bx = x0 + (x1 - x0 - bw) / 2
        cum = 0
        for idx, fill in segments:
            v = b["vals"][idx]
            if v:
                s.append(f'<rect x="{bx:.1f}" y="{y_at(cum + v):.1f}" width="{bw:.1f}" '
                         f'height="{seg_h(v):.1f}" fill="{fill}"/>')
                cum += v
        s.append(f'<text x="{bx + bw/2:.1f}" y="{y_at(b["total"]) - 7:.1f}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="11" fill="#555">{b["total"]}</text>')

    # x-axis baseline
    s.append(f'<line x1="{ml}" y1="{bottom}" x2="{ml + pw:.1f}" y2="{bottom}" stroke="#333" stroke-width="1.2"/>')

    # x ticks + labels every 5 years (longer/thicker at the decades)
    s.append(f'<g font-family="{MONO}" font-size="11" fill="#9a9a9a" text-anchor="middle">')
    yr = AXIS_LO
    while yr <= AXIS_HI:
        xx = x_yr(yr)
        major = (yr % 10 == 0)
        tlen = 9 if major else 5
        s.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + tlen}" '
                 f'stroke="#333" stroke-width="{1.2 if major else 0.8}"/>')
        s.append(f'<text x="{xx:.1f}" y="{bottom + 24:.1f}">{yr}</text>')
        yr += 5
    s.append('</g>')

    # x-axis title
    s.append(f'<text x="{cx:.1f}" y="{h - 26:.1f}" text-anchor="middle" font-family="{SERIF}" '
             f'font-size="14" fill="#9a9a9a">birth year</text>')

    # legend + n-label, top-right
    lx, ly = ml + pw - 150, mt + 6
    s.append(f'<g font-family="{MONO}" font-size="12" fill="#555">')
    yoff = 0
    for label, fill in legend:
        s.append(f'<rect x="{lx}" y="{ly + yoff}" width="14" height="14" fill="{fill}"/>')
        s.append(f'<text x="{lx + 20}" y="{ly + yoff + 12}">{label}</text>')
        yoff += 22
    if n_label:
        s.append(f'<text x="{lx}" y="{ly + yoff + 12}">{n_label}</text>')
    s.append('</g>')

    s.append('</svg>')
    out_path.write_text("\n".join(s), encoding="utf-8")


def main():
    sub2 = "data collected + computed by hand &#8212; graphed via Claude-generated script + Sketch App"

    # --- Apollo: stacked LLO (deep space) + LEO (earth orbit) ---
    ap = load(HERE / "apollo_birth_years.csv", ["llo", "leo"])
    n_llo = sum(b["vals"][0] for b in ap)
    n_leo = sum(b["vals"][1] for b in ap)
    if (n_llo, n_leo) != (24, 5):
        sys.exit(f"Apollo totals off: LLO={n_llo} (want 24), LEO={n_leo} (want 5).")
    render(
        ap, [(0, LLO_FILL), (1, LEO_FILL)],
        HERE / "apollo_birth_years.svg",
        "Apollo Astronauts by Birth Year",
        "29 Apollo-era astronauts &#183; LLO = flew to lunar orbit (deep space) &#183; LEO = low Earth orbit only",
        sub2, Y_MAX_APOLLO,
        [("LLO  (lunar orbit)", LLO_FILL), ("LEO  (earth orbit)", LEO_FILL)], "n = 29",
    )

    # --- non-Apollo: single series ---
    na = load(HERE / "nonapollo_birth_years.csv", ["count"])
    n_na = sum(b["total"] for b in na)
    if n_na != 69:
        sys.exit(f"Non-Apollo total off: {n_na} (want 69).")
    render(
        na, [(0, SOLO_FILL)],
        HERE / "nonapollo_birth_years.svg",
        "Non-Apollo Astronauts by Birth Year",
        "69-astronaut comparison cohort (Apollo removed) &#183; Dyna-Soar &#183; MOL &#183; X-15 &#183; core NASA non-Apollo",
        sub2, Y_MAX_NONAPOLLO,
        [], "n = 69",
    )

    print(f"Apollo:     LLO={n_llo} + LEO={n_leo} = {n_llo + n_leo}  -> apollo_birth_years.svg")
    print(f"Non-Apollo: n={n_na}  -> nonapollo_birth_years.svg")
    print(f"Shared x-axis: {AXIS_LO}-{AXIS_HI}, {BIN}-year bins. y-max: Apollo {Y_MAX_APOLLO}, non-Apollo {Y_MAX_NONAPOLLO}.")


if __name__ == "__main__":
    main()
