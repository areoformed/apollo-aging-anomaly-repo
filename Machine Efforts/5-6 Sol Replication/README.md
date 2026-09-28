# Sol Replication

**Status:** protocol frozen on 2026-07-22 at 19:59:27 PDT (-0700); live-run status is recorded in `ACTION_LOG.md`.

This folder is the complete experimenter-side record for a context-blind Sol replication of the Apollo aging-anomaly analysis. Its purpose is narrow:

> Determine whether the Apollo-flown cohort exhibits an observational anomaly in survival and/or publicly documented high-level functioning after age 80, relative to several same-era comparison cohorts.

This is not a test of a causal mechanism. Public activity is not a clinical cognitive examination, and absence of public evidence is not evidence of impairment.

## Why this design is stricter than the Fable run

The Fable protocol correctly used a fresh context, staged disclosure, per-row sourcing, and a null-publication rule. The Sol protocol retains those protections and adds:

1. A fixed primary late-life endpoint before person-level outcome research begins. Sol may not redefine the endpoint after seeing the evidence.
2. A codebook-only stage that is hashed before outcome searches begin.
3. Four nested comparator families rather than one agent-chosen comparator.
4. A fixed age-80 landmark, so dying before 80 is not silently counted as adverse late-life functioning.
5. A distinction between a documented public-functioning event and a clinical claim about cognition.
6. Uniform minimum search effort, exact query and opened-URL logs, and evidence collection in deterministic shuffled order.
7. Missingness bounds and documentation-depth sensitivities specified before analysis.
8. A locked blind conclusion before any comparison with the existing project datasets.
9. One primary Sol instance with no research subagents, preserving a single recoverable context and tool trail.

## Folder map

- `PREREGISTRATION.md` — estimands, endpoints, analysis rules, blinding, and success criteria.
- `PROMPTS_CONTROLLER_ONLY.md` — exact staged messages. Never give this whole file to Sol.
- `LAUNCH_RUNBOOK.md` — how to spawn, advance, hash, audit, and stop the run.
- `DESIGN_RATIONALE.md` — what was changed from Fable and why.
- `REFERENCE_COHORTS.md` — experimenter-only record of the existing comparator datasets; disclosed only after the blind conclusion is locked.
- `ACTION_LOG.md` — chronological record of every design action taken so far and a template for the live run.
- `DEVIATIONS.md` — append-only protocol-deviation register.
- `run/AGENTS.md` — local guardrails for the Sol instance.
- `run/sol_001/` — the only local directory the actual replication instance may inspect or modify.

## The clean-spawn answer

Use a child agent created with `fork_turns: "none"` and send it **only** the Stage 1 message from `PROMPTS_CONTROLLER_ONLY.md`. A disposable probe on 2026-07-21 showed that this produces a new context with no Apollo hypotheses, results, datasets, identities, methods, or prior conversation. The unavoidable information was only the project-directory label and the Human Efforts prohibition; Stage 1 itself necessarily names Apollo, so the directory label adds no analytic information.

This is strong **contextual blinding**, not an operating-system security boundary: child agents share the parent filesystem. The local `run/AGENTS.md`, the exact spawn task, and the controller’s audit enforce the no-parent-read rule. If adversarial filesystem isolation is required, execute the same frozen prompts in a new container or OS account with only a copy of `run/sol_001/` mounted.

## Freeze rule

The author authorized launch and the protocol was frozen on 2026-07-22 at
19:59:27 PDT (-0700). The immutable protocol files are covered by
`PROTOCOL_SHA256.txt`. After freeze:

1. launch exactly one primary run;
2. do not edit frozen protocol inputs;
3. record live controller actions in `ACTION_LOG.md`;
4. record any protocol change in `DEVIATIONS.md` rather than silently editing
   the frozen design.
