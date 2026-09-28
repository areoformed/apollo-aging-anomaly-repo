#!/usr/bin/env python3
"""Recover the append-only action-log state at initial Stage 3 completion."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(
    "./Machine Efforts"
    "/5-6 Sol Replication/run/sol_002"
)
SOURCE = ROOT / "ACTION_LOG.md"
DESTINATION = ROOT / "snapshots" / "ACTION_LOG_STAGE3_INITIAL.md"
EXPECTED = "bf01f109b374a3cf9505329b50e26b1258e8d4fad5a981f7f509af8d032c7e8c"
INITIAL_LINE_COUNT = 2472


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if DESTINATION.exists():
        raise FileExistsError(DESTINATION)
    lines = SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(lines) < INITIAL_LINE_COUNT:
        raise RuntimeError("Current append-only log is shorter than initial Stage 3")
    DESTINATION.write_text(
        "".join(lines[:INITIAL_LINE_COUNT]),
        encoding="utf-8",
    )
    if sha256(DESTINATION) != EXPECTED:
        raise RuntimeError(
            f"Recovered prefix hash {sha256(DESTINATION)} does not match {EXPECTED}"
        )

    manifest = ROOT / "STAGE3_SHA256.txt"
    manifest_lines = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if not line.endswith("  snapshots/ACTION_LOG_STAGE3_INITIAL.md")
    ]
    manifest_lines.append(
        f"{EXPECTED}  snapshots/ACTION_LOG_STAGE3_INITIAL.md"
    )
    manifest.write_text(
        "\n".join(sorted(manifest_lines)) + "\n",
        encoding="utf-8",
    )
    print(f"SNAPSHOT_OK {DESTINATION}")
    print(f"manifest_sha256={sha256(manifest)}")


if __name__ == "__main__":
    main()
