#!/usr/bin/env python3
"""
generate_lifespan_charts.py
---------------------------
Generates publication-quality distribution charts comparing Apollo 7-17
astronaut lifespans against the non-Apollo cohort (after excluding
pre-1970 accidental deaths from both groups).

Outputs PNG files to 'Claude Generated Graphs/'.
Read-only on source data — does NOT modify any TSV files.

Usage:  python3 generate_lifespan_charts.py
"""

import csv
import statistics
from pathlib import Path
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

BASE = Path("./Claude Compiled Data")
ENRICHED = BASE / "Final - Analysis - Enriched Datasets"
OUT = BASE / "Claude Generated Graphs"

NON_APOLLO_FILES = {
    "Non-Apollo NASA": ENRICHED / "03E-non-apollo-enriched.tsv",
    "X-15 Pilots":     ENRICHED / "09-x15-pilots-enriched.tsv",
    "Dyna-Soar Pilots": ENRICHED / "10-dyna-soar-pilots-enriched.tsv",
    "MOL-Only":        ENRICHED / "11-mol-full-enriched.tsv",
}

APOLLO_FILES = {
    "Lunar Apollo":     ENRICHED / "07E-lunar-enriched.tsv",
    "Non-Lunar Apollo": ENRICHED / "08E-non-lunar-apollo-enriched.tsv",
}

APOLLO_COLOR = "#2D6A9F"
NON_APOLLO_COLOR = "#B85C3A"
LIVING_ALPHA = 0.45
BG_COLOR = "#FAFAF7"
GRID_COLOR = "#D5D5D0"

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
    for fmt in ("%Y-%m-%d",):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None

def load_cohort(file_dict):
    people = []
    for label, path in file_dict.items():
        for r in load_tsv(path):
            r["_source"] = label
            people.append(r)
    return people

def exclude_pre1970_accidents(people):
    retained = []
    for p in people:
        acc = p.get("Accidental Death", "").strip().upper() == "Y"
        dod = parse_date(p.get("Date of Death", ""))
        if acc and dod and dod.year < 1970:
            continue
        retained.append(p)
    return retained

def extract_ages(people):
    dead_nat = []
    dead_acc = []
    living = []
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

def style_ax(ax):
    ax.set_facecolor(BG_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")
    ax.tick_params(colors="#555555", labelsize=10)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)


# ── Load and filter ──────────────────────────────────────────────────

apollo_all = load_cohort(APOLLO_FILES)
nonapollo_all = load_cohort(NON_APOLLO_FILES)

apollo = exclude_pre1970_accidents(apollo_all)
nonapollo = exclude_pre1970_accidents(nonapollo_all)

ap_nat, ap_acc, ap_liv = extract_ages(apollo)
na_nat, na_acc, na_liv = extract_ages(nonapollo)

ap_all_ages = ap_nat + ap_acc + ap_liv
na_all_ages = na_nat + na_acc + na_liv

ap_nonacc = ap_nat + ap_liv
na_nonacc = na_nat + na_liv

edges_5 = np.arange(50, 102.5, 5)
edges_centers = (edges_5[:-1] + edges_5[1:]) / 2


# ════════════════════════════════════════════════════════════════════
# CHART 1: Side-by-side histogram — all causes (dead + living)
# ════════════════════════════════════════════════════════════════════

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
fig.patch.set_facecolor(BG_COLOR)

for ax, ages, color, label, n_total in [
    (ax1, ap_all_ages, APOLLO_COLOR, "Apollo 7–17", len(apollo)),
    (ax2, na_all_ages, NON_APOLLO_COLOR, "Non-Apollo", len(nonapollo)),
]:
    style_ax(ax)
    counts, _, bars = ax.hist(ages, bins=edges_5, color=color, alpha=0.85,
                              edgecolor="white", linewidth=1.2, rwidth=0.88)
    ax.set_xlabel("Age", fontsize=12, color="#333333")
    ax.set_title(f"{label}  (N={n_total})", fontsize=14, fontweight="bold",
                 color="#222222", pad=12)
    ax.set_xlim(48, 100)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                    str(int(count)), ha="center", va="bottom", fontsize=9,
                    color="#333333", fontweight="bold")

ax1.set_ylabel("Number of Astronauts", fontsize=12, color="#333333")

fig.suptitle("Age Distribution: Apollo vs Non-Apollo Astronauts\n"
             "(Pre-1970 accidental deaths excluded  ·  Living shown at current age)",
             fontsize=15, fontweight="bold", color="#111111", y=1.02)
fig.tight_layout()
fig.savefig(OUT / "01_side_by_side_histogram.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 01_side_by_side_histogram.png")


