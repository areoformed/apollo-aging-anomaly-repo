# Experimenter Action Log

This is the chronological record of the Sol replication design and, after launch, the controller’s actions. It is experimenter-only until the blind result is locked.

## 2026-07-21 — protocol design pass

### 1. Received scope and guardrails

- the author identified the Sol replication directory and the existing Fable preregistration/prompts and comparator-cohort directory.
- the author explicitly requested a fresh, blind Sol instance and then requested that every step be documented inside this folder.
- The workspace `AGENTS.md` was honored: the sibling `Human Efforts` directory was not inspected or modified.

### 1A. Reconstructed pre-protocol colleague context

This protocol-design turn continued a longer colleague-side discussion. Before the step-by-step log began, the context-rich controller had already:

- explored Machine Efforts and read the then-current Substack preview at `[UNPUBLISHED-DRAFT-URL]`;
- discussed the narrow question “is there an anomaly?” while explicitly declining to test or tell the replication instance a causal mechanism;
- inspected or discussed NASA former-astronaut medical-surveillance material beginning with `https://www.nasa.gov/directorates/esdmd/hhp/treat/medical-examination-requirements-mer-for-former-astronauts/`;
- checked official NASA material about Apollo prime/backup crew rotation and accepted the author’s correction that backup crews commonly trained comprehensively and rotated toward later prime assignments, subject to exceptions;
- learned from the author that several comparator cohorts had already been materialized under `GPT 5-5/data/derived_cohorts/cohorts/`.

The exact earlier web-tool sequence and every additional NASA URL are no longer present in the visible context after automatic compaction, so they are not reconstructed as verbatim commands. This limitation is recorded rather than filled with invented detail. None of this context was or will be passed to the context-blind Sol instance.

### 2. Chose not to launch the real replication before freeze

The actual analytic instance was deliberately not spawned. Launching while prompts and endpoints were still being redesigned would either expose a mutable protocol or turn later improvements into undisclosed post-launch changes.

### 3. Ran an expendable context-leakage probe

- Spawn name: `blindness_audit`
- Context setting: `fork_turns: "none"`
- The probe was instructed not to inspect any file, not to conduct research, and only to report whether its initial context already contained substantive Apollo-project information. The exact tool-call message is not recoverable verbatim in the visible transcript after context compaction; this is a faithful semantic reconstruction and is labeled as such.
- Result, verbatim:

  > No substantive project-specific information is present. The initial context contains only:
  >
  > - The project/directory label “Apollo Aging Anomaly.”
  > - A “Machine Efforts” working directory and a separate “Human Efforts” directory.
  > - A guardrail prohibiting inspection or modification of “Human Efforts” unless the author explicitly requests it.
  >
  > It contains no results, hypotheses, datasets, astronaut identities, aging/vitality claims, methods, or prior analyses.

- Disposition: probe completed and is permanently excluded from the real run.
- Inference: `fork_turns: none` is adequate for substantive context blinding. Filesystem isolation remains procedural because child agents share the workspace.

### 4. Performed a minimal memory-registry check

Command:

```sh
rg -n -i "Apollo|Fable|Sol|aging anomaly" [PATH]
```

Result: no relevant Apollo-project memory entry was found; only unrelated string matches appeared. No prior-run memory content was imported into the design.

### 5. Inventoried the Machine Efforts workspace

Commands, run with working directory `./Machine Efforts`:

```sh
rg --files -g '!**/.git/**' | sed -n '1,240p'
find '5-6 Sol Replication' -maxdepth 4 -print
find 'GPT 5-5/data/derived_cohorts/cohorts' -maxdepth 2 -type f -print | sort
```

Observations:

- `5-6 Sol Replication` existed and was empty.
- Fable protocol and execution artifacts existed under `Fable Replication/`.
- Seven materialized cohort TSVs existed under `GPT 5-5/data/derived_cohorts/cohorts/`.
- The inventory remained entirely inside Machine Efforts.

### 6. Read the prior Fable design

Commands:

```sh
sed -n '1,260p' 'Fable Replication/preregistration.md'
sed -n '1,320p' 'Fable Replication/prompts.md'
```

Recorded strengths: clean context, staged disclosure, fixed censor date, per-row provenance, contamination control, decision logs, null reporting, and scope reconciliation.

Recorded improvement targets: endpoint chosen after evidence existed; public evidence framed as cognitive status; one constructor-chosen comparison frame; age cutoff left to the agent; and no exact mandatory query/opened-URL transcript.

### 7. Read comparator metadata and verified row counts

Commands:

```sh
sed -n '1,260p' 'GPT 5-5/data/derived_cohorts/README.md'
sed -n '1,220p' 'GPT 5-5/data/derived_cohorts/dataset_manifest.csv'
wc -l 'GPT 5-5/data/derived_cohorts/cohorts/'*.tsv
```

Result: the documented row counts and line counts agreed after accounting for one header line. The seven cohort names, meanings, counts, and manifest hashes were transcribed into `REFERENCE_COHORTS.md` for post-lock reconciliation only.

### 8. Read the Fable execution audit

Commands:

```sh
sed -n '1,300p' 'Fable Replication/Fable 5 – One Shot Data - Analysis/AUDIT_TRAIL.md'
sed -n '1,320p' 'Fable Replication/Fable 5 – One Shot Data - Analysis/DECISIONS_and_CONTAMINATION.md'
```

Material design observation: Fable used 17 research subagents and later disclosed that exact keystroke-level query sequences and all opened-but-uncited pages were not fully recoverable. This directly motivated the single-primary-agent and exact-log requirements here.

### 9. Re-read the applicable local guardrail

Command:

```sh
sed -n '1,220p' AGENTS.md
```

Confirmed again that Human Efforts was off-limits. No access was attempted.

### 10. Designed the Sol protocol

Decisions made before any Sol run:

- keep the research question noncausal;
- separate survival from public late-life functioning;
- fix an age-80 landmark;
- define affirmative function events without calling them clinical cognition;
- preserve no-public-evidence as unknown;
- construct core NASA, X-15, Dyna-Soar, MOL, union, and early-accident sensitivity cohorts;
- prohibit a backup-crew-as-control interpretation;
- add a no-browsing codebook stage before person-level outcome searches;
- require deterministic shuffled research order and exact search/opened-URL logs;
- precommit effect sizes, intervals, documentation sensitivities, and missingness bounds;
- lock the blind conclusion before existing-project reconciliation;
- use one primary Sol context and no subagents.

### 11. Created the protocol package

Files created with an atomic patch-based editing tool:

- `README.md`
- `PREREGISTRATION.md`
- `PROMPTS_CONTROLLER_ONLY.md`
- `LAUNCH_RUNBOOK.md`
- `DESIGN_RATIONALE.md`
- `REFERENCE_COHORTS.md`
- `DEVIATIONS.md`
- `ACTION_LOG.md`
- `run/AGENTS.md`
- `run/README.md`
- `run/sol_001/README.md`

No file outside `5-6 Sol Replication` was changed.

### 12. Verification still to be recorded

The following are completed later in this same design pass and appended below rather than backdated:

