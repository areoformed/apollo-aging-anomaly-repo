#!/usr/bin/env python3
"""
Apollo Monte Carlo -> two clean, layered SVGs (Sketch-friendly), same lineage
as apollo_lifespan_histograms.py.

Reads [AUTHOR]'s million-deck output (astronaut-monte-carlo-results.tsv, written by
her astro-game2.c on 2026-09-07) and draws:

  (1) mc_smr_histogram.svg      -- histogram of the 1,000,000 synthetic-cohort
                                   SMRs, with the REAL Apollo-29 SMR as a vertical
                                   rule and its percentile printed on the plot.
  (2) mc_grandpa_histogram.svg  -- same treatment for the space-grandpa count.

DISSIMILAR REDUNDANCY, on purpose (the house rule for every figure here):
  (a) The REAL Apollo values (SMR, grandpa count, hit-80 count, median age) are
      NOT copied from the C output. They are recomputed here, independently, from
      the same raw source her C reads (apolloData.h + 1930CohortSSAData.h) by a
      Python regex parse and the same formula calculateSMR() uses
      (expected deaths = sum of -ln(alive[age]/alive[30]); SMR = observed/expected).
      If the two toolchains disagree, that disagreement is a true signal.
  (b) Every histogram bin is computed two independent ways (Counter vs. manual
      loop) and asserted equal BEFORE anything is drawn.
  (c) The percentile is computed two ways (count-and-divide vs. sorted bisect)
      and asserted equal.
  (d) If matplotlib is present, a throwaway "_verify" rendering of the same
      counts is dumped alongside -- a dissimilar renderer to eyeball against.

Nothing hand-drawn; every number traceable to the TSV or the .h files.
Run:  python3 apollo_mc_smr_histogram.py
"""
import re, sys, math, bisect
from pathlib import Path
from collections import Counter

HERE   = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / "Human Efforts" / "scripts" / "Astronaut MC"
TSV    = SCRIPTS / "astronaut-monte-carlo-results.tsv"
DATA_H = SCRIPTS / "apolloData.h"
SSA_H  = SCRIPTS / "1930CohortSSAData.h"
OUT    = HERE
VERIFY = HERE / "_verify"

STUDY_YEAR = 2026      # mirrors astroOnp.h `studyYear` and astro-game2.c line 205
SELECT_AGE = 30        # mirrors astroOnp.h `assumedSelectAge`
SMR_BIN    = 0.01      # histogram bin width for SMR

# ---------------------------------------------------------------- readers
def read_tsv(path):
    if not path.exists():
        sys.exit(f"Can't find the MC output at:\n  {path}")
    seed = None; rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                m = re.search(r"(\d+)", line); seed = int(m.group(1)) if m else None
                continue
            if not line.strip() or line.startswith("Deck"):
                continue
            i, g, h, med, s = line.rstrip("\n").split("\t")
            rows.append((int(i), int(g), int(h), int(med), float(s)))
    if not rows: sys.exit("Parsed 0 rows from the TSV.")
    return seed, rows

def read_apollo(path):
    text = path.read_text()
    row = re.compile(r'\{\s*"((?:[^"\\]|\\.)+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
                     r'\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*,'
                     r'\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*\}')
    astros = [dict(name=m.group(1), birth=int(m.group(2)), death=int(m.group(3)),
                   lunar=m.group(4)=="true", stroll=m.group(5)=="true", leo=m.group(6)=="true",
                   trainAcc=m.group(7)=="true", hitEighty=m.group(8)=="true",
                   spaceGrandpa=m.group(9)=="true") for m in row.finditer(text)]
    declared = re.search(r'#define\s+apolloAstrosCount\s+(\d+)', text)
    if declared and int(declared.group(1)) != len(astros):
        sys.exit(f"PARSE MISMATCH: apolloAstrosCount={declared.group(1)} but parsed {len(astros)} rows.")
    return astros

def read_ssa(path):
    text = path.read_text()
    alive = {int(a): int(n) for a, n in re.findall(r'\{\s*(\d+)\s*,\s*(\d+)\s*\}', text)}
    if SELECT_AGE not in alive: sys.exit("SSA table missing age 30.")
    return alive

# ---------------------------------------------------------- real Apollo values
def real_apollo(astros, alive):
    """Same definitions as astro-game2.c lines 182-215 + astroOnp.h calculateSMR."""
    hit80 = sum(1 for a in astros if a["hitEighty"])
    grandpa = sum(1 for a in astros if a["hitEighty"] and a["spaceGrandpa"])
    ages = sorted((a["death"] - a["birth"]) if a["death"] else (STUDY_YEAR - a["birth"]) for a in astros)
    median = ages[14]                              # her C: astroAgeArray[14] of 29
    observed = sum(1 for a in astros if a["death"])
    expected = sum(-math.log(alive[(a["death"]-a["birth"]) if a["death"] else (STUDY_YEAR-a["birth"])] / alive[SELECT_AGE])
                   for a in astros)
    return dict(hit80=hit80, grandpa=grandpa, median=median, observed=observed,
                expected=expected, smr=observed/expected)

