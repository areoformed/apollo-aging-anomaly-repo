#!/usr/bin/env python3
"""
Apollo cohort age histogram — 29-astronaut version (lunar LLO + Earth-orbit LEO),
deceased (charcoal, age at death) stacked with the living (grey, current age).

Same clean style as age_at_death_clean.svg, axis 30–120. Unlike the sibling
tool this does NOT re-derive from apolloData.h, because the .h holds only the 24
lunar astronauts; the 5 Earth-orbit (LEO) people live in the author's own binning.
So the source here is HER table, cohort_29_bins.csv — and the tool's job is to
plot it faithfully and re-check its internal arithmetic (total == alive + mort
per bin, and the totals) before drawing.

Run:  python3 apollo_age_29cohort.py
"""

import csv
import sys
from pathlib import Path

AGE_BIN = 5
CURRENT_YEAR = 2026
Y_AXIS_MAX = 12   # fixed y-axis ceiling for headroom above the data max (=10); bump to 16 for more air
DECEASED_FILL = "#3a3a3a"   # charcoal, as the original
LIVING_FILL   = "#bdbdbd"   # the living, in grey

HERE = Path(__file__).resolve().parent
CSV  = HERE / "cohort_29_bins.csv"
OUT  = HERE / "age_29cohort_with_living.svg"


def load_bins(path):
    """Read the author's binned figures. Re-check arithmetic before trusting them."""
    rows = list(csv.DictReader(path.open()))
    bins = []
    for r in rows:
        st    = int(r["bin_start"])
        llo   = int(r["llo"]); leo = int(r["leo"])
        total = int(r["total"]); alive = int(r["alive"]); mort = int(r["mort"])
        # dissimilar-redundancy checks on the supplied data
        if llo + leo != total:
            sys.exit(f"BIN {st}: llo+leo ({llo}+{leo}) != total ({total}).")
        if alive + mort != total:
            sys.exit(f"BIN {st}: alive+mort ({alive}+{mort}) != total ({total}).")
        bins.append({"start": st, "alive": alive, "mort": mort,
                     "total": total, "llo": llo, "leo": leo})
    return bins


def bin_label(start, width=AGE_BIN):
    return f"{start}–{str(start + width - 1)[-2:]}"


