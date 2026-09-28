#!/usr/bin/env python3
"""
non_apollo_demographics.py
--------------------------
Read-only demographic analysis of the 69 non-Apollo astronauts across four
enriched datasets:
  03E  – Non-Apollo NASA astronauts (Groups 1-7, never flew Apollo 7-17)
  09   – X-15 research pilots
  10   – X-20 Dyna-Soar pilots
  11   – MOL-only astronauts (never transferred to NASA)

Outputs summary statistics to stdout. Does NOT modify any source files.

Usage:  python3 non_apollo_demographics.py
"""

import csv
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date, datetime
import statistics

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"

FILES = {
    "Non-Apollo NASA": ENRICHED / "03E-non-apollo-enriched.tsv",
    "X-15 Pilots":     ENRICHED / "09-x15-pilots-enriched.tsv",
    "Dyna-Soar Pilots": ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    "MOL-Only":        ENRICHED / "11-mol-full-enriched.tsv",
}

TODAY = date(2026, 5, 25)

def parse_date(s):
    if not s or s.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None

def parse_float(s):
    if not s or s.strip() == "":
        return None
    try:
        return float(s.strip())
    except ValueError:
        return None

def load_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("Name", "").strip():
                rows.append(row)
    return rows

def extract_highest_degree(edu_str):
    if not edu_str:
        return "Unknown"
    edu = edu_str.lower()
    if "phd" in edu or "scd" in edu or "d.sc" in edu or "doctorate" in edu:
        return "PhD/ScD"
    if "md" in edu and ("medicine" in edu or "medical" in edu or "md," in edu or "md " in edu):
        return "MD"
    if "jd " in edu or "jd," in edu or "law" in edu:
        return "JD"
    if "md" in edu:
        return "MD"
    if "ms " in edu or "ms," in edu or "m.s." in edu or "msc" in edu or "master" in edu:
        return "MS/MA"
    if "mba" in edu:
        return "MBA"
    if "mph" in edu:
        return "MPH"
    if "bs " in edu or "bs," in edu or "b.s." in edu or "ba " in edu or "ba," in edu or "b.a." in edu or "be " in edu or "bsc" in edu:
        return "BS/BA"
    return "Unknown"

def extract_highest_degree_rank(edu_str):
    if not edu_str:
        return (0, "Unknown")
    edu = edu_str.lower()
    if "phd" in edu or "scd" in edu or "d.sc" in edu or "doctorate" in edu:
        return (5, "PhD/ScD")
    if "md" in edu:
        return (5, "MD")
    if "jd " in edu or "jd," in edu:
        return (4, "JD")
    if "mba" in edu:
        return (3, "MBA")
    if "mph" in edu:
        return (3, "MPH")
    if "ms " in edu or "ms," in edu or "m.s." in edu or "msc" in edu or "master" in edu or "ma " in edu or "ma," in edu:
        return (3, "MS/MA")
    if "bs " in edu or "bs," in edu or "b.s." in edu or "ba " in edu or "ba," in edu or "b.a." in edu or "be " in edu or "bsc" in edu:
        return (2, "BS/BA")
    return (0, "Unknown")