- recursive file inventory;
- checks for draft/freeze consistency;
- checks that controller-only outcome/prompt material is absent from the Sol-visible directory;
- cross-file stage-name and artifact consistency checks;
- final status that the real run remains unlaunched.

### 13. Verified reference-dataset hashes

Command:

```sh
shasum -a 256 'GPT 5-5/data/derived_cohorts/cohorts/'*.tsv
```

Result: all seven current TSV hashes matched `dataset_manifest.csv` and the values recorded in `REFERENCE_COHORTS.md`.

### 14. Ran the first mechanical package checks

Commands from `5-6 Sol Replication/`:

```sh
find . -maxdepth 4 -type f -print | sort
rg -n "DRAFT|NOT YET FROZEN|NOT YET|TBD|not yet" .
rg -n -i "hypoth|prior result|risk difference|cognit|vitali|survival|endpoint|comparator|Fable|29|44|69|98" run
rg -n "STAGE1_COMPLETE|STAGE1B_COMPLETE|STAGE1C_COMPLETE|STAGE2_COMPLETE|Stage 3|stage3" README.md PREREGISTRATION.md PROMPTS_CONTROLLER_ONLY.md LAUNCH_RUNBOOK.md
wc -l *.md run/*.md run/sol_001/*.md
```

Results:

- all expected files existed;
- draft/freeze markers were consistent with an unlaunched protocol;
- the Sol-visible directory contained no prior result, hypothesis, endpoint, cohort count, comparator definition, or Fable content;
- the stage names were consistently referenced;
- one mismatch was found: the Stage 1 prompt listed six artifacts but called them five.

### 15. Made pre-freeze mechanical corrections

- Corrected the Stage 1 completion count from five artifacts to six.
- Added a direction-neutral `search_disambiguator` fixed during Stage 1 so outcome queries do not call every military/test-pilot comparator an astronaut.
- Clarified that military program-history flags may overlap Apollo, but the `MILITARY_ONLY` comparator and `OTHER_ALL` exclude `apollo_flew=1`.
- Added RFC 4180/multi-value encoding rules to the Stage 1 CSV.
- Added `run/sol_001/AGENTS.md` so the no-parent-read rule exists inside the exact permitted directory, not only in its parent.

These are pre-freeze design edits, not deviations.

### 16. Spawned a read-only protocol auditor

- Spawn name: `protocol_audit`
- Context setting: `fork_turns: "all"`
- Scope: read only `5-6 Sol Replication`; no Human Efforts access; no edits.
- Requested checks: context/data leakage into `run/`, contradictions or missing stage artifacts, statistical defects, prompt/preregistration alignment, and action-log completeness with exact line references.
- This auditor is not the real Sol replication and will never be reused as it.

### 17. Managed the auditor’s duration without hiding it

The auditor did not return within the first 10-second and several 30-second waits. It was asked to stop exhaustive review and prioritize high-impact findings, then interrupted once and resumed with a follow-up request for at most ten bullets and no more tool calls. These controller actions did not touch the real run.

### 18. Received and applied the adversarial audit

The read-only auditor returned ten findings:

1. unequal observation time in an “any event after 80” endpoint;
2. overlapping/incomplete temporal outcome states;
3. discretionary extra searching and outcome-dependent documentation strata;
4. insufficiently fixed survival estimand;
5. nested comparator sensitivities described too much like independent corroboration;
6. missingness bounds answering a different estimand from observed detection;
7. Stage 1 wording leaking the class of later questions despite a stronger blinding claim;
8. a Stage 1C artifact-count mismatch;
9. self-attested rather than verifiable filesystem isolation;
10. incompleteness in this action log’s reconstructed pre-protocol context.

Pre-freeze corrections applied:

- made the primary public-function estimand five-year cumulative incidence after age 80, with death as a competing event and administrative censoring;
- retained crude “any event at age 80+” only as secondary;
- made temporal outcome states mutually exclusive and exhaustive;
- fixed six query families, ranked-result capture, a uniform page-opening budget, and capped resolution searches;
- relabeled documentation-depth analyses as descriptive source-availability checks, not adjustment or complete-case correction;
- made 1973-01-01 landmark RMST over 50 years the primary survival estimand, with birth-origin KM secondary;
- fixed primary effect measures and practical thresholds before launch;
- labeled all non-primary cohort contrasts as nested composition sensitivities;
- separated observed public-detection results from a differently interpreted latent-event bound;
- made Stage 1 contamination language outcome-generic and weakened the Stage 1 blindness claim honestly;
- corrected the Stage 1C artifact count from seven to eight;
- changed the runbook from an unverifiable promise to an explicit self-attested/procedural read boundary;
- added this reconstructed earlier-context entry and the missing local guardrail creation.

### 19. Removed a mathematically redundant sensitivity

A post-audit consistency pass identified that `OTHER_AVAILABLE` differs from `OTHER_ALL` only by pre-1970 deaths. Those people are already absent from both the 1973 landmark survival risk set and the age-80 outcome risk set. The protocol was corrected so `OTHER_AVAILABLE` appears only in secondary birth-origin survival description and as an explicit identity check elsewhere; it is not counted as another robustness result.

The auditor supplied advice only and modified no file.

### 20. Delegated threshold calibration to a context-clean methodologist

- Spawn name: `threshold_calibration`
- Context setting: `fork_turns: "none"`
- Restrictions: no local files, memory, prior conversation, or web.
- Information supplied: only a generic two-cohort setup of roughly 30 versus 70 people; a fixed 50-year post-landmark RMST estimand; a five-year post-age-80 public-detection risk difference; and the request for round practical-materiality anchors.
- No Apollo result, study-specific estimate, or predicted direction was supplied.

Result, verbatim:

> (A) RMST difference: **5 years** over the fixed 50-year horizon.  
> (B) Five-year detection risk difference: **10 percentage points**.  
> These round, conservative anchors represent clearly interpretable shifts while limiting overinterpretation in small, selected cohorts; they are neither power targets nor significance cutoffs. I received no study-specific result and no predicted direction.

The protocol was changed from the controller’s provisional 2.0-year/15-point anchors to the clean methodologist’s 5.0-year/10-point anchors. This occurred before freeze and before the real Sol run.

### 21. Performed a targeted post-correction re-audit

The same read-only `protocol_audit` agent was asked to check whether its ten findings were resolved and to report only remaining launch blockers. It found the search budget, temporal states, missingness distinction, Stage 1 disclosure, artifact count, and action-log reconstruction resolved. It identified three remaining blockers and one partial specification:

- an apparent event-window conflict;
- positive-only anomaly classification despite a two-sided “different” question;
- omission of `run/sol_001/AGENTS.md` from the freeze hash;
- analyst choice remaining in bootstrap/age-standardization details.

Disposition:

- the event-window conflict had already been corrected while the auditor was reading by separating the full age-80+ evidence-collection window from the primary age-[80,85) analytic window;
- classification was made symmetric by separating strength from direction;
- the Sol-local guardrail was added to both the review list and protocol hash command;
- bootstrap type, resampling unit, replicates, seed, percentiles, age-adjustment model, tie method, interval, and diagnostic were fixed before launch;
- partial event-date precision and boundary sensitivity were added because the five-year estimand requires an auditable date rule.

