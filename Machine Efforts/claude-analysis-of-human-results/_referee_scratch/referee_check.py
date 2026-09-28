#!/usr/bin/env python3
"""Referee scratch (research-statistician, 2026-09-07). Independent parse of [AUTHOR]'s .h files,
independent recompute of the real-Apollo numbers, TSV percentiles with point masses,
closed-form hypergeometric checks, conditional vitality test, and the E-deltas
(per-birth-cohort tables, left truncation). Reads Human Efforts read-only."""
import re, math, csv, bisect, sys
from pathlib import Path
from collections import Counter
from math import comb, log, exp, sqrt

BASE = Path(".")
MC   = BASE/"Human Efforts/scripts/Astronaut MC"
SSA_CSV = BASE/"Human Efforts/Manually Compiled Data/Third Party/US Social Security/Actuarial Study 120/CohLifeTables_M_Alt2_TR2024.csv"
MAN  = BASE/"Human Efforts/Manually Compiled Data/Apollo Astronaut Data"
ENR  = BASE/"Machine Efforts/Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data/Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv"
STUDY, SEL = 2026, 30

# ---------------------------------------------------------------- my own .h parser (line-based, not regex-over-file)
def parse_h(path):
    out = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s.startswith('{"'):
            continue
        m = re.match(r'\{"((?:\\.|[^"\\])*)"\s*,\s*(.*?)\}\s*,?$', s)
        assert m, s
        name = m.group(1).replace('\\"', '"')
        f = [x.strip() for x in m.group(2).split(',')]
        assert len(f) == 8, (name, f)
        b, d = int(f[0]), int(f[1])
        bo = [x == 'true' for x in f[2:8]]
        assert all(x in ('true', 'false') for x in f[2:8])
        out.append(dict(name=name, birth=b, death=d, lunar=bo[0], stroll=bo[1], leo=bo[2],
                        trainAcc=bo[3], hit80=bo[4], sg=bo[5]))
    return out

def parse_ssa_h(path):
    t = {}
    for line in path.read_text().splitlines():
        m = re.match(r'\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}', line)
        if m: t[int(m.group(1))] = int(m.group(2))
    return t

def load_csv_tables():
    tabs = {}
    with open(SSA_CSV, newline='') as f:
        for row in csv.reader(f):
            if len(row) > 3 and row[0].isdigit() and row[1].isdigit():
                tabs.setdefault(int(row[0]), {})[int(row[1])] = int(row[3])
    return tabs

apollo = parse_h(MC/"apolloData.h")
other  = parse_h(MC/"nasaNonApolloAstroPre1970.h")
ssa_h  = parse_ssa_h(MC/"1930CohortSSAData.h")
tabs   = load_csv_tables()
assert len(apollo) == 29 and len(other) == 44, (len(apollo), len(other))
# header vs CSV agreement for 1930
mism = [a for a in range(0, 120) if ssa_h.get(a) != tabs[1930].get(a)]
print(f"[SSA] 1930CohortSSAData.h vs TR2024 CSV row 1930: {'IDENTICAL ages 0-119' if not mism else 'MISMATCH at ages '+str(mism)}")

def age(a): return (a['death'] - a['birth']) if a['death'] else (STUDY - a['birth'])
def H(tab, a0, a1):  # cumulative reference hazard from exact age a0 to a1
    return -log(tab[a1] / tab[a0])