def classify_branch(branch_str):
    if not branch_str:
        return "Unknown"
    b = branch_str.lower()
    if "none" in b or "civilian" in b:
        return "Civilian"
    if "marine" in b:
        return "USMC"
    if "navy" in b or "naval" in b:
        return "USN"
    if "air force" in b or "usaf" in b:
        return "USAF"
    if "army" in b:
        return "USA/USAAF"
    if "australian" in b or "raaf" in b:
        return "Foreign Military"
    return branch_str.strip()

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
    print(f"DEMOGRAPHIC PROFILE: 69 NON-APOLLO ASTRONAUTS")
    print(f"(Astronauts who did NOT fly on Apollo 7 through Apollo 17)")
    print("=" * 72)
    print()

    # --- Source breakdown ---
    print("SOURCE DATASET BREAKDOWN")
    print("-" * 40)
    for label, count in group_counts.items():
        print(f"  {label:25s}  {count:3d}")
    print(f"  {'TOTAL':25s}  {N:3d}")
    print()

    # --- Astronaut Group distribution ---
    print("ASTRONAUT GROUP / PROGRAM DISTRIBUTION")
    print("-" * 55)
    group_counter = Counter()
    for p in all_people:
        grp = p.get("Astronaut Group", "Unknown").strip()
        group_counter[grp] += 1
    for grp, cnt in sorted(group_counter.items(), key=lambda x: -x[1]):
        print(f"  {grp:45s}  {cnt:3d}")
    print()

    # --- Birth year ---
    birth_years = []
    for p in all_people:
        by = p.get("Birth Year", "")
        if by:
            try:
                birth_years.append(int(by))
            except ValueError:
                pass
    if birth_years:
        print("BIRTH YEAR DISTRIBUTION")
        print("-" * 40)
        print(f"  Range:    {min(birth_years)} – {max(birth_years)}")
        print(f"  Mean:     {statistics.mean(birth_years):.1f}")
        print(f"  Median:   {statistics.median(birth_years):.1f}")
        print(f"  Std Dev:  {statistics.stdev(birth_years):.1f}")
        print()
        decade_counter = Counter()
        for y in birth_years:
            decade = (y // 5) * 5
            decade_counter[decade] += 1
        print("  Five-year cohorts:")
        for decade in sorted(decade_counter):
            bar = "#" * decade_counter[decade]
            print(f"    {decade}-{decade+4}:  {decade_counter[decade]:3d}  {bar}")
        print()

    # --- Age at selection ---
    ages_at_sel = []
    for p in all_people:
        a = parse_float(p.get("Age at Selection", ""))
        if a:
            ages_at_sel.append(a)
    if ages_at_sel:
        print("AGE AT SELECTION")
        print("-" * 40)
        print(f"  N:        {len(ages_at_sel)}")
        print(f"  Range:    {min(ages_at_sel):.1f} – {max(ages_at_sel):.1f}")
        print(f"  Mean:     {statistics.mean(ages_at_sel):.1f}")
        print(f"  Median:   {statistics.median(ages_at_sel):.1f}")
        print(f"  Std Dev:  {statistics.stdev(ages_at_sel):.1f}")
        print()

    # --- Military branch ---
    print("MILITARY SERVICE BRANCH")
    print("-" * 40)
    branch_counter = Counter()
    for p in all_people:
        b = classify_branch(p.get("Military Branch", ""))
        branch_counter[b] += 1
    for br, cnt in sorted(branch_counter.items(), key=lambda x: -x[1]):
        pct = 100.0 * cnt / N
        print(f"  {br:20s}  {cnt:3d}  ({pct:5.1f}%)")
    print()

    # --- Education ---
    print("HIGHEST DEGREE ATTAINED")
    print("-" * 40)
    degree_counter = Counter()
    multi_degree = 0
    for p in all_people:
        edu = p.get("Education", "")
        rank, deg = extract_highest_degree_rank(edu)
        degree_counter[deg] += 1
        if edu:
            deg_mentions = 0
            for token in ["BS", "BA", "BE", "MS", "MA", "MBA", "MPH", "PhD", "ScD", "MD", "JD"]:
                if token in edu:
                    deg_mentions += 1
            if deg_mentions >= 2:
                multi_degree += 1
    for deg, cnt in sorted(degree_counter.items(), key=lambda x: -x[1]):
        pct = 100.0 * cnt / N
        print(f"  {deg:15s}  {cnt:3d}  ({pct:5.1f}%)")
    print(f"\n  Holding 2+ distinct degrees: {multi_degree}")
    print()

    # --- Survival status ---
    print("VITAL STATUS (as of 2026-05-25)")
    print("-" * 40)
    living = [p for p in all_people if p.get("Status", "").strip().lower() == "living"]
    deceased = [p for p in all_people if p.get("Status", "").strip().lower() == "deceased"]
    print(f"  Living:    {len(living):3d}  ({100*len(living)/N:.1f}%)")
    print(f"  Deceased:  {len(deceased):3d}  ({100*len(deceased)/N:.1f}%)")
    print()

    # --- Living: current ages ---
    living_ages = []
    for p in living:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        if a:
            living_ages.append((p["Name"], a))
    if living_ages:
        ages = [a for _, a in living_ages]
        print("LIVING ASTRONAUTS — CURRENT AGES")
        print("-" * 55)
        print(f"  N:        {len(ages)}")
        print(f"  Range:    {min(ages):.1f} – {max(ages):.1f}")
        print(f"  Mean:     {statistics.mean(ages):.1f}")
        print(f"  Median:   {statistics.median(ages):.1f}")
        print()
        print("  Individual ages (sorted):")
        for name, age in sorted(living_ages, key=lambda x: -x[1]):
            print(f"    {name:45s}  {age:5.1f}")
        print()

    # --- Deceased: ages at death ---
    death_ages = []
    accidental_deaths = []
    natural_deaths = []
    for p in deceased:
        a = parse_float(p.get("Current Age or Age at Death", ""))
        acc = p.get("Accidental Death", "").strip().upper()
        if a:
            death_ages.append((p["Name"], a, acc == "Y"))
            if acc == "Y":
                accidental_deaths.append((p["Name"], a))
            else:
                natural_deaths.append((p["Name"], a))

    if death_ages:
        ages = [a for _, a, _ in death_ages]
        print("DECEASED ASTRONAUTS — AGE AT DEATH (all causes)")
        print("-" * 55)
        print(f"  N:        {len(ages)}")
        print(f"  Range:    {min(ages):.1f} – {max(ages):.1f}")
        print(f"  Mean:     {statistics.mean(ages):.1f}")
        print(f"  Median:   {statistics.median(ages):.1f}")
        if len(ages) > 1:
            print(f"  Std Dev:  {statistics.stdev(ages):.1f}")
        print()

    if accidental_deaths:
        ages = [a for _, a in accidental_deaths]
        print("ACCIDENTAL DEATHS")
        print("-" * 55)
        print(f"  Count:    {len(accidental_deaths)} of {len(deceased)} deceased ({100*len(accidental_deaths)/len(deceased):.1f}%)")
        print(f"  Ages:     {min(ages):.1f} – {max(ages):.1f} (mean {statistics.mean(ages):.1f})")
        print()
        for name, age in sorted(accidental_deaths, key=lambda x: x[1]):
            cause = ""
            for p in all_people:
                if p["Name"] == name:
                    cause = p.get("Mort / cause note", "")[:80]
                    break
            print(f"    {name:45s}  age {age:5.1f}  {cause}")
        print()

    if natural_deaths:
        ages = [a for _, a in natural_deaths]
        print("NON-ACCIDENTAL DEATHS — AGE AT DEATH")
        print("-" * 55)
        print(f"  N:        {len(ages)}")
        print(f"  Range:    {min(ages):.1f} – {max(ages):.1f}")
        print(f"  Mean:     {statistics.mean(ages):.1f}")
        print(f"  Median:   {statistics.median(ages):.1f}")
        if len(ages) > 1:
            print(f"  Std Dev:  {statistics.stdev(ages):.1f}")
        print()

    # --- Flight status ---
    print("SPACEFLIGHT STATUS")
    print("-" * 40)
    flew = [p for p in all_people if p.get("Went to Space", "").strip().upper() == "Y"]
    never = [p for p in all_people if p.get("Went to Space", "").strip().upper() == "N"]
    print(f"  Flew in space:       {len(flew):3d}  ({100*len(flew)/N:.1f}%)")
    print(f"  Never flew in space: {len(never):3d}  ({100*len(never)/N:.1f}%)")
    print()

    # Flight count distribution for those who flew
    flight_counts = []
    for p in flew:
        nf = p.get("Number of Flights", "")
        try:
            flight_counts.append(int(nf))
        except (ValueError, TypeError):
            pass
    if flight_counts:
        fc_counter = Counter(flight_counts)
        print("  Number of flights (among those who flew):")
        for n in sorted(fc_counter):
            print(f"    {n} flight(s): {fc_counter[n]}")
        if len(flight_counts) > 1:
            print(f"    Mean: {statistics.mean(flight_counts):.1f}")
        print()

    # --- Cause of death summary ---
    print("CAUSE OF DEATH SUMMARY (deceased, non-accidental)")
    print("-" * 55)
    cause_counter = Counter()
    for p in deceased:
        acc = p.get("Accidental Death", "").strip().upper()
        if acc == "Y":
            continue
        cause = p.get("Mort / cause note", "").strip()
        if not cause:
            cause = "Not specified"
        cause_counter[cause] += 1
    for cause, cnt in sorted(cause_counter.items(), key=lambda x: -x[1]):
        c_short = cause[:70]
        print(f"  {c_short:70s}  {cnt}")
    print()

    # --- Space Grandpa ---
    print('"SPACE GRANDPA" STATUS (active at 80+)')
    print("-" * 40)
    sg_y = sum(1 for p in all_people if p.get("Space Grandpa", "").strip().upper() == "Y")
    sg_n = sum(1 for p in all_people if p.get("Space Grandpa", "").strip().upper() == "N")
    print(f"  Space Grandpa (Y):  {sg_y:3d}")
    print(f"  Not (N):            {sg_n:3d}")
    reached_80 = sum(1 for p in all_people
                     if (parse_float(p.get("Current Age or Age at Death", "")) or 0) >= 80)
    print(f"  Reached age 80:     {reached_80:3d}")
    if reached_80:
        print(f"  SG rate among 80+:  {100*sg_y/reached_80:.1f}%")
    print()

    # --- Sub-group comparison table ---
    print("SUB-GROUP COMPARISON TABLE")
    print("-" * 72)
    header = f"{'Group':25s} {'N':>3s} {'BirthYr':>8s} {'SelAge':>7s} {'%Flew':>6s} {'%Liv':>5s} {'%Acc':>5s} {'MedAge':>7s}"
    print(header)
    print("-" * 72)

    by_source = defaultdict(list)
    for p in all_people:
        by_source[p["_source"]].append(p)

    for label in ["Non-Apollo NASA", "X-15 Pilots", "Dyna-Soar Pilots", "MOL-Only"]:
        grp = by_source[label]
        n = len(grp)
        bys = [int(p.get("Birth Year", 0)) for p in grp if p.get("Birth Year")]
        sels = [parse_float(p.get("Age at Selection", "")) for p in grp]
        sels = [s for s in sels if s]
        flew_pct = 100 * sum(1 for p in grp if p.get("Went to Space", "").strip().upper() == "Y") / n if n else 0
        liv_pct = 100 * sum(1 for p in grp if p.get("Status", "").strip().lower() == "living") / n if n else 0
        dec = [p for p in grp if p.get("Status", "").strip().lower() == "deceased"]
        acc_pct = 100 * sum(1 for p in dec if p.get("Accidental Death", "").strip().upper() == "Y") / len(dec) if dec else 0
        ages = [parse_float(p.get("Current Age or Age at Death", "")) for p in grp]
        ages = [a for a in ages if a]
        med_age = statistics.median(ages) if ages else 0

        by_mean = f"{statistics.mean(bys):.0f}" if bys else "N/A"
        sel_mean = f"{statistics.mean(sels):.1f}" if sels else "N/A"

        print(f"  {label:23s} {n:3d} {by_mean:>8s} {sel_mean:>7s} {flew_pct:5.1f}% {liv_pct:4.1f}% {acc_pct:4.1f}% {med_age:6.1f}")

    # Now all combined
    bys_all = [int(p.get("Birth Year", 0)) for p in all_people if p.get("Birth Year")]
    sels_all = [parse_float(p.get("Age at Selection", "")) for p in all_people]
    sels_all = [s for s in sels_all if s]
    flew_pct_all = 100 * len(flew) / N
    liv_pct_all = 100 * len(living) / N
    acc_pct_all = 100 * len(accidental_deaths) / len(deceased) if deceased else 0
    ages_all = [parse_float(p.get("Current Age or Age at Death", "")) for p in all_people]
    ages_all = [a for a in ages_all if a]
    print("-" * 72)
    print(f"  {'ALL COMBINED':23s} {N:3d} {statistics.mean(bys_all):.0f}  {statistics.mean(sels_all):>7.1f} {flew_pct_all:5.1f}% {liv_pct_all:4.1f}% {acc_pct_all:4.1f}% {statistics.median(ages_all):6.1f}")
    print()

    # --- Individual roster ---
    print("FULL ROSTER — SORTED BY BIRTH YEAR")
    print("=" * 110)
    header = f"{'#':>3s}  {'Name':45s} {'Born':>6s} {'Group':>25s} {'Branch':>12s} {'Status':>8s} {'Age':>5s}"
    print(header)
    print("-" * 110)
    sorted_people = sorted(all_people, key=lambda p: p.get("Birth Year", "0"))
    for i, p in enumerate(sorted_people, 1):
        name = p["Name"][:45]
        born = p.get("Birth Year", "?")
        grp = p.get("Astronaut Group", "?")
        if len(grp) > 25:
            grp = grp[:25]
        branch = classify_branch(p.get("Military Branch", ""))
        status = p.get("Status", "?")
        age = p.get("Current Age or Age at Death", "?")
        try:
            age = f"{float(age):.1f}"
        except (ValueError, TypeError):
            pass
        print(f"{i:3d}  {name:45s} {born:>6s} {grp:>25s} {branch:>12s} {status:>8s} {age:>5s}")

    print()
    print("=" * 72)
    print("Script: non_apollo_demographics.py")
    print("Data sources: 03E, 09, 10, 11 enriched TSVs")
    print("No source files were modified.")
    print("=" * 72)


if __name__ == "__main__":
    main()
