# Preregistration: Context-Blind Sol Replication

**Protocol version:** 1.0 frozen  
**Drafted:** 2026-07-21  
**Frozen:** 2026-07-22 19:59:27 PDT (-0700)  
**Censoring date:** 2026-06-01  
**Planned primary runs:** one  
**Status:** frozen; execution authorized

## 1. Research question

Does the cohort of American astronauts who flew Apollo 7–17 exhibit an observational anomaly in either of two separate domains?

1. **Survival:** all-cause survival or attained age relative to same-era, highly selected comparison cohorts and appropriate U.S. male birth-cohort expectations.
2. **Publicly documented late-life functioning:** affirmative, dated evidence of substantive high-level activity at or after age 80, relative to the same comparison cohorts.

The study does **not** ask why any difference exists and does not test a training, lunar-exposure, selection, personality, occupational, or other causal mechanism. Group labels describe historical cohorts, not randomized treatments.

## 2. Epistemic status

This is a prospectively frozen, context-blind reanalysis, not independent hypothesis generation. The experimenter has seen prior project results, a prior Fable replication, and existing comparator datasets. Sol will see none of those before locking its blind conclusion.

The public-functioning outcome is an ascertainment-sensitive biographical endpoint. It can establish that qualifying behavior was publicly documented; it cannot establish clinical cognitive normality. `NEITHER_FOUND` means no qualifying event was detected under the fixed search process, not impairment.

## 3. Blinding

### 3.1 What Sol may know at each stage

- **Stage 1:** cohort-construction task, roster concepts, vital-status fields, fixed censoring date, and source rules. The requested birth/death fields make a possible survival use visible, but Sol receives no hypothesis, predicted direction, planned contrast, prior result, post, existing table, or late-life-function endpoint.
- **Stage 1B:** the fixed codebook and age-80 outcome definition. No predicted direction or prior result. Sol writes the operational codebook without browsing.
- **Stage 1C:** the locked codebook and Sol’s own Stage 1 cohort. No prior project data or results.
- **Stage 2:** the two analytic questions and prespecified analysis plan. Sol uses only its own locked data.
- **Stage 3:** only after the Stage 2 conclusion is hashed, the experimenter may disclose existing project cohort files for reconciliation. Stage 3 cannot alter the blind conclusion.

### 3.2 Context isolation

The primary instance is spawned with `fork_turns: "none"`. It receives only the current stage’s exact message. It may work only in `run/sol_001/`, may not inspect parent or sibling directories, and may not use agent memory or prior local project materials. Web research is allowed and required.

A disposable, non-analytic probe performed before protocol drafting found no substantive context leakage: the clean child knew only the project-directory label and the Human Efforts guardrail. It knew no hypotheses, results, cohorts, people, methods, or prior analyses. The probe was terminated as an experimental candidate and will not perform the real run.

### 3.3 Contamination

During Stage 1, Sol must not open any source whose purpose is statistical or comparative analysis of people in the named cohorts/programs; primary rosters, program histories, biographies, mission pages, and ordinary obituaries remain permitted. From Stage 1B onward, this explicitly includes existing group-level work about survival, aging, late-life vitality, or cognitive outcomes. If a search result exposes a prohibited item, Sol records the title, URL, stage, and what was visible without opening it, then continues from permitted primary/biographical sources.

Model pretraining cannot be removed and is outside the operational contamination definition. Any explicit recollection of a published/project result must nevertheless be logged.

### 3.4 Filesystem limitation

The child process shares the parent filesystem, so the restriction is a documented contextual boundary rather than cryptographic isolation. Any parent/sibling read is a major deviation. A hard-isolation replication may later repeat the frozen protocol in a clean container, but it is not silently substituted for this one-run design.

## 4. Run count and agent topology

There will be one primary Sol run. The same context persists across Stages 1, 1B, 1C, and 2. Sol may not spawn subagents. This preserves a single inspectable tool and decision trail and avoids the lost-query-log problem in the Fable run.

If the primary context is lost, replaced, or compacted so severely that Sol cannot attest continuity, the controller stops. Restarting with another instance is a disclosed deviation and a new run identifier, not a continuation.

## 5. Cohort construction

Sol constructs the historical frame from primary roster and program sources, not from an existing mortality study or project dataset.

### 5.1 Target cohort

- `APOLLO_FLEW`: every person who launched on Apollo 7 through Apollo 17.
- Apollo 1 is separately flagged and is never silently counted as an Apollo flyer.

