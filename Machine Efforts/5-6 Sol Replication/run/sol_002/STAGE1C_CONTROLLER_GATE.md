# sol_002 Stage 1C controller gate

Gate time: 2026-07-23T05:57:04Z

## Result

Pass after a direction-blind semantic repair, with declared audit
qualifications `DEV-20260722-05` through `DEV-20260722-07`.

Stage 1C is now locked. Cohort flags and all group comparisons remained hidden
from the experimenter throughout collection, initial adjudication, controller
review, and repair.

## Preserved versions

The complete initial version is preserved at
`stage1c_pre_semantic_repair/`. It structurally passed but did not pass the
controller's source-by-source semantic audit. The controller therefore sent
only the no-browsing, group-blind consistency instruction in
`controller/sol_002/STAGE1C_SEMANTIC_GATE_REPAIR.txt`.

The same memory-disabled Sol thread re-audited every positive and analogous
candidate using only the already stored evidence and the frozen Stage 1B
codebook. It did not browse, receive cohort flags, or receive any group count,
rate, direction, or prior result.

## Final validation

The final locked files contain:

- 95 unique worklist and outcome records;
- 57 age-80-eligible people;
- six fixed base-query families for every eligible person;
- 342 fixed base-query families in total;
- 57 preserved raw JSON audit records;
- 2,887 search-log rows;
- six qualifying evidence rows;
- five people with at least one full-window qualifying function event;
- two people with a primary-window qualifying function event;
- one qualifying impairment row, followed for the same person by a directly
  documented function interview.

These are ungrouped audit totals, not a cohort comparison.

The independent controller validator passed exact schemas, row/linkage rules,
raw-result ranks and URLs, page-access records, derived-state consistency,
query/page caps, prior-stage immutability, and the declared single timestamp
inversion. All files listed in `STAGE1C_SHA256.txt` reverified byte-for-byte.

## Audit qualifications

- `DEV-20260722-05`: one person's first batched search call produced merged
  base-result streams. Stage 2 must include a direction-neutral sensitivity
  excluding that record from public-function comparisons.
- `DEV-20260722-06`: the initial adjudication inconsistently admitted evidence
  types or date proxies excluded by the codebook. The complete initial version
  is preserved; the final version is the uniform no-browsing repair.
- `DEV-20260722-07`: one pair of adjacent action-log entries has a one-second
  inversion. It is preserved verbatim and does not bracket a material
  adjudication.

## Hashes

- frozen Stage 1C launch message:
  `3334a02a864dc414d806cda22eb5c4b198308115002bb596fcc24617804b211b`
- semantic-repair message:
  `dd306e1021a95fc9ef1d6452694a45391575ec1054b69c6e3d4d8396281bf5c1`
- controller semantic audit:
  `5ccb64cb79b2da98d9b34aeb8a2fa8fa4e5753596e6e48a2f2ad01fd82e6bd5b`
- independent controller validator:
  `c1fe10c002430ee7fb0306163d9e09ec40f4f03b27fae73693d2985b96d9d67a`
- repaired child final response:
  `fc576b5dbddb0306e818f25973af7206f9634b0d59c414a7cb380caf1690c3be`
- final Stage 1C manifest:
  `150c1b5e02e6769a63ccdfee2446c8f4159765e8fc34791e661a61a27242a8eb`

## Runtime usage

The session's cumulative usage after repair was 59,551,895 input tokens,
58,309,888 cached input tokens, 204,171 output tokens, and 69,716 reasoning
output tokens. The repair turn added 9,893,541 input, 9,742,592 cached input,
30,918 output, and 11,410 reasoning output tokens.

## Decision

Stage 1C passes and is locked. Stage 2 may reveal cohort labels and run only
the prespecified comparisons, after recording the R001 exclusion sensitivity
without knowing its group membership or the direction of any comparison.
