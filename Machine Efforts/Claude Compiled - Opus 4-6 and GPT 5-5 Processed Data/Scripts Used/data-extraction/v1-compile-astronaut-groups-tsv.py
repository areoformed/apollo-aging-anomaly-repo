#!/usr/bin/env python3
"""
Reconstruct: v1 astronaut groups 1-7 TSV compilation.

Source: Conversation 7f7e191c-4c17-49e5-830d-c58195e61e2c
Timestamp: 2026-04-22T08:16:16Z (line 13744)

What it does: This is a RECONSTRUCTED script. In the original v1 session,
the 121-row TSV of US astronaut groups (X-15 through NASA Group 7, plus
Dyna-Soar, Man in Space Soonest, and USAF MOL groups) was compiled MANUALLY
by the model from two WebFetch calls to Wikipedia:
  - https://en.wikipedia.org/wiki/List_of_Apollo_astronauts (line 2844)
  - https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection (line 13734, 13738)

The model parsed the Wikipedia tables in-context and wrote the TSV directly
via a Write tool call. No Python script was used. This reconstruction
shows the equivalent logic.

Output: us-astronaut-groups-1-7.tsv (121 rows, 4 columns: Name, Group, Selection Date, Wikipedia Link)
Groups included: X-15 Pilot Group, Man in Space Soonest, NASA Groups 1-7,
                 Dyna-Soar Groups 1-2, USAF MOL Groups 1-3

Status: SUPERSEDED by v2 build_lists_v1.py / build_lists_v2.py which use
        cached Wikipedia individual pages instead of summary tables.
"""

# NOTE: The original v1 TSV was produced by the model directly reading
# Wikipedia pages and emitting the TSV content inline. No script existed.
# The data was written to:
#   <workspace>/output/us-astronaut-groups-1-7.tsv
# then moved to:
#   <workspace>/projects/apollo-aging-anomaly/us-astronaut-groups-1-7.tsv
#
# This file exists for provenance documentation only.
# The actual TSV content is preserved in the data-extraction/ directory
# as v1-us-astronaut-groups-1-7.tsv.

print("This is a documentation-only reconstruction.")
print("The original v1 TSV was compiled manually by the model from Wikipedia WebFetch results.")
print("See v1-us-astronaut-groups-1-7.tsv for the actual data produced.")