No real Sol analysis was launched.

### 22. Completed the final mechanical verification pass

Completion time: `2026-07-21 01:14:35 PDT (-0700)`.

Additional commands used during the post-audit pass included:

```sh
tail -n 90 ACTION_LOG.md
sed -n '88,215p' PREREGISTRATION.md
sed -n '78,220p' PROMPTS_CONTROLLER_ONLY.md
rg -n "2\.0|15 percentage|age-standard|influence-function|chosen method|fixed before group|primary effect to be positive|at least two|five query|seven paths|FUNCTION_DOCUMENTED|NO_QUALIFYING|within the window" README.md PREREGISTRATION.md PROMPTS_CONTROLLER_ONLY.md DESIGN_RATIONALE.md LAUNCH_RUNBOOK.md
rg -n "50,000|20260721|Schoenfeld|HIGHER|LOWER|evidence-collection window|analytic window|boundary-sensitive" PREREGISTRATION.md PROMPTS_CONTROLLER_ONLY.md
rg -n "run/sol_001/AGENTS.md|PROTOCOL_SHA256" LAUNCH_RUNBOOK.md README.md ACTION_LOG.md
rg -n -i "apollo|fable|survival|cognit|vitali|function|endpoint|comparator|risk|29|44|69|98|rmst|higher|lower" run
rg -n "DRAFT|NOT YET FROZEN|not yet frozen" README.md PREREGISTRATION.md PROMPTS_CONTROLLER_ONLY.md DEVIATIONS.md
find . -maxdepth 4 -type f -print | sort
date '+%Y-%m-%d %H:%M:%S %Z (%z)'
```

Results:

- no obsolete endpoint labels, provisional thresholds, old artifact counts, open-ended method choices, or positive-only classification text remained;
- the evidence-collection and primary analytic windows were distinct and consistent across the preregistration and exact prompts;
- bootstrap, age-adjustment, partial-date, direction, and boundary-sensitivity rules appeared in both protocol and prompt;
- the entire Sol-visible area remained free of Apollo, Fable, survival, vitality, cognition, endpoint, comparator, cohort-count, RMST, or direction language;
- all seven comparator hashes still matched their source manifest from the earlier checksum pass;
- `run/sol_001/README.md`, like the local guardrail, was added to the review and freeze-hash list because it is visible to Sol;
- draft markers consistently state that the protocol is not frozen;
- the real Sol run directory contains only its two neutral guardrail/status files;
- no file in Human Efforts was accessed or changed;
- the real Sol replication remains unlaunched pending the author’s review and freeze decision.

## Live-run append template

### 2026-07-22 19:59:27 PDT (-0700) — protocol freeze authorized

- **Run/stage:** `sol_001`, preflight.
- **Controller action or exact message:** [AUTHOR] explicitly authorized freezing and launching the Sol replication in parallel and requested mindful token use.
- **Runtime/model label:** Codex primary controller based on GPT-5; fresh child runtime requested through the integrated collaboration runtime with `fork_turns: "none"`.
- **Tool availability recorded at freeze:** local shell and patch editing, public-web research, local-file inspection, and controller/child collaboration messaging. The child receives the tools available to the integrated agent runtime but no inherited conversation.
- **Controller identity:** canonical root controller `/root`.
- **Planned run ID:** `sol_001`; planned child task name `sol_replication_001`.
- **Files inspected:** all protocol, controller, reference, guardrail, and neutral run-status files listed by `LAUNCH_RUNBOOK.md`.
- **Validation performed:** prior adversarial protocol audit, targeted re-audit, threshold calibration, final mechanical consistency pass, and a fresh preflight status-marker/run-directory check.
- **Hashes recorded:** pending the immediately following immutable-protocol manifest step.
- **Contamination/deviation status:** none; no real analytic instance had been launched before freeze.
- **Decision:** advance to manifest generation and clean-workspace verification.

### 2026-07-22 20:00:23 PDT (-0700) — frozen manifest and clean-workspace gate passed

- **Run/stage:** `sol_001`, preflight.
- **Controller action or exact message:** generated `PROTOCOL_SHA256.txt` from the eight immutable protocol inputs listed by `LAUNCH_RUNBOOK.md`, verified every entry with `shasum -a 256 -c`, hashed the manifest itself, and rechecked the Sol-visible workspace.
- **Agent response marker:** not applicable; the real child had not yet been spawned.
- **Files inspected:** `PROTOCOL_SHA256.txt` and the complete two-file prelaunch inventory under `run/sol_001/`.
- **Validation performed:** all eight protocol hashes returned `OK`; no unresolved `DRAFT`, `TBD`, or placeholder marker remained in the immutable launch inputs; `run/sol_001/` contained only `AGENTS.md` and `README.md`; the forbidden analytic-string scan returned no match.
- **Hashes recorded:** manifest SHA-256 `818add6cf973680ea0162bb08640a2eefa8665fcd7f23c55d2a51b09b7154684`.
- **Contamination/deviation status:** none.
- **Decision:** advance to the single fresh `sol_replication_001` spawn with the frozen Stage 1 message only.

### 2026-07-22 20:01:28 PDT (-0700) — primary Sol run launched

- **Run/stage:** `sol_001`, Stage 1.
- **Controller action or exact message:** spawned task `sol_replication_001` with `fork_turns: "none"` and delivered only the verbatim frozen `SPAWN / STAGE 1` message from `PROMPTS_CONTROLLER_ONLY.md`. No preface, article, hypothesis, prior number, result summary, Fable material, or future-stage prompt was sent.
- **Agent response marker:** canonical child task `/root/sol_replication_001`; controller status check returned `running`.
- **Files inspected:** none after spawn; the controller did not inspect mutable child outputs during this launch-status check.
- **Validation performed:** confirmed the child exists under the expected canonical task name and is actively running.
- **Hashes recorded:** frozen protocol manifest SHA-256 `818add6cf973680ea0162bb08640a2eefa8665fcd7f23c55d2a51b09b7154684`.
- **Contamination/deviation status:** none observed at launch.
- **Decision:** Stage 1 is live in parallel; wait for `STAGE1_COMPLETE` or a blocking failure without sending additional content.

### 2026-07-22 20:33:36 PDT (-0700) — Stage 1 preserved; frozen stop conditions triggered

- **Run/stage:** `sol_001`, Stage 1 gate.
- **Controller action or exact message:** received `STAGE1_COMPLETE`; inspected the six required artifacts, context attestation, child action log, construction/validation scripts, and run inventory; independently re-ran the child’s read-only mechanical validator; created and verified `run/sol_001/STAGE1_SHA256.txt`.
- **Agent response marker:** `STAGE1_COMPLETE`; six required paths; blocking failure claimed as none.
- **Files inspected:** all files under `run/sol_001/` as of the gate.
- **Validation performed:** 95 unique cohort rows, 552 source-ledger rows, exact schemas, dates, Boolean flags, deduplication, roster counts, source coverage, and 2,194 child validator checks passed. The six artifact hashes matched the hashes reported in the child log.
- **Hashes recorded:** Stage 1 manifest SHA-256 `952c7f42e8b4cf814e48aa2de802e78156b02982ceae973f6077a336b4e53ffb`.
- **Contamination/deviation status:** `DEV-20260722-01` records system-memory leakage of prior Apollo-project methods/context. `DEV-20260722-02` records impossible and internally nonmonotonic child timestamps. Both affect frozen stop conditions.
- **Decision:** stop before Stage 1B. Preserve the useful Stage 1 dataset as a contaminated, audit-qualified construction; do not send a follow-up prompt or restart without [AUTHOR]’s explicit decision.

