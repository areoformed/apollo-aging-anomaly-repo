# Protocol Deviations

**Protocol status:** frozen 2026-07-22 19:59:27 PDT (-0700). Pre-freeze edits were design revisions, not deviations.

After freeze, append entries; do not rewrite earlier entries.

## Entry template

### DEV-YYYYMMDD-NN — Short title

- **Timestamp:**
- **Run/stage:**
- **Discovered by:**
- **What happened:**
- **Frozen requirement affected:**
- **Files/messages affected:**
- **Had any group-level outcome result been seen?** yes/no/uncertain
- **Repair or disposition:**
- **Potential directional effect:** none known / describe
- **the author’s decision:**

## Entries

None as of protocol freeze.

### DEV-20260722-01 — System memory leaked prior Apollo-project context

- **Timestamp:** 2026-07-22 20:32:49 PDT (-0700)
- **Run/stage:** `sol_001`, Stage 1 gate.
- **Discovered by:** controller review of `run/sol_001/CONTEXT_ATTESTATION.md`.
- **What happened:** despite `fork_turns: "none"`, the child received a system-provided memory summary stating that the workspace concerned an Apollo aging-anomaly mortality/vitality effort, that a prior analysis used SMR and a comparison-specific accident rule, that it used a hazard-based SMR method and censored run distributions, and that an MHAS `54/334` quantity was provisional. The child reported no person-level roster facts, group estimate, or prior conclusion.
- **Frozen requirement affected:** Stage 1 contextual blinding and the stop condition for substantive prior project knowledge.
- **Files/messages affected:** `run/sol_001/CONTEXT_ATTESTATION.md`; all later Stage 1 work inherits this disclosed context.
- **Had any group-level outcome result been seen?** no result estimate was reported, but prior methods and one provisional external quantity were visible before Stage 1.
- **Repair or disposition:** Stage 1 artifacts were preserved and hashed. The controller stopped before Stage 1B and did not send another prompt. No quiet restart is permitted.
- **Potential directional effect:** unknown; likely limited for top-down roster construction, but it defeats the preregistered clean-context claim.
- **the author’s decision:** On 2026-07-22, [AUTHOR] directed a fresh blind rerun. Preserve `sol_001` as the stopped contaminated run and launch a separately labeled `sol_002`; do not reuse the contaminated child context.

### DEV-20260722-02 — Stage 1 durable timestamps are not reliable wall-clock times

- **Timestamp:** 2026-07-22 20:32:49 PDT (-0700)
- **Run/stage:** `sol_001`, Stage 1 gate.
- **Discovered by:** controller comparison of the host clock with the child action log and Stage 1 files.
- **What happened:** at host time 2026-07-23 03:32:49 UTC, the child log already contained entries through 03:57 UTC. `DECISIONS.md` records a Dyna-Soar roster amendment at 03:51 UTC even though `STAGE_COMPLETE.md` records completion at 03:25:01 UTC. The action log also appends 03:12–03:16 entries after entries timestamped through 03:57. The substantive sequence is partly recoverable from row order and file content, but the claimed timestamps cannot be treated as exact.
- **Frozen requirement affected:** timestamped append-only action logging, decision-before-data auditability, and materially complete logs.
- **Files/messages affected:** `run/sol_001/ACTION_LOG.md`, `run/sol_001/stage1/DECISIONS.md`, `run/sol_001/stage1/CONTAMINATION.md`, and `run/sol_001/stage1/STAGE_COMPLETE.md`.
- **Had any group-level outcome result been seen?** no.
- **Repair or disposition:** preserve the files verbatim; do not back-edit their timestamps. Record the controller-observed discrepancy and stop before Stage 1B.
- **Potential directional effect:** none known on cohort values; material adverse effect on audit confidence and proof of ordering.
- **the author’s decision:** On 2026-07-22, [AUTHOR] directed a fresh blind rerun. The rerun must obtain logged timestamps from real clock calls rather than generating them.

### DEV-20260722-03 — Rerun through a memory-disabled external runtime

