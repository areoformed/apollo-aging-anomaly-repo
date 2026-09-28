#!/usr/bin/env python3
"""
Stacked interval histogram from a pre-binned CSV -> clean layered SVG for Sketch.

Reads AgeStart,Bin,Alive,Mort and draws each bar positioned by AgeStart on a
TRUE numeric axis, spanning one bin width. A bar literally begins at its bin's
left edge -- so 90 is the START of [90, 95), not a parked category. Mort stacks
on the bottom, Alive on top.

Why this exists: RAWGraphs bar charts are CATEGORICAL -- each bin label is a
discrete, alphabetically-sorted slot, which is why the 100s jumped and why it
never understood that 90 begins an interval. This renders the axis as real
numbers, so the bins sit where their ages actually are.

Output groups are named (series-Mort, series-Alive, x-axis, y-axis, ...) and
every bar has an id (Mort-90, Alive-90) -> tidy, re-styleable Sketch layers.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV  = HERE / "alive_vs_mort_bins.csv"
OUT  = HERE / "alive_vs_mort_histogram.svg"

BIN_WIDTH    = 5
X_MIN, X_MAX = 30, 110                     # selection age -> ceiling
STACK_ORDER  = ["Mort", "Alive"]          # bottom -> top
COLORS       = {"Mort": "#E07B39", "Alive": "#3B6FA0"}  # restyle freely in Sketch


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for d in csv.DictReader(f):
            rows.append({
                "age":   int(d["AgeStart"]),
                "bin":   d["Bin"],
                "Alive": int(d["Alive"]),
                "Mort":  int(d["Mort"]),
            })
    return rows


def render(rows, out):
    W, H = 900, 560
    l, r, t, b = 70, 30, 44, 70
    pw, ph = W - l - r, H - t - b
    bottom = t + ph
    ymax = max(max(row["Alive"] + row["Mort"] for row in rows), 10)
    sx = pw / (X_MAX - X_MIN)
    sy = ph / ymax

    def X(age): return l + (age - X_MIN) * sx
    def Yh(v):  return v * sy

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">']
    s.append(f'<g id="background"><rect width="{W}" height="{H}" fill="#ffffff"/></g>')
    s.append(f'<g id="title"><text x="{l}" y="26" font-size="18" font-weight="bold" '
             f'fill="#111">Apollo astronauts — age reached (died vs. still living)</text></g>')

    # y gridlines + ticks
    s.append('<g id="y-axis" font-size="11" fill="#999" text-anchor="end">')
    step = 1 if ymax <= 12 else 2
    for tv in range(0, ymax + 1, step):
        yy = bottom - Yh(tv)
        s.append(f'<line x1="{l}" y1="{yy:.1f}" x2="{l + pw}" y2="{yy:.1f}" stroke="#ececec"/>')
        s.append(f'<text x="{l - 8}" y="{yy + 4:.1f}">{tv}</text>')
    s.append('</g>')

    # stacked bars (Mort bottom, Alive top); 1px gap so bins stay legible
    for series in STACK_ORDER:
        below_of = STACK_ORDER[:STACK_ORDER.index(series)]
        s.append(f'<g id="series-{series}" fill="{COLORS[series]}">')
        for row in rows:
            v = row[series]
            if v == 0:
                continue
            below = sum(row[o] for o in below_of)
            x = X(row["age"]) + 0.5
            w = BIN_WIDTH * sx - 1.0
            y = bottom - Yh(below + v)
            h = Yh(v)
            s.append(f'<rect id="{series}-{row["age"]}" x="{x:.1f}" y="{y:.1f}" '
                     f'width="{w:.1f}" height="{h:.1f}"/>')
        s.append('</g>')

    # totals above each non-empty bar
    s.append('<g id="value-labels" font-size="11" fill="#222" text-anchor="middle">')
    for row in rows:
        tot = row["Alive"] + row["Mort"]
        if tot == 0:
            continue
        cx = X(row["age"]) + BIN_WIDTH * sx / 2
        s.append(f'<text x="{cx:.1f}" y="{bottom - Yh(tot) - 5:.1f}">{tot}</text>')
    s.append('</g>')

    # x baseline + numeric ticks every 10 yrs
    s.append('<g id="x-axis" font-size="11" fill="#444" text-anchor="middle">')
    s.append(f'<line x1="{l}" y1="{bottom}" x2="{l + pw}" y2="{bottom}" stroke="#333" stroke-width="1.5"/>')
    for age in range(X_MIN, X_MAX + 1, 10):
        xx = X(age)
        s.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + 5}" stroke="#333"/>')
        s.append(f'<text x="{xx:.1f}" y="{bottom + 18:.1f}">{age}</text>')
    s.append('</g>')

    s.append(f'<g id="axis-titles" font-size="12" fill="#555">'
             f'<text x="{l + pw / 2:.1f}" y="{H - 12}" text-anchor="middle">'
             f'Age (years) — 30 = age at selection</text></g>')

    # legend
    lx, ly = l + pw - 150, t + 4
    s.append('<g id="legend" font-size="12" fill="#333">')
    s.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{COLORS["Mort"]}"/>'
             f'<text x="{lx + 18}" y="{ly + 11}">Died at this age</text>')
    s.append(f'<rect x="{lx}" y="{ly + 20}" width="12" height="12" fill="{COLORS["Alive"]}"/>'
             f'<text x="{lx + 18}" y="{ly + 31}">Still living</text>')
    s.append('</g>')

    s.append('</svg>')
    out.write_text("\n".join(s), encoding="utf-8")
    return ymax


def main():
    rows = load(CSV)
    total = sum(r["Alive"] + r["Mort"] for r in rows)
    ymax = render(rows, OUT)
    print(f"Read {len(rows)} bins, {total} astronauts (Alive+Mort), y-axis 0..{ymax}.")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
