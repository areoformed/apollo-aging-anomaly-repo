# sol_002 Stage 1 controller gate

Gate time: 2026-07-23T04:18:25Z

The append-only root `ACTION_LOG.md` must continue changing in later stages.
Its exact Stage 1 gate state is therefore preserved immutably as
`snapshots/ACTION_LOG_STAGE1.md` and that snapshot, rather than the mutable
working log, is listed in `STAGE1_SHA256.txt`.

## Isolation

- External analytic thread: `019f8d11-b42b-71f1-97a7-da53c0f8656d`.
- Runtime flags disabled memories and ignored user configuration.
- The actual working path was the neutral
  `[TMPDIR]/historical-cohort-replication-002`.
- `CONTEXT_ATTESTATION.md` was written at 2026-07-23T03:43:08Z, before web
  research, and reports no pre-message project facts, hypotheses, results,
  person-level data, or prior methods.
- No controller message was delivered during Stage 1.
- The experimenter reported no prohibited source encounter or parent/local-path
  read.

## Mechanical validation

The child validator and the independent controller validator both passed.
Controller validator SHA-256:

`46d9f85332b80b54449affe86da24cade27859cb9bdafa3588f95e068a2f93ac`

Checked:

- exact 23-column cohort schema and 10-column source-log schema;
- 95 unique person IDs and case-folded names;
- 489 source-ledger rows;
- ISO dates, chronology, censoring, status/death-field consistency;
- Boolean fields and the exact `other_all` union;
- Apollo flag/mission consistency;
- no Apollo/core-NASA-comparator overlap;
- membership, birth, death, and living-status source coverage;
- every cohort source URL represented by a fetched source-ledger row;
- 19 of 19 living people represented by a targeted 2024–2026-06-01
  death/obituary check;
- RFC 4180 CRLF records;
- 202 durable action-log timestamps in nondecreasing real-clock order;
- no source or action timestamp after the lock ceiling;
- expected file inventory only in the external workspace.

`result_rank=direct` is treated as a valid nonnumeric value for direct
navigation. `SOURCE_LOG.csv` is grouped by person/fact, so its rows are not
chronologically sorted; exact times are valid and chronology is carried by the
append-only `ACTION_LOG.md`.

## Locked counts

- 95 people total;
- 29 Apollo 7–17 flyers;
- 44 core NASA non-Apollo members;
- 12 X-15 pilots;
- 6 Dyna-Soar selected-to-fly pilots;
- 17 MOL selectees;
- 66 in the deduplicated non-Apollo union;
- 19 alive and 76 deceased at 2026-06-01.

These are construction/integrity counts only. No group-outcome contrast was
performed.

## Runtime usage

The Stage 1 turn reported:

- input tokens: 14,821,247;
- cached input tokens: 14,425,088;
- output tokens: 65,553;
- reasoning output tokens: 24,429.

Because Stage 1 required many public-web calls and the noninteractive runtime
replayed a growing context, the gross input count is large but mostly cached.
This usage is recorded before deciding on later evidence-collection stages.

## Gate decision

Pass. The identified `sol_001` stop conditions did not recur. Stage 1 is locked
at the hashes in `STAGE1_SHA256.txt`; neither the archived copy nor the neutral
working copy may be altered.