- **Timestamp:** 2026-07-22 20:39:42 PDT (-0700)
- **Run/stage:** `sol_002`, preflight.
- **Discovered by:** controller investigation after [AUTHOR] requested a genuinely blind rerun.
- **What happened:** `fork_turns: "none"` suppresses inherited conversation turns but does not suppress system/developer material shared by agents in the same collaboration tree. A second integrated child would therefore receive the same Apollo-related automatic memory summary. The controller instead tested a separate ephemeral Codex CLI runtime launched with `--ignore-user-config`, `--disable memories`, and a neutral temporary working directory. Before reading files or the web, that runtime reported no project-specific people, topics, hypotheses, methods, or results in its initial context.
- **Frozen requirement affected:** the frozen launch runbook names the integrated child runtime, task `sol_replication_001`, path `run/sol_001`, and `fork_turns: "none"`. The separately labeled rerun uses an external persistent runtime, run ID `sol_002`, and a neutral temporary working directory.
- **Files/messages affected:** `controller/sol_002/RERUN_PROTOCOL.md`, `controller/sol_002/STAGE1_LAUNCH.txt`, the external runtime workspace, and the eventual archived `run/sol_002/` artifacts.
- **Had any group-level outcome result been seen?** The context-rich controller has seen prior project material; the probe runtime reported none, and the analytic runtime will be a new session launched with the same memory-disabled boundary.
- **Repair or disposition:** preserve `sol_001`; launch `sol_002` with model `gpt-5.6-sol`, `xhigh` reasoning, memory disabled, user configuration ignored, live web search enabled, and a neutral workspace. Keep the frozen analytic instructions unchanged except for the permitted path/run label and a non-analytic requirement to obtain each timestamp from a real clock call.
- **Potential directional effect:** disabling memory and neutralizing the visible working path removes the identified contextual direction; the clock instruction affects audit fidelity only.
- **the author’s decision:** explicitly authorized: “Let’s re-run it… The point of this is blind replication.”

### DEV-20260722-04 — Stage 1B operations omitted from researcher action log

- **Timestamp:** 2026-07-22 21:29:24 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 1B gate.
- **Discovered by:** controller comparison of the external JSON event stream with the researcher `ACTION_LOG.md`.
- **What happened:** Stage 1B created the codebook/completion files and ran one read-only validation command, but it did not append those operations to the researcher action log. The Stage 1B prompt required only the two `stage1b` files and did not repeat the Stage 1 action-log instruction; the same session nevertheless should have continued the durable log.
- **Frozen requirement affected:** complete durable action logging across stages.
- **Files/messages affected:** `run/sol_002/ACTION_LOG.md`; repaired at the controller level by `run/sol_002/STAGE1B_RUNTIME_TRANSCRIPT.md`.
- **Had any group-level outcome result been seen?** no. The Stage 1B completion attests that no person-level record, group count, or group outcome rate was inspected, and the runtime emitted no web call.
- **Repair or disposition:** do not invent exact historical timestamps or modify the locked codebook. Preserve the external runtime’s exact ordered tool-event transcript with the controller-observed turn interval. Before Stage 1C, deliver this exact technical correction as its own non-analytic turn:

  > TECHNICAL LOGGING CORRECTION ONLY.
  >
  > Before beginning Stage 1C, obtain the current UTC time with an actual `date -u '+%Y-%m-%dT%H:%M:%SZ'` call and append a correction note to `ACTION_LOG.md`: Stage 1B created `stage1b/CODEBOOK.md` and `stage1b/STAGE_COMPLETE.md`, ran one read-only local validation, performed no browsing or outcome inspection, and did not append those operations to this log. State that exact individual historical timestamps are unavailable and are not being reconstructed.
  >
  > From now on, continue the append-only `ACTION_LOG.md` required by the original instructions. Obtain every timestamp from an actual UTC clock call; do not estimate, synthesize, backdate, or manually increment timestamps. Log each command, query, opened URL, file change, access failure, and material decision.
  >
  > Do not alter any locked Stage 1 or Stage 1B file. Do not browse, inspect cohort/person/group data, or begin Stage 1C during this correction turn.
  >
  > Stop and reply only: LOGGING_CORRECTION_COMPLETE, followed by the `ACTION_LOG.md` path and any blocking failure.
- **Potential directional effect:** none known; the omitted actions were directory creation, two file writes implementing the supplied direction-neutral codebook task, and a keyword validator.
- **the author’s decision:** not required for continuation because the sequence is completely recoverable and contains no outcome work; retain as a declared audit qualification.

### DEV-20260722-05 — One person’s initial base-result streams merged

