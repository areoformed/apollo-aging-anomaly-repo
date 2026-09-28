#!/usr/bin/env python3
"""
lifespan_binned_csvs.py
-----------------------
Generates 2-year and 3-year binned lifespan distribution CSVs for both
Apollo 7-17 and non-Apollo cohorts (after excluding pre-1970 accidental
deaths). Each CSV has columns for both cohorts side by side.

Outputs to 'Intermediate datasets for human analysis/'.
Read-only on source data — does NOT modify any TSV files.

Usage:  python3 lifespan_binned_csvs.py
"""

import csv
from pathlib import Path
from datetime import datetime

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"
OUT = BASE / "Intermediate datasets for human analysis"

NON_APOLLO_FILES = [
    ENRICHED / "03E-non-apollo-enriched.tsv",
    ENRICHED / "09-x15-pilots-enriched.tsv",
    ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    ENRICHED / "11-mol-full-enriched.tsv",
]

APOLLO_FILES = [
    ENRICHED / "07E-lunar-enriched.tsv",
    ENRICHED / "08E-non-lunar-apollo-enriched.tsv",
]

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
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None

def load_cohort(file_list):
    people = []
    for path in file_list:
        people.extend(load_tsv(path))
    return people

def exclude_pre1970_accidents(people):
    return [p for p in people
            if not (p.get("Accidental Death", "").strip().upper() == "Y"
                    and (d := parse_date(p.get("Date of Death", ""))) is not None
                    and d.year < 1970)]

def extract_ages_by_status(people):
    dead_nat, dead_acc, living = [], [], []
    for p in people:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a is None:
            continue
        status = p.get("Status", "").strip().lower()
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        if status == "living":
            living.append(a)
        elif acc:
            dead_acc.append(a)
        else:
            dead_nat.append(a)
    return dead_nat, dead_acc, living

def bin_ages(ages, bin_width, lo, hi):
    counts = {}
    for edge in range(lo, hi, bin_width):
        counts[edge] = 0
    for a in ages:
        edge = lo + int((a - lo) // bin_width) * bin_width
        if edge in counts:
            counts[edge] += 1
    return counts

def write_binned_csv(filepath, bin_width, apollo_nat, apollo_acc, apollo_liv,
                     nonapollo_nat, nonapollo_acc, nonapollo_liv):
    lo = 50
    hi = 100

    ap_all = apollo_nat + apollo_acc + apollo_liv
    na_all = nonapollo_nat + nonapollo_acc + nonapollo_liv
    ap_nonacc = apollo_nat + apollo_liv
    na_nonacc = nonapollo_nat + nonapollo_liv

    ap_nat_bins = bin_ages(apollo_nat, bin_width, lo, hi)
    ap_acc_bins = bin_ages(apollo_acc, bin_width, lo, hi)
    ap_liv_bins = bin_ages(apollo_liv, bin_width, lo, hi)
    ap_all_bins = bin_ages(ap_all, bin_width, lo, hi)
    ap_nonacc_bins = bin_ages(ap_nonacc, bin_width, lo, hi)

    na_nat_bins = bin_ages(nonapollo_nat, bin_width, lo, hi)
    na_acc_bins = bin_ages(nonapollo_acc, bin_width, lo, hi)
    na_liv_bins = bin_ages(nonapollo_liv, bin_width, lo, hi)
    na_all_bins = bin_ages(na_all, bin_width, lo, hi)
    na_nonacc_bins = bin_ages(na_nonacc, bin_width, lo, hi)

    edges = sorted(ap_nat_bins.keys())

    with open(filepath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Bin Start", "Bin End", "Bin Label",
            "Apollo: Deceased Non-Accidental",
            "Apollo: Deceased Accidental (post-1970)",
            "Apollo: Living",
            "Apollo: All (dead+living)",
            "Apollo: Non-Accidental (dead+living)",
            "Non-Apollo: Deceased Non-Accidental",
            "Non-Apollo: Deceased Accidental (post-1970)",
            "Non-Apollo: Living",
            "Non-Apollo: All (dead+living)",
            "Non-Apollo: Non-Accidental (dead+living)",
        ])

        for edge in edges:
            end = edge + bin_width - 1
            label = f"{edge}-{end}"
            w.writerow([
                edge, end, label,
                ap_nat_bins[edge],
                ap_acc_bins[edge],
                ap_liv_bins[edge],
                ap_all_bins[edge],
                ap_nonacc_bins[edge],
                na_nat_bins[edge],
                na_acc_bins[edge],
                na_liv_bins[edge],
                na_all_bins[edge],
                na_nonacc_bins[edge],
            ])

        # Totals row
        w.writerow([
            "", "", "TOTAL",
            len(apollo_nat), len(apollo_acc), len(apollo_liv),
            len(ap_all), len(ap_nonacc),
            len(nonapollo_nat), len(nonapollo_acc), len(nonapollo_liv),
            len(na_all), len(na_nonacc),
        ])


def main():
    apollo = exclude_pre1970_accidents(load_cohort(APOLLO_FILES))
    nonapollo = exclude_pre1970_accidents(load_cohort(NON_APOLLO_FILES))

    ap_nat, ap_acc, ap_liv = extract_ages_by_status(apollo)
    na_nat, na_acc, na_liv = extract_ages_by_status(nonapollo)

    f2 = OUT / "lifespan_distribution_2yr_bins.csv"
    write_binned_csv(f2, 2, ap_nat, ap_acc, ap_liv, na_nat, na_acc, na_liv)
    print(f"  Saved {f2.name}")

    f3 = OUT / "lifespan_distribution_3yr_bins.csv"
    write_binned_csv(f3, 3, ap_nat, ap_acc, ap_liv, na_nat, na_acc, na_liv)
    print(f"  Saved {f3.name}")

    print(f"\nApollo:     {len(ap_nat)} non-acc dead, {len(ap_acc)} acc dead, {len(ap_liv)} living = {len(apollo)} total")
    print(f"Non-Apollo: {len(na_nat)} non-acc dead, {len(na_acc)} acc dead, {len(na_liv)} living = {len(nonapollo)} total")
    print("\nNo source files were modified.")


if __name__ == "__main__":
    main()