### 5.2 Prespecified nested comparator families

Sol constructs and retains disjoint source-program flags so these can be analyzed separately and together:

1. `CORE_NASA_NON_APOLLO`: same-era NASA astronaut corps members who did not fly Apollo 7–17.
2. `MILITARY_X15`: U.S. X-15/high-speed research pilots meeting the documented inclusion rule.
3. `MILITARY_DYNA_SOAR`: selected X-20 Dyna-Soar pilots.
4. `MILITARY_MOL`: selected USAF Manned Orbiting Laboratory astronauts, with overlap deduplicated.
5. `MILITARY_ONLY`: anyone with at least one of the three military-program flags **and not `APOLLO_FLEW`**. Program-history flags may overlap Apollo; the comparison indicator may not.
6. `OTHER_ALL`: union of the non-Apollo core-NASA and `MILITARY_ONLY` families.
7. `OTHER_AVAILABLE`: `OTHER_ALL` excluding prespecified pre-1970 accidental deaths, reported only for secondary birth-origin survival description—not as an intrinsically superior control. It is mathematically redundant after the 1973 survival landmark and inside the age-80 risk set.

Sol must state and source exact inclusion rules before collecting individual vital outcomes. Definitional disagreements with the existing project frame are preserved as findings and reconciled only after Stage 2.

Backup-crew status may be recorded as a role, but backup crews must not be treated as an untreated control group. Crew rotation, cross-over into later prime crews, suitability exclusions, and cancellations preclude that interpretation.

### 5.3 Required person-level fields

Stage 1 produces one row per person with at least:

`person_id,full_name,search_disambiguator,birth_date,death_date,vital_status_20260601,first_selection_date,first_spaceflight_date,apollo_flew,apollo_missions,apollo1_crew,core_nasa_non_apollo,military_x15,military_dyna_soar,military_mol,other_all,pre1970_accidental_death,backup_crew_roles,membership_source_urls,birth_source_url,death_source_url,confidence,notes`

Dates use ISO `YYYY-MM-DD`; Boolean fields use `0`/`1`. `search_disambiguator` is a direction-neutral role/program phrase fixed during cohort construction, such as `NASA astronaut` or `X-15 test pilot`, for later same-name control. Every inclusion and vital fact has per-row provenance. Living status requires a targeted 2024–2026 obituary/death search.

## 6. Outcome codebook

### 6.1 Eligibility, observation time, and time window

The fixed late-life landmark is the 80th birthday. A person is eligible if they reached age 80 on or before death/censoring.

The **evidence-collection window** runs from the 80th birthday through death or 2026-06-01. Inside it, the **primary analytic window** is the first five years after the 80th birthday: age `[80, 85)`. Primary follow-up ends at the earliest of the first qualifying function event, death, the 85th birthday, or 2026-06-01. Death before a detected event is a competing event; administrative end before age 85 is right censoring. Sol records potential and observed follow-up days for every eligible person while still collecting later evidence for secondary descriptions.

“Any qualifying event at any age 80+ through death/censoring” is a mandatory secondary description, not the primary fixed-window estimand.

A death before age 80 is `NOT_ELIGIBLE_UNDER_80`, not evidence against late-life functioning.

### 6.2 Primary public-functioning event

A `QUALIFYING_FUNCTION_EVENT` is a dated, attributable event within the evidence-collection window that affirmatively demonstrates substantive self-directed activity. Events inside the first five years contribute to the primary endpoint; later events contribute only to secondary descriptions. Qualifying families are:

- a substantive interview or unscripted Q&A containing the person’s own responsive answers;
- an original authored or co-authored substantive work with evidence of contemporaneous participation;
- a lecture, technical presentation, teaching session, or public discussion with substantive participation;
- active professional, advisory, organizational, civic, artistic, or technical responsibility;
- verified active piloting, operation of complex equipment, fieldwork, or similarly demanding activity.

The following do not qualify alone: mere attendance, a photograph, an award listing, a birthday notice, a quotation of unknown date, generic praise, a signature, a reissued old work, or absence of reported impairment.

This is evidence of documented functioning during an event, not a diagnosis of intact cognition.

### 6.3 Impairment evidence

