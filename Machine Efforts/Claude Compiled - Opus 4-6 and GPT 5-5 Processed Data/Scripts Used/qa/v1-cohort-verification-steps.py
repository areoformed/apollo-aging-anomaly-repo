#!/usr/bin/env python3
"""
Documentation: v1 QA / verification steps for Apollo cohort data.

Source: Conversation 7f7e191c-4c17-49e5-830d-c58195e61e2c
Timestamps: 2026-04-17T06:46:02Z (line 538), 2026-04-17T14:38:23Z (line 939)

What it does: This is a DOCUMENTATION file. The v1 session planned but did
not fully execute a QA pipeline. Here's what was done and what was deferred:

EXECUTED (manually, not scripted):
  1. Spot-check of 29 astronauts' DOB/DOD against Wikipedia / NASA sources
  2. Verification of recent deaths (Lovell Aug 2025, Anders Jun 2024, Borman Nov 2023)
  3. Computation of summary statistics (line 944):
     - Median age at end of observation: 88
     - Median age at death (n=23 deceased): 86
     - Median birth year: 1930 (key for SSA life table selection)
     - Sorted ages: 51,56,57,61,61,69,74,82,82,84,85,86,87,87,88,88,90,90,90,90,90,90,92,93,93,93,95,96,97
  4. Identification of accidental deaths to right-censor:
     - Pete Conrad (69): motorcycle accident, July 8, 1999
     - William Anders (90): plane crash, June 7, 2024

PLANNED BUT DEFERRED:
  1. SSA 1930 male cohort life table lookup for each astronaut's age band
  2. Expected deaths computation: E = sum of q(x) over person-years
  3. SMR = O/E with Poisson confidence interval
  4. Monte Carlo simulation (parametric bootstrap, 10k cohorts)
  5. Cross-validation against Navy 1000 Aviators published SMRs

The five-gate QA framework (added in edit at line 575):
  Gate 1: Novelty check (done — novelty-assessment.md)
  Gate 2: Healthy-astronaut-effect acknowledgment (planned)
  Gate 3: Comparison with published all-astronaut SMRs (data collected)
  Gate 4: Right-censoring methodology for accidental deaths (planned)
  Gate 5: Direct comparison with age-matched highly-selected populations (planned)

Status: SUPERSEDED by v2 which uses systematic WebFetch + human review QA.
"""

print("This is a documentation-only file.")
print("QA steps in v1 were manual and partially deferred.")