# ---------------------------------------------------------------- real Apollo, independently
def cohort_stats(people, tab=tabs[1930]):
    O = sum(1 for a in people if a['death'])
    E = sum(H(tab, SEL, age(a)) for a in people)
    h = sum(1 for a in people if a['hit80'])
    g = sum(1 for a in people if a['hit80'] and a['sg'])
    ages = sorted(age(a) for a in people)
    med = ages[len(ages)//2]
    return O, E, O/E, h, g, med, ages

O, E, S, h80, g, med, ages = cohort_stats(apollo)
print(f"[REAL Apollo-29, my parser] observed={O} expected={E:.6f} SMR={S:.6f} hit80={h80} grandpa={g} median(sorted[14])={med}")
print(f"   sorted ages: {ages}")
print(f"   ages[13],[14],[15] = {ages[13]},{ages[14]},{ages[15]}")
# internal consistency of the hitEighty flag vs computed age
bad = [a['name'] for a in apollo+other if a['hit80'] != (age(a) >= 80)]
print(f"[FLAG CHECK] hitEighty == (age>=80) for all 73: {'yes' if not bad else 'NO: '+str(bad)}")
bad = [a['name'] for a in apollo+other if a['sg'] and not a['hit80']]
print(f"[FLAG CHECK] spaceGrandpa implies hitEighty: {'yes' if not bad else 'NO: '+str(bad)}")
bad = [a['name'] for a in apollo+other if a['trainAcc'] and not (a['death'] and a['death'] <= 1970)]
print(f"[FLAG CHECK] trainAcc implies death<=1970: {'yes' if not bad else 'NO: '+str(bad)}")
bad = [a['name'] for a in apollo+other if (a['death'] and a['death'] <= 1970) and not a['trainAcc']]
print(f"[FLAG CHECK] death<=1970 implies trainAcc: {'yes' if not bad else 'NO: '+str(bad)}")
print(f"   trainAcc names: {[a['name'] for a in apollo+other if a['trainAcc']]}")
print(f"   any at-risk exit age < 30 (would give negative E)? {[a['name'] for a in apollo+other if age(a) < 30]}")
print(f"   living Apollo: {[a['name'] for a in apollo if not a['death']]}")
print(f"   deaths 1970-1979 anywhere in the 73: {[(a['name'],a['death']) for a in apollo+other if 1970 <= a['death'] <= 1979]}")

pool = [a for a in apollo+other if not a['trainAcc']]
N = len(pool); K_g = sum(1 for a in pool if a['hit80'] and a['sg']); K_h = sum(1 for a in pool if a['hit80']); K_d = sum(1 for a in pool if a['death'])
print(f"[POOL] non-accident pool N={N}; grandpas={K_g}; hit80={K_h}; dead={K_d}; birth years {min(a['birth'] for a in pool)}-{max(a['birth'] for a in pool)}")
others36 = [a for a in other if not a['trainAcc']]
Oo, Eo, So, ho, go, medo, _ = cohort_stats(others36)
Op, Ep, Sp, hp, gp, medp, _ = cohort_stats(pool)
print(f"[NON-APOLLO 36] O={Oo} E={Eo:.4f} SMR={So:.4f} hit80={ho} grandpa={go} median={medo}")
print(f"[POOL 65]       O={Op} E={Ep:.4f} SMR={Sp:.4f} hit80={hp} grandpa={gp} median={medp}")
print(f"   Apollo/non-Apollo SMR ratio = {S/So:.4f}")

# ---------------------------------------------------------------- Byar / Garwood CI on the real Apollo SMR (question 2 of 2: vs general population)
def byar(O, E, z=1.959964):
    lo = (O/E) * (1 - 1/(9*O) - z/(3*sqrt(O)))**3
    hi = ((O+1)/E) * (1 - 1/(9*(O+1)) + z/(3*sqrt(O+1)))**3
    return lo, hi
def pois_cdf(k, mu):
    return sum(exp(-mu) * mu**i / math.factorial(i) for i in range(k+1))
def garwood(O, E, alpha=0.05):
    # lower: mu s.t. P(X>=O)=alpha/2 ; upper: mu s.t. P(X<=O)=alpha/2
    def solve(fn, target, lo, hi):
        for _ in range(200):
            mid = (lo+hi)/2
            if fn(mid) > target: lo = mid
            else: hi = mid
        return (lo+hi)/2
    muL = solve(lambda m: 1 - pois_cdf(O-1, m), alpha/2, 0, 10*O) if O > 0 else 0.0
    # 1-cdf(O-1,m) is increasing in m; we want it == alpha/2 -> use decreasing form
    muL = solve(lambda m: pois_cdf(O-1, m), 1-alpha/2, 0, 10*O)
    muU = solve(lambda m: pois_cdf(O, m), alpha/2, 0, 10*O)
    return muL/E, muU/E
bl, bh = byar(O, E); gl, gh = garwood(O, E)
print(f"[CI vs general pop] Apollo SMR {S:.3f}: Byar 95% [{bl:.3f}, {bh:.3f}] ; exact Poisson (Garwood) [{gl:.3f}, {gh:.3f}]")
bl2, bh2 = byar(Oo, Eo); print(f"   non-Apollo-36 SMR {So:.3f}: Byar 95% [{bl2:.3f}, {bh2:.3f}]")
bl3, bh3 = byar(Op, Ep); print(f"   pool-65 SMR {Sp:.3f}: Byar 95% [{bl3:.3f}, {bh3:.3f}]")

# ---------------------------------------------------------------- TSV
rows = []; seed = None
with open(MC/"astronaut-monte-carlo-results.tsv") as f:
    for line in f:
        if line.startswith('#'):
            seed = int(re.search(r'(\d+)', line).group(1)); continue
        if not line.strip() or line.startswith('Deck'): continue
        i, gg, hh, mm, ss = line.rstrip('\n').split('\t')
        rows.append((int(i), int(gg), int(hh), int(mm), float(ss)))
n = len(rows)
idx = [r[0] for r in rows]
print(f"[TSV] rows={n:,} seed={seed}; indices contiguous 0..{n-1}: {idx == list(range(n))}")
smr = [r[4] for r in rows]; G = [r[1] for r in rows]; Hh = [r[2] for r in rows]; M = [r[3] for r in rows]
ss = sorted(smr)
print(f"[TSV SMR] min {ss[0]:.6f} p1 {ss[n//100]:.4f} p5 {ss[n//20]:.4f} p25 {ss[n//4]:.4f} median {ss[n//2]:.6f} mean {sum(smr)/n:.6f} p75 {ss[3*n//4]:.4f} p95 {ss[19*n//20]:.4f} p99 {ss[99*n//100]:.4f} max {ss[-1]:.6f}")
mu = sum(smr)/n; sd = sqrt(sum((x-mu)**2 for x in smr)/(n-1))
print(f"   SD {sd:.4f}; decks with SMR >= 1: {sum(1 for x in smr if x >= 1.0)}")
le = bisect.bisect_right(ss, S); lt = bisect.bisect_left(ss, S)
print(f"   real SMR {S:.6f}: P(<=)={le/n:.4%}  P(<)={lt/n:.4%}  ties={le-lt}  two-sided p (2*min tail) = {2*min(le/n, 1-lt/n):.3f}; MC SE of the percentile = {sqrt(0.4264*0.5736/n):.4%}")
for name, vals, real in (("grandpa", G, g), ("hit80", Hh, h80), ("median age", M, med)):
    c = Counter(vals)
    ple = sum(v for k, v in c.items() if k <= real)/n; plt_ = sum(v for k, v in c.items() if k < real)/n; peq = c[real]/n
    print(f"[TSV {name}] real={real}: P(<=)={ple:.4%} P(<)={plt_:.4%} P(=)={peq:.4%} P(>=)={1-plt_:.4%} P(>)={1-ple:.4%}")
    print(f"   distribution: {sorted(c.items())}")

# ---------------------------------------------------------------- closed-form hypergeometric vs MC
def hyper_pmf(k, Kp, Np, nd): return comb(Kp, k)*comb(Np-Kp, nd-k)/comb(Np, nd)
for name, vals, Kp, real in (("grandpa", G, K_g, g), ("hit80", Hh, K_h, h80)):
    c = Counter(vals); chi = 0.0; lines = []
    for k in range(0, 30):
        p = hyper_pmf(k, Kp, N, 29); expc = p*n; obs = c.get(k, 0)
        if expc >= 5: chi += (obs-expc)**2/expc
        if expc > 0.5 or obs: lines.append(f"{k}:{obs}/{expc:.0f}")
    pge = sum(hyper_pmf(k, Kp, N, 29) for k in range(real, 30)); pgt = sum(hyper_pmf(k, Kp, N, 29) for k in range(real+1, 30)); ple = sum(hyper_pmf(k, Kp, N, 29) for k in range(0, real+1))
    print(f"[HYPERGEOM {name}] K={Kp} of N={N}, draw 29; mean={29*Kp/N:.3f}; exact P(>= {real})={pge:.4%} P(> {real})={pgt:.4%} P(<= {real})={ple:.4%}")
    print(f"   MC obs / exact expected per bin: {' '.join(lines)}")
    print(f"   chi-square (bins with expected>=5) = {chi:.2f}")

# ---------------------------------------------------------------- vitality given survival (grandpa rate among hit-80)
r_real = g/h80
byh = Counter(); byh_ge = Counter()
for gg, hh in zip(G, Hh):
    byh[hh] += 1
    if gg >= 19: byh_ge[hh] += 1
print(f"[VITALITY | h=22] decks with h=22: {byh[22]:,}; of those g>=19: {byh_ge[22]:,} -> P(g>=19 | h=22) = {byh_ge[22]/byh[22]:.4%}")
pf = sum(hyper_pmf(k, K_g, K_h, 22) for k in range(19, 23))
print(f"   Fisher/hypergeometric exact: {K_g} grandpas among {K_h} hit-80 in pool; Apollo 22 hit-80 -> P(X>=19) = {pf:.4%}; P(X>=20)={sum(hyper_pmf(k, K_g, K_h, 22) for k in range(20,23)):.4%}; P(X>=21)={sum(hyper_pmf(k, K_g, K_h, 22) for k in range(21,23)):.4%}")
print(f"   2x2: Apollo {g}/{h80} = {r_real:.3f} ; non-Apollo {go}/{ho} = {go/ho:.3f}")
fr = sum(1 for gg, hh in zip(G, Hh) if hh and gg/hh >= r_real - 1e-12)/n
print(f"   unconditional: P(deck g/h >= {r_real:.4f}) = {fr:.4%}")

# ---------------------------------------------------------------- E deltas: per-birth-cohort tables, left truncation
def sel_year_map():
    m = {}
    for fn in ("Lunar Astronauts-Apollo Astronauts.tsv", "Non-Lunar Astronauts-LEO-Only Apollo.tsv"):
        with open(MAN/fn, newline='') as f:
            rd = csv.reader(f, delimiter='\t'); next(rd)
            for row in rd:
                m[row[0].strip()] = int(row[3].split()[-1])
    with open(ENR, newline='') as f:
        rd = csv.reader(f, delimiter='\t'); next(rd)
        for row in rd:
            m[row[0].strip()] = int(row[3][:4])
    return m
selmap = sel_year_map()
missing = [a['name'] for a in apollo+other if a['name'] not in selmap]
print(f"[SELECTION YEARS] names not matched: {missing}")

def E_variants(people):
    e0 = sum(H(tabs[1930], SEL, age(a)) for a in people)
    e_co = sum(H(tabs[a['birth']], SEL, age(a)) for a in people)
    e_tr70 = sum(H(tabs[1930], max(SEL, 1970 - a['birth']), age(a)) for a in people)
    e_sel = sum(H(tabs[1930], max(SEL, selmap[a['name']] - a['birth']), age(a)) for a in people)
    e_co_tr70 = sum(H(tabs[a['birth']], max(SEL, 1970 - a['birth']), age(a)) for a in people)
    return e0, e_co, e_tr70, e_sel, e_co_tr70
for label, ppl in (("Apollo-29", apollo), ("non-Apollo-36", others36), ("pool-65", pool)):
    Ox = sum(1 for a in ppl if a['death'])
    e0, eco, etr, esel, ecotr = E_variants(ppl)
    print(f"[E VARIANTS {label}] O={Ox}  E(1930 table, from 30)={e0:.3f} SMR={Ox/e0:.4f} | per-birth-cohort tables: E={eco:.3f} SMR={Ox/eco:.4f} ({(Ox/eco)/(Ox/e0)-1:+.1%}) | left-truncate at 1970: E={etr:.3f} SMR={Ox/etr:.4f} ({(Ox/etr)/(Ox/e0)-1:+.1%}) | start at selection: E={esel:.3f} SMR={Ox/esel:.4f} ({(Ox/esel)/(Ox/e0)-1:+.1%}) | cohort+trunc1970: E={ecotr:.3f} SMR={Ox/ecotr:.4f} ({(Ox/ecotr)/(Ox/e0)-1:+.1%})")
print(f"   Apollo birth years: {sorted(Counter(a['birth'] for a in apollo).items())}; mean {sum(a['birth'] for a in apollo)/29:.1f}")
print(f"   H(30->80) by birth cohort: " + ", ".join(f"{y}:{H(tabs[y],30,80):.3f}" for y in (1921,1923,1925,1928,1930,1932,1935,1937,1940,1942)))
# race note: no white-male cohort table in the folder; not computable here.
# age-convention note: year-difference age is unbiased for exact age at death (u_d - u_b has mean 0); living: 2026-b overstates exact age at a June-1 epoch by ~0.08y
liv = [a for a in apollo if not a['death']]
dE = sum(H(tabs[1930], age(a)-1, age(a)) for a in liv)
print(f"   living Apollo n={len(liv)}; one full year of hazard at their current ages sums to {dE:.3f} (so a ~0.1-0.2y epoch shift moves E by ~{0.15*dE:.3f})")
