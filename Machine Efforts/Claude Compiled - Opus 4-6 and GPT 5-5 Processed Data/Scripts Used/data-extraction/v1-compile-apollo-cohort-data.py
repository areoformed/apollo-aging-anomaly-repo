#!/usr/bin/env python3
"""
Reconstruct: v1 Apollo 7-17 cohort data compilation.

Source: Conversation 7f7e191c-4c17-49e5-830d-c58195e61e2c
Pre-existing file read at: 2026-04-17T14:38:23Z (line 939)
Originally compiled: Early April 2026 (pre-dates this conversation)

What it does: This is a DOCUMENTATION file. The 29-astronaut Apollo 7-17
cohort dataset (cohort-data.md) was compiled MANUALLY — not by any script.
The model compiled it from its training knowledge + web verification,
stored as a markdown table with columns:
  - Name, Role (CDR/CMP/LMP), Born, Died, Age at Death/Current Age,
    Cause of Death, Moon Status, Cognitive Decline Notes

The dataset was organized by mission (Apollo 7 through Apollo 17) and
included key epidemiological annotations:
  - Accidental deaths flagged (Conrad: motorcycle, Anders: plane crash)
  - Cognitive decline status for each astronaut
  - Living vs. deceased status as of April 2026
  - Cause of death specificity (heart attack, stroke, natural causes, etc.)

Summary statistics computed in-session (line 944):
  - Median age at end of observation (all 29): 88
  - Median age at death (deceased only, n=23): 86
  - Median birth year: 1930
  - 6 alive, all 90+ (ages 90-96)
  - Only 1 documented cognitive concern (Aldrin, contested)

Status: SUPERSEDED by v2 enriched datasets (07E-lunar-enriched.tsv,
        08E-non-lunar-apollo-enriched.tsv) which add DOB/DOD in ISO format,
        Wikipedia-verified causes of death, and standardized field structure.
"""

print("This is a documentation-only file.")
print("The original v1 cohort data was hand-compiled in markdown.")
print("See cohort-data.md in the apollo-aging-anomaly project directory.")
