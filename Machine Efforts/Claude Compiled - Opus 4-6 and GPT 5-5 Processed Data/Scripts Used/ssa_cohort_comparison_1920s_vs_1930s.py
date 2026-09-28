#!/usr/bin/env python3
"""
ssa_cohort_comparison_1920s_vs_1930s.py
---------------------------------------
Computes mean and median age at death from SSA male cohort life tables
(Actuarial Study 120, Alt 2, 2024 Trustees Report) for the 1920-1929
and 1930-1939 birth cohorts. Also computes conditional statistics for
men who survived to age 30 (the astronaut selection filter).

Read-only — does NOT modify any source files.

Usage:  python3 ssa_cohort_comparison_1920s_vs_1930s.py
"""

import csv
from pathlib import Path
import statistics

SSA_FILE = Path("./"
                "Human Efforts/Manually Compiled Data/Third Party/"
                "US Social Security/Actuarial Study 120/"
                "CohLifeTables_M_Alt2_TR2024.csv")

def load_ssa_data(filepath):
    data = {}
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 8:
                continue
            try:
                year = int(parts[0])
                age = int(parts[1])
                qx = float(parts[2])
                lx = float(parts[3])
                dx = float(parts[4])
                ex = float(parts[7])
            except (ValueError, IndexError):
                continue
            if year not in data:
                data[year] = {}
            data[year][age] = {"qx": qx, "lx": lx, "dx": dx, "ex": ex}
    return data

def compute_stats(year_data):
    ages = sorted(year_data.keys())
    l0 = year_data[0]["lx"]

    # Mean age at death (from birth)
    mean_from_birth = sum((a + 0.5) * year_data[a]["dx"] for a in ages) / l0

    # Median age at death (from birth): age where l(x) drops below l(0)/2
    half = l0 / 2
    median_from_birth = None
    for a in ages:
        if year_data[a]["lx"] <= half:
            lx_prev = year_data[a - 1]["lx"] if a > 0 else l0
            lx_curr = year_data[a]["lx"]
            median_from_birth = (a - 1) + (lx_prev - half) / (lx_prev - lx_curr)
            break

    # Life expectancy at birth (from table)
    e0 = year_data[0]["ex"]

    # Conditional on surviving to 30
    if 30 not in year_data:
        return mean_from_birth, median_from_birth, e0, None, None, None

    l30 = year_data[30]["lx"]

    # Mean age at death given survival to 30
    mean_from_30 = sum((a + 0.5) * year_data[a]["dx"]
                       for a in ages if a >= 30) / l30

    # Median age at death given survival to 30
    half_30 = l30 / 2
    median_from_30 = None
    for a in ages:
        if a < 30:
            continue
        if year_data[a]["lx"] <= half_30:
            lx_prev = year_data[a - 1]["lx"]
            lx_curr = year_data[a]["lx"]
            median_from_30 = (a - 1) + (lx_prev - half_30) / (lx_prev - lx_curr)
            break

    # Life expectancy at 30 (from table) + 30
    e30 = year_data[30]["ex"]
    expected_age_at_death_from_30 = 30 + e30

    return mean_from_birth, median_from_birth, e0, mean_from_30, median_from_30, expected_age_at_death_from_30


