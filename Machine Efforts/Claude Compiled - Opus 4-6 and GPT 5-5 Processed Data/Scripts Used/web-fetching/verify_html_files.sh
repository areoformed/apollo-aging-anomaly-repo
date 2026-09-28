#!/bin/bash
#
# Verify all HTML files exist and check for suspiciously small (blocked) files.
#
# Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
# Timestamps: 2026-05-20T09:19:52Z (line 3967) and 2026-05-20T09:25:11Z (line 4002)
# What it does: Walks all cached page directories, checks each HTML file exists and
#               is > 5KB (Wikipedia pages are typically 100KB+; blocked responses are 2173 bytes).
#               Reports individual, group, and military files separately.
#
# Run from: anywhere (uses absolute paths)

BASE="./Claude Compiled Data/Cached Pages"

echo "=== INDIVIDUAL HTML FILES ==="
total=0; missing=0; small=0
for d in "$BASE/wiki-individual"/*/; do
    name=$(basename "$d")
    html="$d/$name.html"
    if [ -f "$html" ]; then
        size=$(wc -c < "$html")
        if [ "$size" -lt 10000 ]; then
            echo "  SMALL ($size bytes): $name"
            small=$((small+1))
        fi
        total=$((total+1))
    else
        echo "  MISSING: $name"
        missing=$((missing+1))
    fi
done
echo "Total HTML: $total | Missing: $missing | Suspiciously small: $small"

echo ""
echo "=== GROUP PAGE HTML FILES ==="
for d in "$BASE"/wiki-*/; do
    [ -d "$d/wiki-individual" ] && continue  # skip the individual dir itself
    name=$(basename "$d")
    html="$d/$name.html"
    if [ -f "$html" ]; then
        size=$(wc -c < "$html")
        echo "  OK ($size bytes): $name"
    else
        echo "  MISSING: $name"
    fi
done

echo ""
echo "=== MILITARY HTML FILES ==="
for prog in x-15 dyna-soar mol; do
    echo "--- $prog ---"
    for d in "$BASE/military-programs/$prog"/*/; do
        name=$(basename "$d")
        html="$d/$name.html"
        if [ -f "$html" ]; then
            size=$(wc -c < "$html")
            if [ "$size" -lt 5000 ]; then
                echo "  SMALL ($size bytes): $name"
            else
                echo "  OK ($size bytes): $name"
            fi
        else
            echo "  MISSING: $name"
        fi
    done
done

echo ""
echo "=== SUMMARY ==="
total=$(find "$BASE" -name "*.html" | wc -l | tr -d ' ')
good=$(find "$BASE" -name "*.html" ! -size -5000c | wc -l | tr -d ' ')
bad=$(find "$BASE" -name "*.html" -size -5000c | wc -l | tr -d ' ')
echo "Total HTML files: $total"
echo "Good (>5KB): $good"
echo "Bad (<5KB): $bad"
