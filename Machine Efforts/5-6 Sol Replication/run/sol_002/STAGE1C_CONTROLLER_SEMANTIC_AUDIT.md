# sol_002 Stage 1C controller semantic audit

Audit time: 2026-07-23T05:49:40Z

## Purpose

The experimenter’s initial Stage 1C mechanical validation did not test whether
each positive source satisfied the locked substantive-content and dating rules.
Before cohort flags were revealed, the controller compared every initial event
row with its locally retained opened-page text. The first derived version was
preserved at `stage1c_pre_semantic_repair/`; no initial raw search record was
altered.

The experimenter then received the exact no-browsing message in
`../../controller/sol_002/STAGE1C_SEMANTIC_GATE_REPAIR.txt`. It re-audited all
event rows and analogous candidates under the existing codebook, without a web
call, cohort flag, group count, group rate, or comparison question.

## Retained qualifying records

- `R001`: the stored Space.com report states that the person was piloting the
  aircraft when it crashed and that his son confirmed he was the pilot. This
  supports family 5 on the date of death, after age 85. It is a secondary
  age-80-plus event, not a primary five-year event. Its nonuniform merged
  base-result stream remains a declared data-quality limitation.
- `R058`: the stored ABC report attributes to adult children a guardianship
  petition alleging persistent cognitive decline with memory loss, confusion,
  delusions, paranoia, and unusual behavior. That meets the codebook’s
  credible-attributable-report path for major impairment, although it was
  disputed and is retained at medium confidence. The same dated article also
  contains multiple direct, substantive answers from the person. The bounded
  May 2018 impairment report precedes the June 26, 2018 function interview;
  both occur after age 85.
- `R060`: the NASA page contains multiple substantive answers and describes
  them as a recent interview. With no indication that the interview was
  materially earlier, the frozen edited-interview publication-date proxy
  applies. This is a primary five-year function event.
- `R064`: the dated CBS report contains direct substantive statements plus
  documented civic action: a proposed land donation and a letter to a senator.
  This is a secondary age-80-plus function event.
- `R078`: the opened Publishers Weekly record identifies a new original memoir
  by the person with a named collaborator, describes the person’s substantive
  contribution throughout the work, and dates the issue to September 2012.
  The frozen month-midpoint rule applies. This is a primary five-year event.

## Uniform exclusions

The repaired artifacts exclude every initial positive whose locally stored
source did not itself establish the frozen requirements. The exclusions cover:

- an episode date applied to an interview explicitly described as recorded
  about two years earlier;
- a book publication year that did not establish when an embedded interview
  occurred;
- future-tense event announcements;
- a schedule, photograph, or caption saying someone spoke without evidence of
  substantive content;
- a crash report that did not explicitly establish who operated the aircraft;
- derived notes whose locally retained source excerpt did not preserve enough
  responsive content to verify the candidate.

These are applications of rules already written in Stage 1B, not a new
endpoint or post-result threshold.

## Controller judgment

The repaired six-row event ledger is semantically consistent with the frozen
codebook on the locally retained evidence. It contains five function rows and
one impairment row. Two people have a primary age-[80,85) function event.
These are ungrouped integrity counts only. No cohort-level outcome result was
computed during this audit.