# ════════════════════════════════════════════════════════════════════
# CHART 2: Overlaid histogram — non-accidental dead + living
# ════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(BG_COLOR)
style_ax(ax)

width = 2.0
offsets_ap = edges_centers - width / 2
offsets_na = edges_centers + width / 2

ap_counts, _ = np.histogram(ap_nonacc, bins=edges_5)
na_counts, _ = np.histogram(na_nonacc, bins=edges_5)

bars_ap = ax.bar(offsets_ap, ap_counts, width=width, color=APOLLO_COLOR, alpha=0.85,
                 edgecolor="white", linewidth=1, label=f"Apollo 7–17 (N={len(ap_nonacc)})")
bars_na = ax.bar(offsets_na, na_counts, width=width, color=NON_APOLLO_COLOR, alpha=0.85,
                 edgecolor="white", linewidth=1, label=f"Non-Apollo (N={len(na_nonacc)})")

for bars, counts in [(bars_ap, ap_counts), (bars_na, na_counts)]:
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                    str(int(count)), ha="center", va="bottom", fontsize=9,
                    color="#333333", fontweight="bold")

ax.set_xlabel("Age", fontsize=12, color="#333333")
ax.set_ylabel("Number of Astronauts", fontsize=12, color="#333333")
ax.set_xlim(48, 100)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.legend(fontsize=11, frameon=True, facecolor="white", edgecolor="#CCCCCC",
          loc="upper left")

ax.set_title("Non-Accidental Deaths + Living Survivors\n"
             "(Pre-1970 accidents excluded  ·  Living at current age)",
             fontsize=14, fontweight="bold", color="#111111", pad=14)
fig.tight_layout()
fig.savefig(OUT / "02_overlaid_histogram.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 02_overlaid_histogram.png")


# ════════════════════════════════════════════════════════════════════
# CHART 3: Stacked bar — dead vs living within each bin
# ════════════════════════════════════════════════════════════════════

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
fig.patch.set_facecolor(BG_COLOR)

for ax, nat, liv, color, label in [
    (ax1, ap_nat, ap_liv, APOLLO_COLOR, "Apollo 7–17"),
    (ax2, na_nat, na_liv, NON_APOLLO_COLOR, "Non-Apollo"),
]:
    style_ax(ax)
    dead_counts, _ = np.histogram(nat, bins=edges_5)
    live_counts, _ = np.histogram(liv, bins=edges_5)

    ax.bar(edges_centers, dead_counts, width=4, color=color, alpha=0.9,
           edgecolor="white", linewidth=1, label="Deceased (non-accidental)")
    ax.bar(edges_centers, live_counts, width=4, bottom=dead_counts,
           color=color, alpha=0.35, edgecolor="white", linewidth=1,
           hatch="///", label="Living (current age)")

    for x, d, l in zip(edges_centers, dead_counts, live_counts):
        total = d + l
        if total > 0:
            ax.text(x, total + 0.15, str(int(total)), ha="center", va="bottom",
                    fontsize=9, color="#333333", fontweight="bold")

    n_total = len(nat) + len(liv)
    ax.set_ylabel("Count", fontsize=11, color="#333333")
    ax.set_title(f"{label}  (N={n_total}: {len(nat)} deceased, {len(liv)} living)",
                 fontsize=13, fontweight="bold", color="#222222", pad=10)
    ax.legend(fontsize=10, frameon=True, facecolor="white", edgecolor="#CCCCCC",
              loc="upper left")
    ax.set_xlim(48, 100)

ax2.set_xlabel("Age (5-year bins)", fontsize=12, color="#333333")
ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))

fig.suptitle("Lifespan Distribution: Deceased vs Still Living\n"
             "(Pre-1970 accidental deaths excluded)",
             fontsize=15, fontweight="bold", color="#111111", y=1.01)
fig.tight_layout()
fig.savefig(OUT / "03_stacked_dead_living.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 03_stacked_dead_living.png")


# ════════════════════════════════════════════════════════════════════
# CHART 4: Dot / strip chart — every individual
# ════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(14, 5))
fig.patch.set_facecolor(BG_COLOR)
style_ax(ax)

def jitter_strip(ages_dead, ages_live, y_base, color, label):
    np.random.seed(42)
    for i, a in enumerate(sorted(ages_dead)):
        jit = np.random.uniform(-0.15, 0.15)
        ax.plot(a, y_base + jit, "o", color=color, markersize=7,
                markeredgecolor="white", markeredgewidth=0.8, alpha=0.85,
                label=f"{label} (deceased)" if i == 0 else "")
    for i, a in enumerate(sorted(ages_live)):
        jit = np.random.uniform(-0.15, 0.15)
        ax.plot(a, y_base + jit, "D", color=color, markersize=7,
                markeredgecolor="white", markeredgewidth=0.8, alpha=0.4,
                label=f"{label} (living)" if i == 0 else "")