- **Timestamp:** 2026-07-22 22:33:31 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 1C initial gate.
- **Discovered by:** experimenter during collection and confirmed by controller review.
- **What happened:** the runtime’s first batched web-search call merged four base-query result streams for research ID `R001`; the two remaining base streams were inaccessible. The experimenter preserved the technical record, assigned the merged stream to the four affected families, and used the maximum two triggered extra queries and three extra page attempts. All later people were searched with one built-in search call per query family.
- **Frozen requirement affected:** separate first-ten rank logging and uniform first-two eligible page opening for each of six base query families.
- **Files/messages affected:** `stage1c/raw/R001.json`, `stage1c/SEARCH_LOG.csv`, `stage1c/PERSON_OUTCOMES.csv`, `stage1c/DECISIONS_AND_DEVIATIONS.md`, and the action log.
- **Had any group-level outcome result been seen?** no; cohort flags and comparison questions remained undisclosed.
- **Repair or disposition:** preserve the raw failure without fabricating six independent streams. Require Stage 2 to retain this audit limitation and include a direction-neutral exclusion sensitivity for this record’s public-function analyses.
- **Potential directional effect:** unknown for that person; the salted work order and technical failure were fixed before cohort labels were available to the experimenter.
- **the author’s decision:** pending; controller provisionally retains the record with an explicit required sensitivity rather than silently discarding or reconstructing it.

### DEV-20260722-06 — Initial event adjudications did not uniformly apply the locked codebook

- **Timestamp:** 2026-07-22 22:33:31 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 1C initial gate.
- **Discovered by:** controller comparison of every qualifying row with its locally stored opened-source text.
- **What happened:** structural validation passed, but several apparent qualifying events relied on evidence that the Stage 1B codebook expressly excludes or dates differently: event announcements or captions without proof of substantive participation, a later publication year treated as an earlier interview date, and an episode date applied to an embedded interview the episode says was recorded earlier.
- **Frozen requirement affected:** substantive self-directed evidence, excluded-evidence rules, retrospective-account dating, date proxies, and complete gate validation.
- **Files/messages affected:** initial derived Stage 1C evidence/outcome artifacts and compiler; raw collection files remain preserved.
- **Had any group-level outcome result been seen?** no by the blind experimenter; the controller did not compute a group outcome rate or contrast.
- **Repair or disposition:** preserve the complete initial gate at `run/sol_002/stage1c_pre_semantic_repair/`; before revealing cohort flags, send only `controller/sol_002/STAGE1C_SEMANTIC_GATE_REPAIR.txt`. It requires a no-browsing audit of every positive and analogous candidate using only stored evidence and the existing codebook, followed by full revalidation.
- **Potential directional effect:** the initial errors could inflate public-evidence detection for whichever groups contain the affected people. The repair is defined without group labels or result direction and applies to every event row.
- **the author’s decision:** pending; this is a mandatory pre-lock validation repair, not a change to the endpoint.

### DEV-20260722-07 — One one-second action-log inversion

- **Timestamp:** 2026-07-22 22:49:40 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 1C controller gate.
- **Discovered by:** independent controller validator.
- **What happened:** the append-only researcher log places an R005 clock-call line timestamped `2026-07-23T04:43:33Z` immediately before the already-run batch-reader command timestamped `2026-07-23T04:43:32Z`. This is the only decreasing timestamp among 2,200 durable timestamped lines.
- **Frozen requirement affected:** nondecreasing append-only real-clock audit order.
- **Files/messages affected:** `ACTION_LOG.md` only.
- **Had any group-level outcome result been seen?** no.
- **Repair or disposition:** preserve the historical lines verbatim; do not reorder or invent a replacement time. The exact one-second inversion is accepted as a declared audit qualification. All material person-level decisions occur later and remain in real-time order.
- **Potential directional effect:** none known; it concerns the placement of a read-only batch command immediately before the next person’s clock call.
- **the author’s decision:** not required for analytic continuation; preserve and disclose.

### DEV-20260722-08 — R001 exclusion sensitivity added before cohort-label reveal

- **Timestamp:** 2026-07-22 22:57:04 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 2 launch preparation.
- **Discovered by:** controller implementation of `DEV-20260722-05`.
- **What happened:** the frozen Stage 2 prompt did not expressly name a sensitivity for a nonuniform person-level search stream because that technical failure did not yet exist at protocol freeze. Before revealing cohort labels, the controller added a requirement to report the public-function primary and secondary comparisons with research ID `R001` excluded, alongside rather than instead of the prespecified results.
- **Frozen requirement affected:** the Stage 2 prompt is supplemented by one technical, direction-neutral sensitivity analysis.
- **Files/messages affected:** `controller/sol_002/STAGE2_LAUNCH.txt` and the eventual Stage 2 public-function outputs.
- **Had any group-level outcome result been seen?** no. The supplement was fixed before the experimenter received cohort flags or computed a group comparison, and it states no group membership or direction.
- **Repair or disposition:** retain every prespecified primary and sensitivity analysis unchanged; add the R001-excluded results with an explicit technical-deviation label. Do not treat this sensitivity as primary or as an independent confirmation.
- **Potential directional effect:** unknown by construction; exclusion may move the public-evidence contrast in either direction.
- **the author’s decision:** [AUTHOR] authorized launch of the blind replication; this controller supplement implements the predeclared disposition of the observed collection failure without changing any primary endpoint.