### 2026-07-22 20:39:42 PDT (-0700) — author authorized a genuinely blind rerun

- **Run/stage:** `sol_002`, preflight.
- **Controller action or exact message:** [AUTHOR] directed the controller to rerun the replication and emphasized that the purpose is blindness. The controller traced the leak: `fork_turns: "none"` excludes inherited chat turns but integrated children still receive the shared system/developer envelope containing the automatic Apollo memory summary. The controller did not delete `sol_001`; it remains the audit record of the failed isolation mechanism.
- **Agent response marker:** not applicable.
- **Files inspected:** `run/sol_001/CONTEXT_ATTESTATION.md`, the frozen launch/run files, the local Codex feature/config listing, and the CLI help.
- **Validation performed:** launched a disposable external Codex probe in neutral path `[TMPDIR]/sol-blind-probe-20260722` with `--ephemeral --ignore-user-config --disable memories`, read-only sandboxing, and no file/web/environment inspection. It reported no project-specific people, research topics, hypotheses, methods, or results in its pre-message context. Probe thread ID `019f8d0d-e3e8-7f91-a047-9004179e4f2e`; input 14,376 tokens, of which 12,032 were cached; output 286 tokens; reasoning output 187 tokens.
- **Hashes recorded:** frozen protocol manifest remains `818add6cf973680ea0162bb08640a2eefa8665fcd7f23c55d2a51b09b7154684`; derived rerun-file hashes pending.
- **Contamination/deviation status:** `DEV-20260722-03` records the replacement runtime and narrowly scoped launch-mechanics changes.
- **Decision:** prepare separately labeled `sol_002` in a new persistent memory-disabled CLI session, with a neutral actual working directory and real-clock timestamp logging.

### 2026-07-22 20:42:00 PDT (-0700) — sol_002 clean-workspace and derived-prompt gate passed

- **Run/stage:** `sol_002`, preflight.
- **Controller action or exact message:** created the neutral actual workspace `[TMPDIR]/historical-cohort-replication-002`, confirmed it was empty, wrote the controller-only rerun protocol and Stage 1 launch message, and created the empty permanent archive marker `run/sol_002/README.md`.
- **Agent response marker:** not applicable; the analytic runtime had not been launched.
- **Files inspected:** `controller/sol_002/RERUN_PROTOCOL.md`, `controller/sol_002/STAGE1_LAUNCH.txt`, `run/sol_002/README.md`, and the neutral workspace inventory.
- **Validation performed:** confirmed the Stage 1 launch contains no prior method, number, result, article, Fable reference, hypothesis, or direction-revealing project title. The changes from the frozen Stage 1 message are limited to the neutral permitted path, operationally exact memory-disabled runtime wording, and real-clock timestamp instruction documented in `DEV-20260722-03`.
- **Hashes recorded:** rerun protocol `7967a3cf4555aacefc162cd5c8e00185fc9b8f419c58617457dc8b486342cd51`; Stage 1 message `d2257930bb726e727722ed98eb1131c00091c6b19a96eb2bcdbf516fdf19db58`; archive README `a3e2528117c1db45bf39d5efd08ce7fede9dbb275f15e28ef2d3a3b763c58681`.
- **Contamination/deviation status:** replacement launch mechanics already declared in `DEV-20260722-03`; no analytic runtime context exists yet.
- **Decision:** launch one new persistent external `gpt-5.6-sol` session with memory disabled and deliver only the derived Stage 1 message.

### 2026-07-22 20:43:04 PDT (-0700) — sol_002 memory-disabled runtime launched

- **Run/stage:** `sol_002`, Stage 1.
- **Controller action or exact message:** launched a new non-ephemeral Codex CLI session with `--disable memories`, `--ignore-user-config`, `--ignore-rules`, model `gpt-5.6-sol`, reasoning effort `xhigh`, live web search, workspace-write sandboxing, approval policy `never`, and working root `[TMPDIR]/historical-cohort-replication-002`; delivered only the bytes of `controller/sol_002/STAGE1_LAUNCH.txt` through stdin.
- **Agent response marker:** external thread ID `019f8d11-b42b-71f1-97a7-da53c0f8656d`; controller process session ID `87147`; turn started.
- **Files inspected:** the neutral workspace remained empty immediately after the launch event.
- **Validation performed:** the analytic thread ID differs from the disposable probe; no prior session was resumed; the launch omitted `--ephemeral` solely to allow later frozen-stage continuation in the same context.
- **Hashes recorded:** delivered Stage 1 message SHA-256 `d2257930bb726e727722ed98eb1131c00091c6b19a96eb2bcdbf516fdf19db58`.
- **Contamination/deviation status:** `DEV-20260722-03`; no contamination reported at launch.
- **Decision:** let Stage 1 run without controller messages; monitor only process state and the required early context-attestation file.

### 2026-07-22 21:18:25 PDT (-0700) — sol_002 Stage 1 locked and passed

- **Run/stage:** `sol_002`, Stage 1 gate.
- **Controller action or exact message:** received `STAGE1_COMPLETE` from external thread `019f8d11-b42b-71f1-97a7-da53c0f8656d`; hashed the neutral-workspace files; ran the child validator and an independent controller validator; copied the complete locked workspace into `run/sol_002/`; compared the temporary and archived stage directories byte-for-byte; and created `STAGE1_SHA256.txt` plus `STAGE1_CONTROLLER_GATE.md`.
- **Agent response marker:** `STAGE1_COMPLETE`, six required artifact paths, blocking failure reported as none.
- **Files inspected:** all files in the neutral workspace and all archived Stage 1 files.
- **Validation performed:** 95 cohort rows, 489 source rows, exact schemas, unique IDs/names, dates/status/censoring, Boolean/union rules, Apollo mission consistency, URL/fact coverage, 19/19 living-person searches, RFC 4180 records, expected inventory, and 202 nondecreasing real-clock action timestamps all passed. The context attestation was created before web work and reports no pre-message project information. No group contrast was performed.
- **Hashes recorded:** full locked-file hashes are in `run/sol_002/STAGE1_SHA256.txt`; controller validator SHA-256 `46d9f85332b80b54449affe86da24cade27859cb9bdafa3588f95e068a2f93ac`.
- **Runtime usage:** 14,821,247 input tokens, 14,425,088 cached input tokens, 65,553 output tokens, and 24,429 reasoning output tokens. The gross input is large because the web-heavy noninteractive turn replayed a growing context; most input was cached.
- **Contamination/deviation status:** `DEV-20260722-03` remains the declared launch-mechanics deviation. Neither prior Apollo memory leakage nor fabricated/future wall-clock timestamps recurred. The failed direct `curl` fetch and one corrected build-script delimiter error were logged by the experimenter and did not survive as data-integrity failures.
- **Decision:** Stage 1 passes and is locked. Advance only through the same persistent external thread, without any result summary or reference material.

