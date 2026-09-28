#!/bin/bash
# v1 WebFetch calls for Apollo Aging Anomaly data gathering.
#
# Source: Conversation 7f7e191c-4c17-49e5-830d-c58195e61e2c
# Dates: 2026-04-17 through 2026-04-22
#
# What it does: Documents the WebFetch MCP tool calls used to gather
# source data for the v1 Apollo dataset. These were NOT bash scripts --
# they were Claude Code MCP tool invocations. Documented here for
# provenance.
#
# Status: SUPERSEDED by v2 which used systematic per-astronaut Wikipedia
#         fetches cached to wiki-individual/*.md files.

echo "=== WebFetch calls in v1 session ==="
echo ""
echo "1. Thousand Aviator Study (line 564, 2026-04-17T06:54:42Z)"
echo "   URL: https://atlaslongitudinaldatasets.ac.uk/datasets/thousand-aviator-study"
echo "   Prompt: Does this dataset include mortality data? What variables? Sample size,"
echo "           follow-up period, access policy? Direct download or application?"
echo "   Result: 403 error on direct access. Web search confirmed study details."
echo "   Used for: comparison-data.md Navy 1000 Aviators section"
echo ""
echo "2. Wikipedia: List of Apollo Astronauts (line 2844, 2026-04-19T07:17:41Z)"
echo "   URL: https://en.wikipedia.org/wiki/List_of_Apollo_astronauts"
echo "   Used for: Cross-referencing cohort-data.md astronaut list"
echo ""
echo "3. Wikipedia: Astronauts by Year of Selection #1 (line 13734, 2026-04-22T08:13:50Z)"
echo "   URL: https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection"
echo "   Used for: Building us-astronaut-groups-1-7.tsv (121 rows)"
echo ""
echo "4. Wikipedia: Astronauts by Year of Selection #2 (line 13738, 2026-04-22T08:14:57Z)"
echo "   URL: https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection"
echo "   Used for: Continuation of group compilation (fetched twice for full coverage)"
echo ""
echo "Note: All fetches used Claude Code's WebFetch MCP tool, not curl/wget."
echo "The model parsed HTML tables in-context to produce the TSV output."
