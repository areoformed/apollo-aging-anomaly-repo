#!/usr/bin/env python3
"""
Apollo astronauts' attained ages vs the SSA 1930-cohort median lifespan ([AUTHOR]'s ask, 2026-09-07 19:19 PDT).
Bars: each of the 29 Apollo astronauts' attained age (age at death, or age in 2026 if living — living bars are
drawn hollow because they are still counting). Reference lines: the 1930 birth-cohort median age at death
(a) from birth and (b) conditional on surviving to 30 (the analysis' at-risk start), both read straight off
her 1930CohortSSAData.h survivorship column; plus the Apollo median (element [14] of the sorted 29, her C's rule).
Same lineage as the other tools here: independent parse of her .h files, every number printed, hand-rolled SVG,
matplotlib only as a verify render. Nothing hand-drawn.
"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / "Human Efforts" / "scripts" / "Astronaut MC"
STUDY_YEAR, SELECT_AGE = 2026, 30
ROW = re.compile(r'\{\s*"((?:[^"\\]|\\.)+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,')
astros = [dict(name=m.group(1).replace('\\"','"'), birth=int(m.group(2)), death=int(m.group(3))) for m in ROW.finditer((SCRIPTS/"apolloData.h").read_text())]
assert len(astros)==29, len(astros)
alive = {int(a):int(n) for a,n in re.findall(r'\{\s*(\d+)\s*,\s*(\d+)\s*\}', (SCRIPTS/"1930CohortSSAData.h").read_text())}
l0, l30 = alive[0], alive[SELECT_AGE]
def median_age(threshold):
    # first age at which fewer than half of the reference group is still alive; linear interpolation inside the year
    ages = sorted(alive)
    for a in ages:
        if alive[a] <= threshold:
            prev = a-1; la, lb = alive[prev], alive[a]
            return prev + (la-threshold)/(la-lb) if la!=lb else a
    return None
med_birth = median_age(l0/2); med_30 = median_age(l30/2)
for a in astros:
    a["age"] = (a["death"]-a["birth"]) if a["death"] else (STUDY_YEAR-a["birth"]); a["living"] = a["death"]==0
ages_sorted = sorted(a["age"] for a in astros); apollo_median = ages_sorted[14]
print(f"1930 cohort: l(0)={l0:,} l(30)={l30:,}; median age at death from birth = {med_birth:.1f}; conditional on reaching 30 = {med_30:.1f}")
print(f"Apollo 29: attained ages sorted {ages_sorted}; median (sorted[14]) = {apollo_median}; living = {sum(a['living'] for a in astros)}")

# ---- SVG
order = sorted(astros, key=lambda a: a["age"])
W,H,L,R,T,B = 1200,700,70,40,80,150
PW,PH = W-L-R, H-T-B; ymax = 100
def Y(v): return T+PH-(v/ymax)*PH
bw = PW/len(order)
g=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
   f'<rect id="bg" width="{W}" height="{H}" fill="#fff"/>',
   f'<g id="title"><text x="{L}" y="32" font-size="20" font-weight="bold" fill="#111">Attained age of the 29 Apollo astronauts vs. the US 1930 birth cohort\'s median lifespan</text>',
   f'<text x="{L}" y="54" font-size="13" fill="#666">ages at death, or age in {STUDY_YEAR} for the living (hollow bars, still counting) · reference: SSA 1930 cohort survivorship (her 1930CohortSSAData.h) · Apollo median = sorted[14], her C\'s rule</text></g>',
   f'<g id="axes" stroke="#333"><line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}"/><line x1="{L}" y1="{T+PH}" x2="{L+PW}" y2="{T+PH}"/></g>',
   '<g id="y-labels" font-size="12" fill="#333" text-anchor="end">']
for v in range(0,101,10): g.append(f'<text x="{L-8}" y="{Y(v)+4:.1f}">{v}</text>')
g.append(f'<text transform="translate(22,{T+PH/2:.0f}) rotate(-90)" text-anchor="middle" font-size="14">age (years)</text></g><g id="bars">')
for i,a in enumerate(order):
    x=L+i*bw+2; y=Y(a["age"]); h=T+PH-y
    style = 'fill="#4a6fa5"' if not a["living"] else 'fill="#fff" stroke="#4a6fa5" stroke-width="2"'
    g.append(f'<rect id="bar-{i}" x="{x:.1f}" y="{y:.1f}" width="{bw-4:.1f}" height="{h:.1f}" {style}/>')
    g.append(f'<text x="{x+(bw-4)/2:.1f}" y="{y+14:.1f}" font-size="11" text-anchor="middle" fill="{"#fff" if not a["living"] else "#4a6fa5"}">{a["age"]}</text>')
g.append('</g><g id="x-labels" font-size="10" fill="#333">')
for i,a in enumerate(order):
    x=L+i*bw+(bw)/2; toks=[t for t in a["name"].replace('"','').split() if t not in ("Jr.","Jr","III","II")]; short="Schweickart" if "Schweickart" in a["name"] else toks[-1]
    g.append(f'<text transform="translate({x:.1f},{T+PH+8}) rotate(60)" text-anchor="start">{short}{"*" if a["living"] else ""}</text>')
g.append(f'<text x="{L+PW/2:.0f}" y="{H-12}" font-size="12" fill="#666" text-anchor="middle">* living in {STUDY_YEAR}</text></g>')
rules=[(med_birth, "#c0392b", f"1930 cohort median age at death, from birth: {med_birth:.1f}"),
       (med_30,    "#7d3c98", f"1930 cohort median age at death, given survival to 30: {med_30:.1f}"),
       (apollo_median, "#1e8449", f"Apollo 29 median attained age: {apollo_median}")]
g.append('<g id="rules">')
for v,col,lab in rules: g.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{L+PW}" y2="{Y(v):.1f}" stroke="{col}" stroke-width="2" stroke-dasharray="7,5"/>')
g.append(f'</g><g id="legend" font-size="13"><rect x="{L+4}" y="{T+2}" width="470" height="64" fill="#fff" fill-opacity="0.92" stroke="#ddd"/>')
for k,(v,col,lab) in enumerate(rules):
    y=T+18+k*20; g.append(f'<line x1="{L+10}" y1="{y-4}" x2="{L+36}" y2="{y-4}" stroke="{col}" stroke-width="2" stroke-dasharray="7,5"/><text x="{L+44}" y="{y}" fill="{col}">{lab}</text>')
g.append('</g></svg>')
(HERE/"apollo_ages_vs_cohort_median.svg").write_text("\n".join(g)); print("wrote apollo_ages_vs_cohort_median.svg")
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(14,5)); ax.bar(range(29),[a["age"] for a in order],color=["#4a6fa5" if not a["living"] else "#ffffff" for a in order],edgecolor="#4a6fa5")
    for v,col,lab in rules: ax.axhline(v,color=col,ls="--",label=lab)
    ax.set_xticks(range(29)); ax.set_xticklabels([a["name"].split()[-1] for a in order],rotation=60,ha="right",fontsize=8); ax.legend(fontsize=8); ax.set_title("verify")
    fig.tight_layout(); (HERE/"_verify").mkdir(exist_ok=True); fig.savefig(HERE/"_verify"/"apollo_ages_verify.png",dpi=110); print("verify written")
except ImportError: pass
