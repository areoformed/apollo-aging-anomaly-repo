#!/usr/bin/env python3
"""
non_apollo_exclude_pre1970_accidents.py
---------------------------------------
Recalculates lifespan statistics for the 69 non-Apollo astronauts after
excluding those killed in accidents before 1970 — i.e. people removed
from the astronaut candidate pool by premature accidental death before
the Apollo program concluded.

Reports mean, median, and modal age at death (or current age for living).

Read-only — does NOT modify any source files.

Usage:  python3 non_apollo_exclude_pre1970_accidents.py
"""

import csv
import statistics
from pathlib import Path
from collections import Counter
from datetime import datetime

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

def parse_date(s):
    if not s or s.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None

def main():
    all_people = []
    for label, path in FILES.items():
        rows = load_tsv(path)
        for r in rows:
            r["_source"] = label
            all_people.append(r)

    print("=" * 72)
    print("LIFESPAN AFTER EXCLUDING PRE-1970 ACCIDENTAL DEATHS")
    print("=" * 72)
    print()

    # Identify pre-1970 accidental deaths
    excluded = []
    retained = []

    for p in all_people:
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        dod = parse_date(p.get("Date of Death", ""))

        if acc and dod and dod.year < 1970:
            excluded.append(p)
        else:
            retained.append(p)

    # Report who was excluded
    print(f"EXCLUDED: {len(excluded)} accidental deaths before 1970")
    print("-" * 72)
    excluded_sorted = sorted(excluded, key=lambda p: p.get("Date of Death", ""))
    for p in excluded_sorted:
        name = p["Name"][:42]
        dod = p.get("Date of Death", "?")
        age = parse_float(p.get("Current Age or Age at Death", ""))
        cause = p.get("Mort / cause note", "").strip()[:50]
        age_str = f"{age:.1f}" if age else "?"
        print(f"  {dod}  {name:42s}  age {age_str:>5s}  {cause}")
    print()

    N = len(retained)
    print(f"RETAINED POOL: {N} astronauts")
    print("=" * 72)
    print()

    # Separate retained into living, deceased-accidental (post-1970), deceased-natural
    living = []
    deceased_acc_post70 = []
    deceased_natural = []

    for p in retained:
        status = p.get("Status", "").strip().lower()
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        if status == "living":
            living.append(p)
        elif acc:
            deceased_acc_post70.append(p)
        else:
            deceased_natural.append(p)

    print(f"  Living:                          {len(living):3d}")
    print(f"  Deceased (non-accidental):        {len(deceased_natural):3d}")
    print(f"  Deceased (accidental, post-1970): {len(deceased_acc_post70):3d}")
    print()

    if deceased_acc_post70:
        print("  Post-1970 accidental deaths (still in pool):")
        for p in sorted(deceased_acc_post70, key=lambda x: x.get("Date of Death", "")):
            name = p["Name"][:42]
            dod = p.get("Date of Death", "?")
            age = parse_float(p.get("Current Age or Age at Death", ""))
            cause = p.get("Mort / cause note", "").strip()[:50]
            print(f"    {dod}  {name:42s}  age {age:.1f}  {cause}")
        print()

    # --- All retained: age at death or current age ---
    all_ages = []
    for p in retained:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a is not None:
            all_ages.append(a)

    print("─" * 72)
    print("A. ALL RETAINED (dead + living, all causes)")
    print("─" * 72)
    print(f"   N:       {len(all_ages)}")
    print(f"   Mean:    {statistics.mean(all_ages):.1f}")
    print(f"   Median:  {statistics.median(all_ages):.1f}")
    bins5 = Counter()
    for a in all_ages:
        bins5[int(a // 5) * 5] += 1
    mode5 = max(bins5, key=bins5.get)
    print(f"   Mode:    {mode5}-{mode5+4} bin ({bins5[mode5]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5 else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # --- Deceased only (excluding post-1970 accidents too) ---
    nat_ages = [parse_float(p.get("Current Age or Age at Death", ""))
                for p in deceased_natural]
    nat_ages = [a for a in nat_ages if a is not None]

    print("─" * 72)
    print("B. DECEASED, NON-ACCIDENTAL ONLY")
    print("─" * 72)
    print(f"   N:       {len(nat_ages)}")
    print(f"   Mean:    {statistics.mean(nat_ages):.1f}")
    print(f"   Median:  {statistics.median(nat_ages):.1f}")
    bins5n = Counter()
    for a in nat_ages:
        bins5n[int(a // 5) * 5] += 1
    mode5n = max(bins5n, key=bins5n.get)
    print(f"   Mode:    {mode5n}-{mode5n+4} bin ({bins5n[mode5n]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5n.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5n else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # --- Deceased (all causes, post-1970 accidents included) ---
    all_deceased_ages = []
    for p in deceased_natural + deceased_acc_post70:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a is not None:
            all_deceased_ages.append(a)

    print("─" * 72)
    print("C. ALL DECEASED IN RETAINED POOL (incl. post-1970 accidents)")
    print("─" * 72)
    print(f"   N:       {len(all_deceased_ages)}")
    print(f"   Mean:    {statistics.mean(all_deceased_ages):.1f}")
    print(f"   Median:  {statistics.median(all_deceased_ages):.1f}")
    bins5d = Counter()
    for a in all_deceased_ages:
        bins5d[int(a // 5) * 5] += 1
    mode5d = max(bins5d, key=bins5d.get)
    print(f"   Mode:    {mode5d}-{mode5d+4} bin ({bins5d[mode5d]} people)")
    print()
    print("   5-year bins:")
    for edge in range(50, 100, 5):
        cnt = bins5d.get(edge, 0)
        bar = "#" * cnt
        marker = " <-- MODE" if edge == mode5d else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {cnt:3d}  {bar}{marker}")
    print()

    # --- Combined: non-accidental dead + living (right-censored) ---
    combined = nat_ages + [parse_float(p.get("Current Age or Age at Death", ""))
                           for p in living]
    combined = [a for a in combined if a is not None]

    print("─" * 72)
    print("D. NON-ACCIDENTAL DEAD + LIVING (right-censored estimate)")
    print("─" * 72)
    print(f"   N:       {len(combined)} ({len(nat_ages)} dead + {len(living)} living)")
    print(f"   Mean:    {statistics.mean(combined):.1f}")
    print(f"   Median:  {statistics.median(combined):.1f}")
    bins5c = Counter()
    for a in combined:
        bins5c[int(a // 5) * 5] += 1
    mode5c = max(bins5c, key=bins5c.get)
    print(f"   Mode:    {mode5c}-{mode5c+4} bin ({bins5c[mode5c]} people)")
    print()
    print("   5-year bins (D=died, L=living):")
    for edge in range(50, 100, 5):
        d_cnt = sum(1 for a in nat_ages if edge <= a < edge + 5)
        l_cnt = sum(1 for p in living
                    if (parse_float(p.get("Current Age or Age at Death", "")) or 0) >= edge
                    and (parse_float(p.get("Current Age or Age at Death", "")) or 0) < edge + 5)
        total = d_cnt + l_cnt
        d_bar = "#" * d_cnt
        l_bar = "+" * l_cnt
        marker = " <-- MODE" if edge == mode5c else ""
        print(f"     {edge:3d}-{edge+4:3d}:  {total:3d}  {d_bar}{l_bar}  (D={d_cnt}, L={l_cnt}){marker}")
    print()

    # --- Summary table ---
    print("=" * 72)
    print("SUMMARY TABLE")
    print("=" * 72)
    print()
    print(f"  {'Measure':<55s} {'Mean':>6s} {'Median':>7s} {'Mode bin':>10s}")
    print(f"  {'-'*55} {'─'*6} {'─'*7} {'─'*10}")
    print(f"  {'A. All retained (dead+living, all causes)':<55s} "
          f"{statistics.mean(all_ages):6.1f} {statistics.median(all_ages):7.1f} "
          f"  {mode5}-{mode5+4}")
    print(f"  {'B. Deceased non-accidental only':<55s} "
          f"{statistics.mean(nat_ages):6.1f} {statistics.median(nat_ages):7.1f} "
          f"  {mode5n}-{mode5n+4}")
    print(f"  {'C. All deceased in pool (incl post-1970 accidents)':<55s} "
          f"{statistics.mean(all_deceased_ages):6.1f} {statistics.median(all_deceased_ages):7.1f} "
          f"  {mode5d}-{mode5d+4}")
    print(f"  {'D. Non-acc dead + living (right-censored)':<55s} "
          f"{statistics.mean(combined):6.1f} {statistics.median(combined):7.1f} "
          f"  {mode5c}-{mode5c+4}")
    print()
    print("  Note: Living survivors are right-censored — they will die")
    print("  later, so rows A and D underestimate the true final values.")
    print()
    print("=" * 72)
    print("Script: non_apollo_exclude_pre1970_accidents.py")
    print("No source files were modified.")
    print("=" * 72)


if __name__ == "__main__":
    main()
