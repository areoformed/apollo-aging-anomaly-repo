#!/bin/bash
#
# Restructure cached pages from flat files into folder-per-astronaut layout.
#
# Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
# Timestamp: 2026-05-20T09:16:44Z (line 3916)
# What it does: Moves cached .md files from flat wiki-individual/ directory into
#               subdirectories (one per astronaut), and similarly for group pages
#               and military program pages. This creates the folder structure needed
#               for HTML files to be co-located with their .md summaries.
#
# Before: wiki-individual/aldrin-buzz.md
# After:  wiki-individual/aldrin-buzz/aldrin-buzz.md
#
# Run from the Cached Pages directory.

cd "./Claude Compiled Data/Cached Pages"

echo "=== Restructuring wiki-individual ==="
for f in wiki-individual/*.md; do
    base=$(basename "$f" .md)
    mkdir -p "wiki-individual/$base"
    mv "$f" "wiki-individual/$base/$base.md"
    echo "  $base/"
done

echo ""
echo "=== Restructuring group pages ==="
for f in wiki-apollo-astronauts.md wiki-astronauts-by-selection.md wiki-group-6-scientists-1967.md wiki-group-7-mol-transfer.md; do
    base=$(basename "$f" .md)
    mkdir -p "$base"
    mv "$f" "$base/$base.md"
    echo "  $base/"
done

echo ""
echo "=== Restructuring military/x-15 ==="
for f in military-programs/x-15/*.md; do
    base=$(basename "$f" .md)
    mkdir -p "military-programs/x-15/$base"
    mv "$f" "military-programs/x-15/$base/$base.md"
    echo "  x-15/$base/"
done

echo ""
echo "=== Restructuring military/dyna-soar ==="
for f in military-programs/dyna-soar/*.md; do
    base=$(basename "$f" .md)
    mkdir -p "military-programs/dyna-soar/$base"
    mv "$f" "military-programs/dyna-soar/$base/$base.md"
    echo "  dyna-soar/$base/"
done

echo ""
echo "=== Restructuring military/mol ==="
for f in military-programs/mol/*.md; do
    base=$(basename "$f" .md)
    mkdir -p "military-programs/mol/$base"
    mv "$f" "military-programs/mol/$base/$base.md"
    echo "  mol/$base/"
done

echo "DONE"
