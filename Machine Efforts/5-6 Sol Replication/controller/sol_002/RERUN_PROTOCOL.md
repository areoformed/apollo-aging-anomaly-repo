# sol_002 Rerun Protocol

## Purpose

`sol_002` is the author-authorized replacement for the stopped, context-contaminated
`sol_001` run. `sol_001` remains preserved and is not an analytic continuation.

## Immutable parent protocol

The analytic design remains the protocol frozen on 2026-07-22 at 19:59:27 PDT.
Its manifest hash is:

`818add6cf973680ea0162bb08640a2eefa8665fcd7f23c55d2a51b09b7154684`

## Runtime boundary

The integrated collaboration-child mechanism is not used. All children in that
tree inherit the same system/developer envelope, including the automatic memory
summary, even when `fork_turns` is `none`.

The replacement is a new persistent Codex CLI session launched with:

- model `gpt-5.6-sol`;
- reasoning effort `xhigh`;
- `--ignore-user-config`;
- `--disable memories`;
- live web search explicitly enabled;
- no inherited conversation or prior session;
- a neutral actual working directory:
  `[TMPDIR]/historical-cohort-replication-002`;
- workspace-write sandboxing;
- no approval prompts within the noninteractive run.

An earlier disposable probe used the same memory-disabled/user-config-disabled
boundary in `[TMPDIR]/sol-blind-probe-20260722`. Without reading files, the
web, environment variables, repositories, or memory, it reported no
project-specific people, research topics, hypotheses, methods, or results.
Probe thread ID: `019f8d0d-e3e8-7f91-a047-9004179e4f2e`. The probe was
ephemeral and is not resumed for the real run.

## Permitted changes from the frozen launch mechanics

The Stage 1 message is copied from the frozen controller prompt with only:

1. the permitted working path changed from the direction-revealing project path
   to the neutral temporary path;
2. the fresh-context sentence made operationally exact: a separate runtime with
   memory disabled;
3. an audit-only instruction added requiring every logged timestamp to come
   from an actual UTC clock call rather than model generation.

No cohort definition, field, source rule, contamination rule, censoring date,
or analytic instruction is changed.

## Archival procedure

The experimenter works only in the neutral temporary directory. At a stage
gate, the controller:

1. stops or waits for the external turn to finish;
2. hashes the locked temporary-stage artifacts;
3. copies the complete run workspace into `run/sol_002/`;
4. verifies the copied hashes;
5. records the external thread ID, exact launch command, final response, token
   usage, and gate decision;
6. resumes the same external thread for the next frozen stage only if all stop
   conditions pass.

The context-rich controller never sends prior results, the article, hypotheses,
Fable materials, reference cohort files, or summaries of earlier runs.
