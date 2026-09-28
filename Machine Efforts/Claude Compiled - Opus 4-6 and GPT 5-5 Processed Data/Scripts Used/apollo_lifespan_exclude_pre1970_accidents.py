#!/usr/bin/env python3
"""
apollo_lifespan_exclude_pre1970_accidents.py
--------------------------------------------
Lifespan statistics for the 29 Apollo 7-17 astronauts, applying the same
pre-1970 accidental death exclusion used on the non-Apollo cohort.
(No Apollo 7-17 crewmember died in a pre-1970 accident, so all 29 remain.)

Reports mean, median, and modal age at death / current age.

Read-only — does NOT modify any source files.

Usage:  python3 apollo_lifespan_exclude_pre1970_accidents.py
"""

import csv
import statistics
from pathlib import Path
from collections import Counter
from datetime import datetime

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"

FILES = {
    "Lunar Apollo (8-17)":     ENRICHED / "07E-lunar-enriched.tsv",
    "Non-Lunar Apollo (7, 9)": ENRICHED / "08E-non-lunar-apollo-enriched.tsv",
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

def parse_date(s):
    if not s or s.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None

def histogram_dual(dead_ages, living_ages, bin_width, lo, hi):
    all_vals = [(a, "D") for a in dead_ages] + [(a, "L") for a in living_ages]
    max_count = 0
    bins = {}
    for edge in range(lo, hi, bin_width):
        d = sum(1 for a, t in all_vals if t == "D" and edge <= a < edge + bin_width)
        l = sum(1 for a, t in all_vals if t == "L" and edge <= a < edge + bin_width)
        bins[edge] = (d, l)
        if d + l > max_count:
            max_count = d + l
    mode_val = max(d + l for d, l in bins.values())
    for edge in sorted(bins):
        d, l = bins[edge]
        total = d + l
        d_bar = "#" * d
        l_bar = "+" * l
        marker = " <-- MODE" if total == mode_val and total > 0 else ""
        print(f"    {edge:3d}-{edge+bin_width-1:3d}:  {total:3d}  {d_bar}{l_bar}  (D={d}, L={l}){marker}")

def main():
    all_people = []
    group_counts = {}
    for label, path in FILES.items():
        rows = load_tsv(path)
        group_counts[label] = len(rows)
        for r in rows:
            r["_source"] = label
            all_people.append(r)

    N = len(all_people)
    print("=" * 72)
    print("LIFESPAN ANALYSIS: 29 APOLLO 7-17 ASTRONAUTS")
    print("(After excluding pre-1970 accidental deaths)")
    print("=" * 72)
    print()

    # Check for pre-1970 accidental deaths
    excluded = []
    retained = []
    for p in all_people:
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        dod = parse_date(p.get("Date of Death", ""))
        if acc and dod and dod.year < 1970:
            excluded.append(p)
        else:
            retained.append(p)

    print(f"Pre-1970 accidental deaths: {len(excluded)}")
    if excluded:
        for p in excluded:
            print(f"  {p['Name']} — {p.get('Date of Death', '?')}")
    else:
        print("  (None — all 29 retained)")
    print()

    print(f"SOURCE BREAKDOWN")
    print("-" * 40)
    for label, count in group_counts.items():
        print(f"  {label:30s}  {count:3d}")
    print(f"  {'TOTAL':30s}  {N:3d}")
    print()

    # Separate into categories
    living = []
    deceased_acc = []
    deceased_natural = []

    for p in retained:
        status = p.get("Status", "").strip().lower()
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        if status == "living":
            living.append(p)
        elif acc:
            deceased_acc.append(p)
        else:
            deceased_natural.append(p)

    print(f"VITAL STATUS")
    print("-" * 40)
    print(f"  Living:                          {len(living):3d}")
    print(f"  Deceased (non-accidental):        {len(deceased_natural):3d}")
    print(f"  Deceased (accidental, post-1970): {len(deceased_acc):3d}")
    print()

    if deceased_acc:
        print("  Post-1970 accidental deaths (still in pool):")
        for p in sorted(deceased_acc, key=lambda x: x.get("Date of Death", "")):
            name = p["Name"][:42]
            dod = p.get("Date of Death", "?")
            age = parse_float(p.get("Current Age or Age at Death", ""))
            cause = p.get("Mort / cause note", "").strip()[:55]
            print(f"    {dod}  {name:42s}  age {age:.1f}  {cause}")
        print()

    # Extract ages
    living_ages = [parse_float(p.get("Current Age or Age at Death", ""))
                   for p in living]
    living_ages = [a for a in living_ages if a is not None]

    nat_ages = [parse_float(p.get("Current Age or Age at Death", ""))
                for p in deceased_natural]
    nat_ages = [a for a in nat_ages if a is not None]

    acc_ages = [parse_float(p.get("Current Age or Age at Death", ""))
                for p in deceased_acc]
    acc_ages = [a for a in acc_ages if a is not None]

    all_deceased_ages = nat_ages + acc_ages
    all_ages = nat_ages + acc_ages + living_ages

    # ── A. All retained ──
    print("─" * 72)
    print("A. ALL 29 (dead + living, all causes)")
    print("─" * 72)
    print(f"   N:       {len(all_ages)}")
    print(f"   Mean:    {statistics.mean(all_ages):.1f}")
    print(f"   Median:  {statistics.median(all_ages):.1f}")
    bins5a = Counter()
    for a in all_ages:
        bins5a[int(a // 5) * 5] += 1
    mode5a = max(bins5a, key=bins5a.get)
    print(f"   Mode:    {mode5a}-{mode5a+4} bin ({bins5a[mode5a]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5a.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5a else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # ── B. Deceased non-accidental only ──
    print("─" * 72)
    print("B. DECEASED, NON-ACCIDENTAL ONLY")
    print("─" * 72)
    print(f"   N:       {len(nat_ages)}")
    print(f"   Mean:    {statistics.mean(nat_ages):.1f}")
    print(f"   Median:  {statistics.median(nat_ages):.1f}")
    if len(nat_ages) > 1:
        print(f"   Std Dev: {statistics.stdev(nat_ages):.1f}")
    bins5b = Counter()
    for a in nat_ages:
        bins5b[int(a // 5) * 5] += 1
    mode5b = max(bins5b, key=bins5b.get)
    print(f"   Mode:    {mode5b}-{mode5b+4} bin ({bins5b[mode5b]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5b.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5b else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # ── C. All deceased (incl post-1970 accidents) ──
    print("─" * 72)
    print("C. ALL DECEASED IN POOL (incl. post-1970 accidents)")
    print("─" * 72)
    print(f"   N:       {len(all_deceased_ages)}")
    print(f"   Mean:    {statistics.mean(all_deceased_ages):.1f}")
    print(f"   Median:  {statistics.median(all_deceased_ages):.1f}")
    if len(all_deceased_ages) > 1:
        print(f"   Std Dev: {statistics.stdev(all_deceased_ages):.1f}")
    bins5c = Counter()
    for a in all_deceased_ages:
        bins5c[int(a // 5) * 5] += 1
    mode5c = max(bins5c, key=bins5c.get)
    print(f"   Mode:    {mode5c}-{mode5c+4} bin ({bins5c[mode5c]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5c.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5c else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # ── D. Non-accidental dead + living ──
    combined = nat_ages + living_ages
    print("─" * 72)
    print("D. NON-ACCIDENTAL DEAD + LIVING (right-censored estimate)")
    print("─" * 72)
    print(f"   N:       {len(combined)} ({len(nat_ages)} dead + {len(living)} living)")
    print(f"   Mean:    {statistics.mean(combined):.1f}")
    print(f"   Median:  {statistics.median(combined):.1f}")
    bins5d = Counter()
    for a in combined:
        bins5d[int(a // 5) * 5] += 1
    mode5d = max(bins5d, key=bins5d.get)
    print(f"   Mode:    {mode5d}-{mode5d+4} bin ({bins5d[mode5d]} people)")
    print()
    print("   5-year bins (D=died non-acc, L=living):")
    histogram_dual(nat_ages, living_ages, 5, 50, 100)
    print()

    # ── Individual roster ──
    print("─" * 72)
    print("INDIVIDUAL ROSTER — SORTED BY AGE")
    print("─" * 72)
    roster = sorted(retained, key=lambda p: parse_float(p.get("Current Age or Age at Death", "0")) or 0)
    for p in roster:
        name = p["Name"][:40]
        age = parse_float(p.get("Current Age or Age at Death", ""))
        status = p.get("Status", "?").strip()
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        cause = p.get("Mort / cause note", "").strip()[:40]
        flag = ""
        if status.lower() == "living":
            flag = "(living)"
        elif acc:
            flag = f"(ACCIDENTAL: {cause})"
        else:
            flag = f"({cause})"
        print(f"  {age:5.1f}  {name:40s}  {flag}")
    print()

    # ── Summary table ──
    print("=" * 72)
    print("SUMMARY TABLE — APOLLO 7-17 ASTRONAUTS")
    print("=" * 72)
    print()
    print(f"  {'Measure':<55s} {'Mean':>6s} {'Median':>7s} {'Mode bin':>10s}")
    print(f"  {'-'*55} {'─'*6} {'─'*7} {'─'*10}")
    print(f"  {'A. All 29 (dead+living, all causes)':<55s} "
          f"{statistics.mean(all_ages):6.1f} {statistics.median(all_ages):7.1f} "
          f"  {mode5a}-{mode5a+4}")
    print(f"  {'B. Deceased non-accidental only':<55s} "
          f"{statistics.mean(nat_ages):6.1f} {statistics.median(nat_ages):7.1f} "
          f"  {mode5b}-{mode5b+4}")
    print(f"  {'C. All deceased (incl post-1970 accidents)':<55s} "
          f"{statistics.mean(all_deceased_ages):6.1f} {statistics.median(all_deceased_ages):7.1f} "
          f"  {mode5c}-{mode5c+4}")
    print(f"  {'D. Non-acc dead + living (right-censored)':<55s} "
          f"{statistics.mean(combined):6.1f} {statistics.median(combined):7.1f} "
          f"  {mode5d}-{mode5d+4}")
    print()

    # ── Side-by-side comparison with non-Apollo ──
    print("=" * 72)
    print("SIDE-BY-SIDE: APOLLO vs NON-APOLLO (same methodology)")
    print("=" * 72)
    print()
    print("  Non-Apollo figures (from prior script, N=55 after exclusion):")
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print("  │  Measure                                   Mean  Med  Mode │")
    print("  │  A. All retained (dead+living)             81.2  84.6 85-89│")
    print("  │  B. Deceased non-accidental                80.1  80.7 85-89│")
    print("  │  C. All deceased in pool                   78.3  80.6 85-89│")
    print("  │  D. Non-acc dead + living                  82.9  85.5 85-89│")
    print("  └─────────────────────────────────────────────────────────────┘")
    print()
    print("  Apollo figures (this script, N=29):")
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  A. All 29 (dead+living)                 {statistics.mean(all_ages):5.1f} {statistics.median(all_ages):5.1f} {mode5a}-{mode5a+4} │")
    print(f"  │  B. Deceased non-accidental              {statistics.mean(nat_ages):5.1f} {statistics.median(nat_ages):5.1f} {mode5b}-{mode5b+4} │")
    print(f"  │  C. All deceased in pool                 {statistics.mean(all_deceased_ages):5.1f} {statistics.median(all_deceased_ages):5.1f} {mode5c}-{mode5c+4} │")
    print(f"  │  D. Non-acc dead + living                {statistics.mean(combined):5.1f} {statistics.median(combined):5.1f} {mode5d}-{mode5d+4} │")
    print("  └─────────────────────────────────────────────────────────────┘")
    print()
    print("  Delta (Apollo minus Non-Apollo):")
    na_means = [81.2, 80.1, 78.3, 82.9]
    na_meds  = [84.6, 80.7, 80.6, 85.5]
    ap_means = [statistics.mean(all_ages), statistics.mean(nat_ages),
                statistics.mean(all_deceased_ages), statistics.mean(combined)]
    ap_meds  = [statistics.median(all_ages), statistics.median(nat_ages),
                statistics.median(all_deceased_ages), statistics.median(combined)]
    labels = ["A", "B", "C", "D"]
    for i in range(4):
        dm = ap_means[i] - na_means[i]
        dd = ap_meds[i] - na_meds[i]
        sign_m = "+" if dm >= 0 else ""
        sign_d = "+" if dd >= 0 else ""
        print(f"    {labels[i]}:  mean {sign_m}{dm:.1f},  median {sign_d}{dd:.1f}")
    print()
    print("=" * 72)
    print("Script: apollo_lifespan_exclude_pre1970_accidents.py")
    print("No source files were modified.")
    print("=" * 72)


if __name__ == "__main__":
    main()
