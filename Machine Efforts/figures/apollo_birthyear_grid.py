#!/usr/bin/env python3
"""
Empty BIRTH-YEAR chart grid, styled to be a visual SIBLING of the author's
"Apollo Astronauts Age Distribution" Sketch chart — so the two read as a set.

Generates the FRAME only: horizontal gridlines, a "# count" y-axis, a birth-year
x-axis, the DECEASED / LIVING legend, and the title block. No bars yet — it's a
clean grid to drop bars into (in Sketch) or to wire up here later.

Every style token (canvas size, plot box, gridline colour + spacing, tick
lengths, fonts, label colours, legend swatches) is lifted straight off:
    Human Efforts/Graphs/For Claude Mutation/Apollo Astronauts Age — SSA overlay (v1).svg
so it lands on the same visual language.

FLAGS for the author — all easy to change, constants up top:
  * X axis = 1910-1945 ("the long span"), ticks every 5, longer ticks on the decades.
  * Y axis = 0-12 (# count), matching the age chart. Bump Y_MAX if a bin runs taller.
  * No bars yet. Say the word and I'll add the DECEASED/LIVING stacked bars from the
    binned birth-year data.

Fonts: the SVG names your Sketch fonts (Adobe Garamond Pro + SF Mono). A previewer
without those installed will substitute — but Sketch will render them true.

Run:  python3 apollo_birthyear_grid.py
"""

from pathlib import Path

# ---- output ----
OUT = Path(__file__).resolve().parent / "apollo_birthyear_grid.svg"

# ---- canvas (matches the age chart) ----
W, H = 1440, 1080

# ---- plot box, absolute canvas coords (lifted off the age chart) ----
PLOT_L, PLOT_R = 102.12, 1386.09     # x of left / right edge of the gridlines
PLOT_B         = 871.68              # y of count = 0 (the baseline)
PER_COUNT      = 55.8077             # px per count unit (the age chart's spacing)

# ---- axes (the knobs the author changes) ----
Y_MAX                = 12            # top of the "# count" axis
BIRTH_LO, BIRTH_HI   = 1910, 1945   # "the long span"
TICK_STEP, MAJOR_EVERY = 5, 10      # x ticks every 5yr; longer tick every decade

# ---- style tokens (verbatim from the age chart) ----
GRID       = "#ECECEC"
TICK       = "#2B2B2B"
BASELINE   = "#333333"
LBL_FILL   = "#999999"
TITLE_FILL = "#111111"
SUB_FILL   = "#777777"
AXIS_FILL  = "#C1C7C9"
DECEASED   = "#274060"   # navy  (fill-opacity 0.852)
LIVING     = "#DACDCC"   # taupe
LEG_TEXT   = "#555555"

GARAMOND = "AGaramondPro-Regular, Adobe Garamond Pro"
MONO     = "SFMono-Regular, SF Mono"
MONO_LT  = "SFMono-Light, SF Mono"

PLOT_T   = PLOT_B - Y_MAX * PER_COUNT
PER_YEAR = (PLOT_R - PLOT_L) / (BIRTH_HI - BIRTH_LO)

def x_year(y):  return PLOT_L + (y - BIRTH_LO) * PER_YEAR
def y_count(c): return PLOT_B - c * PER_COUNT