jitter_strip(ap_nat + ap_acc, ap_liv, 2, APOLLO_COLOR, "Apollo 7–17")
jitter_strip(na_nat + na_acc, na_liv, 1, NON_APOLLO_COLOR, "Non-Apollo")

ap_med = statistics.median(ap_nonacc)
na_med = statistics.median(na_nonacc)
ax.axvline(ap_med, color=APOLLO_COLOR, linewidth=1.5, linestyle="--", alpha=0.7)
ax.axvline(na_med, color=NON_APOLLO_COLOR, linewidth=1.5, linestyle="--", alpha=0.7)
ax.text(ap_med + 0.5, 2.45, f"Median {ap_med:.1f}", fontsize=9,
        color=APOLLO_COLOR, fontweight="bold")
ax.text(na_med + 0.5, 0.55, f"Median {na_med:.1f}", fontsize=9,
        color=NON_APOLLO_COLOR, fontweight="bold")

ax.set_yticks([1, 2])
ax.set_yticklabels(["Non-Apollo\n(N=55)", "Apollo 7–17\n(N=29)"], fontsize=11)
ax.set_ylim(0.4, 2.7)
ax.set_xlim(48, 100)
ax.set_xlabel("Age at Death or Current Age (living)", fontsize=12, color="#333333")
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), fontsize=10, frameon=True,
          facecolor="white", edgecolor="#CCCCCC", loc="upper left", ncol=2)

ax.set_title("Individual Lifespan: Every Astronaut\n"
             "(Circles = deceased  ·  Diamonds = living  ·  "
             "Dashed lines = median  ·  Pre-1970 accidents excluded)",
             fontsize=13, fontweight="bold", color="#111111", pad=14)
fig.tight_layout()
fig.savefig(OUT / "04_dot_strip_chart.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 04_dot_strip_chart.png")


# ════════════════════════════════════════════════════════════════════
# CHART 5: Box + swarm comparison
# ════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 7))
fig.patch.set_facecolor(BG_COLOR)
style_ax(ax)

bp = ax.boxplot([na_nonacc, ap_nonacc], positions=[1, 2], widths=0.5,
                patch_artist=True, showmeans=True,
                meanprops=dict(marker="D", markerfacecolor="gold",
                               markeredgecolor="#333333", markersize=8),
                medianprops=dict(color="#111111", linewidth=2),
                whiskerprops=dict(color="#666666"),
                capprops=dict(color="#666666"),
                flierprops=dict(marker="o", markerfacecolor="#AAAAAA",
                                markeredgecolor="white", markersize=6))

bp["boxes"][0].set_facecolor(NON_APOLLO_COLOR)
bp["boxes"][0].set_alpha(0.3)
bp["boxes"][1].set_facecolor(APOLLO_COLOR)
bp["boxes"][1].set_alpha(0.3)

np.random.seed(99)
for pos, ages, color in [(1, na_nonacc, NON_APOLLO_COLOR),
                          (2, ap_nonacc, APOLLO_COLOR)]:
    jit = np.random.uniform(-0.12, 0.12, len(ages))
    ax.scatter(np.full(len(ages), pos) + jit, ages, color=color, alpha=0.6,
               s=30, edgecolors="white", linewidth=0.5, zorder=5)

ax.set_xticks([1, 2])
ax.set_xticklabels([f"Non-Apollo\n(N={len(na_nonacc)})",
                     f"Apollo 7–17\n(N={len(ap_nonacc)})"], fontsize=12)
ax.set_ylabel("Age at Death or Current Age", fontsize=12, color="#333333")
ax.yaxis.set_major_locator(ticker.MultipleLocator(5))

ap_mean = statistics.mean(ap_nonacc)
na_mean = statistics.mean(na_nonacc)
ax.text(1.35, na_med + 0.5, f"Median: {na_med:.1f}", fontsize=10,
        color=NON_APOLLO_COLOR, fontweight="bold")
ax.text(1.35, na_mean - 2, f"Mean: {na_mean:.1f}", fontsize=10,
        color=NON_APOLLO_COLOR)
ax.text(2.35, ap_med + 0.5, f"Median: {ap_med:.1f}", fontsize=10,
        color=APOLLO_COLOR, fontweight="bold")
ax.text(2.35, ap_mean - 2, f"Mean: {ap_mean:.1f}", fontsize=10,
        color=APOLLO_COLOR)

