# Pre-Registration: Blind Independent Replication of Cohort Construction and Analysis

**Project:** Apollo-era astronaut survival and late-life cognitive outcomes
**Replication codename:** Fable Replication
**Frozen:** June 9, 2026
**Status:** Pre-execution. This document was frozen before the replication run and is withheld from publication until execution completes, so that the replication instance cannot encounter it through web search.

## 1. Background and purpose

The primary analysis examines mortality and late-life cognitive outcomes in astronauts who flew Apollo missions, against (a) a selection-matched astronaut comparison group and (b) era- and sex-matched general-population expectations. The project dataset (V2, n=98) has previously been constructed independently three times, and the analysis independently re-run approximately five times — including an adversarial referee review (June 4, 2026) that rejected an earlier longevity-anomaly framing as a healthy-selectee artifact and confirmed a cognitive-preservation signal under a joint endpoint.

What no prior replication has been is **blind**. Every earlier pass had access to the project's data, its framing, or both. This replication tests for construction bias — including any bias introduced by AI assistants embedded in the project — by having an isolated AI instance (Claude, model claude-fable-5, Anthropic; hence "Fable") rebuild the dataset and the analysis from scratch, with no knowledge of the project, the hypothesis, or the investigator.

## 2. Design

- **Clean environment.** A fresh instance with no project files, memory, or context. Web access enabled (required for vital-status research).
- **Staged disclosure.** Stage 1 (cohort construction; no analytic question disclosed) → output saved to disk → Stage 1b (blind cognitive-status and documentation-depth coding) → output saved → Stage 2 (analytic questions disclosed; the instance analyzes only its own dataset).
- **Fixed censoring date:** June 1, 2026, specified in the prompt so data-vintage differences cannot masquerade as disagreements.
- **Per-row provenance.** A cited source for every birth and death date; cognitive codings cited; intactness may not be inferred from the absence of impairment reports.
- **Contamination control.** The instance is prohibited from reading cohort or membership tables in existing astronaut-mortality studies and must log any encounter in a CONTAMINATION section.
- **Exact prompts** are frozen verbatim in `prompts.md` (same directory, same date). Any post-freeze change to the prompts is a protocol deviation (§7).

## 3. Number of runs

**One.** Rationale: dataset construction and analysis already have an internal replication series (three constructions, approximately five analyses). The marginal value of this run is blinding and pre-registration, not repetition; additional blind replicates were considered and judged redundant.

## 4. Predictions (recorded before execution)

- **P1 — Comparison-group scope.** The investigator predicts the instance **will include** military-program selectees (e.g., USAF MOL pilots) in its comparison group. Rationale, recorded in advance: the eligible sample is small, so the methodologically natural move is to broaden the comparator to those who met identical or closely similar physical and mental selection requirements.
- **P2 — Era boundary (open observation, not a prediction).** The prompts do not impose a pre-1970 boundary. Because NASA selected no new astronaut group between August 1969 and January 1978, and because post-1978 selection requirements differed materially from Apollo-era requirements, a careful constructor should re-derive an effectively pre-1970 comparison cohort on its own. Whether it does so is recorded as an open test of that boundary's naturalness.

## 5. Comparison protocol (two passes)

- **Pass 1 — scope reconciliation.** The instance's cohort definitions versus the project's, adjudicated against each side's *stated* criteria. Definitional divergence is treated as a finding about defensibility, not as error.
- **Pass 2 — row-level comparison within the shared scope.** Membership, dates, sources, and cognitive codings. All disagreements adjudicated at the source level.
- Then: decision-log comparison (which judgment calls were independently re-derived), and comparison of the instance's Stage 2 conclusions against the project's results.

## 6. Decision rules (pre-committed)

**6.1 Bias standard for V2 (strict, direction-blind).** Any material error in V2 surfaced by this replication counts against V2 and is corrected, regardless of whether the error favored or disfavored the hypothesis. (A directional-skew-only standard was considered and rejected as too permissive.)

**6.2 Process audit of the replication.** The replication's own quality is assessed against the following rigor checklist, fixed now to prevent post-hoc rigor judgments:

- **R1.** Decision rubrics are stated before data (DECISIONS precedes the CSV).
- **R2.** Every row carries cited sources for vital data.
- **R3.** No cognitive coding infers intactness from the absence of impairment reports.
- **R4.** Documentation depth is coded for all individuals.
- **R5.** Search effort is documented for LOW-documentation individuals (no silent ascertainment failure).
- **R6.** Spot-check: the investigator audits at least 10 randomly selected rows (or 10% of rows, whichever is greater) against primary sources; passing requires no unexplained material discrepancies.
- **R7.** The CONTAMINATION section is completed, including an explicit "no encounters" attestation where applicable.

**6.3 Null rule (pre-committed publication consequence).** If the instance's independent Stage 2 analysis finds no cognitive signal in its own data:

- If the run **passes** the rigor checklist → the piece is published with the blind null reported and discussed transparently alongside the primary analysis.
- If the run **fails** the checklist → the failure modes are documented, all disagreements are adjudicated at the source level before any publication decision, and the replication attempt is disclosed in the piece regardless of outcome.

In neither case is the replication silently discarded.

## 7. Deviations

Any deviation from this protocol after the freeze date is recorded in a DEVIATIONS appendix to this document, with date and reason. Deviations do not invalidate the run but must be disclosed wherever results are reported.

## 8. Provenance

Protocol designed by the investigator, with drafting assistance from Claude (claude-fable-5, Anthropic) acting on the experimenter side. The replication is executed by a separate, context-isolated instance of the same model. The two share weights but no context: the blinding is contextual, not architectural — which is precisely what makes this an experiment about context-induced bias rather than model identity.