### DEV-20260722-09 — Full SSA cohort table inaccessible; official fallback fixed before models

- **Timestamp:** 2026-07-22 23:07:31 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 2 external population benchmark.
- **Discovered by:** blind experimenter during permitted official-source access.
- **What happened:** the official SSA 2023 Alternative II male cohort CSV was identified, but the web connector exposed only a truncated preview and the isolated shell could not resolve the SSA host. Before running a group outcome model, the experimenter fixed a fallback to exact-year male cohort life expectancy from official SSA Actuarial Study 120 Table 11 and linearly interpolated survival to age 80 from official Table 7 decennial male-cohort anchors.
- **Frozen requirement affected:** the frozen analysis required an official era- and sex-matched U.S. population expectation but did not prescribe a specific release. The experimenter's pre-model decision file initially preferred a complete exact-year table capable of a conditional landmark expectation; the fallback limits the external benchmark to exact-year life expectancy at birth and birth-year-standardized survival to age 80.
- **Files/messages affected:** `stage2/ANALYSIS_DECISIONS.md`, `stage2/EXTERNAL_SOURCE_LOG.csv`, `stage2/ssa_male_cohort_expectations.csv`, `stage2/population_expectation.csv`, `stage2/ANALYSIS_REPORT.md`, and `ACTION_LOG.md`.
- **Had any group-level outcome result been seen?** no. The group/risk-set inventory had been checked, but the action log records that no group outcome model had run when the source fallback was frozen.
- **Repair or disposition:** retain the official SSA fallback and its narrower external estimand. Do not synthesize unavailable age-specific values. The controller independently verified all annual values and four survivor anchors against the official pages after the blind conclusion locked.
- **Potential directional effect:** none on any astronaut-versus-astronaut primary or sensitivity contrast, interval, threshold, or classification. The external healthy-selectee benchmark is less complete than planned.
- **the author’s decision:** not required for analytic continuation; preserve and disclose as an external-benchmark limitation.

### DEV-20260722-10 — Two self-generated temporary hash files briefly used outside the neutral root

- **Timestamp:** 2026-07-22 23:23:53 PDT (-0700)
- **Run/stage:** `sol_002`, Stage 2 deterministic-rerun check.
- **Discovered by:** blind experimenter and self-reported immediately in the action log.
- **What happened:** the deterministic artifact check wrote `[TMPDIR]/stage2_hash_before.txt` and `[TMPDIR]/stage2_hash_after.txt`. Each contained only a self-generated artifact count and aggregate hash. The experimenter immediately removed exactly those two files without a glob.
- **Frozen requirement affected:** the rerun protocol designated the neutral workspace as the analytic output root.
- **Files/messages affected:** the two deleted temporary files and `ACTION_LOG.md`; no project artifact or external dataset.
- **Had any group-level outcome result been seen?** yes, but the files contained only hashes of already generated locked Stage 2 artifacts.
- **Repair or disposition:** exact-path deletion completed within the same turn; preserve the action-log disclosure. No data were read from another workspace.
- **Potential directional effect:** none.
- **the author’s decision:** not required; retain as a minor procedural qualification.

### DEV-20260723-11 — Stale five-year public-function endpoint survived the author’s correction

