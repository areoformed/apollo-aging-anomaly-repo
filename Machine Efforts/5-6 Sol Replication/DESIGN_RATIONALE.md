# Design Rationale

## Bottom line

There is a real, answerable observational question here, but the public record supports a claim about **documented late-life functioning**, not a clinical diagnosis of preserved cognition. The Sol design asks whether that documented pattern is unusual while making visibility, survival selection, and comparator choice explicit.

## What the Fable design got right

- Fresh context and staged disclosure.
- Cohort decisions before data.
- Per-row provenance.
- An explicit contamination register.
- A rule that null results are still reported.
- Acknowledgment that comparison-group definitions can legitimately differ.

These features are retained.

## What changes for Sol

### 1. Fix the endpoint before outcome research

Fable’s Stage 2 allowed the agent to “define an endpoint you consider fair” after its evidence table existed. That makes endpoint drift possible and makes a discrepancy hard to interpret: did the evidence differ, or did the question change?

Sol receives a fixed age-80 public-functioning endpoint. It may resolve edge cases in a codebook-only stage, but the primary event definition and risk set are not negotiable after evidence collection.

### 2. Stop calling public activity clinical cognition

An interview, book, lecture, flight, or advisory role is affirmative evidence of functioning at a time. It is not a neurological exam, and public silence is not impairment. The design therefore retains dated events and uses the term `public-evidence detection rate`.

Any future NASA clinical-data analysis is a separate study. It should not be smuggled into a biographical proxy or used to retroactively validate one.

### 3. Use age 80 as a landmark and equalize opportunity

People who die before 80 never enter the late-life-function risk set. Counting them as negative confounds survival with functioning. A crude “any event after 80” measure also gives older and longer-lived people more opportunity to become positive. The primary Sol estimand therefore uses the first five years after age 80, time to first detected function event, administrative censoring, and death as a competing event. The all-ages-80+ binary remains secondary.

### 4. Analyze several comparator families

A single comparator invites argument over scope. The project already has defensible nested frames: core NASA non-Apollo, military-only, their union, and an availability sensitivity excluding early accidental deaths. Sol constructs the program families independently and reports all of them.

The early-accident exclusion is not treated as automatically correct; it can remove precisely the events that distinguish a future-defined Apollo-flyer group from contemporaries. It is therefore a labeled sensitivity.

### 5. Do not use backup crews as controls

Backup crews received near-complete mission training and commonly rotated into later prime assignments, with exceptions for suitability, cancellation, and program contingencies. They are neither untreated nor cleanly separated. Their roles may be recorded, but no causal control contrast is built around them.

### 6. Preserve and equalize the search process

Fable’s final audit honestly noted that its 17-subagent execution could not recover every keystroke-level query and every opened-but-uncited page. Sol uses one primary agent, six fixed query families, ranked-result logs, a fixed page-opening/stopping budget, exact query and URL logs, and deterministic shuffled research order. Extra searching is capped and allowed only for predeclared resolution triggers.

### 7. Lock the blind answer before reconciliation

Sol must first answer from the cohort and evidence it independently constructed. Only then does it see the existing materialized cohort files. This distinguishes independent replication from debugging or harmonization.

## What “fresh baby” means operationally

It means no inherited conversation turns (`fork_turns: none`), no project memory, no draft, no prior numbers, no causal story, and no future-stage prompts. It does not mean blank model pretraining or a cryptographically inaccessible parent filesystem.

The disposable probe confirmed that the context-fork mechanism is clean at the substantive level. The remaining blindness rests on staged prompt delivery and a recorded no-parent-read rule. For stronger adversarial isolation, use the same protocol in a clean container with only the run directory mounted.

## Interpretation discipline

The practical-materiality anchors were not chosen by the context-rich controller. Before freeze, a disposable `fork_turns: none` methodologist received only the generic estimands and approximate group sizes, no study result or predicted direction. It selected 5 RMST years over the 50-year survival horizon and a 10-percentage-point five-year public-detection risk difference. These are interpretation anchors, not power targets, clinical cutoffs, or substitutes for intervals.

The strongest result available from this design would be:

> Apollo flyers have an unusually high rate of publicly documented substantive functioning after age 80 across several same-era selected comparison frames, and the pattern survives prespecified documentation and missingness sensitivities.

That still would not show that Apollo caused the pattern, that the selection/training process caused it, or that every individual was clinically cognitively intact. Those are distinct questions requiring distinct data.
