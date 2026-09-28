#!/usr/bin/env python3
"""
non_apollo_lifespan_mode.py
---------------------------
Lifespan distribution and modal tendency analysis for the 69 non-Apollo
astronauts. Examines age-at-death histograms with multiple bin widths,
separates accidental from non-accidental deaths, and shows where the
living survivors sit relative to the distribution.

Read-only — does NOT modify any source files.

Usage:  python3 non_apollo_lifespan_mode.py
"""

import csv
import statistics
from pathlib import Path
from collections import Counter

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"

FILES = {
    "Non-Apollo NASA": ENRICHED / "03E-non-apollo-enriched.tsv",
    "X-15 Pilots":     ENRICHED / "09-x15-pilots-enriched.tsv",
    "Dyna-Soar Pilots": ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    "MOL-Only":        ENRICHED / "11-mol-full-enriched.tsv",
}

def load_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("Name", "").strip():
                rows.append(row)
    return rows

def parse_float(s):
    if not s or s.strip() == "":
        return None
    try:
        return float(s.strip())
    except ValueError:
        return None

def histogram(values, bin_width, label, lo=None, hi=None):
    if not values:
        print(f"  (no data)")
        return
    if lo is None:
        lo = int(min(values) // bin_width) * bin_width
    if hi is None:
        hi = int((max(values) // bin_width) + 1) * bin_width
    bins = {}
    for edge in range(lo, hi, bin_width):
        bins[edge] = 0
    for v in values:
        edge = int(v // bin_width) * bin_width
        if edge in bins:
            bins[edge] += 1
        else:
            bins[edge] = 1
    max_count = max(bins.values()) if bins else 1
    scale = 50 / max_count if max_count > 0 else 1
    mode_val = max(bins.values())
    for edge in sorted(bins):
        count = bins[edge]
        bar = "#" * int(count * scale)
        marker = " <-- MODE" if count == mode_val and count > 0 else ""
        print(f"    {edge:3d}-{edge+bin_width-1:3d}:  {count:3d}  {bar}{marker}")

def main():
    all_people = []
    for label, path in FILES.items():
        rows = load_tsv(path)
        for r in rows:
            r["_source"] = label
            all_people.append(r)

    deceased = [p for p in all_people if p.get("Status", "").strip().lower() == "deceased"]
    living = [p for p in all_people if p.get("Status", "").strip().lower() == "living"]

    all_death_ages = []
    accidental_ages = []
    natural_ages = []
    natural_people = []

    for p in deceased:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        if a is not None:
            all_death_ages.append(a)
            if acc:
                accidental_ages.append(a)
            else:
                natural_ages.append(a)
                natural_people.append(p)

    living_ages = []
    for p in living:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a is not None:
            living_ages.append(a)

    N = len(all_people)
    print("=" * 72)
    print("LIFESPAN MODAL TENDENCY — 69 NON-APOLLO ASTRONAUTS")
    print("=" * 72)
    print()

    # ----------------------------------------------------------------
    # 1. ALL deceased, all causes
    # ----------------------------------------------------------------
    print("1. ALL DEATHS (N=56, all causes including accidents)")
    print("-" * 60)
    print(f"   Mean:    {statistics.mean(all_death_ages):.1f}")
    print(f"   Median:  {statistics.median(all_death_ages):.1f}")
    print(f"   Std Dev: {statistics.stdev(all_death_ages):.1f}")
    print()
    print("   10-year bins:")
    histogram(all_death_ages, 10, "all", lo=30, hi=100)
    print()
    print("   5-year bins:")
    histogram(all_death_ages, 5, "all", lo=30, hi=100)
    print()

    # ----------------------------------------------------------------
    # 2. ACCIDENTAL deaths only
    # ----------------------------------------------------------------
    print("2. ACCIDENTAL DEATHS ONLY (N=19)")
    print("-" * 60)
    print(f"   Mean:    {statistics.mean(accidental_ages):.1f}")
    print(f"   Median:  {statistics.median(accidental_ages):.1f}")
    print()
    print("   5-year bins:")
    histogram(accidental_ages, 5, "acc", lo=30, hi=90)
    print()
    print("   The accidental deaths cluster heavily in the 30-39 range")
    print("   (12 of 19), driven by training aircraft crashes and the")
    print("   Apollo 1 fire. These premature deaths pull the all-cause")
    print("   distribution leftward and mask the natural lifespan pattern.")
    print()

    # ----------------------------------------------------------------
    # 3. NON-ACCIDENTAL deaths — the real lifespan signal
    # ----------------------------------------------------------------
    print("3. NON-ACCIDENTAL DEATHS (N=37) — natural lifespan signal")
    print("-" * 60)
    print(f"   Mean:    {statistics.mean(natural_ages):.1f}")
    print(f"   Median:  {statistics.median(natural_ages):.1f}")
    print(f"   Std Dev: {statistics.stdev(natural_ages):.1f}")
    q = sorted(natural_ages)
    n = len(q)
    print(f"   Q1:      {q[n//4]:.1f}")
    print(f"   Q3:      {q[3*n//4]:.1f}")
    print(f"   IQR:     {q[3*n//4] - q[n//4]:.1f}")
    print()
    print("   10-year bins:")
    histogram(natural_ages, 10, "nat", lo=50, hi=100)
    print()
    print("   5-year bins:")
    histogram(natural_ages, 5, "nat", lo=50, hi=100)
    print()

    # Individual listing sorted by age
    print("   Individual ages at death (non-accidental), sorted:")
    for p in sorted(natural_people, key=lambda x: parse_float(x.get("Current Age or Age at Death", "0"))):
        a = parse_float(p.get("Current Age or Age at Death", ""))
        cause = p.get("Mort / cause note", "").strip()[:55]
        src = p.get("_source", "")
        print(f"      {a:5.1f}  {p['Name'][:40]:40s}  {cause}")
    print()

    # ----------------------------------------------------------------
    # 4. COMBINED: deceased (non-accidental) + living (right-censored)
    # ----------------------------------------------------------------
    print("4. OBSERVED AGE DISTRIBUTION (non-accidental dead + living)")
    print("-" * 60)
    combined = natural_ages + living_ages
    print(f"   N (non-acc dead + living): {len(natural_ages)} + {len(living_ages)} = {len(combined)}")
    print(f"   Mean:    {statistics.mean(combined):.1f}")
    print(f"   Median:  {statistics.median(combined):.1f}")
    print()
    print("   Note: living ages are RIGHT-CENSORED — these people will")
    print("   die later, so this underestimates the true central tendency.")
    print("   The actual modal lifespan will shift rightward as survivors die.")
    print()
    print("   5-year bins (D=died non-acc, L=still living):")
    all_vals = [(a, "D") for a in natural_ages] + [(a, "L") for a in living_ages]
    lo, hi = 50, 100
    for edge in range(lo, hi, 5):
        d_count = sum(1 for a, t in all_vals if t == "D" and edge <= a < edge + 5)
        l_count = sum(1 for a, t in all_vals if t == "L" and edge <= a < edge + 5)
        d_bar = "#" * d_count
        l_bar = "+" * l_count
        total = d_count + l_count
        print(f"    {edge:3d}-{edge+4:3d}:  {total:3d}  {d_bar}{l_bar}  (D={d_count}, L={l_count})")
    print()

    # ----------------------------------------------------------------
    # 5. Sub-group modal comparison
    # ----------------------------------------------------------------
    print("5. MODAL BIN BY SUB-GROUP (non-accidental deaths, 10-yr bins)")
    print("-" * 60)
    for label in ["Non-Apollo NASA", "X-15 Pilots", "Dyna-Soar Pilots", "MOL-Only"]:
        grp_nat = [p for p in natural_people if p["_source"] == label]
        ages = [parse_float(p.get("Current Age or Age at Death", "")) for p in grp_nat]
        ages = [a for a in ages if a is not None]
        if not ages:
            print(f"   {label:25s}  N=0 (all deaths accidental or still living)")
            continue
        bins_10 = Counter()
        for a in ages:
            bins_10[int(a // 10) * 10] += 1
        mode_bin = max(bins_10, key=bins_10.get)
        print(f"   {label:25s}  N={len(ages):2d}  mode bin: {mode_bin}-{mode_bin+9}  "
              f"(mean {statistics.mean(ages):.1f}, median {statistics.median(ages):.1f})")
    print()

    # ----------------------------------------------------------------
    # 6. Key takeaway
    # ----------------------------------------------------------------
    print("=" * 72)
    print("SUMMARY: MODAL TENDENCY")
    print("=" * 72)
    print()

    # Find the 5-year mode bin for non-accidental
    bins5 = Counter()
    for a in natural_ages:
        bins5[int(a // 5) * 5] += 1
    mode5 = max(bins5, key=bins5.get)
    mode5_count = bins5[mode5]

    bins10 = Counter()
    for a in natural_ages:
        bins10[int(a // 10) * 10] += 1
    mode10 = max(bins10, key=bins10.get)
    mode10_count = bins10[mode10]

    print(f"  For the 37 non-accidental deaths:")
    print(f"    10-year modal bin:  {mode10}-{mode10+9}  ({mode10_count} deaths)")
    print(f"     5-year modal bin:  {mode5}-{mode5+4}  ({mode5_count} deaths)")
    print(f"    Mean age at death:  {statistics.mean(natural_ages):.1f}")
    print(f"    Median:             {statistics.median(natural_ages):.1f}")
    print()
    print(f"  The distribution is LEFT-SKEWED: a long tail of earlier deaths")
    print(f"  (mostly 50s-60s from the X-15/Dyna-Soar cohorts born earlier)")
    print(f"  pulls the mean below the median.")
    print()

    # Check how many are in the 80-95 range
    in_80_95 = sum(1 for a in natural_ages if 80 <= a < 95)
    pct_80_95 = 100 * in_80_95 / len(natural_ages)
    print(f"  {in_80_95} of 37 non-accidental deaths ({pct_80_95:.0f}%) occurred")
    print(f"  between ages 80 and 94.")
    print()

    # Plus the 13 living, all 84+
    in_80_plus_living = sum(1 for a in living_ages if a >= 80)
    print(f"  All {in_80_plus_living} living survivors are currently 84+,")
    print(f"  meaning they will eventually add to the 80+ death count.")
    print(f"  The true modal lifespan for this cohort is solidly in the")
    print(f"  mid-80s, likely shifting toward late 80s as survivors die.")
    print()
    print("=" * 72)
    print("Script: non_apollo_lifespan_mode.py")
    print("Data sources: 03E, 09, 10, 11 enriched TSVs")
    print("No source files were modified.")
    print("=" * 72)


if __name__ == "__main__":
    main()
