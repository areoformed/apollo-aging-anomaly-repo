# Script Extraction Log (v2 Session)

Source conversation: `8ed732b6-ca07-4e46-a666-94fc1f98b7f8`
JSONL file: `[PATH]` (28MB, 5161 lines)
Session dates: 2026-05-17 through 2026-05-20
Extraction date: 2026-05-22

## Method

Mined the JSONL for all Bash tool calls containing Python scripts, heredoc blocks, or data-processing pipelines. Filtered to Apollo-specific scripts (excluded Swiggy food analysis, Amazon Pay spending, SSGL poster work, and conversation-extraction utilities that were also in this session).

Found 66 Apollo-related Bash tool calls total. Of these:
- ~15 were simple grep/ls/find/head commands (exploratory, not saved)
- ~10 were inline data-inspection one-liners (cut, wc, etc.)
- ~15 were substantial Python scripts (saved as .py files)
- ~8 were substantial bash scripts for web fetching (saved as .sh files)
- The rest were duplicates (the JSONL contains both sidechain and main entries for the same commands)

All scripts were INLINE (executed via `python3 << 'PYEOF'` or `cat > [TMPDIR]/file.py << 'PYEOF'`). No scripts were saved via the Write tool to .py/.sh files during the session.

## Pipeline Order

The v2 dataset was built in this approximate sequence:

### Phase 1: Directory Setup (May 19, ~02:16 UTC)
- Created Cached Pages directories
- Copied Lists 6-8 TSVs from Track project data

### Phase 2: Data Extraction from Wiki Summaries (May 19, ~02:44-02:50 UTC)
- `build_lists_v1.py` -- first attempt, name-matching bugs
- `build_lists_v2.py` -- fixed version using filename-based classification
- Produced Lists 01-05 as TSV files

### Phase 3: Manual Enrichment (May 19, ~03:00 UTC)
- 08E-non-lunar-apollo-enriched.tsv was written directly as a heredoc (not a script)
  - This was hand-constructed data, not programmatic extraction
  - Each row was individually researched and composed by Claude

### Phase 4: QA and Enrichment Fixes (May 19, ~09:47-09:52 UTC)
- `qa_fix_enriched_tsvs.py` -- filled blank fields, fixed Group 3 dates, standardized Accidental Death column
- `update_mort_fields.py` -- added verified cause-of-death strings
- `upgrade_space_grandpas.py` -- promoted 5 astronauts to SG=Y with citations

### Phase 5: Military Programs Deduplication (May 20, ~06:05-07:06 UTC)
- `sg_denominator_breakdown.py` -- analyzed who had reached 80+ and how they were classified
- `analyze_military_overlaps.py` -- mapped all overlaps across core-73 and military files
- `dedup_military_files.py` -- removed core-73 members and cross-program duplicates
- `reconstruct_white_gordon.py` -- fixed over-dedup (surname collision: White/Gordon)
- `v1_v2_name_comparison.py` -- found 3 people in V1 missing from V2
- `append_x15_pilots.py` -- added the 3 missing high-speed research pilots

### Phase 6: Statistical Verification (May 20, ~08:49 UTC)
- `lunar_median_ages.py` -- computed median/mean ages for 24 lunar astronauts

### Phase 7: Web Archiving (May 20, ~09:13-09:25 UTC)
- `restructure_cached_pages.sh` -- reorganized flat .md files into folder-per-person layout
- `fetch_wiki_html_all.sh` -- downloaded raw Wikipedia HTML for all ~100 people (6 batches)
- `verify_html_files.sh` -- checked for blocked/missing pages
- `retry_blocked_pages.sh` -- re-fetched with User-Agent header (Wikipedia blocked bare curl)

## Files Saved

### data-extraction/
| File | Source Line | Timestamp | Description |
|------|-----------|-----------|-------------|
| `build_lists_v1.py` | 1517/2992 | May 19 02:44 | Extract astronaut data from cached wiki summaries (SUPERSEDED) |
| `build_lists_v2.py` | 1521/2996 | May 19 02:47 | Same but with filename-based classification (PRODUCTION) |

### enrichment/
| File | Source Line | Timestamp | Description |
|------|-----------|-----------|-------------|
| `update_mort_fields.py` | 2131 | May 19 09:47 | Apply verified cause-of-death to 07E and 03E |
| `upgrade_space_grandpas.py` | 2140 | May 19 09:52 | Promote 5 astronauts to Space Grandpa status |