- **Timestamp:** 2026-07-23
- **Run/stage:** protocol freeze through `sol_002` Stage 2.
- **Discovered by:** [AUTHOR] immediately after review of the locked Stage 2 result.
- **What happened:** before launch, [AUTHOR] had rejected the age-80-to-85 restriction as contrary to the intended question: a qualifying achievement at age 90 should count rather than be excluded, and differing public-documentation opportunity should be described rather than hidden by an arbitrary five-year window. The controller nevertheless froze the stale five-year cumulative-incidence endpoint as primary in `PREREGISTRATION.md`, copied it into the Stage 1B and Stage 2 prompts, and later summarized that stale endpoint as though it answered [AUTHOR]’s intended question.
- **Frozen requirement affected:** the public-function primary estimand, its ten-percentage-point materiality interpretation, and the `PUBLIC FUNCTION` Stage 2 classification. Survival methods and results are unaffected.
- **Files/messages affected:** `PREREGISTRATION.md`, `PROMPTS_CONTROLLER_ONLY.md`, `run/sol_002/stage1b/CODEBOOK.md`, `run/sol_002/stage2/ANALYSIS_DECISIONS.md`, `run/sol_002/stage2/ANALYSIS_REPORT.md`, `run/sol_002/stage2/BLIND_CONCLUSION.md`, and the controller’s initial result summary.
- **Had any group-level outcome result been seen?** yes when the mismatch was recognized. The author’s endpoint objection predates launch, but the durable protocol failed to encode it; the correction therefore cannot honestly be called a preregistered change.
- **Repair or disposition:** preserve every original file and hash. Do not rewrite the locked blind result. The evidence-collection window already continued from age 80 through death or 2026-06-01, so no search or adjudication rerun is required. Run a separately labeled `Stage 2R` analysis on the locked full-window evidence with any detected qualifying function event at any age 80+ as primary, the complete age-80-origin competing-risk curve and latest event ages as support-aware descriptions, and the old five-year result demoted to a curve readout/sensitivity.
- **Potential directional effect:** material and unknown at protocol freeze. In the already locked secondary table, using the full window changes both the event counts and comparator-coherence pattern relative to the five-year endpoint.
- **the author’s decision:** explicit on 2026-07-23: “Perfect, can you make note of this slip up and continue?”

### DEV-20260723-12 — Original Stage 2 secondary risk-difference interval mislabeled as Newcombe

- **Timestamp:** 2026-07-23
- **Run/stage:** controller audit of corrected `sol_002r` Stage 2R.
- **Discovered by:** independent controller reproduction of the corrected unrestricted contrast.
- **What happened:** original `sol_002/stage2/analysis.py` computed its secondary risk-difference interval by subtracting the upper and lower Wilson endpoints (`L1-U0`, `U1-L0`) but labeled the result a Newcombe score interval. The proper Newcombe method-10 construction combines the component Wilson distances by square root. For 3/22 versus 2/35, the original reported interval was approximately `[-13.9, +31.8]` percentage points; the corrected method-10 interval is `[-7.7, +28.0]`.
- **Frozen requirement affected:** the compatible interval attached to the original Stage 2 secondary crude public-function risk difference. No primary five-year estimate, bootstrap, survival analysis, event count, or point estimate is affected.
- **Files/messages affected:** original `run/sol_002/stage2/analysis.py`, `public_function_crude.csv`, `RESULTS_SUMMARY.csv`, `ANALYSIS_REPORT.md`, and the controller’s first summary; corrected implementation and results are in `run/sol_002r/stage2r/`.
- **Had any group-level outcome result been seen?** yes; discovered during post-lock method reproduction.
- **Repair or disposition:** preserve original locked files and hashes. Use the separately labeled Stage 2R interval for the corrected unrestricted endpoint and disclose the original mislabel.
- **Potential directional effect:** none on the point estimate, sign, fixed-threshold comparison, or endpoint classification; the corrected interval is narrower but still includes zero.
- **the author’s decision:** not required for completion; this is a mandatory audit correction discovered while executing the authorized Stage 2R.

### DEV-20260723-13 — Stage 2 implemented `OTHER_AVAILABLE` as all usable non-Apollo rows