def render(bins, out_path, n_dead, n_alive):
    starts = [b["start"] for b in bins]
    n = len(starts)
    y_max = max(Y_AXIS_MAX, max((b["total"] for b in bins), default=1))

    ml, mr, mt, mb = 70, 30, 64, 80
    w, h = 820, 520
    pw, ph = w - ml - mr, h - mt - mb
    bottom = mt + ph
    slot = pw / n
    bar_w = slot * 0.72

    def x_of(i):  return ml + i * slot + (slot - bar_w) / 2
    def y_at(v):  return bottom - (v / y_max) * ph
    def seg_h(c): return (c / y_max) * ph

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">')
    s.append(f'<g id="background"><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/></g>')

    s.append('<g id="title">')
    s.append(f'<text x="{ml}" y="30" font-size="20" font-weight="bold" fill="#111">'
             f'Apollo astronauts — age at death + the living</text>')
    s.append(f'<text x="{ml}" y="49" font-size="12" fill="#777">'
             f'29-astronaut cohort, lunar + Earth-orbit · '
             f'charcoal = {n_dead} deceased (age at death) · grey = {n_alive} living (current age, {CURRENT_YEAR})</text>')
    s.append('</g>')

    s.append('<g id="grid-yaxis" font-size="11" fill="#999" text-anchor="end">')
    for t in range(0, y_max + 1):
        yy = bottom - (t / y_max) * ph
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw:.1f}" y2="{yy:.1f}" '
                 f'stroke="#ececec" stroke-width="1"/>')
        s.append(f'<text x="{ml - 10}" y="{yy + 4:.1f}">{t}</text>')
    s.append('</g>')

    s.append(f'<g id="bars-deceased" fill="{DECEASED_FILL}">')
    for i, b in enumerate(bins):
        if b["mort"] == 0:
            continue
        s.append(f'<rect id="dead-{b["start"]}" x="{x_of(i):.1f}" y="{y_at(b["mort"]):.1f}" '
                 f'width="{bar_w:.1f}" height="{seg_h(b["mort"]):.1f}"/>')
    s.append('</g>')

    s.append(f'<g id="bars-living" fill="{LIVING_FILL}">')
    for i, b in enumerate(bins):
        if b["alive"] == 0:
            continue
        top = b["mort"] + b["alive"]
        s.append(f'<rect id="alive-{b["start"]}" x="{x_of(i):.1f}" y="{y_at(top):.1f}" '
                 f'width="{bar_w:.1f}" height="{seg_h(b["alive"]):.1f}"/>')
    s.append('</g>')

    s.append('<g id="value-labels" font-size="11" fill="#333" text-anchor="middle">')
    for i, b in enumerate(bins):
        if b["total"] == 0:
            continue
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{y_at(b["total"]) - 6:.1f}">{b["total"]}</text>')
    s.append('</g>')

    s.append('<g id="x-labels" font-size="11" fill="#444" text-anchor="middle">')
    for i, b in enumerate(bins):
        s.append(f'<text x="{x_of(i) + bar_w / 2:.1f}" y="{bottom + 18:.1f}">{bin_label(b["start"])}</text>')
    s.append('</g>')

    s.append(f'<g id="axis-baseline"><line x1="{ml}" y1="{bottom}" x2="{ml + pw:.1f}" y2="{bottom}" '
             f'stroke="#333" stroke-width="1.5"/></g>')

    # x-axis ticks for hand-labeling: a notch every 5 years (each bin boundary),
    # slightly longer + thicker every 10 years. Below the baseline, clear of the bin labels.
    s.append('<g id="x-ticks" stroke="#333">')
    for k in range(n + 1):
        age = bins[0]["start"] + k * AGE_BIN
        xx = ml + k * slot
        major = (age % 10 == 0)
        tick_len = 8 if major else 5
        s.append(f'<line x1="{xx:.1f}" y1="{bottom}" x2="{xx:.1f}" y2="{bottom + tick_len}" '
                 f'stroke-width="{1.5 if major else 1}"/>')
    s.append('</g>')

    s.append('<g id="axis-titles" font-size="12" fill="#555">')
    s.append(f'<text x="{ml + pw / 2:.1f}" y="{h - 14}" text-anchor="middle">Age (years)</text>')
    ytx, yty = 20, mt + ph / 2
    s.append(f'<text x="{ytx}" y="{yty:.1f}" text-anchor="middle" '
             f'transform="rotate(-90 {ytx} {yty:.1f})">Astronauts</text>')
    s.append('</g>')

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


def main():
    bins = load_bins(CSV)
    n_dead  = sum(b["mort"] for b in bins)
    n_alive = sum(b["alive"] for b in bins)
    n_total = sum(b["total"] for b in bins)
    n_llo   = sum(b["llo"] for b in bins)
    n_leo   = sum(b["leo"] for b in bins)

    print(f"Cohort: {n_total} ({n_llo} lunar + {n_leo} Earth-orbit) -> {n_dead} deceased, {n_alive} living.")
    print(f"\n{'bin':>8} {'mort':>5} {'alive':>6} {'tot':>4}")
    for b in bins:
        if b["total"]:
            print(f"{bin_label(b['start']):>8} {b['mort']:>5} {b['alive']:>6} {b['total']:>4}")

    w, h, ymax = render(bins, OUT, n_dead, n_alive)
    print(f"\nWrote {OUT.name}  ({w}x{h}, y_max={ymax}) — open in Sketch.")


if __name__ == "__main__":
    main()