def main():
    data = load_ssa_data(SSA_FILE)

    print("=" * 80)
    print("SSA MALE COHORT LIFE TABLE COMPARISON: 1920s vs 1930s BIRTH COHORTS")
    print("Source: Actuarial Study 120, Alt 2, 2024 Trustees Report")
    print("=" * 80)
    print()

    # ── Individual year stats ──
    print("INDIVIDUAL BIRTH YEAR STATISTICS")
    print("-" * 80)
    print(f"  {'Year':>4s}  {'e(0)':>6s}  {'Mean':>6s}  {'Median':>7s}  "
          f"{'e(30)+30':>8s}  {'Mean|30':>7s}  {'Med|30':>7s}")
    print(f"  {'':>4s}  {'':>6s}  {'birth':>6s}  {'birth':>7s}  "
          f"{'':>8s}  {'surv30':>7s}  {'surv30':>7s}")
    print("-" * 80)

    decade_stats = {"1920s": [], "1930s": []}

    for year in range(1920, 1940):
        if year not in data:
            continue
        mean_b, med_b, e0, mean_30, med_30, eage_30 = compute_stats(data[year])
        decade = "1920s" if year < 1930 else "1930s"
        decade_stats[decade].append({
            "year": year, "e0": e0, "mean_b": mean_b, "med_b": med_b,
            "mean_30": mean_30, "med_30": med_30, "eage_30": eage_30,
        })

        sep = "  " if year != 1930 else "──"
        if year == 1930:
            print(f"  {'────':>4s}  {'──────':>6s}  {'──────':>6s}  {'───────':>7s}  "
                  f"{'────────':>8s}  {'───────':>7s}  {'───────':>7s}")

        print(f"  {year:4d}  {e0:6.2f}  {mean_b:6.2f}  {med_b:7.2f}  "
              f"{eage_30:8.2f}  {mean_30:7.2f}  {med_30:7.2f}")

    print()

    # ── Decade averages ──
    print("DECADE AVERAGES")
    print("-" * 80)
    print(f"  {'Decade':>7s}  {'e(0)':>6s}  {'Mean':>6s}  {'Median':>7s}  "
          f"{'e(30)+30':>8s}  {'Mean|30':>7s}  {'Med|30':>7s}")
    print("-" * 80)

    for decade_label in ["1920s", "1930s"]:
        stats = decade_stats[decade_label]
        avg_e0 = statistics.mean(s["e0"] for s in stats)
        avg_mean_b = statistics.mean(s["mean_b"] for s in stats)
        avg_med_b = statistics.mean(s["med_b"] for s in stats)
        avg_eage_30 = statistics.mean(s["eage_30"] for s in stats)
        avg_mean_30 = statistics.mean(s["mean_30"] for s in stats)
        avg_med_30 = statistics.mean(s["med_30"] for s in stats)
        print(f"  {decade_label:>7s}  {avg_e0:6.2f}  {avg_mean_b:6.2f}  {avg_med_b:7.2f}  "
              f"{avg_eage_30:8.2f}  {avg_mean_30:7.2f}  {avg_med_30:7.2f}")

    # Deltas
    s20 = decade_stats["1920s"]
    s30 = decade_stats["1930s"]
    d_e0 = statistics.mean(s["e0"] for s in s30) - statistics.mean(s["e0"] for s in s20)
    d_mean_b = statistics.mean(s["mean_b"] for s in s30) - statistics.mean(s["mean_b"] for s in s20)
    d_med_b = statistics.mean(s["med_b"] for s in s30) - statistics.mean(s["med_b"] for s in s20)
    d_eage_30 = statistics.mean(s["eage_30"] for s in s30) - statistics.mean(s["eage_30"] for s in s20)
    d_mean_30 = statistics.mean(s["mean_30"] for s in s30) - statistics.mean(s["mean_30"] for s in s20)
    d_med_30 = statistics.mean(s["med_30"] for s in s30) - statistics.mean(s["med_30"] for s in s20)
    print(f"  {'Delta':>7s}  {d_e0:+6.2f}  {d_mean_b:+6.2f}  {d_med_b:+7.2f}  "
          f"{d_eage_30:+8.2f}  {d_mean_30:+7.2f}  {d_med_30:+7.2f}")
    print()

    # ── Conditional survival to 30 detail ──
    print("KEY COMPARISON: EXPECTED AGE AT DEATH GIVEN SURVIVAL TO 30")
    print("(This is the relevant baseline for astronaut candidates)")
    print("-" * 60)
    avg_30_1920s = statistics.mean(s["med_30"] for s in s20)
    avg_30_1930s = statistics.mean(s["med_30"] for s in s30)
    avg_mean_30_1920s = statistics.mean(s["mean_30"] for s in s20)
    avg_mean_30_1930s = statistics.mean(s["mean_30"] for s in s30)
    print(f"  1920s cohort  —  Mean: {avg_mean_30_1920s:.1f}   Median: {avg_30_1920s:.1f}")
    print(f"  1930s cohort  —  Mean: {avg_mean_30_1930s:.1f}   Median: {avg_30_1930s:.1f}")
    print(f"  Delta (30s-20s) — Mean: {d_mean_30:+.1f}   Median: {d_med_30:+.1f}")
    print()
    print("  The 1930s birth cohort gains ~{:.1f} years in median expected".format(d_med_30))
    print("  lifespan (conditional on reaching 30) over the 1920s cohort.")
    print()

    # ── Context for astronaut comparison ──
    print("=" * 80)
    print("CONTEXT FOR ASTRONAUT LONGEVITY COMPARISON")
    print("=" * 80)
    print()
    print("  Apollo 7-17:   6 born 1920s, 23 born 1930s")
    print("  Non-Apollo:   21 born 1920s, 44 born 1930s")
    print()
    pct_20s_apollo = 100 * 6 / 29
    pct_20s_nonapollo = 100 * 21 / 69
    print(f"  1920s share:  Apollo {pct_20s_apollo:.0f}%  vs  Non-Apollo {pct_20s_nonapollo:.0f}%")
    print()
    print(f"  The non-Apollo group has ~{pct_20s_nonapollo - pct_20s_apollo:.0f} percentage points")
    print(f"  more 1920s-born members, who carry a ~{abs(d_med_30):.1f}-year actuarial")
    print(f"  disadvantage in median expected lifespan (given survival to 30).")
    print()

    # Weighted expected median for each group
    w_apollo = (6 * avg_30_1920s + 23 * avg_30_1930s) / 29
    w_nonapollo = (21 * avg_30_1920s + 44 * avg_30_1930s) / 65
    print(f"  Cohort-weighted expected median lifespan (given survival to 30):")
    print(f"    Apollo:      {w_apollo:.1f}")
    print(f"    Non-Apollo:  {w_nonapollo:.1f}")
    print(f"    Delta:       {w_apollo - w_nonapollo:+.1f} years")
    print()
    print("  This is the gap explained by birth-cohort composition alone.")
    print()
    print("=" * 80)
    print("Script: ssa_cohort_comparison_1920s_vs_1930s.py")
    print("No source files were modified.")
    print("=" * 80)


if __name__ == "__main__":
    main()
