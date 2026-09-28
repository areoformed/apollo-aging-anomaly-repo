#!/usr/bin/env python3
"""
five_group_summary.py
---------------------
Produces a single summary table comparing five groups:
  1. All 29 Apollo 7-17 astronauts
  2. The 24 Apollo Lunar mission astronauts (Apollo 8-17)
  3. All 69 non-Apollo astronauts
  4. Non-Apollo with pre-1970 accidental deaths removed (55)
  5. SSA 1930 male birth cohort (conditional on survival to 30)

Reports: N, mean, median, mode (5-yr bin), std dev, Q1, Q3,
% reaching 80, % reaching 90, still living count.

Read-only — does NOT modify any source files.

Usage:  python3 five_group_summary.py
"""

import csv
import statistics
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"
SSA_FILE = Path("./"
                "Human Efforts/Manually Compiled Data/Third Party/"
                "US Social Security/Actuarial Study 120/"
                "CohLifeTables_M_Alt2_TR2024.csv")

NON_APOLLO_FILES = [
    ENRICHED / "03E-non-apollo-enriched.tsv",
    ENRICHED / "09-x15-pilots-enriched.tsv",
    ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    ENRICHED / "11-mol-full-enriched.tsv",
]
APOLLO_LUNAR_FILE = ENRICHED / "07E-lunar-enriched.tsv"
APOLLO_NONLUNAR_FILE = ENRICHED / "08E-non-lunar-apollo-enriched.tsv"


def load_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("Name", "").strip():
                rows.append(row)
    return rows

def parse_float(s):
    try:
        return float(s.strip())
    except (ValueError, TypeError, AttributeError):
        return None

def parse_date(s):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError, AttributeError):
        return None

def load_cohort(file_list):
    people = []
    for p in file_list:
        people.extend(load_tsv(p))
    return people

def exclude_pre1970_accidents(people):
    return [p for p in people
            if not (p.get("Accidental Death", "").strip().upper() == "Y"
                    and (d := parse_date(p.get("Date of Death", ""))) is not None
                    and d.year < 1970)]

