#!/usr/bin/env python3
"""
Apollo Monte Carlo -> distribution TABLES + two more figures ([AUTHOR]'s ask, 2026-09-07 18:38 PDT):
  (a) space grandpas / hit-80 per synthetic deck, real Apollo vs the rest  -> table + histogram
  (b) ALL one-million SMR values, binned at 0.01 (table) and 0.001 (fine histogram)

Same lineage as apollo_mc_smr_histogram.py: reads her TSV, recomputes the real-cohort values
independently from her .h files, tallies every bin two ways and asserts equal, hand-rolled SVG
with named <g> layers, matplotlib only as a dissimilar verify renderer. Nothing hand-drawn.

The reference lines on the SMR figure use HER smr.c output (run 2026-09-07):
  Apollo 29 = 0.490450 · other NASA astronauts = 0.671723 · corrected NASA cohort = 0.514837
(the Python recompute of the Apollo value from the .h files agrees to six figures).
Run:  python3 apollo_mc_tables.py
"""
import re, sys, math, bisect, csv
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / "Human Efforts" / "scripts" / "Astronaut MC"
TSV = SCRIPTS / "astronaut-monte-carlo-results.tsv"
DATA_A = SCRIPTS / "apolloData.h"; DATA_N = SCRIPTS / "nasaNonApolloAstroPre1970.h"
VERIFY = HERE / "_verify"

# her smr.c numbers (Sep 7 2026 run), used as labelled reference rules
SMRC = {"Apollo 29 (smr.c)": 0.490450, "other NASA astronauts (smr.c)": 0.671723, "corrected NASA cohort (smr.c)": 0.514837}

ROW = re.compile(r'\{\s*"((?:[^"\\]|\\.)+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*,'
                 r'\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*\}')
def read_h(path):
    return [dict(name=m.group(1), trainAcc=m.group(7)=="true", hit80=m.group(8)=="true", grandpa=m.group(9)=="true")
            for m in ROW.finditer(path.read_text())]

def read_tsv(path):
    seed=None; rows=[]
    for line in open(path):
        if line.startswith("#"):
            m=re.search(r"(\d+)", line); seed=int(m.group(1)) if m else None; continue
        if not line.strip() or line.startswith("Deck"): continue
        i,g,h,med,s=line.rstrip("\n").split("\t"); rows.append((int(g),int(h),float(s)))
    return seed, rows

def tally2(keys):
    c1=Counter(keys); c2={}
    for k in keys: c2[k]=c2.get(k,0)+1
    assert dict(c1)==c2, "tally self-check failed"
    return c1