### 2026-07-22 21:26:35 PDT (-0700) — sol_002 advanced to Stage 1B

- **Run/stage:** `sol_002`, Stage 1B.
- **Controller action or exact message:** resumed external thread `019f8d11-b42b-71f1-97a7-da53c0f8656d` with memories disabled, user configuration/rules ignored, no live-search option, model `gpt-5.6-sol`, reasoning effort `xhigh`, workspace-write sandboxing, and the same neutral root. Delivered only `controller/sol_002/STAGE1B_LAUNCH.txt`. The first resume command exited before starting a turn because `--skip-git-repo-check` was omitted; the corrected command added that flag and started the turn.
- **Agent response marker:** controller process session ID `83502`; same external thread ID; turn started.
- **Files inspected:** frozen Stage 1 manifest and derived Stage 1B prompt.
- **Validation performed:** every entry in `run/sol_002/STAGE1_SHA256.txt` verified `OK`; the append-only Stage 1 action-log state is preserved at `snapshots/ACTION_LOG_STAGE1.md`.
- **Hashes recorded:** Stage 1 manifest `4e030c8cc74cdc550130baf94535df9cb0b76c95a40ed32aa4739697e0b7f296`; Stage 1 controller gate `350593edd65e32fd9e15d257efe9a778522839d9e069f4f1f9949e22a1e14b9b`; delivered Stage 1B message `6070b0d833ea1f3314a5bc3ca98f48c4166c6d131c841b37636ea38ecb6be284`.
- **Contamination/deviation status:** no new analytic deviation; the pre-turn command-line error delivered no prompt and created no model turn.
- **Decision:** allow the no-browsing codebook stage to complete; do not send any summary or hint.

### 2026-07-22 21:29:24 PDT (-0700) — sol_002 Stage 1B complete; audit repair declared

- **Run/stage:** `sol_002`, Stage 1B gate.
- **Controller action or exact message:** received `STAGE1B_COMPLETE`; inspected both required files; verified the child’s codebook checks; confirmed the external event stream contained no web call or person/group inspection; confirmed the temporary Stage 1 directory remained byte-identical to the locked archive; and copied the Stage 1B files and final response into `run/sol_002/`.
- **Agent response marker:** `STAGE1B_COMPLETE`, two required artifact paths, blocking failure reported as none.
- **Files inspected:** `stage1b/CODEBOOK.md`, `stage1b/STAGE_COMPLETE.md`, the Stage 1B final-message file, the external event stream, and locked Stage 1 directories.
- **Validation performed:** the codebook preserves the fixed endpoint, mutually exclusive/exhaustive states, date bounds/midpoint/sensitivities, source tiers, publisher independence, documentation depth, impairment rule, absence-of-evidence rule, practical thresholds, and blank deviation table. Stage 1 files were unchanged.
- **Hashes recorded:** codebook `088b7571e8c80f2bde68b32948a093c211ccfa9018326058231f9585a2de8535`; Stage 1B completion `3d8222c30c6441f073c9f474e915c39ce361dbe72641a2da804206afee0e5db7`; final response `06b6dfd721b1e5e01f844645271f35e6317042482a7acf23eba04a31d691282e`.
- **Runtime usage:** the session reported cumulative 15,252,665 input / 14,844,928 cached input / 73,280 output / 27,396 reasoning-output tokens. Stage 1B’s delta from the prior completion event was 431,418 input / 419,840 cached / 7,727 output / 2,967 reasoning-output tokens.
- **Contamination/deviation status:** `DEV-20260722-04`: Stage 1B operations were not appended to the researcher action log. Their exact order and controller-observed interval are preserved in `STAGE1B_RUNTIME_TRANSCRIPT.md`; no historical timestamps are invented.
- **Decision:** Stage 1B analytic/codebook gate passes. Before Stage 1C, send only a predeclared technical reminder to resume real-clock action logging, followed separately by the frozen Stage 1C prompt.

### 2026-07-22 21:34:03 PDT (-0700) — logging repaired and sol_002 Stage 1C launched

- **Run/stage:** `sol_002`, Stage 1C.
- **Controller action or exact message:** first delivered the exact predeclared `controller/sol_002/LOGGING_CORRECTION.txt` as a separate no-browsing turn. The instance called the real UTC clock at 2026-07-23T04:32:00Z, appended a prospective correction without inventing historical timestamps, altered no locked file, and returned `LOGGING_CORRECTION_COMPLETE`. The controller archived the updated log and response, verified both prior stage manifests, then resumed the same thread with live search and delivered only `controller/sol_002/STAGE1C_LAUNCH.txt`.
- **Agent response marker:** correction complete with no blocker; Stage 1C controller process session ID `87431`; same external thread ID; Stage 1C turn started.
- **Files inspected:** appended action log, correction response, Stage 1/1B manifests, and frozen Stage 1C prompt.
- **Validation performed:** every Stage 1 and Stage 1B manifest entry verified `OK`; `snapshots/ACTION_LOG_PRE_STAGE1C.md` preserves the corrected pre-Stage-1C log state.
- **Hashes recorded:** correction message `be9892e97aa6d83106814923ab965296cefb5d6b9106b625380c3520eaf80ad7`; corrected log snapshot `4636d54dd893ba14b5764825c44d6c4d2d0f5026fa49cc5d013a0eebd650d5b3`; correction response `e664fe0d6a321a1715be95dea82828a99b543718ed46c90cd69528daf01b618c`; delivered Stage 1C message `3334a02a864dc414d806cda22eb5c4b198308115002bb596fcc24617804b211b`.
- **Runtime usage:** the correction turn reported cumulative 15,589,944 input / 15,179,008 cached input / 73,992 output / 27,656 reasoning-output tokens. Its increment over Stage 1B was 337,279 input / 334,080 cached / 712 output / 260 reasoning-output tokens.
- **Contamination/deviation status:** `DEV-20260722-04` is durably repaired prospectively and remains transparently documented.
- **Decision:** Stage 1C is live. Do not send any controller message or expose any group flag/result until `STAGE1C_COMPLETE` or a blocking failure.

### 2026-07-22 22:33:31 PDT (-0700) — sol_002 Stage 1C initial gate preserved; semantic repair required

