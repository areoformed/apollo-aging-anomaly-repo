#!/usr/bin/env python3
"""Independent Monte Carlo (research-statistician, 2026-09-07). Different language, different RNG
(numpy PCG64), direct uniform 29-subset sampling of the 65-person non-accident pool (which is what
her shuffle-and-skip procedure samples). Baseline + sensitivity variants. Reads Human Efforts read-only."""
import re, csv, sys, time
from math import log
from pathlib import Path
import numpy as np

BASE = Path(".")
MC   = BASE/"Human Efforts/scripts/Astronaut MC"
SSA_CSV = BASE/"Human Efforts/Manually Compiled Data/Third Party/US Social Security/Actuarial Study 120/CohLifeTables_M_Alt2_TR2024.csv"
MAN  = BASE/"Human Efforts/Manually Compiled Data/Apollo Astronaut Data"
ENR  = BASE/"Machine Efforts/Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data/Final - Analysis - Enriched Datasets/03E-non-apollo-enriched.tsv"
STUDY, SEL = 2026, 30
ROUNDS = 1_000_000; CHUNK = 50_000

def parse_h(path):
    out = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s.startswith('{"'): continue
        m = re.match(r'\{"((?:\\.|[^"\\])*)"\s*,\s*(.*?)\}\s*,?$', s)
        name = m.group(1).replace('\\"', '"'); f = [x.strip() for x in m.group(2).split(',')]
        bo = [x == 'true' for x in f[2:8]]
        out.append(dict(name=name, birth=int(f[0]), death=int(f[1]), trainAcc=bo[3], hit80=bo[4], sg=bo[5], apollo=None))
    return out
def tables():
    t = {}
    with open(SSA_CSV, newline='') as f:
        for row in csv.reader(f):
            if len(row) > 3 and row[0].isdigit() and row[1].isdigit():
                t.setdefault(int(row[0]), {})[int(row[1])] = int(row[3])
    return t
def groups():
    gmap = {}
    for fn in ("Lunar Astronauts-Apollo Astronauts.tsv", "Non-Lunar Astronauts-LEO-Only Apollo.tsv"):
        with open(MAN/fn, newline='') as f:
            rd = csv.reader(f, delimiter='\t'); next(rd)
            for row in rd: gmap[row[0].strip()] = {'Mercury Seven':1,'New Nine':2,'The Fourteen':3,'The Scientists':4,'The Original Nineteen':5}[row[1].strip()]
    with open(ENR, newline='') as f:
        rd = csv.reader(f, delimiter='\t'); next(rd)
        for row in rd: gmap[row[0].strip()] = int(re.search(r'Group\s+(\d+)', row[1]).group(1))
    return gmap

ap = parse_h(MC/"apolloData.h"); ot = parse_h(MC/"nasaNonApolloAstroPre1970.h")
for a in ap: a['apollo'] = True
for a in ot: a['apollo'] = False
T = tables(); gmap = groups()
pool = [a for a in ap+ot if not a['trainAcc']]
for a in pool: a['group'] = gmap[a['name']]
print(f"pool N={len(pool)}; groups: {sorted(set((a['group']) for a in pool))}; Apollo groups: {sorted(set(a['group'] for a in pool if a['apollo']))}")
print(f"Group 6+7 members in pool (not Apollo): {sum(1 for a in pool if a['group']>=6)}")

def age(a): return (a['death']-a['birth']) if a['death'] else (STUDY-a['birth'])
def H(tab, a0, a1): return -log(tab[a1]/tab[a0])
dead = np.array([1.0 if a['death'] else 0.0 for a in pool])
E30  = np.array([H(T[1930], SEL, age(a)) for a in pool])
Eco  = np.array([H(T[a['birth']], SEL, age(a)) for a in pool])
Etr  = np.array([H(T[1930], max(SEL, 1970-a['birth']), age(a)) for a in pool])
Ecotr= np.array([H(T[a['birth']], max(SEL, 1970-a['birth']), age(a)) for a in pool])
h80  = np.array([1 if a['hit80'] else 0 for a in pool]); gp = np.array([1 if (a['hit80'] and a['sg']) else 0 for a in pool])
ages = np.array([age(a) for a in pool], dtype=np.int64)
isap = np.array([a['apollo'] for a in pool])
def real(Evec, mask=None):
    m = isap if mask is None else (isap & mask)
    return dead[m].sum()/Evec[m].sum()
real_smr = real(E30); real_g = int(gp[isap].sum()); real_h = int(h80[isap].sum()); real_med = int(np.sort(ages[isap])[14])
print(f"real Apollo (numpy path): SMR={real_smr:.6f} g={real_g} h={real_h} median={real_med}; SMR per-cohort={real(Eco):.6f} trunc1970={real(Etr):.6f} cohort+trunc={real(Ecotr):.6f}")

def run(Evec, member_mask, seed, label):
    idx_pool = np.flatnonzero(member_mask); Np = len(idx_pool)
    rng = np.random.default_rng(seed)
    n_le = n_lt = 0; g_ge = h_ge = m_ge = 0; g_eq = 0; rate_ge = 0; cond_n = cond_ge = 0; smr_max = 0; smr_min = 9; ssum = 0.0
    rs = dead[idx_pool].sum()/Evec[idx_pool & isap].sum() if False else dead[isap & member_mask].sum()/Evec[isap & member_mask].sum()
    rr = real_g/real_h
    t0 = time.time()
    for start in range(0, ROUNDS, CHUNK):
        keys = rng.random((CHUNK, Np)); sel = np.argsort(keys, axis=1)[:, :29]; pick = idx_pool[sel]
        d = dead[pick].sum(1); e = Evec[pick].sum(1); s = d/e
        gg = gp[pick].sum(1); hh = h80[pick].sum(1); med = np.sort(ages[pick], axis=1)[:, 14]
        n_le += int((s <= rs).sum()); n_lt += int((s < rs).sum()); smr_max = max(smr_max, s.max()); smr_min = min(smr_min, s.min()); ssum += s.sum()
        g_ge += int((gg >= real_g).sum()); g_eq += int((gg == real_g).sum()); h_ge += int((hh >= real_h).sum()); m_ge += int((med >= real_med).sum())
        rate_ge += int(((gg/hh) >= rr - 1e-12).sum()); c = hh == real_h; cond_n += int(c.sum()); cond_ge += int((gg[c] >= real_g).sum())
    n = ROUNDS
    print(f"[{label}] pool={Np} realSMR={rs:.4f}: P(SMR<=real)={n_le/n:.4%} P(<)={n_lt/n:.4%} mean={ssum/n:.4f} min={smr_min:.4f} max={smr_max:.4f} | P(g>={real_g})={g_ge/n:.4%} P(g={real_g})={g_eq/n:.4%} P(h>={real_h})={h_ge/n:.4%} P(med>={real_med})={m_ge/n:.4%} | P(g/h>={rr:.4f})={rate_ge/n:.4%} P(g>=19|h=22)={cond_ge/max(cond_n,1):.4%} ({time.time()-t0:.0f}s)")

allm = np.ones(len(pool), dtype=bool)
run(E30,  allm, 20260907, "baseline, 1930 table, from age 30")
run(E30,  allm, 8641,     "baseline, second seed")
run(Eco,  allm, 20260907, "per-birth-cohort tables")
run(Etr,  allm, 20260907, "left-truncated at 1970")
run(Ecotr,allm, 20260907, "per-cohort + truncated 1970")
g15 = np.array([a['group'] <= 5 for a in pool])
run(E30,  g15,  20260907, "pool restricted to Groups 1-5 survivors")