- **Timestamp:** 2026-07-23 01:26:39 PDT (-0700)
- **Run/stage:** controller review during authorized `sol_002` Stage 3 reconciliation.
- **Discovered by:** controller comparison of the frozen preregistration with `stage2/analysis.py` and its generated birth-origin outputs.
- **What happened:** the preregistration defines `OTHER_AVAILABLE` as `OTHER_ALL` excluding prespecified pre-1970 accidental deaths. The Stage 2 implementation instead coded it as every non-Apollo row with usable birth and endpoint data. It consequently reported `OTHER_AVAILABLE` as 66 people, byte-for-person identical to `OTHER_ALL`, in the secondary birth-origin tables. The locked Stage 2 decision text also repeated the incorrect all-usable definition.
- **Frozen requirement affected:** the `OTHER_AVAILABLE` secondary birth-origin description only. The common 1973 landmark and age-80 risk sets are unchanged because every excluded death occurred before those origins; no primary RMST, corrected age-80-plus public-function estimate, bootstrap interval, composition sensitivity, or classification uses this mistaken birth-origin set.
- **Files/messages affected:** locked `run/sol_002/stage2/ANALYSIS_DECISIONS.md`, `analysis.py`, `survival_group_summary.csv`, `population_expectation.csv`, `km_birth_selected_ages.csv`, `RESULTS_SUMMARY.csv`, `ANALYSIS_REPORT.md`, and validation claims concerning `OTHER_AVAILABLE`.
- **Had any group-level outcome result been seen?** yes; this was found only during labeled post-lock reconciliation.
- **Repair or disposition:** preserve every locked Stage 2 file and hash. Reconstruct the preregistered accident-excluded set only in Stage 3, report the discrepancy as an implementation error rather than a rival scientific definition, and verify the mathematical identity of the corrected set with `OTHER_ALL` after the 1973 landmark and inside the age-80 risk set.
- **Potential directional effect:** the corrected secondary birth-origin comparator will appear longer-lived than the mistakenly unfiltered set because it removes pre-1970 accidental deaths. There is no effect on either locked primary conclusion.
- **the author’s decision:** not required to preserve the lock; the author explicitly authorized continuation through post-lock reconciliation.

### DEV-20260723-14 — Stage 3 exploratory import briefly wrote bytecode inside the reference tree

- **Timestamp:** 2026-07-23 01:33:03 PDT (-0700)
- **Run/stage:** `sol_002`, initial post-lock Stage 3 reconciliation.
- **Discovered by:** experimenter during its own immutable-tree hash check.
- **What happened:** an exploratory dynamic import of the approved reference analysis module caused Python to create one `__pycache__/apollo_mortality_survival_analysis.cpython-313.pyc` file under the staged immutable reference-code directory. The experimenter identified the exact file, deleted only that self-created bytecode and its empty cache directory, then reverified the complete reference tree against its pre-analysis aggregate and 63-file source manifest.
- **Frozen requirement affected:** the Stage 3 operational instruction not to edit `stage3/reference/`, although no source file or reference datum was edited.
- **Files/messages affected:** one transient generated bytecode file, the experimenter action log, Stage 3 contamination record, and runtime transcript.
- **Had any group-level outcome result been seen?** yes; Stage 3 is explicitly post-lock and comparative.
- **Repair or disposition:** exact-path removal completed during the same turn. Final reference aggregate `d4bc2493af7604615b5c9f6efd417d8ae4fe4799f5e27436c7d18bc23bd0e363` and every source/copy hash match. The final reconciliation reimplemented the needed small functions locally and did not import the reference module.
- **Potential directional effect:** none; the bytecode was a cache of already approved reference code and was removed before final analysis.
- **the author’s decision:** not required; preserve as a procedural qualification.

### DEV-20260723-15 — Experimenter Stage 3 validator is neutral-runtime specific

- **Timestamp:** 2026-07-23 02:04:03 PDT (-0700)
- **Run/stage:** controller audit of the permanent repaired Stage 3 archive.
- **Discovered by:** controller rerun of `stage3/validate.py` after archival.
- **What happened:** the experimenter validator hard-codes aggregate hashes of the neutral runtime’s locked trees. The permanent Stage 2 archive contains a controller-regenerated `analysis.cpython-313.pyc` already recorded by the official locked `STAGE2_SHA256.txt`; the neutral runtime retains the earlier bytecode build. Source `analysis.py`, every data/result file, and all conclusion hashes are identical, but the path-embedded generated bytecode differs, so the experimenter validator passes in the neutral runtime and fails its aggregate assertion if invoked from the permanent archive.
- **Frozen requirement affected:** validator portability only, not the analysis or lock.
- **Files/messages affected:** the two pre-existing Stage 2 bytecode copies and the experimenter Stage 3 validator’s runtime-specific aggregate constant. No locked file was changed during this audit.
- **Had any group-level outcome result been seen?** yes; this is post-lock validation.
- **Repair or disposition:** preserve both bytecode files and both manifests. The independent controller validator verifies the permanent official Stage 2 manifest, the neutral-runtime Stage 3 lock record, all source/data hashes, both conclusion hashes, and independently reconstructs every key Stage 3 result without importing experimenter code. It passes.
- **Potential directional effect:** none; bytecode is generated from byte-identical `analysis.py`, and the independent recomputation uses source CSVs directly.
- **the author’s decision:** not required; preserve as an archive-validation qualification.