def main():
    cx = (PLOT_L + PLOT_R) / 2
    s = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<svg width="{W}px" height="{H}px" viewBox="0 0 {W} {H}" '
         f'xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>']

    # --- title + two-line subtitle (centred on the plot) ---
    s.append(f'<text x="{cx:.1f}" y="121" text-anchor="middle" font-family="{GARAMOND}" '
             f'font-size="42" fill="{TITLE_FILL}">Apollo Astronauts by Birth Year</text>')
    s.append(f'<text x="{cx:.1f}" y="151" text-anchor="middle" font-family="{MONO_LT}" '
             f'font-size="11" fill="{SUB_FILL}">29-astronaut cohort, lunar + Earth-orbit '
             f'&#183; data collected + computed by hand &#8212;</text>')
    s.append(f'<text x="{cx:.1f}" y="164" text-anchor="middle" font-family="{MONO_LT}" '
             f'font-size="11" fill="{SUB_FILL}">graphed via Claude-generated script + '
             f'Sketch App (by birth year)</text>')

    # --- horizontal gridlines ---
    for c in range(Y_MAX + 1):
        yy = y_count(c)
        s.append(f'<line x1="{PLOT_L:.2f}" y1="{yy:.2f}" x2="{PLOT_R:.2f}" y2="{yy:.2f}" '
                 f'stroke="{GRID}"/>')

    # --- y-axis labels (# count), right-aligned just left of the plot ---
    for c in range(Y_MAX + 1):
        s.append(f'<text x="{PLOT_L-14:.1f}" y="{y_count(c)+4.5:.1f}" text-anchor="end" '
                 f'font-family="{MONO}" font-size="14" fill="{LBL_FILL}">{c}</text>')

    # --- x-axis ticks + birth-year labels ---
    yr = BIRTH_LO
    while yr <= BIRTH_HI:
        xx = x_year(yr)
        major = (yr % MAJOR_EVERY == 0)
        tlen  = 14.2488 if major else 8.9055
        sw    = ' stroke-width="1.5"' if major else ''
        s.append(f'<line x1="{xx:.2f}" y1="{PLOT_B:.2f}" x2="{xx:.2f}" '
                 f'y2="{PLOT_B + tlen:.2f}" stroke="{TICK}"{sw}/>')
        s.append(f'<text x="{xx:.2f}" y="{PLOT_B+30:.1f}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="14" fill="{LBL_FILL}">{yr}</text>')
        yr += TICK_STEP

    # --- baseline (count 0), heavier ---
    s.append(f'<line x1="{PLOT_L:.2f}" y1="{PLOT_B:.2f}" x2="{PLOT_R:.2f}" y2="{PLOT_B:.2f}" '
             f'stroke="{BASELINE}" stroke-width="1.5"/>')

    # --- axis titles ---
    s.append(f'<text x="{cx:.1f}" y="{PLOT_B+80:.1f}" text-anchor="middle" '
             f'font-family="{GARAMOND}" font-size="32" fill="{AXIS_FILL}">birth year</text>')
    ymid = (PLOT_T + PLOT_B) / 2
    s.append(f'<text x="40" y="{ymid:.1f}" text-anchor="middle" font-family="{GARAMOND}" '
             f'font-size="32" fill="{AXIS_FILL}" transform="rotate(-90 40 {ymid:.1f})">'
             f'# count</text>')

    # --- legend (top-right), matching the age chart ---
    lx, ly = 1193.5, 200.1
    s.append(f'<rect x="{lx}" y="{ly}" width="23.18" height="23.15" fill="{DECEASED}" '
             f'fill-opacity="0.852"/>')
    s.append(f'<text x="{lx+33.3:.1f}" y="{ly+17.5:.1f}" font-family="{MONO_LT}" '
             f'font-size="16" fill="{LEG_TEXT}">DECEASED</text>')
    s.append(f'<rect x="{lx}" y="{ly+35.62}" width="23.18" height="23.15" fill="{LIVING}"/>')
    s.append(f'<text x="{lx+33.3:.1f}" y="{ly+53.1:.1f}" font-family="{MONO_LT}" '
             f'font-size="16" fill="{LEG_TEXT}">LIVING</text>')

    s.append('</svg>')
    OUT.write_text("\n".join(s), encoding="utf-8")

    print(f"Wrote: {OUT.name}")
    print(f"  x-axis: {BIRTH_LO}-{BIRTH_HI}, ticks every {TICK_STEP} (longer every {MAJOR_EVERY}); "
          f"{PER_YEAR:.2f} px/yr")
    print(f"  y-axis: 0-{Y_MAX} (# count)")
    print(f"  plot box: x[{PLOT_L:.1f}, {PLOT_R:.1f}]  y[{PLOT_T:.1f}, {PLOT_B:.1f}]")


if __name__ == "__main__":
    main()
