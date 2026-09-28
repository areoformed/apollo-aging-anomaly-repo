# Derived Cohort Datasets

This folder materializes cohort labels used by the Apollo mortality/survival analysis as row-level TSV datasets.

The important correction is that `other_all` and `all_astronauts` were not original input files. They were generated in `scripts/apollo_mortality_survival_analysis.py`; this folder now saves those generated cohorts explicitly.

## Source Archive Used

`data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/Final - Analysis - Enriched Datasets/`

## Files

| Dataset key | Rows | Type | File | Construction |
|---|---:|---|---|---|
| other_all | 69 | generated_cohort | `cohorts/other_all.tsv` | Rows where analysis_primary == 'other'; combines other_core_nasa, military_x15, military_dyna_soar, and military_mol. |
| all_astronauts | 98 | generated_cohort | `cohorts/all_astronauts.tsv` | All loaded rows; equivalent to apollo + other_all. |
| apollo | 29 | generated_cohort | `cohorts/apollo.tsv` | Rows where analysis_primary == 'apollo'; combines apollo_lunar and apollo_non_lunar. |
| other_available | 55 | generated_cohort | `cohorts/other_available.tsv` | other_all minus rows where analysis_pre1970_accidental_death == 'Y'. |
| core_nasa_non_apollo | 44 | generated_cohort | `cohorts/core_nasa_non_apollo.tsv` | Rows where analysis_source_key == 'other_core_nasa'. |
| military_only | 25 | generated_cohort | `cohorts/military_only.tsv` | Rows where analysis_source_key starts with 'military_'. |
| other_pre1970_accidents | 14 | generated_exclusion_set | `cohorts/other_pre1970_accidents.tsv` | Rows in other_all where analysis_pre1970_accidental_death == 'Y'. |
| other_core_nasa | 44 | source_key_dataset | `source_keys/other_core_nasa.tsv` | Rows loaded directly from archived source file 03E-non-apollo-enriched.tsv. |
| apollo_lunar | 24 | source_key_dataset | `source_keys/apollo_lunar.tsv` | Rows loaded directly from archived source file 07E-lunar-enriched.tsv. |
| apollo_non_lunar | 5 | source_key_dataset | `source_keys/apollo_non_lunar.tsv` | Rows loaded directly from archived source file 08E-non-lunar-apollo-enriched.tsv. |
| military_x15 | 13 | source_key_dataset | `source_keys/military_x15.tsv` | Rows loaded directly from archived source file 09-x15-pilots-enriched.tsv. |
| military_dyna_soar | 4 | source_key_dataset | `source_keys/military_dyna_soar.tsv` | Rows loaded directly from archived source file 10-dyna-soar-pilots-enriched.tsv. |
| military_mol | 8 | source_key_dataset | `source_keys/military_mol.tsv` | Rows loaded directly from archived source file 11-mol-full-enriched.tsv. |

## Provenance Columns

Each TSV begins with `analysis_*` columns showing the generated dataset key, source-key mapping, archived source file, original source row number, and whether the row was treated as a pre-1970 accidental death exclusion.

The original enriched TSV columns follow those provenance columns unchanged.