### qa/
| File | Source Line | Timestamp | Description |
|------|-----------|-----------|-------------|
| `qa_fix_enriched_tsvs.py` | 2119 | May 19 09:47 | Fix blanks, dates, whitespace across all 3 core TSVs |
| `sg_denominator_breakdown.py` | 3360 | May 20 06:05 | Analyze SG classification by age threshold |
| `lunar_median_ages.py` | 3817 | May 20 08:49 | Compute median/mean ages for lunar astronauts |
| `v1_v2_name_comparison.py` | 3616 | May 20 06:57 | Find people in V1 dataset missing from V2 |

### military-programs/
| File | Source Line | Timestamp | Description |
|------|-----------|-----------|-------------|
| `analyze_military_overlaps.py` | 3531/3549 | May 20 06:37 | Map all cross-program and core-73 overlaps |
| `dedup_military_files.py` | 3563 | May 20 06:49 | Remove overlapping people from X-15, Dyna-Soar, MOL |
| `reconstruct_white_gordon.py` | 3590 | May 20 06:51 | Fix over-dedup of Robert White and Henry Gordon |
| `append_x15_pilots.py` | 3683 | May 20 07:06 | Add 3 missing high-speed research pilots |

### web-fetching/
| File | Source Line | Timestamp | Description |
|------|-----------|-----------|-------------|
| `restructure_cached_pages.sh` | 3916 | May 20 09:16 | Reorganize flat files into folder-per-person |
| `fetch_wiki_html_all.sh` | 3944-3952 | May 20 09:18 | Download all Wikipedia HTML pages (6 batches) |
| `verify_html_files.sh` | 3967/4002 | May 20 09:19 | Check for missing or blocked HTML files |
| `retry_blocked_pages.sh` | 3988/3993 | May 20 09:21 | Re-fetch blocked pages with User-Agent |

### life-tables/
| File | Location | Description |
|------|----------|-------------|
| `parse_ssa_lifetable.py` | Parent dir (pre-existing) | SSA life table parsing (not from this session) |

## Scripts NOT Saved (inline one-liners or exploratory)

These were short commands used for inspection, not data transformation:
- grep/cut commands checking individual names in TSV files (Haise, Mattingly, Bobko, Adams)
- wc -l on cached files
- ls and find for directory exploration
- Simple name-check Python one-liners (e.g., verifying White/Gordon in core-73)
- Git status/checkout commands checking if files were tracked

## Data Not Produced by Scripts

The 08E-non-lunar-apollo-enriched.tsv file was written as a heredoc (line 1605/3052), not generated by a script. Each row was individually researched -- it contains hand-authored data for Apollo astronauts who flew on Apollo 7-17 but were NOT on lunar surface missions. This was a manual data composition step, not a programmatic extraction.

## Relationship to Pre-Existing Files

A prior extraction pass had already placed scripts in these directories with `may18-*` / `may19-*` / `v1-*` prefixes. Those files cover the same JSONL session and contain similar (sometimes identical) script content. The newly written files use more descriptive names and have fuller header comments. The mapping:

| New file | Pre-existing equivalent |
|----------|----------------------|
| `build_lists_v2.py` | `may18-build-lists-v2.py` |
| `qa_fix_enriched_tsvs.py` | `may19-qa-fixes.py` |
| `update_mort_fields.py` | `may19-update-mort-fields.py` |
| `upgrade_space_grandpas.py` | `may19-space-grandpa-upgrades.py` |
| `dedup_military_files.py` | `may19-dedup-military-files.py` |
| `reconstruct_white_gordon.py` | `may19-reconstruct-white-gordon.py` |
| `append_x15_pilots.py` | `may19-append-missing-pilots.py` |
| `lunar_median_ages.py` | `may19-median-ages-lunar.py` |
| `sg_denominator_breakdown.py` | `may19-sg-denominator-breakdown.py` |
| `v1_v2_name_comparison.py` | `may19-v1-v2-name-comparison.py` |

The v1-extraction-log.md documents the April 2026 v1 session (conversation `7f7e191c`), which produced no scripts -- only manual data compilation.
