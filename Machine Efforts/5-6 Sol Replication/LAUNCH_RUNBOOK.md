# Launch Runbook

This is the controller’s exact operating procedure. The controller is the context-rich colleague; Sol is the context-blind experimenter.

## 1. Preflight and freeze

1. Confirm `README.md`, `PREREGISTRATION.md`, `PROMPTS_CONTROLLER_ONLY.md`, `DESIGN_RATIONALE.md`, `REFERENCE_COHORTS.md`, `ACTION_LOG.md`, `DEVIATIONS.md`, `run/AGENTS.md`, `run/sol_001/AGENTS.md`, and `run/sol_001/README.md` have been reviewed.
2. Resolve every `DRAFT`, `TBD`, and open question.
3. Enter the freeze time in `PREREGISTRATION.md` and `PROMPTS_CONTROLLER_ONLY.md`.
4. Record runtime/model label, tool availability, controller identity, and planned run ID `sol_001` in `ACTION_LOG.md`.
5. Generate a SHA-256 manifest from the protocol files, excluding the mutable run directory and action/deviation logs. Recommended command from this folder:

   ```sh
   shasum -a 256 README.md PREREGISTRATION.md PROMPTS_CONTROLLER_ONLY.md DESIGN_RATIONALE.md REFERENCE_COHORTS.md run/AGENTS.md run/sol_001/AGENTS.md run/sol_001/README.md > PROTOCOL_SHA256.txt
   ```

6. Record the command, timestamp, and manifest hash in `ACTION_LOG.md`.
7. Confirm `run/sol_001/` contains no project data or future prompt text.

Do not launch while the protocol is still marked draft.

## 2. Spawn the fresh instance

Create exactly one child agent with:

- task name: `sol_replication_001`
- context fork: `none`
- initial message: exactly the `SPAWN / STAGE 1` text in `PROMPTS_CONTROLLER_ONLY.md`, with no preface or summary

For the integrated agent runtime, the controller action is conceptually:

```text
spawn_agent(
  task_name="sol_replication_001",
  fork_turns="none",
  message=<verbatim Stage 1 text>
)
```

Record the returned canonical agent name/ID and launch time. Do not send conversational encouragement, the Substack URL, prior numbers, hypotheses, Fable materials, or future-stage prompts.

## 3. Stage gate procedure

At every completion marker:

1. Do not summarize results back to Sol.
2. Confirm only expected files exist under the run directory.
3. Verify the stage-completion attestation, contamination log, action log, and validation report.
4. Review Sol’s self-attestation, durable action log, and any controller-visible tool transcript for evidence of a read outside `run/sol_001/`. Any discovered parent read is a major deviation. Because this runtime does not provide an OS-level read audit, the absence of forbidden reads cannot be proven; describe the boundary as procedural/self-attested contextual blinding.
5. Run mechanical schema/date/duplicate checks where possible without changing Sol’s data.
6. Hash every completed stage artifact. Example:

   ```sh
   find run/sol_001/stage1 -type f -print0 | sort -z | xargs -0 shasum -a 256 > run/sol_001/STAGE1_SHA256.txt
   ```

7. Hash the manifest itself and append the value and timestamp to the controller `ACTION_LOG.md`.
8. Make no content edits to the locked stage. If a repair is necessary, have Sol create an append-only correction file before advancing and record a deviation.
9. Send the next prompt verbatim using a follow-up task to the same agent context.

The gate sequence is:

`Stage 1 → hash → Stage 1B → hash → Stage 1C → hash → Stage 2 → hash blind conclusion → optional Stage 3`

## 4. Messaging discipline

- The controller sends only the exact current-stage prompt.
- Never send a result summary, hint, reassurance about direction, or comparison with prior work.
- A technical correction may be sent only if required to complete the frozen task. Copy it verbatim into `DEVIATIONS.md` first.
- If Sol asks a methodological question already answered by the frozen prompt, point to the exact prompt clause without elaboration.
- If the prompt genuinely leaves a material choice open, Sol must record its own direction-blind decision before inspecting the relevant outcomes.

## 5. Stop conditions

Stop and do not advance if:

- Sol reports substantive prior knowledge of this project or its results;
- Sol reads a forbidden local parent/sibling file;
- Sol opens a contaminating group-level study/draft rather than merely logging it;
- cohort construction occurs after person-level outcome inspection;
- Stage 1B codebook is written after outcome browsing;
- Stage 1C computes group rates before evidence collection is locked;
- the primary instance spawns subagents;
- required logs are materially incomplete;
- the instance context is replaced or continuity cannot be established.

The event is an operational result. Record it; do not quietly restart. the author decides whether a new, separately labeled run is warranted.

## 6. Reconciliation gate

Stage 3 begins only after:

1. `stage2/BLIND_CONCLUSION.md` exists;
2. all Stage 2 files have hashes;
3. the controller action log records the blind conclusion hash and time;
4. reference files are copied—not linked—into `stage3/reference/` with their original project hashes recorded;
5. the reference copy contains no prose result summaries beyond the declared cohort metadata unless explicitly approved.

## 7. Final archive

The archive must contain:

- frozen protocol and its hash manifest;
- canonical agent name/ID and available model/runtime metadata;
- exact delivered messages and timestamps;
- Sol’s context attestation and complete action/query/URL logs;
- all stage outputs, scripts, software versions, and hash manifests;
- controller validation notes;
- all contaminations and deviations;
- blind conclusion and its pre-reconciliation hash;
- post-lock reconciliation, if run.
