# Dataset Provenance Audit - 2026-06-16

## Scope

Audit the prior Apollo mortality/survival analysis provenance in this folder, especially the mismatch where outputs mention dataset labels such as `all_astronauts` but no same-named dataset file exists in the workspace.

## Current Folder Names

On 2026-06-19, this workspace was reorganized for shipping/readability. The action log below preserves the original June 16 names where those names were used at the time.

Current path equivalents:

| Original path/name | Current path/name |
|---|---|
| `Scripts Used/` | `scripts/` |
| `Intermediate Datasets - Data/` | `data/derived_cohorts/` |
| `source_data/analysis_inputs_2026-06-16/` | `data/source_inputs/analysis_inputs_2026-06-16/` |
| `outputs/apollo_mortality_survival_analysis_2026-06-04/` | `analysis_outputs/mortality_survival_run1_2026-06-04/` |
| `outputs/apollo_mortality_survival_analysis_2026-06-04_run2/` | `analysis_outputs/group29_sensitivity_run2_2026-06-04/` |
| `research/mental-vitality-medical-data-2026-06-04/` | `source_research/mental_vitality_medical_data_2026-06-04/` |

## Action And Tool Log

All paths are relative to this folder unless explicitly absolute.

| Time | Tool | Action | Result |
|---|---|---|---|
| 2026-06-16 | memory / `rg` | Searched `[PATH]` for Apollo mortality provenance hints. | Found prior note identifying `Scripts Used/apollo_mortality_survival_analysis.py`, the SSA lifetable input, and the canonical upstream enriched TSV names as starting points for verification. |
| 2026-06-16 | shell `pwd` | Confirmed current working directory. | Working in `./Machine Efforts/GPT 5-5`. |
| 2026-06-16 | shell `ls` | Listed top-level folder contents. | Found `APOLLO_AGING_ANOMALY_METHOD_AND_FINDINGS_DOSSIER.md`, `Scripts Used/`, `outputs/`, and `research/`. |
| 2026-06-16 | shell `git status --short` | Checked whether the folder is a git repository before editing. | Command reported this folder is not a git repository. |
| 2026-06-16 | shell `find` | Inventoried files and directories up to depth 4. | Confirmed the workspace contains generated outputs, scripts, and mental-vitality research captures, but no local `data/` or `Final - Analysis - Enriched Datasets/` directory. |
| 2026-06-16 | `apply_patch` | Created this audit document. | Provenance and action log will be maintained here. |
| 2026-06-16 | shell `sed`, `rg` | Read `Scripts Used/apollo_mortality_survival_analysis.py`, `cohort_summary.csv`, and the generated report to identify source inputs and generated cohort labels. | Confirmed `other_all` and `all_astronauts` are generated cohort labels, not standalone dataset files. |
| 2026-06-16 | shell `ls` | Checked the script's absolute upstream data root. | Found the six enriched TSV inputs and SSA lifetable files in the sibling processed-data folder. |
| 2026-06-16 | shell `mkdir` | Attempted to create a local source archive directory. | One command was accidentally run without quoting a path containing spaces, which created empty stray directories. |
| 2026-06-16 | shell `find`, `rmdir` | Inspected and removed only the empty stray directories created by the unquoted `mkdir`. | Removed `Analysis`, `Datasets`, `-`, `Enriched`, and the empty `source_data/.../Final` directory. |
| 2026-06-16 | shell `mkdir` | Recreated archive directories with quoted paths. | Created `source_data/analysis_inputs_2026-06-16/upstream_processed_data/Final - Analysis - Enriched Datasets/` and `source_data/analysis_inputs_2026-06-16/upstream_processed_data/data/`. |
| 2026-06-16 | shell `cp` | Copied the six upstream enriched TSV input files into the local source archive. | Archived `03E-non-apollo-enriched.tsv`, `07E-lunar-enriched.tsv`, `08E-non-lunar-apollo-enriched.tsv`, `09-x15-pilots-enriched.tsv`, `10-dyna-soar-pilots-enriched.tsv`, and `11-mol-full-enriched.tsv`. |
| 2026-06-16 | shell `cp` | Copied the SSA lifetable input, metadata, and saved HTML source into the local source archive. | Archived `ssa-1930-male-cohort-lifetable.tsv`, `ssa-1930-male-cohort-lifetable-metadata.md`, and `ssa-1930-male-cohort-lifetable-source.html`. |
| 2026-06-16 | shell `find`, `wc -l`, `shasum -a 256` | Verified archived file list, line counts, and hashes. | Confirmed nine archived source files and captured row-count/hash evidence in `source_data/analysis_inputs_2026-06-16/README.md`. |
| 2026-06-16 | `apply_patch` | Created `source_data/analysis_inputs_2026-06-16/README.md`. | Recorded original upstream location, archived copies, cohort-label construction, SSA baseline provenance, row counts, and SHA-256 hashes. |
| 2026-06-16 | shell `rg`, `find`, `sed` | Searched this folder for cohort/source-key labels and inspected the local source-data manifest before creating intermediate datasets. | Confirmed the row-level cohort/source keys needing materialization: `other_all`, `all_astronauts`, `apollo`, `other_available`, `core_nasa_non_apollo`, `military_only`, `other_pre1970_accidents`, and the six source-key datasets. |
| 2026-06-16 | `apply_patch` | Added `Scripts Used/create_intermediate_cohort_datasets_2026_06_16.py`. | Created a reproducible generator that reads the archived source TSVs and writes row-level intermediate cohort/source-key datasets with `analysis_*` provenance columns. |
| 2026-06-16 | shell `python3` | Ran `python3 "Scripts Used/create_intermediate_cohort_datasets_2026_06_16.py"`. | Created `Intermediate Datasets - Data/` with 13 row-level TSV datasets, `dataset_manifest.csv`, and `README.md`. |
| 2026-06-16 | shell `python3 -c` | Attempted a one-line manifest-vs-file row-count verification. | First attempt failed with a `SyntaxError` caused by a bad escaped newline in the shell command; no files were modified by this failed check. |
| 2026-06-16 | shell `find`, `sed`, `python3 -c` | Listed generated files, inspected the manifest/README, and compared manifest row counts against actual TSV row counts. | Verification passed: all 13 manifest row counts matched their TSV files, including `other_all=69` and `all_astronauts=98`. |

## Preliminary Finding

`all_astronauts` appears to be a cohort label generated inside the analysis scripts or output tables, not a standalone dataset file in this folder. The actual upstream cohort inputs need to be recovered from script path references and/or copied into this folder with explicit provenance.

## Current Provenance Status

Recorded in this folder now:

- `data/source_inputs/analysis_inputs_2026-06-16/README.md` gives the local manifest for actual archived input files.
- `data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/Final - Analysis - Enriched Datasets/` contains the six enriched astronaut TSV inputs used by the mortality/survival analysis.
- `data/source_inputs/analysis_inputs_2026-06-16/upstream_processed_data/data/` contains the SSA 1930 male cohort lifetable input, metadata, and saved source HTML.
- `data/derived_cohorts/` contains row-level materializations of the generated cohort/source-key labels used by the analysis, starting with `cohorts/other_all.tsv` and `cohorts/all_astronauts.tsv`.
- `scripts/create_intermediate_cohort_datasets_2026_06_16.py` is the reproducible generator for the intermediate datasets.

Important distinction:

- `other_all` is a generated cohort from all rows whose script `primary` value is `other`.
- `all_astronauts` is a generated cohort equal to `apollo + other_all`.
- Neither `other_all` nor `all_astronauts` is expected to exist as a standalone input dataset file.