def group_stats(people, label):
    ages = []
    living_count = 0
    deceased_count = 0

    for p in people:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a is None:
            continue
        ages.append(a)
        if p.get("Status", "").strip().lower() == "living":
            living_count += 1
        else:
            deceased_count += 1

    n = len(ages)
    if n == 0:
        return None

    s = sorted(ages)
    mean = statistics.mean(ages)
    median = statistics.median(ages)
    stdev = statistics.stdev(ages) if n > 1 else 0
    q1 = s[n // 4]
    q3 = s[3 * n // 4]

    bins5 = Counter(int(a // 5) * 5 for a in ages)
    mode5_edge = max(bins5, key=bins5.get)
    mode5_count = bins5[mode5_edge]

    reached_80 = sum(1 for a in ages if a >= 80)
    reached_90 = sum(1 for a in ages if a >= 90)

    return {
        "label": label,
        "n": n,
        "mean": mean,
        "median": median,
        "mode_bin": f"{mode5_edge}-{mode5_edge + 4}",
        "mode_count": mode5_count,
        "stdev": stdev,
        "q1": q1,
        "q3": q3,
        "pct_80": 100 * reached_80 / n,
        "pct_90": 100 * reached_90 / n,
        "living": living_count,
        "deceased": deceased_count,
        "min_age": s[0],
        "max_age": s[-1],
    }


def ssa_stats_at_30(filepath, birth_year=1930):
    data = {}
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 8:
                continue
            try:
                yr = int(parts[0])
                age = int(parts[1])
                lx = float(parts[3])
                dx = float(parts[4])
            except (ValueError, IndexError):
                continue
            if yr == birth_year:
                data[age] = {"lx": lx, "dx": dx}

    if 30 not in data:
        return None

    l30 = data[30]["lx"]
    ages = sorted(data.keys())

    # Mean age at death | survived to 30
    mean_30 = sum((a + 0.5) * data[a]["dx"] for a in ages if a >= 30) / l30

    # Median age at death | survived to 30
    half = l30 / 2
    median_30 = None
    for a in ages:
        if a < 30:
            continue
        if data[a]["lx"] <= half:
            lx_prev = data[a - 1]["lx"]
            lx_curr = data[a]["lx"]
            median_30 = (a - 1) + (lx_prev - half) / (lx_prev - lx_curr)
            break

    # Mode: 5-year bin with most deaths (conditional on 30+)
    bins5 = Counter()
    for a in ages:
        if a < 30:
            continue
        edge = (a // 5) * 5
        bins5[edge] += data[a]["dx"]
    mode5_edge = max(bins5, key=bins5.get)
    mode5_count_pct = 100 * bins5[mode5_edge] / l30

    # Std dev
    variance = sum(data[a]["dx"] * ((a + 0.5) - mean_30) ** 2
                   for a in ages if a >= 30) / l30
    stdev = variance ** 0.5

    # Q1, Q3
    q1_target = l30 * 0.75
    q3_target = l30 * 0.25
    q1 = q3 = None
    for a in ages:
        if a < 30:
            continue
        if q1 is None and data[a]["lx"] <= q1_target:
            lx_prev = data[a - 1]["lx"]
            q1 = (a - 1) + (lx_prev - q1_target) / (lx_prev - data[a]["lx"])
        if q3 is None and data[a]["lx"] <= q3_target:
            lx_prev = data[a - 1]["lx"]
            q3 = (a - 1) + (lx_prev - q3_target) / (lx_prev - data[a]["lx"])

    # % reaching 80, 90
    pct_80 = 100 * data[80]["lx"] / l30 if 80 in data else 0
    pct_90 = 100 * data[90]["lx"] / l30 if 90 in data else 0

    return {
        "label": f"SSA {birth_year} Male Cohort\n(conditional on surv. to 30)",
        "n": f"~{int(l30):,}",
        "mean": mean_30,
        "median": median_30,
        "mode_bin": f"{mode5_edge}-{mode5_edge + 4}",
        "mode_pct": f"{mode5_count_pct:.1f}%",
        "stdev": stdev,
        "q1": q1,
        "q3": q3,
        "pct_80": pct_80,
        "pct_90": pct_90,
        "living": "N/A",
        "deceased": "N/A",
    }


def main():
    # Load groups
    apollo_lunar = load_tsv(APOLLO_LUNAR_FILE)
    apollo_nonlunar = load_tsv(APOLLO_NONLUNAR_FILE)
    apollo_all = apollo_lunar + apollo_nonlunar
    nonapollo_all = load_cohort(NON_APOLLO_FILES)
    nonapollo_excl = exclude_pre1970_accidents(nonapollo_all)

    groups = [
        group_stats(apollo_all, "All Apollo 7-17"),
        group_stats(apollo_lunar, "Apollo Lunar (8-17)"),
        group_stats(nonapollo_all, "All Non-Apollo"),
        group_stats(nonapollo_excl, "Non-Apollo\n(pre-1970 acc. removed)"),
    ]

    ssa = ssa_stats_at_30(SSA_FILE, 1930)

    print("=" * 100)
    print("FIVE-GROUP LIFESPAN SUMMARY")
    print("Age at death for deceased; current age for living")
    print("=" * 100)
    print()

    # Header
    col_w = 16
    labels = [g["label"] for g in groups]
    labels.append("SSA 1930 Male\n(surv. to 30)")

    # Print as a vertical table for readability
    def row(metric, values, fmt=".1f"):
        cells = []
        for v in values:
            if v is None or v == "N/A":
                cells.append(f"{'N/A':>{col_w}}")
            elif isinstance(v, str):
                cells.append(f"{v:>{col_w}}")
            elif isinstance(v, int):
                cells.append(f"{v:>{col_w}d}")
            else:
                cells.append(f"{v:>{col_w}{fmt}}")
        print(f"  {metric:<28s}" + "".join(cells))

    # Column headers
    header_line1 = f"  {'':28s}"
    header_line2 = f"  {'':28s}"
    short_labels = [
        "All Apollo", "Apollo Lunar", "All Non-Apollo",
        "Non-Apollo*", "SSA 1930"
    ]
    for sl in short_labels:
        header_line1 += f"{sl:>{col_w}}"
    print(header_line1)

    sub_labels = [
        "(N=29)", "(N=24)", "(N=69)",
        "(N=55)", "(surv.30)"
    ]
    for sl in sub_labels:
        header_line2 += f"{sl:>{col_w}}"
    print(header_line2)
    print("  " + "─" * (28 + col_w * 5))

    # Rows
    vals = lambda key: [g[key] for g in groups] + [ssa[key]]

    row("N", [g["n"] for g in groups] + [ssa["n"]], "")
    row("Still living", [g["living"] for g in groups] + [ssa["living"]], "d")
    row("Deceased", [g["deceased"] for g in groups] + [ssa["deceased"]], "d")
    print()
    row("Mean age", [g["mean"] for g in groups] + [ssa["mean"]])
    row("Median age", [g["median"] for g in groups] + [ssa["median"]])
    row("Modal bin (5-yr)", [g["mode_bin"] for g in groups] + [ssa["mode_bin"]], "")
    row("Std deviation", [g["stdev"] for g in groups] + [ssa["stdev"]])
    print()
    row("Q1 (25th pct)", [g["q1"] for g in groups] + [ssa["q1"]])
    row("Q3 (75th pct)", [g["q3"] for g in groups] + [ssa["q3"]])
    print()
    row("% reaching 80", [g["pct_80"] for g in groups] + [ssa["pct_80"]])
    row("% reaching 90", [g["pct_90"] for g in groups] + [ssa["pct_90"]])

    print()
    print("  " + "─" * (28 + col_w * 5))
    print()
    print("  * Pre-1970 accidental deaths excluded (14 removed)")
    print("  SSA column: 1930 male birth cohort, conditional on survival to age 30")
    print("  Astronaut columns: age at death (deceased) or current age (living)")
    print("  Living survivors are right-censored — final values will shift upward")
    print()

    # ── Delta table ──
    print("─" * 100)
    print("DELTAS vs SSA 1930 BASELINE (conditional on survival to 30)")
    print("─" * 100)
    print()
    ssa_mean = ssa["mean"]
    ssa_med = ssa["median"]

    header = f"  {'':28s}"
    for sl in short_labels[:4]:
        header += f"{sl:>{col_w}}"
    print(header)
    print("  " + "─" * (28 + col_w * 4))

    d_means = [g["mean"] - ssa_mean for g in groups]
    d_meds = [g["median"] - ssa_med for g in groups]

    def row_delta(metric, values):
        cells = []
        for v in values:
            sign = "+" if v >= 0 else ""
            cells.append(f"{sign}{v:>{col_w - 1}.1f}")
        print(f"  {metric:<28s}" + "".join(cells))

    row_delta("Mean delta vs SSA", d_means)
    row_delta("Median delta vs SSA", d_meds)
    print()

    # ── Proportional survival comparison ──
    print("─" * 100)
    print("SURVIVAL RATE COMPARISON vs SSA BASELINE")
    print("─" * 100)
    print()
    header = f"  {'':28s}"
    for sl in short_labels:
        header += f"{sl:>{col_w}}"
    print(header)
    print("  " + "─" * (28 + col_w * 5))
    row("% reaching 80", [g["pct_80"] for g in groups] + [ssa["pct_80"]])
    row("% reaching 90", [g["pct_90"] for g in groups] + [ssa["pct_90"]])

    print()
    print("=" * 100)
    print("Script: five_group_summary.py")
    print("No source files were modified.")
    print("=" * 100)


if __name__ == "__main__":
    main()