- **Run/stage:** `sol_002`, Stage 1C controller gate.
- **Controller action or exact message:** received `STAGE1C_COMPLETE`; preserved the complete initial Stage 1C directory and action-log state before repair; independently checked all qualifying-event rows against the locally stored opened-page evidence and the frozen codebook; prepared the direction-blind, no-browsing consistency-audit message in `controller/sol_002/STAGE1C_SEMANTIC_GATE_REPAIR.txt`.
- **Agent response marker:** `STAGE1C_COMPLETE`, eight required artifact paths, blocking failure reported as none.
- **Files inspected:** all eight required Stage 1C artifacts, all thirteen qualifying-event source records in the raw audit files, the nonqualifying impairment row, Stage 1B codebook, Stage 1C compiler/validator, and the researcher action log.
- **Validation performed:** structural checks passed: 95 worklist/outcome rows, 57 eligible reviews, six base query families per eligible person, 57 raw audit files, 2,887 search-log rows, 14 evidence rows, exact schemas, extra-search/page caps, opened-source linkage, date arithmetic, state linkage, and prior-stage immutability. Semantic validation did not pass: multiple rows appeared to use evidence types or date proxies explicitly excluded by the frozen codebook.
- **Hashes recorded:** initial Stage 1C manifest `36637e1d2c92a878ada27864adff261999d95b1b641fdf89e4154dfeeaee3ef7`; initial action-log snapshot `abeb2613e12fe397eb2d2ed1330a3007046c69eee47304e63b38fe1ccefdc9b3`; delivered Stage 1C launch message `3334a02a864dc414d806cda22eb5c4b198308115002bb596fcc24617804b211b`.
- **Contamination/deviation status:** `DEV-20260722-05` records the one-person merged base-result stream. `DEV-20260722-06` records the semantic gate failure and direction-blind repair.
- **Decision:** do not lock Stage 1C and do not reveal cohort flags. Preserve the initial version, then require a no-browsing uniform re-audit of every candidate under the existing codebook.

### YYYY-MM-DD HH:MM:SS TZ — event

- **Run/stage:**
- **Controller action or exact message:**
- **Agent response marker:**
- **Files inspected:**
- **Validation performed:**
- **Hashes recorded:**
- **Contamination/deviation status:**
- **Decision:** advance / repair / stop

### 2026-07-22 22:57:04 PDT (-0700) — sol_002 Stage 1C repaired, validated, and locked

- **Run/stage:** `sol_002`, Stage 1C final gate.
- **Controller action or exact message:** received the repaired `STAGE1C_COMPLETE` response from the same memory-disabled thread; archived the final repaired directory and response byte-for-byte; preserved the complete initial version separately; wrote a source-by-source semantic audit; ran an independent controller validator; and verified the Stage 1, Stage 1B, and final Stage 1C manifests.
- **Agent response marker:** `STAGE1C_COMPLETE`, eight required artifact paths, blocking failure reported as none.
- **Files inspected:** all repaired Stage 1C artifacts, all stored evidence underlying retained and removed candidates, the frozen codebook, the repair response, the initial preserved version, and all three locked-stage manifests.
- **Validation performed:** 95 outcome/worklist rows, 57 eligible reviews, 342 fixed base-query families, 57 raw JSON records, 2,887 search rows, six final evidence rows, five people with any full-window function detection, two with primary-window function detection, one impairment event, exact source and state linkage, page/query caps, raw-result integrity, and prior-stage immutability passed. The only timestamp-order issue is the declared one-second inversion in `DEV-20260722-07`.
- **Hashes recorded:** final Stage 1C manifest `150c1b5e02e6769a63ccdfee2446c8f4159765e8fc34791e661a61a27242a8eb`; repair message `dd306e1021a95fc9ef1d6452694a45391575ec1054b69c6e3d4d8396281bf5c1`; controller semantic audit `5ccb64cb79b2da98d9b34aeb8a2fa8fa4e5753596e6e48a2f2ad01fd82e6bd5b`; controller validator `c1fe10c002430ee7fb0306163d9e09ec40f4f03b27fae73693d2985b96d9d67a`; repaired final response `fc576b5dbddb0306e818f25973af7206f9634b0d59c414a7cb380caf1690c3be`.
- **Runtime usage:** cumulative 59,551,895 input / 58,309,888 cached input / 204,171 output / 69,716 reasoning-output tokens; repair increment 9,893,541 / 9,742,592 / 30,918 / 11,410.
- **Contamination/deviation status:** `DEV-20260722-05` through `DEV-20260722-07`; no group labels, comparison rate, result direction, prior result, or reference dataset were revealed during repair.
- **Decision:** Stage 1C passes and is locked. Before revealing cohort flags, add only the direction-neutral R001 exclusion sensitivity required by `DEV-20260722-05`; then advance through the frozen Stage 2 analysis prompt.

### 2026-07-22 22:59:51 PDT (-0700) — sol_002 advanced to blind Stage 2 analysis

- **Run/stage:** `sol_002`, Stage 2.
- **Controller action or exact message:** verified the locked Stage 1C manifest and independent validator; wrote `controller/sol_002/STAGE2_LAUNCH.txt` as the exact frozen Stage 2 prompt plus the direction-neutral R001 exclusion sensitivity declared in `DEV-20260722-08`; resumed the same memory-disabled external Sol thread with user configuration/rules ignored, live search permitted only for the official U.S. population life table, and the same neutral workspace.
- **Agent response marker:** external thread `019f8d11-b42b-71f1-97a7-da53c0f8656d`; controller process session ID `93685`; turn started.
- **Files inspected:** final Stage 1C manifest, controller gate, independent validator output, frozen Stage 2 prompt, and derived launch message. No group comparison was computed or shown to the controller before launch.
- **Validation performed:** every final Stage 1C manifest entry returned `OK`; the controller validator returned no problems with 95 worklist rows, 57 eligible records, 2,887 search rows, six event rows, five qualifying-function people, two primary-window function events, one impairment event, and the one declared log inversion.
- **Hashes recorded:** Stage 2 launch message `628606bae2ec906dc00cb047457b57e524ec5e374ad7fe83aa57de7d3d37c567`; Stage 1C controller gate `19c51a793409a898b7e2a2af705f3c6896b7379c440655b9c744ee81f8b83989`; final Stage 1C manifest `150c1b5e02e6769a63ccdfee2446c8f4159765e8fc34791e661a61a27242a8eb`; controller validator `c1fe10c002430ee7fb0306163d9e09ec40f4f03b27fae73693d2985b96d9d67a`.
- **Contamination/deviation status:** `DEV-20260722-08` is the sole Stage 2 prompt supplement. It was fixed before label reveal and conveys no group identity, rate, direction, or prior finding.
- **Decision:** Stage 2 is live. Do not send hints, corrections, prior numbers, or reference data; monitor only until `STAGE2_COMPLETE` or a blocking failure.

### 2026-07-22 23:28:50 PDT (-0700) — sol_002 Stage 2 completed and independent audit passed