# ------------------------------------------------------------- tallies (x2)
def tally_int(values):
    c1 = Counter(values)
    c2 = {}
    for v in values: c2[v] = c2.get(v, 0) + 1
    assert dict(c1) == c2, "integer tally self-check failed"
    lo, hi = min(c1), max(c1)
    return [(k, c1.get(k, 0)) for k in range(lo, hi + 1)]

def tally_smr(values, width):
    keys1 = [int(math.floor(v / width)) for v in values]
    c1 = Counter(keys1)
    c2 = {}
    for v in values:
        k = int(math.floor(v / width)); c2[k] = c2.get(k, 0) + 1
    assert dict(c1) == c2, "SMR tally self-check failed"
    lo, hi = min(c1), max(c1)
    return [(round(k * width, 4), c1.get(k, 0)) for k in range(lo, hi + 1)]

def percentile_of(values, x):
    n = len(values)
    le1 = sum(1 for v in values if v <= x)
    s = sorted(values); le2 = bisect.bisect_right(s, x)
    assert le1 == le2, "percentile self-check failed"
    lt = bisect.bisect_left(s, x)
    return 100.0 * le1 / n, 100.0 * lt / n, s

# --------------------------------------------------------------- SVG writer
def svg_hist(path, bins, title, subtitle, xlabel, real_x, real_label, pct_text, real_index_fn, width=1200, height=660):
    L, R, T, B = 90, 40, 70, 90
    W, H = width - L - R, height - T - B
    n = len(bins); ymax = max(c for _, c in bins)
    bw = W / n
    def y(c): return T + H - (c / ymax) * H
    g = []
    g.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">')
    g.append(f'<rect id="bg" width="{width}" height="{height}" fill="#ffffff"/>')
    g.append(f'<g id="title"><text x="{L}" y="32" font-size="20" font-weight="bold" fill="#111">{title}</text>')
    g.append(f'<text x="{L}" y="54" font-size="13" fill="#666">{subtitle}</text></g>')
    g.append('<g id="axes" stroke="#333" stroke-width="1">')
    g.append(f'<line x1="{L}" y1="{T+H}" x2="{L+W}" y2="{T+H}"/><line x1="{L}" y1="{T}" x2="{L}" y2="{T+H}"/></g>')
    g.append('<g id="bars" fill="#4a6fa5">')
    for i, (k, c) in enumerate(bins):
        x = L + i * bw
        g.append(f'<rect id="bar-{k}" x="{x:.2f}" y="{y(c):.2f}" width="{max(bw-1,0.5):.2f}" height="{(T+H-y(c)):.2f}"/>')
    g.append('</g>')
    # x labels: every k-th bin
    step = max(1, n // 12)
    g.append('<g id="x-labels" font-size="12" fill="#333" text-anchor="middle">')
    for i, (k, c) in enumerate(bins):
        if i % step == 0:
            g.append(f'<text x="{L + i*bw + bw/2:.2f}" y="{T+H+18}">{k}</text>')
    g.append(f'<text x="{L + W/2:.2f}" y="{T+H+48}" font-size="14">{xlabel}</text></g>')
    g.append('<g id="y-labels" font-size="12" fill="#333" text-anchor="end">')
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        g.append(f'<text x="{L-8}" y="{y(frac*ymax)+4:.2f}">{int(round(frac*ymax)):,}</text>')
    g.append(f'<text transform="translate(28,{T+H/2:.2f}) rotate(-90)" text-anchor="middle" font-size="14">decks (of {sum(c for _,c in bins):,})</text></g>')
    # real Apollo rule
    xi = real_index_fn(real_x)          # may be fractional: exact position on the bin axis
    xr = L + xi * bw
    g.append(f'<g id="real-apollo" stroke="#c0392b" stroke-width="2"><line x1="{xr:.2f}" y1="{T}" x2="{xr:.2f}" y2="{T+H}" stroke-dasharray="6,4"/></g>')
    # annotation lives in the clear upper-right corner (the rule sits near the mode, where bars are tallest)
    ax_ = L + W - 8
    g.append(f'<g id="annotation" font-size="13" fill="#c0392b" text-anchor="end">')
    g.append(f'<line x1="{ax_-250}" y1="{T+14}" x2="{ax_-226}" y2="{T+14}" stroke="#c0392b" stroke-width="2" stroke-dasharray="6,4"/>')
    g.append(f'<text x="{ax_:.2f}" y="{T+18}">{real_label}</text><text x="{ax_:.2f}" y="{T+38}">{pct_text}</text></g>')
    g.append('</svg>')
    path.write_text("\n".join(g))

# --------------------------------------------------------------------- main
def main():
    seed, rows = read_tsv(TSV)
    astros = read_apollo(DATA_H); alive = read_ssa(SSA_H)
    real = real_apollo(astros, alive)
    n = len(rows)
    smr = [r[4] for r in rows]; grandpa = [r[1] for r in rows]; hit80 = [r[2] for r in rows]; med = [r[3] for r in rows]

    print(f"TSV: {n:,} decks, seed {seed}")
    print(f"REAL Apollo-29 (independent Python recompute from the .h files): "
          f"observed={real['observed']} expected={real['expected']:.6f} SMR={real['smr']:.6f} "
          f"hit80={real['hit80']} grandpa={real['grandpa']} median_age={real['median']}")
    mean = sum(smr)/n; s_sorted = sorted(smr)
    print(f"MC SMR: min {s_sorted[0]:.6f} median {s_sorted[n//2]:.6f} mean {mean:.6f} max {s_sorted[-1]:.6f}")

    p_le, p_lt, _ = percentile_of(smr, real["smr"])
    print(f"Percentile of real SMR among MC decks: {p_le:.2f}% of decks <= real; {p_lt:.2f}% strictly below")
    gp_le, gp_lt, _ = percentile_of(grandpa, real["grandpa"])
    gp_ge = 100.0 - gp_lt   # P(X >= real): the permutation tail INCLUDES the observed value (referee, 2026-09-07)
    print(f"Grandpa count {real['grandpa']}: {gp_le:.2f}% of decks <= ; {gp_lt:.2f}% strictly below; "
          f"{gp_ge:.2f}% at or above (this is the upper-tail p, not {100-gp_le:.2f}% strictly above)")
    h_le, h_lt, _ = percentile_of(hit80, real["hit80"])
    print(f"Hit-80 count {real['hit80']}: {h_le:.2f}% <= ; {h_lt:.2f}% below")
    m_le, m_lt, _ = percentile_of(med, real["median"])
    print(f"Median age {real['median']}: {m_le:.2f}% <= ; {m_lt:.2f}% below; {100-m_lt:.2f}% at or above (upper-tail p)")

    sb = tally_smr(smr, SMR_BIN); assert sum(c for _, c in sb) == n
    gb = tally_int(grandpa);      assert sum(c for _, c in gb) == n
    print(f"SMR bins: {len(sb)} (width {SMR_BIN}); grandpa bins: {len(gb)}; both sum to {n:,}")

    lo_smr = sb[0][0]
    svg_hist(OUT / "mc_smr_histogram.svg", sb,
             "Mortality of a million synthetic Apollo-sized cohorts",
             f"{n:,} random draws of 29 from the 73 pre-1970 NASA astronauts · SMR vs. US 1930 birth cohort (SSA), at risk from age 30 · seed {seed}",
             "standardized mortality ratio (SMR), bin width 0.01",
             real["smr"], f"real Apollo 29: SMR {real['smr']:.3f}",
             f"{p_le:.1f}% of synthetic cohorts sit at or below it",
             lambda x: (x - lo_smr) / SMR_BIN)          # exact, continuous position
    lo_g = gb[0][0]
    svg_hist(OUT / "mc_grandpa_histogram.svg", gb,
             "Space grandpas in a million synthetic Apollo-sized cohorts",
             f"{n:,} random draws of 29 from the 73 pre-1970 NASA astronauts · seed {seed}",
             "space grandpas per cohort of 29 (the spaceGrandpa flag in the source data; a subset of those who reached 80)",
             real["grandpa"], f"real Apollo 29: {real['grandpa']} space grandpas",
             f"{gp_ge:.1f}% of synthetic cohorts have {real['grandpa']} or more",
             lambda x: x - lo_g + 0.5)                   # integer bins: centre of the bar
    print(f"wrote {OUT/'mc_smr_histogram.svg'} and {OUT/'mc_grandpa_histogram.svg'}")

    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        VERIFY.mkdir(exist_ok=True)
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))
        ax[0].bar([k for k, _ in sb], [c for _, c in sb], width=SMR_BIN, align="edge"); ax[0].axvline(real["smr"], color="r", ls="--")
        ax[0].set_title(f"verify: MC SMR (real {real['smr']:.3f}, {p_le:.1f}th pct)")
        ax[1].bar([k for k, _ in gb], [c for _, c in gb]); ax[1].axvline(real["grandpa"], color="r", ls="--")
        ax[1].set_title(f"verify: grandpa count (real {real['grandpa']})")
        fig.tight_layout(); fig.savefig(VERIFY / "mc_verify.png", dpi=110)
        print(f"wrote {VERIFY/'mc_verify.png'} (dissimilar renderer)")
    except ImportError:
        print("matplotlib not present; skipped the verify render")

if __name__ == "__main__":
    main()
