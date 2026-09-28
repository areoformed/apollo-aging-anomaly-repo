#!/usr/bin/env python3
"""
Documentation: v1 SSA life table methodology plan.

Source: Conversation 7f7e191c-4c17-49e5-830d-c58195e61e2c
Timestamps: 2026-04-17T06:46:02Z (line 538), 2026-04-19T05:53:31Z (line 2774)

What it does: This is a DOCUMENTATION file. No life table parsing script
was written in the v1 session. The session produced:

1. METHODOLOGY PLAN (tomorrow-steps.md, line 538):
   - Session 1: Dataset hygiene — spot-check 29 astronauts' DOB/DOD
   - Session 2: Build spreadsheet, look up S(age) from SSA 1930 cohort
     life table, compute E (expected deaths) by summing q(x) over each
     astronaut's person-years
   - Session 3: Compute SMR = O/E with Poisson CI, interpret

2. SSA DATA SOURCES IDENTIFIED (comparison-data.md):
   - SSA Actuarial Study No. 120, Table 7 (1930 birth cohort)
   - Direct link: https://www.ssa.gov/oact/NOTES/as120/LifeTables_Tbl_7_1930.html
   - CSV download: https://www.ssa.gov/oact/HistEst/CohLifeTables/2024/CohLifeTables2024.html

3. MONTE CARLO APPROACH DISCUSSED (line 2774, 2026-04-19):
   - Parametric bootstrap from SSA life table
   - Simulate thousands of 29-person cohorts drawn from 1930 male SSA distribution
   - Compute summary statistic per simulated cohort
   - Compare Apollo observed value against simulated distribution
   - Three implementation paths discussed: Excel, Python, R
   - No code was written; deferred to future session

4. PRIOR LITERATURE SMRs COMPILED (comparison-data.md):
   - Elgart 2018: CVD SMR=33 (CI 14-65)
   - Hammer 2014: CVD SMR=27 (CI 9-63)
   - Reynolds 2019: CVD SMR=39 (CI 18-73)
   - Navy 1000 Aviators: 54% reduction vs. general pop

Status: SUPERSEDED by parse_ssa_lifetable.py (which parses the saved HTML
        into q(x) values) and the v2 enrichment pipeline.
"""

print("This is a documentation-only file.")
print("No life table parsing script was produced in the v1 session.")
print("The v1 session planned the methodology; v2 implemented it.")