- **Run/stage:** `sol_002`, Stage 2 final gate.
- **Controller action or exact message:** received `STAGE2_COMPLETE`; copied the complete Stage 2 directory, final researcher action log, and final response byte-for-byte into the permanent run archive; ran the experimenter's read-only validator; wrote and ran a separate controller validator that does not import the experimenter's analysis; and opened the cited official SSA tables after the blind conclusion was locked.
- **Agent response marker:** `STAGE2_COMPLETE`, eight required artifact paths, blocking failure reported as none.
- **Files inspected:** all Stage 2 code, decisions, tables, figures, reports, source log, validation, contamination, completion, blind conclusion, the final researcher action log, and official SSA Table 11 / Table 7 pages.
- **Validation performed:** independently reconstructed all groups and events; reproduced all three RMST, all three primary public-function, and the R001-excluded 50,000-replicate bootstraps exactly; checked Cox Efron score/standard errors, crude counts, SSA year coverage and anchors, classifications, and required inventory. The experimenter's validator also passed.
- **Hashes recorded:** controller validator `d5bc3a574f6aba19e13d0152df457a5bfe2263ec4644c2c7c80fefad4fb4dd75`; child final response `0efb2c9d8c42c53bfa98999b58450a498825fc6470c0a18d629d274d865bb86a`; blind conclusion `727d766af5a058012d6f68c6ce1890dc48b1625d9fae9d6ebfd18661579111df`; analysis report `41b26e07f2aac5e48c8da9dac1f2588d08266ec0b2b03073de69f0b5b8931040`; Stage 2 manifest `014ef8b64ef864b17d62857bce13feee8a8d0962aee488cbec815e4fbf355378`.
- **Runtime usage:** cumulative 68,579,545 input / 67,161,600 cached input / 267,594 output / 92,499 reasoning-output tokens. Stage 2 increment over the post-repair cumulative total was 9,027,650 / 8,851,712 / 63,423 / 22,783.
- **Contamination/deviation status:** no prior Apollo result or parent/sibling data entered the blind thread. `DEV-20260722-09` records the official-source fallback; `DEV-20260722-10` records two immediately removed self-generated temporary hash files.
- **Decision:** Stage 2 passes. Lock the complete archive and its blind conclusion before any Stage 3 reconciliation with prior datasets.

### 2026-07-23 — author identified stale endpoint; corrected Stage 2R authorized

- **Run/stage:** `sol_002`, post-lock protocol audit and Stage 2R preparation.
- **Controller action or exact message:** [AUTHOR] questioned the reported “qualifying five-year event” because the prior discussion had rejected the age-80-to-85 restriction. The controller traced the restriction through the frozen preregistration, prompts, codebook, decisions, and report; acknowledged that the stale brief had been frozen in error; and proposed preserving the run while reanalyzing the already collected unrestricted age-80-plus evidence.
- **Agent response marker:** [AUTHOR] replied, “Perfect, can you make note of this slip up and continue?”
- **Files inspected:** frozen protocol, controller-only prompts, Stage 1B codebook, Stage 2 decisions, and Stage 2 report.
- **Validation performed:** confirmed that Stage 1C collection continued after age 85 through death or 2026-06-01 and retained every qualifying full-window event, so no evidence search or adjudication needs repetition.
- **Hashes recorded:** the original Stage 2 manifest remains `014ef8b64ef864b17d62857bce13feee8a8d0962aee488cbec815e4fbf355378`; no locked run artifact was altered.
- **Contamination/deviation status:** `DEV-20260723-11`. Although [AUTHOR]’s correction predates launch, recognition after outcome lock makes Stage 2R a labeled post-lock protocol correction, not a retroactively preregistered primary.
- **Decision:** preserve original Stage 2; create a fresh memory-disabled Stage 2R analyst workspace containing only locked Stages 1–1C, not the original Stage 2 results; make unrestricted any-age-80-plus detection primary and the five-year quantity a sensitivity/curve readout.

### 2026-07-22 23:39:09 PDT (-0700) — fresh memory-disabled Stage 2R analyst launched

- **Run/stage:** `sol_002r`, corrected Stage 2R.
- **Controller action or exact message:** created neutral workspace `[TMPDIR]/historical-cohort-replication-002r`; copied only byte-identical locked `stage1/`, `stage1b/`, and `stage1c/`; delivered only `controller/sol_002r/STAGE2R_LAUNCH.txt` to a new external `gpt-5.6-sol` thread with memories, user configuration, and rules disabled, no web instruction, workspace-write sandbox, and approval policy `never`.
- **Agent response marker:** external thread `019f8db2-15e1-76f0-b56e-fadab843293b`; controller process session ID `99942`; turn started.
- **Files inspected:** the new thread inventory and its pre-data `stage2r/CONTEXT_ATTESTATION.md`.
- **Validation performed:** all three copied locked-stage directories compared byte-for-byte with the permanent `sol_002` archive; the neutral workspace contained no original `stage2/`, prior response, prior action log, prior result, or reference dataset. The attestation reports no pre-message person, cohort outcome, estimate, direction, conclusion, method result, article, or hypothesis.
- **Hashes recorded:** corrected endpoint protocol `42d23d1adeac5c44bed08f98a3e35243410dd1e3a902350a692db32921809861`; launch message `4228a9d18a435ac96a9642027187f6658a544062c0678fb9be7c2ffc4dacaf01`; context attestation `ee988d91571f79101107197d9f73aeb42a28852440d2d92a2d38969908908f5f`.
- **Contamination/deviation status:** `DEV-20260723-11` remains a post-lock endpoint correction; the fresh analyst is blinded to the original Stage 2 result but that runtime isolation does not retroactively make the endpoint change preregistered.
- **Decision:** allow Stage 2R to run without intervention; do not expose the original Stage 2 numbers or conclusions.

### 2026-07-23 — corrected Stage 2R completed and independent reproduction passed

- **Run/stage:** `sol_002r`, Stage 2R final audit.
- **Controller action or exact message:** received `STAGE2R_COMPLETE`; copied the complete neutral workspace artifacts into `run/sol_002r`; inspected all corrected reports/tables; wrote and ran `controller/sol_002r/validate_stage2r_controller.py`, which does not import the experimenter’s analysis.
- **Agent response marker:** `STAGE2R_COMPLETE`, eleven required artifact paths, blocking failure reported as none.
- **Files inspected:** complete Stage 2R artifacts, fresh action log and response, all corrected numerical tables, locked input hash manifest, and the original Stage 2 interval implementation solely for post-lock audit comparison.
- **Validation performed:** independently reproduced the unrestricted counts, point estimate, Newcombe and 50,000-replicate bootstrap intervals, composition/R001 sensitivities, six Aalen–Johansen readouts and risk sets, five event ages, all 86 locked-input hashes, and the corrected conclusion. Validator returned no problems.
- **Hashes recorded:** controller validator `7443d38382c96bdb8238ffbf2a9de9b2edfe0cac4c13e9db2ae9226f79df7b13`; complete Stage 2R manifest `4f201770759a29ee3113c159b1a3f1de9f8523915d43c889031b22429c65e64e`; fresh final response `e4c3634b37ab2b169f9ebeb13de4517534006fdd2a32f2b4d9087b8d2b678367`; corrected conclusion `bccdae4e350accb7c34e7324cfed85f441a181009c73278529af1bb9b83a6600`; fresh thread cumulative usage 1,217,669 input / 1,121,280 cached input / 40,518 output / 11,514 reasoning-output tokens.
- **Contamination/deviation status:** `DEV-20260723-11` remains the material stale-endpoint correction. `DEV-20260723-12` records the newly discovered original secondary-interval mislabel. No original Stage 2 result entered the fresh Stage 2R thread.
- **Decision:** corrected endpoint analysis passes. Preserve both the original blind run and this post-lock corrected branch; lock Stage 2R before any reference-dataset reconciliation.

