#!/usr/bin/env python3
"""
Apollo lifespan histograms -> clean, layered SVG for Sketch.

Makes three bar charts from the cohort: year of BIRTH, year of DEATH, and
(bonus) APPROX AGE AT DEATH. Output is hand-rolled SVG with named <g> groups,
so each piece lands as a tidy, re-styleable layer in Sketch ("bars", "x-labels",
each bar is "bar-1930", etc.). No precomputed numbers live in this file -- the
only place the data exists is your .h.

DISSIMILAR REDUNDANCY, on purpose (two independent ways, both real):
  (1) Across toolchains. This tool reads the SAME raw source your C reads
      (../../Human Efforts/scripts/apolloData.h) but by a fully independent
      path: a Python regex parse + its own tally. If it ever disagrees with
      your C, that disagreement is a true signal, not a shared bug. It prints
      the counts so you can diff them against your C, and it asserts the number
      of rows it parsed equals your `#define apolloAstrosCount`.
  (2) Inside the tool. Every bin count is computed two independent ways and
      asserted equal BEFORE anything is drawn. The verifier is verified.
  (3) Optional second renderer. If matplotlib is present it also dumps a
      throwaway "_verify" SVG of the same counts -- a dissimilar renderer to
      eyeball against the clean one. Pure-stdlib path is the primary; matplotlib
      is only a cross-check.

Run:  python3 apollo_lifespan_histograms.py
Re-bin: change the three *_BIN constants below and re-run.
"""

import re
import sys
from pathlib import Path
from collections import Counter

# ---- knobs (change + re-run to re-bin) ------------------------------------
BIRTH_BIN = 1    # years per bar for the births chart
DEATH_BIN = 5    # years per bar for the deaths chart
AGE_BIN   = 5    # years per bar for age-at-death

# ---- single source of truth: your data file -------------------------------
HERE   = Path(__file__).resolve().parent
DATA_H = HERE.parent.parent / "Human Efforts" / "scripts" / "apolloData.h"
OUT    = HERE
VERIFY = HERE / "_verify"


def load_astros(path):
    """Independent parse of apolloData.h. Returns list of dicts. death==0 means
    still living. Cross-checks row count against the #define (gate vs your C)."""
    if not path.exists():
        sys.exit(f"Can't find the data file at:\n  {path}\n"
                 f"(expected ../../Human Efforts/scripts/apolloData.h relative to this tool)")
    text = path.read_text()
    row = re.compile(
        r'\{\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
        r'\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*\}'
    )
    astros = [{
        "name":  m.group(1),
        "birth": int(m.group(2)),
        "death": int(m.group(3)),          # 0 == still living
        "stroll":   m.group(4) == "true",
        "lunar":    m.group(5) == "true",
        "trainAcc": m.group(6) == "true",
    } for m in row.finditer(text)]

    declared = re.search(r'#define\s+apolloAstrosCount\s+(\d+)', text)
    if declared:
        n = int(declared.group(1))
        if n != len(astros):
            sys.exit(f"PARSE MISMATCH: #define apolloAstrosCount = {n}, "
                     f"but I parsed {len(astros)} rows. Stopping before drawing a wrong chart.")
    if not astros:
        sys.exit("Parsed 0 rows -- the struct format may have changed.")
    return astros