`QUALIFYING_IMPAIRMENT_EVIDENCE` requires a published clinical diagnosis or a credible, attributable report of persistent major cognitive impairment within the evidence-collection window. Frailty, physical disability, stroke without cognitive detail, seclusion, or lack of interviews does not qualify.

Function and impairment events are time-varying and may coexist. Sol records both rather than forcing a lifetime binary.

### 6.4 Person-level outcome states

The full age-80-through-end-of-observation state is exactly one of:

- `FUNCTION_ONLY`
- `IMPAIRMENT_ONLY`
- `FUNCTION_THEN_IMPAIRMENT`
- `IMPAIRMENT_THEN_FUNCTION`
- `BOTH_ORDER_INDETERMINATE_OR_SAME_DATE`
- `NEITHER_FOUND`
- `NOT_ELIGIBLE_UNDER_80`

These states describe detected evidence, not latent health. The primary endpoint is the five-year cumulative incidence of a first `QUALIFYING_FUNCTION_EVENT` after age 80 with death as a competing event. The secondary crude endpoint is whether any such event was detected at any age 80+ through death/censoring. First/latest event age and the full temporal sequence are mandatory descriptors.

Event-date precision is retained (`DAY`, `MONTH`, `YEAR`, or bounded interval). Stage 1B must freeze a direction-neutral analysis-date rule for partial dates before browsing; boundary-sensitive events are separately flagged and rerun at the earliest/latest plausible dates.

### 6.5 Search effort and documentation

Every eligible person receives the same six query families and fixed result-opening budget specified in the Stage 1C prompt. Sol logs every returned result rank, query, opened URL, access failure, source tier, evidence date, and adjudication. Searching does not stop when an event is found. Additional searches are allowed only for predeclared access, identity, date, conflict, or cited-primary-source resolution triggers and are capped.

Documentation depth is based on observable counts rather than fame or group membership:

- `LOW`: 0–1 substantive late-life sources opened.
- `MEDIUM`: 2–4 substantive late-life sources opened.
- `HIGH`: at least 5 substantive late-life sources across at least 2 independent publishers.

The raw counts remain primary; the labels are summaries of public source availability and may themselves depend on whether substantive evidence exists. They are reported descriptively and are not treated as a bias correction. The protocol does not call a MEDIUM/HIGH restriction a “complete-case” estimate.

## 7. Prespecified analysis

All results are descriptive associations among selected historical cohorts. No contrast estimates the causal effect of flying Apollo.

### 7.1 Survival axis

For Apollo and each comparator family, Sol reports deaths, censored observations, ages at death/current age, medians where estimable, and exact uncertainty.

Required analyses:

1. **Primary:** survival from a common 1973-01-01 landmark among people alive on that date; effect measure is Apollo-minus-`OTHER_ALL` restricted mean survival time through 50 years after the landmark. The 95% interval is a stratified nonparametric percentile bootstrap resampling people within the two groups, 50,000 replicates, seed `20260721`, with the 2.5th and 97.5th percentiles.
2. Age at the 1973 landmark and an age-adjusted sensitivity: Cox proportional-hazards model from the landmark with group plus age-at-landmark in years as a prespecified linear covariate, Efron ties, conventional two-sided 95% interval, and a Schoenfeld-residual proportional-hazards diagnostic. This sensitivity does not replace the RMST primary.
3. Kaplan–Meier survival from birth as secondary cohort description, explicitly labeled retrospective and future-flight-selected.
4. Apollo versus `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY` (military flags restricted to non-Apollo) as composition sensitivities, not independent replications.
5. `OTHER_AVAILABLE` only in the secondary birth-origin description; verify and report that it is identical to `OTHER_ALL` after the 1973 landmark.
6. Era- and sex-matched U.S. population expectations using a cited official life table, with healthy-selectee limitations explicit.

Effect sizes and 95% confidence intervals are required. P-values, if used, are supplementary. The prespecified practically material survival threshold is an absolute RMST difference of 5.0 years over the 50-year landmark horizon. Apollo membership is defined by future flight, so selection implications remain and must be discussed; the landmark removes pre-1973 survival opportunity from the contrast but is not a cure for all selection bias.

### 7.2 Public-functioning axis

The risk set is people who reached age 80 by death/censoring. Sol reports observation time, events, competing deaths, censoring, crude detection counts, and raw evidence tables for every group.

Required contrasts:

