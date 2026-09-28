#!/usr/bin/env python3
"""Prepare the explicitly post-lock Stage 3 reference bundle.

This script never reads or writes Human Efforts. It copies selected, already
existing Machine Efforts reference artifacts into the neutral sol_002 runtime,
records source and copied hashes, and adds the separately locked Stage 2R
correction as an immutable supplemental input.
"""

from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path


MACHINE_ROOT = Path(
    "./Machine Efforts"
)
RUNTIME_ROOT = Path("[TMPDIR]/historical-cohort-replication-002")
STAGE3 = RUNTIME_ROOT / "stage3"
REFERENCE = STAGE3 / "reference"
LOCKED_SUPPLEMENT = STAGE3 / "locked_supplement"
CONTROLLER_MANIFEST = (
    MACHINE_ROOT
    / "5-6 Sol Replication"
    / "controller"
    / "sol_002"
    / "STAGE3_REFERENCE_MANIFEST.csv"
)

COPY_SPECS = (
    (
        MACHINE_ROOT / "GPT 5-5" / "data" / "derived_cohorts",
        REFERENCE / "derived_cohorts",
        "approved_reference",
    ),
    (
        MACHINE_ROOT
        / "GPT 5-5"
        / "analysis_outputs"
        / "mortality_survival_run1_2026-06-04",
        REFERENCE / "reference_results" / "mortality_survival_run1_2026-06-04",
        "approved_reference",
    ),
    (
        MACHINE_ROOT / "GPT 5-5" / "APOLLO_AGING_ANOMALY_METHOD_AND_FINDINGS_DOSSIER.md",
        REFERENCE / "reference_results" / "APOLLO_AGING_ANOMALY_METHOD_AND_FINDINGS_DOSSIER.md",
        "approved_reference",
    ),
    (
        MACHINE_ROOT / "GPT 5-5" / "scripts" / "create_intermediate_cohort_datasets_2026_06_16.py",
        REFERENCE / "reference_code" / "create_intermediate_cohort_datasets_2026_06_16.py",
        "approved_reference",
    ),
    (
        MACHINE_ROOT / "GPT 5-5" / "scripts" / "apollo_mortality_survival_analysis.py",
        REFERENCE / "reference_code" / "apollo_mortality_survival_analysis.py",
        "approved_reference",
    ),
    (
        MACHINE_ROOT
        / "GPT 5-5"
        / "data"
        / "source_inputs"
        / "analysis_inputs_2026-06-16"
        / "upstream_processed_data"
        / "data"
        / "ssa-1930-male-cohort-lifetable.tsv",
        REFERENCE / "reference_population" / "ssa-1930-male-cohort-lifetable.tsv",
        "approved_reference",
    ),
    (
        MACHINE_ROOT
        / "GPT 5-5"
        / "data"
        / "source_inputs"
        / "analysis_inputs_2026-06-16"
        / "upstream_processed_data"
        / "data"
        / "ssa-1930-male-cohort-lifetable-metadata.md",
        REFERENCE / "reference_population" / "ssa-1930-male-cohort-lifetable-metadata.md",
        "approved_reference",
    ),
    (
        MACHINE_ROOT / "5-6 Sol Replication" / "run" / "sol_002r" / "stage2r",
        LOCKED_SUPPLEMENT / "stage2r",
        "locked_supplement",
    ),
    (
        MACHINE_ROOT
        / "5-6 Sol Replication"
        / "run"
        / "sol_002r"
        / "STAGE2R_CONTROLLER_GATE.md",
        LOCKED_SUPPLEMENT / "STAGE2R_CONTROLLER_GATE.md",
        "locked_supplement",
    ),
    (
        MACHINE_ROOT
        / "5-6 Sol Replication"
        / "run"
        / "sol_002r"
        / "STAGE2R_SHA256.txt",
        LOCKED_SUPPLEMENT / "STAGE2R_SHA256.txt",
        "locked_supplement",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_under(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(item for item in path.rglob("*") if item.is_file())


def copy_spec(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def main() -> None:
    if STAGE3.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing Stage 3 directory: {STAGE3}"
        )

    rows: list[dict[str, str]] = []
    for source, destination, bundle_class in COPY_SPECS:
        copy_spec(source, destination)
        source_files = files_under(source)
        destination_files = files_under(destination)
        if len(source_files) != len(destination_files):
            raise RuntimeError(f"File-count mismatch for {source}")

        for source_file, destination_file in zip(source_files, destination_files):
            source_hash = sha256(source_file)
            copied_hash = sha256(destination_file)
            if source_hash != copied_hash:
                raise RuntimeError(f"Hash mismatch for {source_file}")
            rows.append(
                {
                    "bundle_class": bundle_class,
                    "source_path": str(source_file),
                    "source_sha256": source_hash,
                    "runtime_path": str(destination_file.relative_to(RUNTIME_ROOT)),
                    "runtime_sha256": copied_hash,
                    "bytes": str(source_file.stat().st_size),
                }
            )

    rows.sort(key=lambda row: (row["bundle_class"], row["runtime_path"]))
    fieldnames = (
        "bundle_class",
        "source_path",
        "source_sha256",
        "runtime_path",
        "runtime_sha256",
        "bytes",
    )
    CONTROLLER_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    for manifest in (
        CONTROLLER_MANIFEST,
        REFERENCE / "STAGE3_REFERENCE_MANIFEST.csv",
    ):
        with manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"STAGE3_BUNDLE_READY files={len(rows)}")
    print(f"controller_manifest={CONTROLLER_MANIFEST}")
    print(f"runtime_manifest={REFERENCE / 'STAGE3_REFERENCE_MANIFEST.csv'}")


if __name__ == "__main__":
    main()