def svg_hist(path, bins, title, subtitle, xlabel, rules, width=1200, height=660, label_every=None):
    """bins: list of (label, x_left, count) in order; rules: list of (x_value, label). x axis is continuous."""
    L,R,T,B = 90,40,70,90; W,H = width-L-R, height-T-B
    n=len(bins); ymax=max(c for _,_,c in bins); xs=[x for _,x,_ in bins]; xmin=xs[0]; step=xs[1]-xs[0] if n>1 else 1; xmax=xs[-1]+step
    def X(v): return L + (v-xmin)/(xmax-xmin)*W
    def Y(c): return T + H - (c/ymax)*H
    g=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect id="bg" width="{width}" height="{height}" fill="#ffffff"/>',
       f'<g id="title"><text x="{L}" y="32" font-size="20" font-weight="bold" fill="#111">{title}</text>',
       f'<text x="{L}" y="54" font-size="13" fill="#666">{subtitle}</text></g>',
       f'<g id="axes" stroke="#333" stroke-width="1"><line x1="{L}" y1="{T+H}" x2="{L+W}" y2="{T+H}"/><line x1="{L}" y1="{T}" x2="{L}" y2="{T+H}"/></g>',
       '<g id="bars" fill="#4a6fa5">']
    bw=W/n
    for lab,x,c in bins:
        g.append(f'<rect id="bar-{lab}" x="{X(x):.2f}" y="{Y(c):.2f}" width="{max(bw-0.6,0.4):.2f}" height="{(T+H-Y(c)):.2f}"/>')
    g.append('</g><g id="x-labels" font-size="12" fill="#333" text-anchor="middle">')
    every = label_every or max(1, n//12)
    tick = every*step   # label where x is a multiple of the tick, so ticks land on round values
    for i,(lab,x,c) in enumerate(bins):
        if abs(x/tick - round(x/tick)) < 1e-6: g.append(f'<text x="{X(x):.2f}" y="{T+H+18}">{lab}</text>')
    g.append(f'<text x="{L+W/2:.2f}" y="{T+H+48}" font-size="14">{xlabel}</text></g>')
    g.append('<g id="y-labels" font-size="12" fill="#333" text-anchor="end">')
    for f in (0,0.25,0.5,0.75,1.0): g.append(f'<text x="{L-8}" y="{Y(f*ymax)+4:.2f}">{int(round(f*ymax)):,}</text>')
    g.append(f'<text transform="translate(28,{T+H/2:.2f}) rotate(-90)" text-anchor="middle" font-size="14">decks (of {sum(c for _,_,c in bins):,})</text></g>')
    colors=["#c0392b","#7d3c98","#1e8449"]
    g.append('<g id="rules">')
    for (v,lab),col in zip(rules,colors):
        xr=X(v); g.append(f'<line x1="{xr:.2f}" y1="{T}" x2="{xr:.2f}" y2="{T+H}" stroke="{col}" stroke-width="2" stroke-dasharray="6,4"/>')
    g.append('</g><g id="annotation" font-size="13" text-anchor="end">')
    for k,((v,lab),col) in enumerate(zip(rules,colors)):
        y=T+18+k*20; ax_=L+W-8
        est=len(lab)*6.6+34   # rough text width at 13px; the dash sits just left of the text
        g.append(f'<line x1="{ax_-est-26:.0f}" y1="{y-4}" x2="{ax_-est:.0f}" y2="{y-4}" stroke="{col}" stroke-width="2" stroke-dasharray="6,4"/><text x="{ax_}" y="{y}" fill="{col}">{lab}</text>')
    g.append('</g></svg>'); path.write_text("\n".join(g))

def write_table(path_md, path_csv, header, rows, note):
    with open(path_csv,"w",newline="") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
    with open(path_md,"w") as f:
        f.write(note+"\n\n| "+" | ".join(header)+" |\n|"+"---|"*len(header)+"\n")
        for r in rows: f.write("| "+" | ".join(str(x) for x in r)+" |\n")

def main():
    seed, rows = read_tsv(TSV); n=len(rows)
    ap=read_h(DATA_A); na=read_h(DATA_N)
    def summ(lst):
        e=[x for x in lst if not x["trainAcc"]]; h=sum(x["hit80"] for x in e); g=sum(x["hit80"] and x["grandpa"] for x in e); return len(e),h,g
    (ea,ha,ga),(en,hn,gn)=summ(ap),summ(na); ratio_ap=ga/ha; ratio_na=gn/hn; ratio_pool=(ga+gn)/(ha+hn)
    print(f"real Apollo: {ga}/{ha} = {ratio_ap:.4f} · non-Apollo eligible: {gn}/{hn} = {ratio_na:.4f} · pool: {ga+gn}/{ha+hn} = {ratio_pool:.4f}")

    # (a) grandpa / hit80 per deck — exact fractions occur; bin at 0.02
    ratios=[g/h for g,h,_ in rows if h>0]; assert len(ratios)==n
    RB=0.02
    keys=[int(math.floor(r/RB+1e-9)) for r in ratios]; c=tally2(keys)
    lo,hi=min(c),max(c); bins=[(f"{k*RB:.2f}", k*RB, c.get(k,0)) for k in range(lo,hi+1)]; assert sum(b[2] for b in bins)==n
    s=sorted(ratios); at_or_above=n-bisect.bisect_left(s,ratio_ap-1e-12); below=bisect.bisect_left(s,ratio_ap-1e-12)
    mean=sum(ratios)/n; sd=math.sqrt(sum((r-mean)**2 for r in ratios)/n)
    print(f"deck ratio: mean {mean:.4f} sd {sd:.4f} · Apollo {ratio_ap:.4f}: {100*at_or_above/n:.2f}% of decks at or above, {100*below/n:.2f}% below")
    cum=0; trows=[]
    for lab,x,cnt in bins:
        cum+=cnt; mark = "◀ real Apollo 19/22 = 0.864" if x<=ratio_ap<x+RB else ("◀ non-Apollo pool 19/28 = 0.679" if x<=ratio_na<x+RB else "")
        trows.append((f"{x:.2f}–{x+RB:.2f}", cnt, f"{100*cnt/n:.2f}%", f"{100*cum/n:.2f}%", mark))
    trows.append(("summary", f"mean {mean:.3f}, sd {sd:.3f}", f"Apollo 0.864 → {100*at_or_above/n:.1f}% at or above", f"non-Apollo 0.679 · pool 0.760", ""))
    write_table(HERE/"mc_grandpa_ratio_table.md", HERE/"mc_grandpa_ratio_table.csv",
                ["grandpas ÷ reached-80 (bin)","decks","share","cumulative","real cohorts"], trows,
                f"# Space grandpas as a share of those who reached 80 — {n:,} synthetic decks (seed {seed})\n"
                f"*Built {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} PDT from her TSV; real cohorts recomputed from apolloData.h / nasaNonApolloAstroPre1970.h (eligible = not trainAcc). Bin width 0.02; a deck's ratio is grandpas ÷ hit-80 for that deck of 29. The ratio is a fraction of two small integers, so it takes only certain values and the bins fill unevenly by construction — the comb in the histogram is arithmetic, not noise.*")
    svg_hist(HERE/"mc_grandpa_ratio_histogram.svg", bins,
             "Space grandpas as a share of survivors to 80, per synthetic cohort",
             f"{n:,} random draws of 29 from the 73 pre-1970 NASA astronauts · grandpas ÷ reached-80 per deck · bin 0.02 · seed {seed}",
             "space grandpas ÷ astronauts who reached 80, per cohort of 29",
             [(ratio_ap, f"real Apollo 29: 19/22 = {ratio_ap:.3f} ({100*at_or_above/n:.1f}% of decks at or above)"),
              (ratio_na, f"non-Apollo pool: 19/28 = {ratio_na:.3f}"),
              (ratio_pool, f"whole pool: 38/50 = {ratio_pool:.3f}")], label_every=5)

    # (b) ALL SMR values — table at 0.01, fine histogram at 0.001
    smr=[s_ for _,_,s_ in rows]; s2=sorted(smr)
    def binned(width):
        ks=[int(math.floor(v/width+1e-9)) for v in smr]; cc=tally2(ks); lo,hi=min(cc),max(cc)
        out=[(f"{k*width:.{3 if width<0.01 else 2}f}", k*width, cc.get(k,0)) for k in range(lo,hi+1)]; assert sum(o[2] for o in out)==n; return out
    b01=binned(0.01); b001=binned(0.001)
    cum=0; trows=[]
    for lab,x,cnt in b01:
        cum+=cnt; marks=[k for k,v in SMRC.items() if x<=v<x+0.01]
        trows.append((f"{x:.2f}–{x+0.01:.2f}", cnt, f"{100*cnt/n:.2f}%", f"{100*cum/n:.2f}%", "; ".join(f"◀ {m} = {SMRC[m]:.3f}" for m in marks)))
    le=bisect.bisect_right(s2,SMRC["Apollo 29 (smr.c)"]); 
    trows.append(("summary", f"min {s2[0]:.3f} · median {s2[n//2]:.3f} · mean {sum(smr)/n:.4f} · max {s2[-1]:.3f}", f"Apollo 0.490 → {100*le/n:.1f}% of decks at or below", "", ""))
    write_table(HERE/"mc_smr_table.md", HERE/"mc_smr_table.csv",
                ["SMR (bin)","decks","share","cumulative","real cohorts (her smr.c, Sep 7)"], trows,
                f"# All {n:,} synthetic-cohort SMRs, binned at 0.01 (seed {seed})\n*Two decimals for the table (70 rows); the fine histogram uses three (0.001 bins). Reference values are her smr.c output of 2026-09-07: Apollo 0.490450, other NASA 0.671723, corrected NASA cohort 0.514837.*")
    svg_hist(HERE/"mc_smr_histogram_fine.svg", b001,
             "All one million synthetic-cohort SMRs, at three decimals",
             f"{n:,} random draws of 29 from the 73 pre-1970 NASA astronauts · bin width 0.001 · reference rules from her smr.c run of Sep 7 · seed {seed}",
             "standardized mortality ratio (SMR) vs US 1930 birth cohort, bin width 0.001",
             [(SMRC["Apollo 29 (smr.c)"], f"Apollo 29: {SMRC['Apollo 29 (smr.c)']:.3f} ({100*le/n:.1f}% of decks at or below)"),
              (SMRC["corrected NASA cohort (smr.c)"], f"corrected NASA cohort: {SMRC['corrected NASA cohort (smr.c)']:.3f}"),
              (SMRC["other NASA astronauts (smr.c)"], f"other NASA astronauts: {SMRC['other NASA astronauts (smr.c)']:.3f}")], label_every=50)
    print("wrote: mc_grandpa_ratio_table.md/.csv, mc_grandpa_ratio_histogram.svg, mc_smr_table.md/.csv, mc_smr_histogram_fine.svg")
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        VERIFY.mkdir(exist_ok=True); fig,ax=plt.subplots(1,2,figsize=(14,5))
        ax[0].bar([x for _,x,_ in bins],[c for _,_,c in bins],width=RB,align="edge"); [ax[0].axvline(v,color=col,ls="--") for v,col in ((ratio_ap,"r"),(ratio_na,"purple"),(ratio_pool,"g"))]; ax[0].set_title("verify: grandpa/hit80 per deck")
        ax[1].bar([x for _,x,_ in b001],[c for _,_,c in b001],width=0.001,align="edge"); [ax[1].axvline(v,color=col,ls="--") for v,col in zip(SMRC.values(),("r","g","purple"))]; ax[1].set_title("verify: SMR at 0.001")
        fig.tight_layout(); fig.savefig(VERIFY/"mc_tables_verify.png",dpi=110); print("verify render written")
    except ImportError: print("no matplotlib; verify skipped")

if __name__=="__main__": main()