ax.set_title("Box Plot: Non-Accidental Deaths + Living\n"
             "(Diamond = mean  ·  Line = median  ·  Pre-1970 accidents excluded)",
             fontsize=13, fontweight="bold", color="#111111", pad=14)
fig.tight_layout()
fig.savefig(OUT / "05_box_swarm.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 05_box_swarm.png")


# ════════════════════════════════════════════════════════════════════
# CHART 6: Cumulative distribution (empirical CDF)
# ════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(BG_COLOR)
style_ax(ax)

for ages, color, label in [
    (sorted(ap_nonacc), APOLLO_COLOR, f"Apollo 7–17 (N={len(ap_nonacc)})"),
    (sorted(na_nonacc), NON_APOLLO_COLOR, f"Non-Apollo (N={len(na_nonacc)})"),
]:
    n = len(ages)
    y = np.arange(1, n + 1) / n
    ax.step(ages, y, color=color, linewidth=2.5, where="post", label=label)

ax.axhline(0.5, color="#999999", linewidth=1, linestyle=":", alpha=0.6)
ax.text(50, 0.51, "50th percentile", fontsize=9, color="#777777")
ax.set_xlabel("Age at Death or Current Age", fontsize=12, color="#333333")
ax.set_ylabel("Cumulative Proportion", fontsize=12, color="#333333")
ax.set_xlim(48, 100)
ax.set_ylim(0, 1.02)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
ax.legend(fontsize=12, frameon=True, facecolor="white", edgecolor="#CCCCCC",
          loc="upper left")

ax.set_title("Cumulative Distribution: Age at Death / Current Age\n"
             "(Non-accidental deaths + living  ·  Pre-1970 accidents excluded)",
             fontsize=14, fontweight="bold", color="#111111", pad=14)
fig.tight_layout()
fig.savefig(OUT / "06_cumulative_distribution.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 06_cumulative_distribution.png")


# ════════════════════════════════════════════════════════════════════
# CHART 7: Summary comparison table as image
# ════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG_COLOR)
ax.axis("off")

ap_bins5 = Counter(int(a // 5) * 5 for a in ap_nonacc)
na_bins5 = Counter(int(a // 5) * 5 for a in na_nonacc)
ap_mode5 = max(ap_bins5, key=ap_bins5.get)
na_mode5 = max(na_bins5, key=na_bins5.get)

table_data = [
    ["N (after pre-1970 accident exclusion)", str(len(ap_nonacc)), str(len(na_nonacc))],
    ["Mean age", f"{statistics.mean(ap_nonacc):.1f}", f"{statistics.mean(na_nonacc):.1f}"],
    ["Median age", f"{statistics.median(ap_nonacc):.1f}", f"{statistics.median(na_nonacc):.1f}"],
    ["Modal 5-year bin", f"{ap_mode5}–{ap_mode5+4}", f"{na_mode5}–{na_mode5+4}"],
    ["Std deviation", f"{statistics.stdev(ap_nonacc):.1f}", f"{statistics.stdev(na_nonacc):.1f}"],
    ["Q1 (25th pct)", f"{sorted(ap_nonacc)[len(ap_nonacc)//4]:.1f}",
     f"{sorted(na_nonacc)[len(na_nonacc)//4]:.1f}"],
    ["Q3 (75th pct)", f"{sorted(ap_nonacc)[3*len(ap_nonacc)//4]:.1f}",
     f"{sorted(na_nonacc)[3*len(na_nonacc)//4]:.1f}"],
    ["Still living", str(len(ap_liv)), str(len(na_liv))],
    ["Died 90+", str(sum(1 for a in ap_nat if a >= 90)),
     str(sum(1 for a in na_nat if a >= 90))],
]

col_labels = ["", "Apollo 7–17", "Non-Apollo"]
table = ax.table(cellText=table_data, colLabels=col_labels, loc="center",
                 cellLoc="center", colColours=[BG_COLOR, APOLLO_COLOR + "33",
                                                NON_APOLLO_COLOR + "33"])
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 1.8)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if row == 0:
        cell.set_text_props(fontweight="bold", fontsize=13)
        cell.set_facecolor("#E8E8E4")
    if col == 0:
        cell.set_text_props(ha="left")
        cell._loc = "left"

ax.set_title("Summary Comparison: Non-Accidental Deaths + Living\n"
             "(Pre-1970 accidental deaths excluded from both cohorts)",
             fontsize=14, fontweight="bold", color="#111111", pad=20)
fig.tight_layout()
fig.savefig(OUT / "07_summary_table.png", dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR)
plt.close(fig)
print("  Saved 07_summary_table.png")


print(f"\nAll charts saved to: {OUT}/")