1. **Primary:** Apollo versus `OTHER_ALL` difference in five-year cumulative incidence of first qualifying function detection after age 80, using Aalen–Johansen with death as a competing event. The primary effect is Apollo-minus-`OTHER_ALL` absolute risk difference at five years. Its 95% interval is a stratified nonparametric percentile bootstrap resampling people within the two groups, 50,000 replicates, seed `20260721`, with the 2.5th and 97.5th percentiles.
2. Composition sensitivities: Apollo versus `CORE_NASA_NON_APOLLO` and `MILITARY_ONLY`; these nested contrasts are not independent confirmations. Verify that `OTHER_AVAILABLE` and `OTHER_ALL` have the same age-80 risk set and report the identity rather than pretending it is another sensitivity.
3. Secondary crude any-time detection: exact numerator/denominator, binomial intervals, risk difference, risk ratio, odds ratio, Fisher exact test, and compatible intervals.
4. Source-availability-stratified descriptions using raw source counts and the prespecified depth categories. These are not adjustment or complete-case correction.
5. Observation-time summaries, latest qualifying-event-age distributions, and exhaustive temporal-state counts.
6. A separately labeled latent-event sensitivity may assign `NEITHER_FOUND` cases in worst/best directions. It answers “what if undetected function occurred?” rather than the observed public-detection question and cannot change the primary detection estimate.

The prespecified practically material public-function threshold is an absolute five-year cumulative-incidence risk difference of 10 percentage points. The primary rate is called a **public-evidence detection rate**, not a prevalence of cognitive intactness.

### 7.3 Anomaly language

Survival and public functioning each receive a **strength** and **direction**:

- Strength `ROBUST`: the absolute primary effect meets its prespecified practical threshold, its primary 95% interval excludes the null, and no prespecified composition sensitivity reverses direction. Nested comparator sensitivities are not counted as independent replications.
- Strength `SUGGESTIVE`: the absolute primary effect is practically material and directionally coherent, but interval width or ascertainment prevents the robust classification.
- Strength `NOT_DETECTED`: small, directionally unstable, or materially explained by the prespecified sensitivities.
- Strength `INDETERMINATE`: data/provenance failures prevent a responsible classification.
- Direction `HIGHER`, `LOWER`, or `UNCERTAIN`, stated from the Apollo-minus-comparator sign. A large precise negative anomaly is classified symmetrically rather than forced into `NOT_DETECTED`.

Classification uses the RMST difference for survival and the five-year cumulative-incidence risk difference for public functioning. The practical thresholds are fixed above before launch and copied into the Stage 1B codebook; Sol may not revise them. Statistical significance alone is neither necessary nor sufficient for `SUGGESTIVE`.

## 8. Validation and audit gates

The controller does not advance a stage until all required artifacts exist and are hashed.

- Cohort membership totals reconcile to named roster sources.
- No duplicate people; all overlap flags are explicit.
- Dates, status, and age calculations validate mechanically.
- Decision documents precede their corresponding data collection.
- Every eligible person meets the fixed search/result-opening budget or carries an explicit failure; rank logs and stop rules validate mechanically.
- Every positive event has a dated source and quoted/paraphrased supporting content.
- No absence-to-intactness inference.
- Contamination attestation exists at every stage.
- All scripts and software versions are retained.
- Stage 2 conclusion is hashed before Stage 3 reconciliation.

Failure of a gate is documented. A repair before the next stage is allowed only with an append-only explanation; changing an analytic decision after examining group results is a protocol deviation.

## 9. Reconciliation with existing project cohorts

After the blind Stage 2 conclusion is locked, the controller compares Sol’s cohort and results against the seven existing materialized datasets listed in `REFERENCE_COHORTS.md`.

Reconciliation has three passes:

1. Definition-level: compare stated inclusion rules without declaring either side correct by fiat.
2. Row-level within shared scope: membership, dates, flags, sources, and outcome evidence.
3. Result-level: reproduce the frozen analyses on harmonized shared-scope data while preserving both original conclusions.

No Stage 3 discovery can rewrite the blind Stage 2 report. Corrections appear in a separate reconciliation report.

## 10. Publication rule

The Sol result is disclosed whether it is robust, suggestive, null, indeterminate, contaminated, or operationally failed. A null or contradiction is not a failed experiment. Operational failure is described rather than silently replaced.

## 11. Deviations

Any post-freeze change is appended to `DEVIATIONS.md` with timestamp, stage, reason, affected artifacts, whether group-level results had been seen, and expected directional effect if known.
