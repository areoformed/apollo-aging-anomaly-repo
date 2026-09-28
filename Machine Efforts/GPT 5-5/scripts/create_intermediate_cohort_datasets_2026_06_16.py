#!/usr/bin/env python3
"""
Create row-level intermediate datasets for named Apollo mortality-analysis cohorts.

The prior analysis used labels such as `other_all` and `all_astronauts` as
computed cohorts, not as input files. This script materializes those cohorts
from the locally archived input TSVs and writes them to:

    data/derived_cohorts/
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = (
    WORKSPACE_ROOT
    / "data"
    / "source_inputs"
    / "analysis_inputs_2026-06-16"
    / "upstream_processed_data"
)
ENRICHED_ROOT = ARCHIVE_ROOT / "Final - Analysis - Enriched Datasets"
OUT_ROOT = WORKSPACE_ROOT / "data" / "derived_cohorts"


@dataclass(frozen=True)
class SourceFile:
    key: str
    label: str
    primary: str
    filename: str

    @property
    def path(self) -> Path:
        return ENRICHED_ROOT / self.filename


SOURCE_FILES = [
    SourceFile(
        "other_core_nasa",
        "Core NASA non-Apollo",
        "other",
        "03E-non-apollo-enriched.tsv",
    ),
    SourceFile(
        "apollo_lunar",
        "Apollo lunar-program crew",
        "apollo",
        "07E-lunar-enriched.tsv",
    ),
    SourceFile(
        "apollo_non_lunar",
        "Apollo 7/9 non-lunar crew",
        "apollo",
        "08E-non-lunar-apollo-enriched.tsv",
    ),
    SourceFile(
        "military_x15",
        "X-15/high-speed pilots",
        "other",
        "09-x15-pilots-enriched.tsv",
    ),
    SourceFile(
        "military_dyna_soar",
        "X-20 Dyna-Soar pilots",
        "other",
        "10-dyna-soar-pilots-enriched.tsv",
    ),
    SourceFile(
        "military_mol",
        "MOL military astronauts",
        "other",
        "11-mol-full-enriched.tsv",
    ),
]


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    label: str
    relative_path: Path
    dataset_type: str
    construction: str
    predicate: Callable[[dict[str, str]], bool]


def parse_date(raw: str) -> datetime | None:
    raw = raw.strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def is_pre1970_accidental_death(row: dict[str, str]) -> bool:
    if row.get("Accidental Death", "").strip().upper() != "Y":
        return False
    death_date = parse_date(row.get("Date of Death", ""))
    return death_date is not None and death_date.year < 1970


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_people() -> tuple[list[dict[str, str]], list[str]]:
    people: list[dict[str, str]] = []
    original_fields: list[str] = []
    for source in SOURCE_FILES:
        with source.path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None:
                raise RuntimeError(f"Missing header: {source.path}")
            for field in reader.fieldnames:
                if field not in original_fields:
                    original_fields.append(field)
            for row_number, row in enumerate(reader, start=2):
                out = dict(row)
                out["analysis_source_key"] = source.key
                out["analysis_source_label"] = source.label
                out["analysis_primary"] = source.primary
                out["analysis_source_file"] = str(
                    source.path.relative_to(WORKSPACE_ROOT)
                )
                out["analysis_source_row_number"] = str(row_number)
                out["analysis_pre1970_accidental_death"] = (
                    "Y" if is_pre1970_accidental_death(out) else "N"
                )
                people.append(out)
    return people, original_fields


def write_tsv(path: Path, rows: list[dict[str, str]], original_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata_fields = [
        "analysis_dataset_key",
        "analysis_dataset_label",
        "analysis_dataset_type",
        "analysis_source_key",
        "analysis_source_label",
        "analysis_primary",
        "analysis_source_file",
        "analysis_source_row_number",
        "analysis_pre1970_accidental_death",
    ]
    fieldnames = metadata_fields + [
        field for field in original_fields if field not in metadata_fields
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def build_specs() -> list[DatasetSpec]:
    specs = [
        DatasetSpec(
            "other_all",
            "Other astronauts including military, all deaths",
            Path("cohorts/other_all.tsv"),
            "generated_cohort",
            "Rows where analysis_primary == 'other'; combines other_core_nasa, military_x15, military_dyna_soar, and military_mol.",
            lambda row: row["analysis_primary"] == "other",
        ),
        DatasetSpec(
            "all_astronauts",
            "All same-era astronauts including Apollo and military",
            Path("cohorts/all_astronauts.tsv"),
            "generated_cohort",
            "All loaded rows; equivalent to apollo + other_all.",
            lambda row: True,
        ),
        DatasetSpec(
            "apollo",
            "Apollo 7-17",
            Path("cohorts/apollo.tsv"),
            "generated_cohort",
            "Rows where analysis_primary == 'apollo'; combines apollo_lunar and apollo_non_lunar.",
            lambda row: row["analysis_primary"] == "apollo",
        ),
        DatasetSpec(
            "other_available",
            "Other Apollo-available, excluding pre-1970 accidental deaths",
            Path("cohorts/other_available.tsv"),
            "generated_cohort",
            "other_all minus rows where analysis_pre1970_accidental_death == 'Y'.",
            lambda row: row["analysis_primary"] == "other"
            and row["analysis_pre1970_accidental_death"] != "Y",
        ),
        DatasetSpec(
            "core_nasa_non_apollo",
            "Core NASA non-Apollo",
            Path("cohorts/core_nasa_non_apollo.tsv"),
            "generated_cohort",
            "Rows where analysis_source_key == 'other_core_nasa'.",
            lambda row: row["analysis_source_key"] == "other_core_nasa",
        ),
        DatasetSpec(
            "military_only",
            "Military comparison rows only",
            Path("cohorts/military_only.tsv"),
            "generated_cohort",
            "Rows where analysis_source_key starts with 'military_'.",
            lambda row: row["analysis_source_key"].startswith("military_"),
        ),
        DatasetSpec(
            "other_pre1970_accidents",
            "Non-Apollo pre-1970 accidental death exclusions",
            Path("cohorts/other_pre1970_accidents.tsv"),
            "generated_exclusion_set",
            "Rows in other_all where analysis_pre1970_accidental_death == 'Y'.",
            lambda row: row["analysis_primary"] == "other"
            and row["analysis_pre1970_accidental_death"] == "Y",
        ),
    ]

    for source in SOURCE_FILES:
        specs.append(
            DatasetSpec(
                source.key,
                source.label,
                Path("source_keys") / f"{source.key}.tsv",
                "source_key_dataset",
                f"Rows loaded directly from archived source file {source.filename}.",
                lambda row, key=source.key: row["analysis_source_key"] == key,
            )
        )

    return specs


def write_manifest(rows: list[dict[str, str]]) -> None:
    path = OUT_ROOT / "dataset_manifest.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "dataset_key",
        "dataset_label",
        "dataset_type",
        "relative_path",
        "row_count",
        "sha256",
        "construction",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(manifest_rows: list[dict[str, str]]) -> None:
    lines = [
        "# Derived Cohort Datasets",
        "",
        "This folder materializes cohort labels used by the Apollo mortality/survival analysis as row-level TSV datasets.",
        "",
        "The important correction is that `other_all` and `all_astronauts` were not original input files. They were generated in `scripts/apollo_mortality_survival_analysis.py`; this folder now saves those generated cohorts explicitly.",
        "",
        "## Source Archive Used",
        "",
        "`data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/Final - Analysis - Enriched Datasets/`",
        "",
        "## Files",
        "",
        "| Dataset key | Rows | Type | File | Construction |",
        "|---|---:|---|---|---|",
    ]
    for row in manifest_rows:
        lines.append(
            "| {dataset_key} | {row_count} | {dataset_type} | `{relative_path}` | {construction} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Provenance Columns",
            "",
            "Each TSV begins with `analysis_*` columns showing the generated dataset key, source-key mapping, archived source file, original source row number, and whether the row was treated as a pre-1970 accidental death exclusion.",
            "",
            "The original enriched TSV columns follow those provenance columns unchanged.",
        ]
    )
    (OUT_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    people, original_fields = load_people()
    specs = build_specs()
    manifest_rows: list[dict[str, str]] = []

    for spec in specs:
        rows = []
        for person in people:
            if not spec.predicate(person):
                continue
            row = dict(person)
            row["analysis_dataset_key"] = spec.key
            row["analysis_dataset_label"] = spec.label
            row["analysis_dataset_type"] = spec.dataset_type
            rows.append(row)

        out_path = OUT_ROOT / spec.relative_path
        write_tsv(out_path, rows, original_fields)
        manifest_rows.append(
            {
                "dataset_key": spec.key,
                "dataset_label": spec.label,
                "dataset_type": spec.dataset_type,
                "relative_path": str(spec.relative_path),
                "row_count": str(len(rows)),
                "sha256": sha256(out_path),
                "construction": spec.construction,
            }
        )

    write_manifest(manifest_rows)
    write_readme(manifest_rows)

    print(f"Wrote {len(manifest_rows)} datasets to {OUT_ROOT}")
    for row in manifest_rows:
        print(f"{row['dataset_key']}: {row['row_count']} rows")


if __name__ == "__main__":
    main()
