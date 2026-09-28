#!/usr/bin/env python3
"""Archive the repaired Stage 3 while preserving the initial completed version."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


MACHINE_ROOT = Path(
    "./Machine Efforts"
)
RUNTIME = Path("[TMPDIR]/historical-cohort-replication-002")
ARCHIVE = MACHINE_ROOT / "5-6 Sol Replication" / "run" / "sol_002"
SOURCE = RUNTIME / "stage3"
CURRENT = ARCHIVE / "stage3"
INITIAL = ARCHIVE / "stage3_pre_controller_repair"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def assert_equal_trees(left: Path, right: Path) -> None:
    left_files = files(left)
    right_files = files(right)
    if [p.relative_to(left) for p in left_files] != [
        p.relative_to(right) for p in right_files
    ]:
        raise RuntimeError(f"Inventory mismatch: {left} versus {right}")
    for left_file, right_file in zip(left_files, right_files):
        if sha256(left_file) != sha256(right_file):
            raise RuntimeError(f"Hash mismatch: {left_file} versus {right_file}")


def main() -> None:
    if not SOURCE.is_dir() or not CURRENT.is_dir():
        raise FileNotFoundError("Repaired source or initial archive is missing")
    if INITIAL.exists():
        raise FileExistsError(INITIAL)

    initial_manifest = ARCHIVE / "STAGE3_INITIAL_SHA256.txt"
    if initial_manifest.exists():
        raise FileExistsError(initial_manifest)
    shutil.copy2(ARCHIVE / "STAGE3_SHA256.txt", initial_manifest)

    CURRENT.rename(INITIAL)
    shutil.copytree(SOURCE, CURRENT)
    assert_equal_trees(SOURCE, CURRENT)

    shutil.copy2(RUNTIME / "ACTION_LOG.md", ARCHIVE / "ACTION_LOG.md")
    for runtime_name, archive_name in (
        (
            "CONTROLLER_LAST_MESSAGE_STAGE3_REPAIR.txt",
            "CONTROLLER_LAST_MESSAGE_STAGE3_REPAIR.txt",
        ),
        ("STAGE3_REPAIR_RUNTIME.jsonl", "STAGE3_REPAIR_RUNTIME_TRANSCRIPT.jsonl"),
        ("STAGE3_REPAIR_RUNTIME.stderr", "STAGE3_REPAIR_RUNTIME.stderr"),
    ):
        shutil.copy2(RUNTIME / runtime_name, ARCHIVE / archive_name)

    manifest = ARCHIVE / "STAGE3_SHA256.txt"
    lines = []
    for tree in (CURRENT, INITIAL):
        for path in files(tree):
            lines.append(f"{sha256(path)}  {path.relative_to(ARCHIVE)}")
    for name in (
        "ACTION_LOG.md",
        "CONTROLLER_LAST_MESSAGE_STAGE3.txt",
        "CONTROLLER_LAST_MESSAGE_STAGE3_REPAIR.txt",
        "STAGE3_RUNTIME_TRANSCRIPT.jsonl",
        "STAGE3_RUNTIME.stderr",
        "STAGE3_REPAIR_RUNTIME_TRANSCRIPT.jsonl",
        "STAGE3_REPAIR_RUNTIME.stderr",
        "STAGE3_INITIAL_SHA256.txt",
        "snapshots/ACTION_LOG_PRE_STAGE3.md",
    ):
        path = ARCHIVE / name
        lines.append(f"{sha256(path)}  {path.relative_to(ARCHIVE)}")
    manifest.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")

    print(f"STAGE3_REPAIR_ARCHIVED current_files={len(files(CURRENT))}")
    print(f"initial_files={len(files(INITIAL))}")
    print(f"manifest={manifest}")
    print(f"manifest_sha256={sha256(manifest)}")


if __name__ == "__main__":
    main()
