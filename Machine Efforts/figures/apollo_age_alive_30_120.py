#!/usr/bin/env python3
"""
Apollo cohort — age histogram, axis 30 to 120, the DECEASED (charcoal, binned by
age at death) stacked with the LIVING (grey, binned by current age).

This is age_at_death_clean.svg with two changes and nothing else: a wider age
axis (more bins) and the living added as a second measure in grey. Same canvas,
margins, fonts, charcoal, gridlines, value-on-top labels, baseline.

Source of truth stays your apolloData.h (READ-ONLY). Independent regex parse +
dissimilar-redundancy self-checks, exactly like the sibling tool: every bin is
counted two ways and asserted equal, and the row count is gated against your
#define apolloAstrosCount. It prints the dead/alive/total table so you can diff
it against your C.

Run:  python3 apollo_age_alive_30_120.py
Re-bin / re-range: change AGE_BIN / AGE_LO / AGE_HI below and re-run.
"""

import re
import sys
from pathlib import Path
from collections import Counter

# ---- knobs (change + re-run) ----------------------------------------------
AGE_BIN = 5
AGE_LO  = 30      # left edge of the axis
AGE_HI  = 115     # left edge of the LAST bin -> axis runs to 120 (115–119)
CURRENT_YEAR = 2026   # living: current age = CURRENT_YEAR - birth
                      # (year-difference, the SAME convention as age-at-death = death - birth)

DECEASED_FILL = "#3a3a3a"   # the original charcoal
LIVING_FILL   = "#bdbdbd"   # the living, in grey

HERE   = Path(__file__).resolve().parent
DATA_H = HERE.parent.parent / "Human Efforts" / "scripts" / "apolloData.h"
OUT    = HERE / "age_at_death_with_living.svg"


def load_astros(path):
    """Independent regex parse of your .h. death==0 means still living.
    Gates the parsed row count against #define apolloAstrosCount."""
    if not path.exists():
        sys.exit(f"Can't find the data file at:\n  {path}")
    text = path.read_text()
    row = re.compile(
        r'\{\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
        r'\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*\}'
    )
    astros = [{"name": m.group(1), "birth": int(m.group(2)), "death": int(m.group(3))}
              for m in row.finditer(text)]
    declared = re.search(r'#define\s+apolloAstrosCount\s+(\d+)', text)
    if declared and int(declared.group(1)) != len(astros):
        sys.exit(f"PARSE MISMATCH: #define = {declared.group(1)} but parsed {len(astros)}.")
    if not astros:
        sys.exit("Parsed 0 rows -- the struct format may have changed.")
    return astros


