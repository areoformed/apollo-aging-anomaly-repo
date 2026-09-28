#!/usr/bin/env python3
"""Apply scoped corrections for DATA-INTEGRITY-ERROR-LOG items E003-E017."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "Final - Analysis - Enriched Datasets"
STD = FINAL / "Standardized Searches"
DATA = ROOT / "data"

CORE_FILES = [
    FINAL / "03E-non-apollo-enriched.tsv",
    FINAL / "07E-lunar-enriched.tsv",
    FINAL / "08E-non-lunar-apollo-enriched.tsv",
]
ALL_ENRICHED_FILES = CORE_FILES + [
    FINAL / "09-x15-pilots-enriched.tsv",
    FINAL / "10-dyna-soar-pilots-enriched.tsv",
    FINAL / "11-mol-full-enriched.tsv",
]
RAW_CORE_FILES = [
    DATA / "01-all-pre-1970-astronauts.tsv",
    DATA / "02-deduplicated-pre-1970.tsv",
    DATA / "03-non-apollo-astronauts.tsv",
    DATA / "04-non-apollo-flew.tsv",
    DATA / "05-non-apollo-never-flew.tsv",
]
RAW_REFERENCE_FILES = [
    DATA / "06-apollo-applications.tsv",
    DATA / "07-lunar-astronauts.tsv",
    DATA / "08-non-lunar-apollo.tsv",
]

SG_UPGRADES_FROM_STANDARDIZED = {
    # Keep Curt Michel as Y for now because the standardized recommendation is low-confidence
    # and conflicts with existing current-data evidence.
    "Neil Armstrong",
    "Eugene Cernan",
    "James McDivitt",
    "Walter Schirra",
    "Philip Chapman",
    "Anthony England",
    "Duane Graveline",
    "William Thornton",
}

PRESERVED_08E_RATIONALES = {
    "Walter Marty Schirra Jr.": "Contributed to books at 82-84 but limited evidence of physical activities in final years",
    "James Alton McDivitt Jr.": "Appeared at Apollo 9 50th anniversary at 89 but limited documented evidence of sustained high acuity beyond commemorative events",
}


def split_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    lines = path.read_text().splitlines()
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if not line:
            continue
        values = line.split("\t")
        if len(values) != len(header):
            raise ValueError(f"{path}: expected {len(header)} columns, got {len(values)}")
        rows.append(dict(zip(header, values)))
    return header, rows


def write_table(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.write_text(
        "\n".join("\t".join(row.get(col, "") for col in header) for row in [dict(zip(header, header))] + rows)
        + "\n"
    )


def line_map(path: Path) -> dict[str, int]:
    out = {}
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if lineno == 1 or not line:
            continue
        out[line.split("\t", 1)[0]] = lineno
    return out


def norm_name(value: str) -> str:
    value = re.sub(r"\([^)]*\)", "", value)
    value = value.replace('"', "")
    value = re.sub(r"\b(later|jr|sr|ii|iii|iv)\b\.?", "", value, flags=re.I)
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def surname_key(value: str) -> str:
    parts = norm_name(value).split()
    return parts[-1] if parts else ""


def wiki_slug(row: dict[str, str]) -> str:
    citations = row.get("Citations", "")
    match = re.search(r"https://en\.wikipedia\.org/wiki/([^;\s]+)", citations)
    if match:
        return "wiki:" + match.group(1)
    return "name:" + re.sub(r"[^a-z0-9]+", "-", row["Name"].lower()).strip("-")


def build_final_index() -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, list[str]], dict[str, str]]:
    by_norm = {}
    by_canonical = {}
    by_surname: dict[str, list[str]] = {}
    person_ids = {}
    for path in CORE_FILES:
        _, rows = split_table(path)
        lines = line_map(path)
        for row in rows:
            row["_final_file"] = str(path.relative_to(ROOT))
            row["_final_line"] = str(lines[row["Name"]])
            key = norm_name(row["Name"])
            by_norm[key] = row
            by_canonical[row["Name"]] = key
            by_surname.setdefault(surname_key(row["Name"]), []).append(key)
            person_ids[row["Name"]] = wiki_slug(row)
    return by_norm, by_canonical, by_surname, person_ids


def match_final(name: str, by_norm: dict[str, dict[str, str]], by_surname: dict[str, list[str]]) -> tuple[dict[str, str], str]:
    key = norm_name(name)
    if key in by_norm:
        return by_norm[key], "normalized_name"
    surname = surname_key(name)
    matches = by_surname.get(surname, [])
    if len(matches) == 1:
        return by_norm[matches[0]], "unique_surname"
    raise KeyError(f"Could not match {name!r}; surname matches={matches}")


def standardized_recommendations() -> dict[str, dict[str, str]]:
    aliases = {
        "James McDivitt": "James Alton McDivitt Jr.",
        "Walter Schirra": "Walter Marty Schirra Jr.",
        "Philip Chapman": "Philip Kenyon Chapman",
        "Anthony England": "Anthony Wayne England",
        "Duane Graveline": 'Duane Edgar "Doc" Graveline',
        "William Thornton": "William Edgar Thornton",
        "Curt Michel": "Frank Curtis Michel",
    }
    out = {}
    for path in [
        STD / "SG-standardized-searches-lunar.tsv",
        STD / "SG-standardized-searches-control.tsv",
    ]:
        with path.open(newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                final_name = aliases.get(row["Name"], row["Name"])
                out[final_name] = row
    return out


def update_final_enriched(std_recs: dict[str, dict[str, str]]) -> dict[str, int]:
    counts = {"sg_upgraded": 0, "sg_n_citations_added": 0, "mort_header_renamed": 0, "time_fixed": 0}
    for path in ALL_ENRICHED_FILES:
        header, rows = split_table(path)
        if "Mort" in header:
            header[header.index("Mort")] = "Mort / cause note"
            for row in rows:
                row["Mort / cause note"] = row.pop("Mort")
            counts["mort_header_renamed"] += 1

        for row in rows:
            rec = std_recs.get(row["Name"])
            short_name = None
            if rec and rec["Name"] in SG_UPGRADES_FROM_STANDARDIZED and rec["Recommended SG"] == "Y":
                short_name = rec["Name"]
            elif row["Name"] in SG_UPGRADES_FROM_STANDARDIZED and rec and rec["Recommended SG"] == "Y":
                short_name = row["Name"]

            if short_name and row["Space Grandpa"] != "Y":
                row["Space Grandpa"] = "Y"
                urls = rec.get("Evidence URLs", "")
                row["Space Grandpa Citation"] = (
                    f"Standardized-search audit (2026-05-23): {rec['Key Evidence']}. Sources: {urls}"
                )
                counts["sg_upgraded"] += 1

            if row["Name"] == "Robert Michael White" and row.get("Time in Space") == "unknown":
                row["Time in Space"] = "Suborbital only"
                counts["time_fixed"] += 1

            if row.get("Space Grandpa") == "N" and not row.get("Space Grandpa Citation", "").strip():
                if row["Name"] in PRESERVED_08E_RATIONALES:
                    row["Space Grandpa Citation"] = PRESERVED_08E_RATIONALES[row["Name"]]
                else:
                    try:
                        age = float(row.get("Current Age or Age at Death", "nan"))
                    except ValueError:
                        age = float("nan")
                    if age < 80:
                        row["Space Grandpa Citation"] = "Did not reach age 80; no qualifying 80+ activity possible."
                    else:
                        row["Space Grandpa Citation"] = (
                            "No documented qualifying 80+ activity in current final dataset; "
                            "retain SG=N unless new evidence is adjudicated."
                        )
                counts["sg_n_citations_added"] += 1

        write_table(path, header, rows)
    return counts


def update_raw_files(
    by_norm: dict[str, dict[str, str]],
    by_surname: dict[str, list[str]],
    person_ids: dict[str, str],
) -> dict[str, int]:
    counts = {"date_filled": 0, "group_fixed": 0, "mission_fixed": 0, "went_fixed": 0, "alias_rows": 0}
    alias_rows = []

    for path in RAW_CORE_FILES + RAW_REFERENCE_FILES:
        header, rows = split_table(path)
        lines = line_map(path)
        for row in rows:
            final_row, method = match_final(row["Name"], by_norm, by_surname)
            if row["Name"] != final_row["Name"]:
                counts["alias_rows"] += 1
            alias_rows.append(
                {
                    "person_id": person_ids[final_row["Name"]],
                    "canonical_name": final_row["Name"],
                    "final_file": final_row["_final_file"],
                    "final_line": final_row["_final_line"],
                    "raw_file": str(path.relative_to(ROOT)),
                    "raw_line": str(lines[row["Name"]]),
                    "raw_name": row["Name"],
                    "match_method": method,
                }
            )

            if "Astronaut Group" in header and row.get("Astronaut Group") != final_row["Astronaut Group"]:
                row["Astronaut Group"] = final_row["Astronaut Group"]
                counts["group_fixed"] += 1

            for col, final_col in [
                ("Date of Birth", "Date of Birth"),
                ("Date of Selection", "Date of Selection"),
            ]:
                if col in header and row.get(col) != final_row[final_col]:
                    row[col] = final_row[final_col]
                    counts["date_filled"] += 1

            if path in RAW_CORE_FILES:
                if row.get("Went to Space") != final_row["Went to Space"]:
                    row["Went to Space"] = final_row["Went to Space"]
                    counts["went_fixed"] += 1
                if row.get("Missions Flown") != final_row["Missions Flown"]:
                    row["Missions Flown"] = final_row["Missions Flown"]
                    counts["mission_fixed"] += 1

        write_table(path, header, rows)

    alias_header = [
        "person_id",
        "canonical_name",
        "final_file",
        "final_line",
        "raw_file",
        "raw_line",
        "raw_name",
        "match_method",
    ]
    write_table(DATA / "person-id-alias-map-2026-05-24.tsv", alias_header, alias_rows)
    return counts


def update_standardized_current_sg() -> dict[str, int]:
    aliases = {
        "James McDivitt",
        "Walter Schirra",
        "Philip Chapman",
        "Anthony England",
        "Duane Graveline",
        "William Thornton",
        "Neil Armstrong",
        "Eugene Cernan",
    }
    counts = {"standardized_current_updated": 0}
    for path in [
        STD / "SG-standardized-searches-lunar.tsv",
        STD / "SG-standardized-searches-control.tsv",
    ]:
        header, rows = split_table(path)
        for row in rows:
            if row["Name"] in aliases and row["Recommended SG"] == "Y" and row["Current SG"] != "Y":
                row["Current SG"] = "Y"
                counts["standardized_current_updated"] += 1
        write_table(path, header, rows)
    return counts


def update_sg_existing_sources(std_recs: dict[str, dict[str, str]]) -> dict[str, int]:
    path = DATA / "SG-audit-existing-sources.tsv"
    header, rows = split_table(path)
    if "Status" not in header:
        idx = header.index("Death Date") + 1
        header.insert(idx, "Status")
    counts = {"living_sentinel_removed": 0, "sg_existing_updated": 0}
    aliases = {
        "Neil Armstrong": "Neil Armstrong",
        "Eugene Cernan": "Eugene Cernan",
        "Walter Marty Schirra Jr.": "Walter Schirra",
        "James Alton McDivitt Jr.": "James McDivitt",
        "Philip Kenyon Chapman": "Philip Chapman",
        "Anthony Wayne England": "Anthony England",
        'Duane Edgar "Doc" Graveline': "Duane Graveline",
        "William Edgar Thornton": "William Thornton",
    }
    for row in rows:
        if row.get("Death Date") == "Living":
            row["Death Date"] = ""
            row["Status"] = "Living"
            counts["living_sentinel_removed"] += 1
        elif not row.get("Status"):
            row["Status"] = "Deceased"

        rec_name = aliases.get(row["Name"])
        if rec_name:
            final_rec = None
            for canonical, rec in std_recs.items():
                if rec["Name"] == rec_name:
                    final_rec = rec
                    break
            if final_rec and final_rec["Recommended SG"] == "Y" and row["Current SG Classification"] != "Y":
                row["Current SG Classification"] = "Y"
                row["SG Citation"] = f"{final_rec['Key Evidence']}. Sources: {final_rec.get('Evidence URLs', '')}"
                row["Sources Consulted"] = "Standardized search audit + URL evidence"
                row["Evidence Strength"] = "Strong" if final_rec["Confidence"] == "High" else "Moderate"
                row["Notes"] = "Updated from SG=N on 2026-05-24 using standardized-search evidence."
                counts["sg_existing_updated"] += 1
    write_table(path, header, rows)
    return counts


def normalize_ssa_table() -> dict[str, int]:
    path = DATA / "ssa-1930-male-cohort-lifetable.tsv"
    lines = path.read_text().splitlines()
    comment_lines = [line for line in lines if line.startswith("#")]
    data_lines = [line for line in lines if not line.startswith("#")]
    metadata = DATA / "ssa-1930-male-cohort-lifetable-metadata.md"
    if comment_lines:
        metadata.write_text(
            "# SSA 1930 Male Cohort Life Table Metadata\n\n"
            + "\n".join(line.lstrip("# ").rstrip() for line in comment_lines)
            + "\n"
        )
        path.write_text("\n".join(data_lines).lstrip("\n") + "\n")
    return {"ssa_comment_lines_moved": len(comment_lines)}


def write_row_provenance(person_ids: dict[str, str]) -> dict[str, int]:
    out_rows = []
    for path in ALL_ENRICHED_FILES:
        header, rows = split_table(path)
        lines = line_map(path)
        for row in rows:
            out_rows.append(
                {
                    "person_id": person_ids.get(row["Name"], wiki_slug(row)),
                    "source_file": str(path.relative_to(ROOT)),
                    "source_line": str(lines[row["Name"]]),
                    "name": row["Name"],
                    "citation_urls": row.get("Citations", ""),
                    "mort_or_cause_note": row.get("Mort / cause note", row.get("Mort", "")),
                    "mort_or_cause_note_provenance": "Derived from row citation/cached biography sources; specificity varies by public disclosure.",
                    "sg_value": row.get("Space Grandpa", ""),
                    "sg_rationale": row.get("Space Grandpa Citation", ""),
                    "sg_provenance": "Space Grandpa Citation field plus standardized-search files where applicable.",
                    "career_education_provenance": "Pre-NASA Career, Education, and Post-NASA Career were derived from row citation/cached biography sources.",
                    "provenance_status": "Row-level source pointer; original enrichment was not a deterministic extraction pipeline.",
                }
            )
    header = [
        "person_id",
        "source_file",
        "source_line",
        "name",
        "citation_urls",
        "mort_or_cause_note",
        "mort_or_cause_note_provenance",
        "sg_value",
        "sg_rationale",
        "sg_provenance",
        "career_education_provenance",
        "provenance_status",
    ]
    write_table(DATA / "enriched-row-provenance-2026-05-24.tsv", header, out_rows)
    return {"provenance_rows": len(out_rows)}


def main() -> None:
    by_norm, _, by_surname, person_ids = build_final_index()
    std_recs = standardized_recommendations()
    summary = {}
    for result in [
        update_final_enriched(std_recs),
        update_raw_files(by_norm, by_surname, person_ids),
        update_standardized_current_sg(),
        update_sg_existing_sources(std_recs),
        normalize_ssa_table(),
        write_row_provenance(person_ids),
    ]:
        summary.update(result)

    for key in sorted(summary):
        print(f"{key}: {summary[key]}")


if __name__ == "__main__":
    main()
