# Apollo Aging Anomaly GPT 5-5 Workspace

Generated: 2026-06-19

This folder contains the GPT 5-5 side of the Apollo Aging Anomaly mortality, longevity, and late-life vitality analysis. It is organized for handoff: start here to see what exists and where to find it. This is not a fresh statistical audit of every file; it is a manifest of the analyses, source archives, derived datasets, scripts, and outputs already present.

## Start Here

| Need | Open |
|---|---|
| Best narrative summary of methods, caveats, and findings | `APOLLO_AGING_ANOMALY_METHOD_AND_FINDINGS_DOSSIER.md` |
| Proof of where the mortality-analysis inputs came from | `DATASET_PROVENANCE_AUDIT_2026-06-16.md` and `data/source_inputs/analysis_inputs_2026-06-16/README.md` |
| Row-level generated cohorts such as `other_all` and `all_astronauts` | `data/derived_cohorts/` |
| Run 1 mortality/survival/SMR outputs | `analysis_outputs/mortality_survival_run1_2026-06-04/` |
| Run 2 group-of-29 probability and vitality outputs | `analysis_outputs/group29_sensitivity_run2_2026-06-04/` |
| Mental-vitality findings and source archive | `mental_vitality_medical_data_findings.md` and `source_research/mental_vitality_medical_data_2026-06-04/` |

## Current Folder Map

| Path | What it contains | Current scale |
|---|---|---:|
| `data/source_inputs/` | Local copies of upstream data used by the mortality scripts. | 10 files, 296K |
| `data/derived_cohorts/` | Explicit row-level TSVs for generated cohort labels and source-key subsets. | 15 files, 472K |
| `scripts/` | Python scripts for Run 1, Run 2, grids, distributions, source-table extraction, and derived-cohort generation. | 7 runnable `.py` scripts |
| `analysis_outputs/` | Generated CSV, Markdown, and SVG outputs from mortality/survival and sensitivity analyses. | 49 files, 928K |
| `source_research/` | Archived medical/vitality source pages, PDFs, extracted tables, source logs, and source hash manifest. | 62 files, 33M |

## Analyses Already Present

| Analysis | Main files | What exists |
|---|---|---|
| Run 1: mortality, SMR, Kaplan-Meier, astronaut comparisons | `scripts/apollo_mortality_survival_analysis.py`; `analysis_outputs/mortality_survival_run1_2026-06-04/` | Cohort summary, person-level analysis, SMR table/graph, KM points/graphs, Monte Carlo death-count summaries, accident exclusions, Space Grandpa/Fisher-test outputs. |
| Run 2: 29-person longevity and vitality sensitivity | `scripts/apollo_mortality_survival_analysis_run2.py`; `analysis_outputs/group29_sensitivity_run2_2026-06-04/` | Probability tables for Apollo-like longevity and vitality under hazard-scale and vitality-rate assumptions. |
| Simple 80+ vitality grid | `scripts/apollo_mortality_survival_analysis_run2_simple_vitality_grid.py` | Blanket 80+ vitality-rate grid with expected-vital-count and probability heatmap outputs. |
| MHAS lower-anchor 80+ grid | `scripts/apollo_mortality_survival_analysis_run2_mhas16_vitality_grid.py` | Grid using the user-supplied MHAS 54/334 lower anchor plus HRS-HCAP upper anchor. |
| Censored run distributions | `scripts/apollo_mortality_survival_analysis_run2_user_requested_distributions.py` | Histograms/SVGs for simulated 22nd-longest-lived age, 13th-longest-lived age, and vitality-count distributions with censored Apollo markers. |
| Mental-vitality source research | `mental_vitality_medical_data_findings.md`; `source_research/mental_vitality_medical_data_2026-06-04/` | Findings memo plus local evidence archive, source log, SHA-256 manifest, and extracted Cao 2024 supplement tables. |
| Input provenance and derived cohorts | `DATASET_PROVENANCE_AUDIT_2026-06-16.md`; `data/derived_cohorts/dataset_manifest.csv` | Local source archive plus 13 explicit row-level cohort/source-key TSV datasets. |

## Naming Cleanup

The folder was reorganized on 2026-06-19 to make the purpose of each area visible without opening files.

| Old name | New name |
|---|---|
| `Scripts Used/` | `scripts/` |
| `Intermediate Datasets - Data/` | `data/derived_cohorts/` |
| `source_data/analysis_inputs_2026-06-16/` | `data/source_inputs/analysis_inputs_2026-06-16/` |
| `outputs/apollo_mortality_survival_analysis_2026-06-04/` | `analysis_outputs/mortality_survival_run1_2026-06-04/` |
| `outputs/apollo_mortality_survival_analysis_2026-06-04_run2/` | `analysis_outputs/group29_sensitivity_run2_2026-06-04/` |
| `research/mental-vitality-medical-data-2026-06-04/` | `source_research/mental_vitality_medical_data_2026-06-04/` |

## Reproduction Commands

Run from this folder:

```bash
python3 scripts/apollo_mortality_survival_analysis.py
python3 scripts/apollo_mortality_survival_analysis_run2.py
python3 scripts/apollo_mortality_survival_analysis_run2_simple_vitality_grid.py
python3 scripts/apollo_mortality_survival_analysis_run2_mhas16_vitality_grid.py
python3 scripts/apollo_mortality_survival_analysis_run2_user_requested_distributions.py
python3 scripts/create_intermediate_cohort_datasets_2026_06_16.py
python3 scripts/extract_cao2024_supplement_tables.py source_research/mental_vitality_medical_data_2026-06-04/references/springer_11357_2024_1180_MOESM1_ESM.txt source_research/mental_vitality_medical_data_2026-06-04/extracted
```

## Caveats

- The main findings and statistical caveats live in the dossier; this README is the folder manifest.
- `Space Grandpa` is a public late-life activity proxy, not a clinical cognition diagnosis.
- The MHAS 54/334 lower anchor is recorded as user-supplied in the sensitivity run; the MHAS microdata count was not reproduced in this workspace.
- The source archive keeps upstream folder names such as `Final - Analysis - Enriched Datasets/` inside `data/source_inputs/` because those names preserve provenance.
