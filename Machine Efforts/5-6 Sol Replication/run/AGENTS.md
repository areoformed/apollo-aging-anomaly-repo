# Blind-Run Guardrails

These instructions apply to every agent working anywhere under this `run/` directory.

## Local read boundary

The assigned run directory is the only permitted local filesystem scope. For run `sol_001`, that is this directory’s child `sol_001/`.

Do not list, search, read, inspect, or copy from:

- the parent of `run/`;
- siblings of the assigned run directory;
- any other project/workspace directory;
- any memory, history, cache, hidden context, or prior-agent artifact outside the assigned run directory.

If any such material is surfaced accidentally, stop reading immediately and record the path and visible information in the current stage’s contamination log.

## Context and delegation

- Use only the exact current-stage task message and files previously created inside the assigned run directory.
- Do not ask for, infer, or search for future-stage instructions.
- Do not spawn subagents or delegate research.
- Do not communicate with any agent except the controller that assigned the run.

## Logging

Maintain an append-only `ACTION_LOG.md` inside the assigned run directory. Record timestamps for:

- every command;
- every web query;
- every URL opened or direct navigation;
- every file creation or edit;
- every substantive decision;
- every access failure and contamination encounter.

Never claim the inaccessible internal tool transcript is sufficient; the durable local log is required.

## Stage integrity

- Do not begin work not present in the current-stage message.
- Do not alter a completed prior stage.
- Stop at the required completion marker and wait.
- Do not compute, speculate about, or discuss group outcomes before the analysis stage explicitly authorizes them.

## Human Efforts

The Human Efforts directory is off-limits. Do not inspect or modify it under any circumstances unless the author explicitly gives a later, specific instruction—which would itself be a protocol deviation during this blind run.

