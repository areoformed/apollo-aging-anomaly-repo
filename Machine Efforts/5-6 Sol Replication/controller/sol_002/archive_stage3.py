#!/usr/bin/env python3
"""Archive the completed neutral-runtime Stage 3 without rewriting locked stages."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


MACHINE_ROOT = Path(
    "./Machine Efforts"
)
RUNTIME = Path("[TMPDIR]/historical-cohort-replication-002")
ARCHIVE = MACHINE_ROOT / "5-6 Sol Replication" / "run" / "sol_002"
STAGE3_SOURCE = RUNTIME / "stage3"
STAGE3_DESTINATION = ARCHIVE / "stage3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def main() -> None:
    if not STAGE3_SOURCE.is_dir():
        raise FileNotFoundError(STAGE3_SOURCE)
    if STAGE3_DESTINATION.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing Stage 3 archive: {STAGE3_DESTINATION}"
        )

    pre_stage3_log = ARCHIVE / "snapshots" / "ACTION_LOG_PRE_STAGE3.md"
    if pre_stage3_log.exists():
        raise FileExistsError(pre_stage3_log)
    shutil.copy2(ARCHIVE / "ACTION_LOG.md", pre_stage3_log)

    shutil.copytree(STAGE3_SOURCE, STAGE3_DESTINATION)
    shutil.copy2(RUNTIME / "ACTION_LOG.md", ARCHIVE / "ACTION_LOG.md")
    shutil.copy2(
        RUNTIME / "CONTROLLER_LAST_MESSAGE_STAGE3.txt",
        ARCHIVE / "CONTROLLER_LAST_MESSAGE_STAGE3.txt",
    )
    shutil.copy2(
        RUNTIME / "STAGE3_RUNTIME.jsonl",
        ARCHIVE / "STAGE3_RUNTIME_TRANSCRIPT.jsonl",
    )
    shutil.copy2(
        RUNTIME / "STAGE3_RUNTIME.stderr",
        ARCHIVE / "STAGE3_RUNTIME.stderr",
    )

    source_files = tree_files(STAGE3_SOURCE)
    destination_files = tree_files(STAGE3_DESTINATION)
    if [p.relative_to(STAGE3_SOURCE) for p in source_files] != [
        p.relative_to(STAGE3_DESTINATION) for p in destination_files
    ]:
        raise RuntimeError("Stage 3 source/archive inventories differ")
    for source, destination in zip(source_files, destination_files):
        if sha256(source) != sha256(destination):
            raise RuntimeError(f"Archive hash mismatch: {source}")

    manifest = ARCHIVE / "STAGE3_SHA256.txt"
    lines = []
    for path in destination_files:
        lines.append(f"{sha256(path)}  {path.relative_to(ARCHIVE)}")
    for name in (
        "ACTION_LOG.md",
        "CONTROLLER_LAST_MESSAGE_STAGE3.txt",
        "STAGE3_RUNTIME_TRANSCRIPT.jsonl",
        "STAGE3_RUNTIME.stderr",
        "snapshots/ACTION_LOG_PRE_STAGE3.md",
    ):
        path = ARCHIVE / name
        lines.append(f"{sha256(path)}  {path.relative_to(ARCHIVE)}")
    manifest.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")

    print(f"STAGE3_ARCHIVED files={len(destination_files)}")
    print(f"manifest={manifest}")
    print(f"manifest_sha256={sha256(manifest)}")


if __name__ == "__main__":
    main()