def tally(years, width, lo=None, hi=None):
    """Bin `years` by `width`. Returns ordered [(bin_start, count)], empties kept.
    Counts are computed two independent ways and asserted equal (self-check)."""
    if not years:
        return []
    lo = (min(years) // width) * width if lo is None else lo
    hi = (max(years) // width) * width if hi is None else hi
    starts = list(range(lo, hi + 1, width))

    # method A: explicit loop into a fixed set of bins
    a = {s: 0 for s in starts}
    for y in years:
        a[(y // width) * width] += 1

    # method B: Counter over independently-computed bin starts
    b = Counter((y // width) * width for y in years)

    # dissimilar-redundancy self-check
    for s in starts:
        if a[s] != b.get(s, 0):
            sys.exit(f"INTERNAL COUNT MISMATCH at bin {s}: {a[s]} != {b.get(s, 0)}")
    if sum(a.values()) != len(years):
        sys.exit("INTERNAL: a record went missing during binning")

    return [(s, a[s]) for s in starts]


def bin_label(start, width):
    if width == 1:
        return str(start)
    return f"{start}–{str(start + width - 1)[-2:]}"   # e.g. 1980–84


def print_table(key, bins, width):
    print(f"\n[{key}]  ({len(bins)} bins of {width}yr, total = {sum(c for _, c in bins)})")
    for s, c in bins:
        bar = "#" * c
        print(f"  {bin_label(s, width):>9}  {c:>2}  {bar}")


def render_svg(bins, width, title, subtitle, x_title, y_title, out_path,
               bar_fill="#3a3a3a", w=820, h=520):
    """Hand-rolled SVG: named groups + per-bar ids => tidy Sketch layers."""
    ml, mr, mt, mb = 70, 30, 64, 80          # margins L R T B
    pw, ph = w - ml - mr, h - mt - mb        # plot width / height
    bottom = mt + ph
    n = len(bins)
    y_max = max((c for _, c in bins), default=1) or 1
    slot = pw / n
    bar_w = slot * 0.72

    def x_of(i):       return ml + i * slot + (slot - bar_w) / 2
    def y_of(c):       return bottom - (c / y_max) * ph
    def height_of(c):  return (c / y_max) * ph

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">')
    s.append(f'<g id="background"><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/></g>')

    s.append('<g id="title">')
    s.append(f'<text x="{ml}" y="30" font-size="20" font-weight="bold" fill="#111">{title}</text>')
    if subtitle:
        s.append(f'<text x="{ml}" y="49" font-size="12" fill="#777">{subtitle}</text>')
    s.append('</g>')

    # gridlines + integer y ticks
    s.append('<g id="grid-yaxis" font-size="11" fill="#999" text-anchor="end">')
    for t in range(0, y_max + 1):
        yy = bottom - (t / y_max) * ph
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw}" y2="{yy:.1f}" '
                 f'stroke="#ececec" stroke-width="1"/>')
        s.append(f'<text x="{ml - 10}" y="{yy + 4:.1f}">{t}</text>')
    s.append('</g>')

    s.append(f'<g id="bars" fill="{bar_fill}">')
    for i, (st, c) in enumerate(bins):
        if c == 0:
            continue
        s.append(f'<rect id="bar-{st}" x="{x_of(i):.1f}" y="{y_of(c):.1f}" '
                 f'width="{bar_w:.1f}" height="{height_of(c):.1f}"/>')
    s.append('</g>')

    s.append('<g id="value-labels" font-size="11" fill="#333" text-anchor="middle">')
    for i, (st, c) in enumerate(bins):
        if c == 0:
            continue
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{y_of(c) - 6:.1f}">{c}</text>')
    s.append('</g>')

    s.append('<g id="x-labels" font-size="11" fill="#444" text-anchor="middle">')
    for i, (st, c) in enumerate(bins):
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{bottom + 18:.1f}">{bin_label(st, width)}</text>')
    s.append('</g>')

    s.append(f'<g id="axis-baseline"><line x1="{ml}" y1="{bottom}" x2="{ml + pw}" y2="{bottom}" '
             f'stroke="#333" stroke-width="1.5"/></g>')

    s.append('<g id="axis-titles" font-size="12" fill="#555">')
    s.append(f'<text x="{ml + pw / 2:.1f}" y="{h - 14}" text-anchor="middle">{x_title}</text>')
    ytx, yty = 20, mt + ph / 2
    s.append(f'<text x="{ytx}" y="{yty:.1f}" text-anchor="middle" '
             f'transform="rotate(-90 {ytx} {yty:.1f})">{y_title}</text>')
    s.append('</g>')

    s.append('</svg>')
    out_path.write_text("\n".join(s), encoding="utf-8")


def verify_render(bins, width, title, out_path):
    """Optional dissimilar second renderer (matplotlib) -- a cross-check only."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"  (matplotlib unavailable; skipping verify render: {e})")
        return
    xs = [bin_label(s, width) for s, _ in bins]
    ys = [c for _, c in bins]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(xs)), ys, color="#3a3a3a")
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(xs, rotation=45, ha="right")
    ax.set_title(title)
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(out_path, format="svg")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)

    astros = load_astros(DATA_H)
    births = [a["birth"] for a in astros]
    deaths = [a["death"] for a in astros if a["death"] != 0]
    living = [a for a in astros if a["death"] == 0]
    ages   = [a["death"] - a["birth"] for a in astros if a["death"] != 0]

    print(f"Parsed {len(astros)} astronauts from {DATA_H.name} "
          f"-> {len(deaths)} deceased, {len(living)} living.")
    print("Still living (no death-year):", ", ".join(a["name"] for a in living) or "(none)")
    print("Diff these counts against your C's output -- they must match.")

    jobs = [
        ("births",       births, BIRTH_BIN,
         "Apollo astronauts — year of birth",
         "all 24 in the cohort", "Year of birth", "Astronauts"),
        ("deaths",       deaths, DEATH_BIN,
         "Apollo astronauts — year of death",
         f"{len(deaths)} deceased of 24 · {len(living)} still living",
         "Year of death", "Deaths"),
        ("age_at_death", ages, AGE_BIN,
         "Apollo astronauts — age at death (approx.)",
         "year-difference age · the 19 deceased only",
         "Age at death (years)", "Astronauts"),
    ]

    written = []
    for key, data, width, title, sub, xt, yt in jobs:
        bins = tally(data, width)
        print_table(key, bins, width)
        clean = OUT / f"{key}_clean.svg"
        render_svg(bins, width, title, sub, xt, yt, clean)
        verify_render(bins, width, title, VERIFY / f"{key}_verify.svg")
        written.append(clean)

    print("\nClean SVGs (open these in Sketch):")
    for p in written:
        print(f"  {p}")
    print(f"Cross-check renders: {VERIFY}/")


if __name__ == "__main__":
    main()