def tally(years, width, lo, hi):
    """Bin into the FIXED [lo, hi] grid (empties kept). Counted two independent
    ways and asserted equal before anything is drawn."""
    starts = list(range(lo, hi + 1, width))
    a = {s: 0 for s in starts}
    for y in years:
        k = (y // width) * width
        if k not in a:
            sys.exit(f"Value {y} falls outside the {lo}–{hi + width} grid; widen AGE_LO/AGE_HI.")
        a[k] += 1
    b = Counter((y // width) * width for y in years)
    for s in starts:
        if a[s] != b.get(s, 0):
            sys.exit(f"INTERNAL COUNT MISMATCH at bin {s}: {a[s]} != {b.get(s, 0)}")
    if sum(a.values()) != len(years):
        sys.exit("INTERNAL: a record went missing during binning")
    return [(s, a[s]) for s in starts]


def bin_label(start, width):
    return f"{start}–{str(start + width - 1)[-2:]}"   # e.g. 85–89


def render(dec_bins, liv_bins, out_path):
    width  = AGE_BIN
    starts = [s for s, _ in dec_bins]
    n      = len(starts)
    totals = [dec_bins[i][1] + liv_bins[i][1] for i in range(n)]
    y_max  = max(totals + [1])

    # geometry: identical to age_at_death_clean.svg (same canvas + margins);
    # the bars just get thinner because there are more bins.
    ml, mr, mt, mb = 70, 30, 64, 80
    w, h = 820, 520
    pw, ph = w - ml - mr, h - mt - mb
    bottom = mt + ph
    slot = pw / n
    bar_w = slot * 0.72

    def x_of(i):  return ml + i * slot + (slot - bar_w) / 2
    def y_at(v):  return bottom - (v / y_max) * ph      # y of a cumulative value
    def seg_h(c): return (c / y_max) * ph

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">')
    s.append(f'<g id="background"><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/></g>')

    s.append('<g id="title">')
    s.append(f'<text x="{ml}" y="30" font-size="20" font-weight="bold" fill="#111">'
             f'Apollo astronauts — age at death + the living</text>')
    s.append(f'<text x="{ml}" y="49" font-size="12" fill="#777">'
             f'year-difference age · charcoal = {len(dec_pop)} deceased (age at death) · '
             f'grey = {len(liv_pop)} living (current age, {CURRENT_YEAR})</text>')
    s.append('</g>')

    # gridlines + integer y ticks
    s.append('<g id="grid-yaxis" font-size="11" fill="#999" text-anchor="end">')
    for t in range(0, y_max + 1):
        yy = bottom - (t / y_max) * ph
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw:.1f}" y2="{yy:.1f}" '
                 f'stroke="#ececec" stroke-width="1"/>')
        s.append(f'<text x="{ml - 10}" y="{yy + 4:.1f}">{t}</text>')
    s.append('</g>')

    # deceased (charcoal) from the baseline up
    s.append(f'<g id="bars-deceased" fill="{DECEASED_FILL}">')
    for i, (st, c) in enumerate(dec_bins):
        if c == 0:
            continue
        s.append(f'<rect id="dead-{st}" x="{x_of(i):.1f}" y="{y_at(c):.1f}" '
                 f'width="{bar_w:.1f}" height="{seg_h(c):.1f}"/>')
    s.append('</g>')

    # living (grey) stacked on top of the deceased segment
    s.append(f'<g id="bars-living" fill="{LIVING_FILL}">')
    for i, (st, c) in enumerate(liv_bins):
        if c == 0:
            continue
        top = dec_bins[i][1] + c
        s.append(f'<rect id="alive-{st}" x="{x_of(i):.1f}" y="{y_at(top):.1f}" '
                 f'width="{bar_w:.1f}" height="{seg_h(c):.1f}"/>')
    s.append('</g>')

    # value label: total on top of each stack
    s.append('<g id="value-labels" font-size="11" fill="#333" text-anchor="middle">')
    for i, st in enumerate(starts):
        if totals[i] == 0:
            continue
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{y_at(totals[i]) - 6:.1f}">{totals[i]}</text>')
    s.append('</g>')

    # x labels (every bin, empties included)
    s.append('<g id="x-labels" font-size="11" fill="#444" text-anchor="middle">')
    for i, st in enumerate(starts):
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{bottom + 18:.1f}">{bin_label(st, width)}</text>')
    s.append('</g>')

    s.append(f'<g id="axis-baseline"><line x1="{ml}" y1="{bottom}" x2="{ml + pw:.1f}" y2="{bottom}" '
             f'stroke="#333" stroke-width="1.5"/></g>')

    s.append('<g id="axis-titles" font-size="12" fill="#555">')
    s.append(f'<text x="{ml + pw / 2:.1f}" y="{h - 14}" text-anchor="middle">Age (years)</text>')
    ytx, yty = 20, mt + ph / 2
    s.append(f'<text x="{ytx}" y="{yty:.1f}" text-anchor="middle" '
             f'transform="rotate(-90 {ytx} {yty:.1f})">Astronauts</text>')
    s.append('</g>')

    # small legend, top-right over the empty high-age bins
    lx, ly = ml + pw - 108, mt + 4
    s.append('<g id="legend" font-size="12" fill="#555">')
    s.append(f'<rect x="{lx}" y="{ly}" width="13" height="13" fill="{DECEASED_FILL}"/>')
    s.append(f'<text x="{lx + 19}" y="{ly + 11}">deceased</text>')
    s.append(f'<rect x="{lx}" y="{ly + 20}" width="13" height="13" fill="{LIVING_FILL}"/>')
    s.append(f'<text x="{lx + 19}" y="{ly + 31}">living</text>')
    s.append('</g>')

    s.append('</svg>')
    out_path.write_text("\n".join(s), encoding="utf-8")
    return w, h, y_max


# populated in main(), referenced by render() for the subtitle counts
dec_pop, liv_pop = [], []


def main():
    global dec_pop, liv_pop
    astros = load_astros(DATA_H)
    dec_pop = [a for a in astros if a["death"] != 0]
    liv_pop = [a for a in astros if a["death"] == 0]
    deceased_ages = [a["death"] - a["birth"] for a in dec_pop]
    living_ages   = [CURRENT_YEAR - a["birth"] for a in liv_pop]

    print(f"Parsed {len(astros)} astronauts -> {len(dec_pop)} deceased, {len(liv_pop)} living.")
    print("Living:", ", ".join(f"{a['name']} ({CURRENT_YEAR - a['birth']})" for a in liv_pop))

    dec_bins = tally(deceased_ages, AGE_BIN, AGE_LO, AGE_HI)
    liv_bins = tally(living_ages,   AGE_BIN, AGE_LO, AGE_HI)

    print(f"\n{'bin':>8} {'dead':>5} {'alive':>6} {'tot':>4}   (diff against your C)")
    for (st, d), (_, l) in zip(dec_bins, liv_bins):
        if d or l:
            print(f"{bin_label(st, AGE_BIN):>8} {d:>5} {l:>6} {d + l:>4}")

    w, h, ymax = render(dec_bins, liv_bins, OUT)
    print(f"\nWrote {OUT.name}  ({w}x{h}, y_max={ymax}) — open in Sketch.")


if __name__ == "__main__":
    main()
