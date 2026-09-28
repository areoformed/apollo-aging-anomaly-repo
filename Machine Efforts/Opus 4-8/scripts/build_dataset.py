#!/usr/bin/env python3
"""
build_dataset.py — Construct the canonical analysis dataset for the Opus 4-8
SuperAger re-analysis.

Merges GPT-5.5 person_level_analysis.csv (the trusted person-level endpoints:
endpoint_age, deceased, accidental flags, reached_80/90, space_grandpa) with the
"Went to Space" flag from the enriched TSVs (needed for flew-restricted cohorts).

Adds:
  - flew (bool)                  : did the person fly in space (any vehicle)
  - flew_nasa (bool)            : flew AND was a NASA selection (not X-15-only wings)
  - superager (bool)            : reached_80 AND space_grandpa=='Y'  (PUBLIC-EVIDENCE proxy)
  - cohort label fields          : apollo / nasa_nonapollo / x15 / dyna_soar / mol
  - selection_group (cleaned)

Writes: outputs of this script go to ../data/analysis_dataset.csv

PROVENANCE: read-only on all source paths. Output only under Opus 4-8/.
"""
import csv, os, sys, re
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "Claude Compiled - Opus 4-6 and GPT 5-5 Processed Data")
ENR = os.path.join(SRC, "Final - Analysis - Enriched Datasets")
GPT = os.path.join(ROOT, "GPT 5-5", "outputs", "apollo_mortality_survival_analysis_2026-06-04")
OUTDATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(OUTDATA, exist_ok=True)

# ---- 1. Load GPT-5.5 person-level (trusted endpoints) ----
pl = pd.read_csv(os.path.join(GPT, "person_level_analysis.csv"))
print(f"[load] person_level_analysis.csv: {len(pl)} rows")

# ---- 2. Load enriched TSVs, collect Name -> Went to Space, plus DoB/AgeSel ----
enriched_files = {
    "07E-lunar-enriched.tsv": "apollo",
    "08E-non-lunar-apollo-enriched.tsv": "apollo",
    "03E-non-apollo-enriched.tsv": "nasa_nonapollo",
    "09-x15-pilots-enriched.tsv": "x15",
    "10-dyna-soar-pilots-enriched.tsv": "dyna_soar",
    "11-mol-full-enriched.tsv": "mol",
}
enr_rows = []
for fn, cohort in enriched_files.items():
    with open(os.path.join(ENR, fn), newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            nm = (r.get("Name") or "").strip()
            if not nm:
                continue
            enr_rows.append({
                "name": nm,
                "enr_cohort": cohort,
                "went_to_space": (r.get("Went to Space") or "").strip().upper(),
                "selection_group": (r.get("Astronaut Group") or "").strip(),
                "age_at_selection": (r.get("Age at Selection") or "").strip(),
                "sg_enriched": (r.get("Space Grandpa") or "").strip().upper(),
                "accidental_enriched": (r.get("Accidental Death") or "").strip().upper(),
            })
enr = pd.DataFrame(enr_rows)
print(f"[load] enriched rows total: {len(enr)}")

# Alias normalization for the one known alias (McCandless long form -> canonical)
ALIAS = {
    "Byron Willis McCandless (later Bruce McCandless II)": "Bruce McCandless II",
}
enr["name"] = enr["name"].replace(ALIAS)

# ---- 3. Map person-CSV source_key -> our cohort label, for join keying ----
def cohort_from_sourcekey(sk):
    if sk in ("apollo_lunar", "apollo_non_lunar"):
        return "apollo"
    if sk == "other_core_nasa":
        return "nasa_nonapollo"
    if sk == "military_x15":
        return "x15"
    if sk == "military_dyna_soar":
        return "dyna_soar"
    if sk == "military_mol":
        return "mol"
    return "other"
pl["cohort"] = pl["source_key"].map(cohort_from_sourcekey)

# ---- 4. Join on (name, cohort). Both sides keyed identically. ----
merged = pl.merge(
    enr[["name", "enr_cohort", "went_to_space", "selection_group",
         "age_at_selection", "sg_enriched", "accidental_enriched"]],
    left_on=["name", "cohort"], right_on=["name", "enr_cohort"],
    how="left", validate="one_to_one",
)

# ---- 5. Integrity checks on the merge ----
n_missing = merged["went_to_space"].isna().sum()
print(f"[merge] rows with NO enriched match (went_to_space NaN): {n_missing}")
if n_missing:
    print(merged.loc[merged["went_to_space"].isna(), ["name", "cohort", "source_key"]].to_string())

# Cross-check: space_grandpa in person-CSV vs enriched SG (must agree where both present)
both = merged.dropna(subset=["sg_enriched"]).copy()
both["sg_pl"] = both["space_grandpa"].str.strip().str.upper()
disagree = both[both["sg_pl"] != both["sg_enriched"]]
print(f"[check] SG disagreements person-CSV vs enriched: {len(disagree)}")
if len(disagree):
    print(disagree[["name", "cohort", "sg_pl", "sg_enriched"]].to_string())

# ---- 6. Derive analysis fields ----
merged["flew"] = (merged["went_to_space"] == "Y")
# flew_nasa: flew AND a NASA selection (apollo or nasa_nonapollo). X-15 wings excluded here.
merged["is_nasa_selection"] = merged["cohort"].isin(["apollo", "nasa_nonapollo"])
merged["flew_nasa"] = merged["flew"] & merged["is_nasa_selection"]

# SuperAger phenotype (PUBLIC-EVIDENCE proxy): reached 80 AND space_grandpa == 'Y'
merged["sg_y"] = (merged["space_grandpa"].str.strip().str.upper() == "Y")
merged["superager"] = merged["reached_80"].astype(bool) & merged["sg_y"]

# Clean selection group (strip the "Group N — " noise to short label where present)
def short_group(g):
    if not isinstance(g, str) or not g:
        return ""
    # e.g. "Group 1 — Mercury Seven" -> "Mercury Seven"; "X-20 Dyna-Soar Pilot" stays
    m = re.match(r"Group\s+\d+\s*[—-]\s*(.+)", g)
    return m.group(1).strip() if m else g.strip()
merged["selection_group_short"] = merged["selection_group"].map(short_group)

# is_apollo convenience
merged["is_apollo"] = (merged["cohort"] == "apollo")

# ---- 7. Sanity: cohort counts ----
print("\n[summary] cohort counts:")
print(merged["cohort"].value_counts().to_string())
print(f"\n[summary] Apollo N={int((merged.cohort=='apollo').sum())}, "
      f"reached80={int(merged.loc[merged.is_apollo,'reached_80'].sum())}, "
      f"SuperAgers={int(merged.loc[merged.is_apollo,'superager'].sum())}")

# ---- 8. Write ----
keep = ["name", "cohort", "source_key", "source_label", "astronaut_group",
        "selection_group", "selection_group_short", "date_of_birth", "date_of_death",
        "endpoint_age", "deceased", "accidental_death", "pre1970_accidental_death",
        "included_in_apollo_vs_other_available", "went_to_space", "flew", "flew_nasa",
        "is_nasa_selection", "reached_80", "reached_90", "space_grandpa", "sg_y",
        "superager", "is_apollo", "age_at_selection", "cause_note"]
out = merged[keep].copy()
outpath = os.path.join(OUTDATA, "analysis_dataset.csv")
out.to_csv(outpath, index=False)
print(f"\n[write] {outpath}  ({len(out)} rows, {len(keep)} cols)")