### 2026-07-23 01:22:02 PDT (-0700) — authorized Stage 3 reconciliation launched

- **Run/stage:** `sol_002`, labeled post-lock Stage 3.
- **Controller action or exact message:** after [AUTHOR] explicitly asked to continue, prepared a hash-verified bundle of approved `GPT 5-5` derived cohorts, reference Run 1 results/code/population file, and the immutable corrected Stage 2R branch; placed it only under the neutral runtime’s `stage3/`; then resumed the same clean external Sol thread with memories, user configuration, and rules disabled. The launch preserved the frozen three-pass Stage 3 prompt and operationally required the corrected unrestricted age-80-plus endpoint to remain primary.
- **Agent response marker:** external thread `019f8d11-b42b-71f1-97a7-da53c0f8656d`; controller process session ID `31324`; turn started.
- **Files inspected:** Stage 3 frozen prompt; locked Stage 2 and Stage 2R gates/manifests; approved reference cohorts, methods dossier, Run 1 outputs/code, and archived SSA file; no Human Efforts file.
- **Validation performed:** 63 bundle entries copied with zero hash mismatches: 39 approved reference files and 24 immutable Stage 2R supplement files. Both locked analysis validators passed immediately before launch.
- **Hashes recorded:** Stage 3 launch message `191ae994389a9ff56af3c48b87d4bbb1b473c94178ace9827ac7978dcceea490`; reference manifest `eeb3244a1885d601718634509db2cf05aa00f59be72a4b74b37b357ad4e3cebe`; preparation script `e7f76f5f7d81ae4940072a526835f7638294e78cae5beb3557000ed9f198bda3`.
- **Contamination/deviation status:** reference exposure is intentional and occurs only after both conclusions were locked. `DEV-20260723-13` records a newly found post-lock implementation error in the secondary `OTHER_AVAILABLE` birth-origin set; it cannot affect either locked primary result.
- **Decision:** Stage 3 is live. Preserve both conclusions verbatim; allow only post-lock reconciliation artifacts to change.

### 2026-07-23 01:44:06 PDT (-0700) — initial Stage 3 completed; controller repair required

- **Run/stage:** `sol_002`, initial labeled Stage 3.
- **Controller action or exact message:** received `STAGE3_COMPLETE`; archived the complete neutral Stage 3, action log, runtime transcript, and final response byte-for-byte; inspected all definitions, row differences, harmonized results, endpoint cross-tabs, validation, contamination, and completion artifacts.
- **Agent response marker:** `STAGE3_COMPLETE`, thirteen Stage 3 artifacts plus the append-only action log; blocking failure reported as none.
- **Files inspected:** complete initial Stage 3 archive; approved reference bundle; locked Stage 2 and Stage 2R conclusions; frozen preregistration solely at the controller layer.
- **Validation performed:** experimenter validation passed in the neutral runtime; controller confirmed 95 shared identities, three reference-only high-speed pilots, exact Apollo membership, three one-day date disagreements, 13 exclusive-source-key/overlap-flag representation differences, and the 57-person public-endpoint cross-tab.
- **Hashes recorded:** initial Stage 3 manifest `fb5af5e314803d03a227fec4e3cf78e6778023a0e7e4bcfcd3ea86ec6464a309`; initial reconciliation `98411aefa2af89adf718e2683c00aee4dd4ac3b68227c9291d2da7565ef80d6b`; initial completion `d14f61b299b00d7657363cf79b8f9e74b6d79daff1611889eb768ed64a0174c9`.
- **Runtime usage:** cumulative clean-thread usage 75,101,109 input / 73,082,880 cached input / 321,074 output / 109,998 reasoning-output tokens; initial Stage 3 increment over locked Stage 2 was 6,521,564 / 5,921,280 / 53,480 / 17,499.
- **Contamination/deviation status:** `DEV-20260723-14` records one transient self-generated reference bytecode cache, removed exactly with the reference hash restored. The controller found that the neutral runtime lacked the frozen `OTHER_AVAILABLE` definition and therefore the initial reconciliation described but did not identify the locked Stage 2 implementation error recorded as `DEV-20260723-13`.
- **Decision:** preserve the complete initial Stage 3; send only the exact frozen `OTHER_AVAILABLE` definition and require a narrow post-lock secondary correction without browsing or primary reanalysis.

### 2026-07-23 02:04:03 PDT (-0700) — repaired Stage 3 independently reproduced and passed

- **Run/stage:** `sol_002`, Stage 3 controller repair and final gate.
- **Controller action or exact message:** resumed the same memory-disabled thread with `controller/sol_002/STAGE3_CONTROLLER_REPAIR.txt`; required reconstruction of the frozen accident-excluded secondary set, a person-level correction table, six corrected birth-origin KM readouts, explicit implementation-error disclosure, deterministic regeneration, and complete lock revalidation. Preserved the initial version separately, archived the repaired canonical version, recovered the exact initial action-log state from the current append-only prefix, and ran a new pure-standard-library independent validator.
- **Agent response marker:** `STAGE3_REPAIR_COMPLETE`, nine repaired Stage 3 artifacts plus the action log; blocking failure reported as none.
- **Files inspected:** repaired Stage 3 code/tables/reports; initial Stage 3 archive; all manifests; runtime and repair transcripts; controller deviation log.
- **Validation performed:** independently reconstructed all cohort sets, corrected `OTHER_AVAILABLE` as 54 with 12 exclusions, exact 53-person post-1973 and 35-person age-80 identities, all six corrected KM points, harmonized RMST and 50,000-bootstrap interval, both public-endpoint risks/Newcombe/Fisher/bootstrap results, and the 57-person cross-tab. Result: `STAGE3_CONTROLLER_VALIDATION_PASS`.
- **Hashes recorded:** controller repair message `3101dbe7b7a8bd0848146b00318d8d754517658a1a5e7929fbf8b5754075f2cd`; canonical repaired Stage 3 manifest `49177788a2459fff0833f6840dd814ff8933bd38e68d41b784447c160e6cde34`; controller validator `6283655bb48bd681a6d48965b4be5a70cc0bcd53ff39ca6af1d6c2cc95143841`; controller audit `f73d65748d5364581a8d0f04d99301f81296e04d6ddbe478120bcc86e6aad124`; controller gate `b3c65152b250acb9309134b8c1b889d68404b8c6fd7e7dce2e9d1d6d2f091fab`.
- **Runtime usage:** repaired cumulative clean-thread usage 77,651,611 input / 75,526,656 cached input / 341,717 output / 118,359 reasoning-output tokens. Total Stage 3 plus repair increment over locked Stage 2: 9,072,066 input / 8,365,056 cached / 74,123 output / 25,860 reasoning output.
- **Contamination/deviation status:** `DEV-20260723-13` is corrected in Stage 3 and affects only secondary birth-origin outputs; `DEV-20260723-14` is fully restored; `DEV-20260723-15` records neutral-runtime validator path specificity caused solely by separately manifested generated bytecode. Both conclusion hashes and every source/data/result hash remain unchanged.
- **Decision:** Stage 3 passes. The blind replication protocol is complete. Interpret future work as article/editorial or a new endpoint study, not as another stage of this run.
