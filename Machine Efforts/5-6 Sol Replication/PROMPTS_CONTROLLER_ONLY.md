# Sol Replication — Controller-Only Frozen Prompts

**Status:** FROZEN 2026-07-22 19:59:27 PDT (-0700); deliver sequentially without paraphrase.  
**Rule:** deliver only one prompt section at a time. Never place this file inside `run/sol_001/`, never tell Sol future prompt contents, and never paraphrase the prompts during a live run.

The absolute run path used below is:

`./Machine Efforts/5-6 Sol Replication/run/sol_001`

## SPAWN / STAGE 1 — cohort construction only

```text
You are the primary researcher for a staged historical-cohort replication. You have been created with a fresh context. Work independently and do not speculate about the eventual analytic question.

LOCAL ISOLATION — HARD PROCEDURAL RULE:
- Your only permitted local working directory is:
  ./Machine Efforts/5-6 Sol Replication/run/sol_001
- Do not list, search, read, or inspect any parent directory, sibling directory, pre-existing project file, memory store, or other local path.
- You may use the public web and files you yourself create inside the permitted directory.
- Do not spawn subagents.
- Before web research, write CONTEXT_ATTESTATION.md listing every project-specific fact, hypothesis, result, person-level datum, or prior method that was present in your context before this message. If none was present, say so explicitly. Also record the model/runtime identity available to you and the time.
- Maintain ACTION_LOG.md as you work. Log every local command, every web query, every URL opened, every file created or changed, and every material decision. Use timestamps. Do not rely on an inaccessible internal tool trail.

CONTAMINATION RULE:
Do not open or read any source whose purpose is statistical or comparative analysis of people in the named cohorts or programs. If a result page reveals such an item, record its title, URL, visible snippet information, and time in stage1/CONTAMINATION.md without opening it, then continue from primary program and biographical sources. Primary rosters, program histories, biographies, mission pages, and ordinary obituaries are permitted.

TASK:
Construct a source-auditable cohort dataset, censored on 2026-06-01, covering:

A. every person who launched on Apollo 7 through Apollo 17;
B. same-era NASA astronaut-corps members who did not launch on Apollo 7–17;
C. the same-era American military/civilian astronaut-like flight-research programs X-15, X-20 Dyna-Soar, and USAF Manned Orbiting Laboratory.

Before collecting person-level birth or death data, write stage1/DECISIONS.md. Define from primary roster/program sources:
- what counts as an Apollo flight;
- treatment of Apollo 1, Skylab, Apollo-Soyuz, and people who never flew;
- exact NASA selection-group boundary;
- exact inclusion rules for X-15, Dyna-Soar, and MOL;
- overlap/deduplication rules;
- backup-crew representation. Do not treat backup crews as an untreated control; record rotations and later prime-crew crossover where relevant;
- accidental-death flagging;
- source hierarchy and confidence rules.

Then construct stage1/cohort.csv with exactly these columns:
person_id,full_name,search_disambiguator,birth_date,death_date,vital_status_20260601,first_selection_date,first_spaceflight_date,apollo_flew,apollo_missions,apollo1_crew,core_nasa_non_apollo,military_x15,military_dyna_soar,military_mol,other_all,pre1970_accidental_death,backup_crew_roles,membership_source_urls,birth_source_url,death_source_url,confidence,notes

Rules:
- dates are YYYY-MM-DD; death_date is empty if alive at the censoring date;
- Boolean fields are 0/1;
- search_disambiguator is a direction-neutral role/program phrase fixed now for later same-name control, such as NASA astronaut or X-15 test pilot;
- military program-history flags may overlap Apollo, but the later MILITARY_ONLY comparator is the union of those flags restricted to apollo_flew=0;
- other_all is the union of all non-Apollo comparison families after deduplication and must never include apollo_flew=1;
- encode the file as valid RFC 4180 CSV; use pipe-separated values inside multi-value fields and quote any field containing a comma, quote, or newline;
- every membership, birth, and death fact has a fetched source URL;
- prefer NASA/USAF/official program material and official or major-outlet obituaries;
- for every apparently living person, run and log a targeted death/obituary search covering 2024 through the censoring date;
- primary rosters must determine inclusion top-down. Never copy membership from a mortality/aging study;
- uncertain inclusions remain visible and flagged rather than silently omitted.

Also write:
- stage1/SOURCE_LOG.csv with timestamp,person_id,query_or_direct_navigation,result_rank,url,opened,access_result,fact_supported,source_tier,notes;
- stage1/VALIDATION.md with cohort counts, overlap checks, duplicate checks, date/status checks, and unresolved issues;
- stage1/CONTAMINATION.md even if there were no encounters;
- stage1/STAGE_COMPLETE.md listing every output and a plain statement that no group-level outcome contrast or analysis was performed.

Do not perform or discuss any group-outcome analysis. Stop after Stage 1 and reply only: STAGE1_COMPLETE, followed by the paths of the six required artifacts and any blocking failure.
```

## STAGE 1B — codebook lock; no browsing

Send only after Stage 1 artifacts have passed validation and been hashed.

```text
Stage 1 is locked. Do not alter any Stage 1 file. Do not browse the web during this stage and do not inspect group counts or person-level outcomes while making codebook decisions.

Your task is to operationalize a fixed public-evidence endpoint before outcome collection. This endpoint is not a clinical cognitive diagnosis.

Eligibility: a person reached age 80 by death or the fixed censoring date 2026-06-01.

The evidence-collection window runs from the 80th birthday through death or 2026-06-01. Inside it, the primary analytic window is the first five years after age 80: age [80,85). Primary follow-up ends at the earliest of first qualifying function event, death, 85th birthday, or 2026-06-01. Death before detected function is a competing event; administrative end before age 85 is right censoring. Continue collecting later evidence for the secondary “any event at any age 80+” description.

A QUALIFYING_FUNCTION_EVENT is dated, attributable evidence in the evidence-collection window of substantive self-directed activity in at least one family. Events within five years of age 80 contribute to the primary endpoint; later events contribute only to secondary descriptions:
1. a substantive interview or unscripted Q&A containing the person’s own responsive answers;
2. original authored/co-authored substantive work with evidence of contemporaneous participation;
3. a lecture, technical presentation, teaching session, or public discussion with substantive participation;
4. active professional, advisory, organizational, civic, artistic, or technical responsibility;
5. verified active piloting, operation of complex equipment, fieldwork, or similarly demanding activity.

These do not qualify alone: attendance, a photograph, an award listing, a birthday notice, a quotation of unknown date, generic praise, a signature, a reissued old work, or absence of an impairment report.

QUALIFYING_IMPAIRMENT_EVIDENCE requires a published clinical diagnosis or credible attributable report of persistent major cognitive impairment in the evidence-collection window. Frailty, physical disability, stroke without cognitive detail, seclusion, or lack of interviews does not qualify.

Function and impairment evidence may coexist and must retain dates. The full-window person-level states are mutually exclusive and exhaustive:
- FUNCTION_ONLY
- IMPAIRMENT_ONLY
- FUNCTION_THEN_IMPAIRMENT
- IMPAIRMENT_THEN_FUNCTION
- BOTH_ORDER_INDETERMINATE_OR_SAME_DATE
- NEITHER_FOUND
- NOT_ELIGIBLE_UNDER_80

The primary endpoint is five-year cumulative incidence of first QUALIFYING_FUNCTION_EVENT after age 80, with death as a competing event. Call it public-evidence detection, never cognitive-intactness prevalence. The secondary crude endpoint is any detected function event at any age 80+.

Documentation depth is mechanical:
- LOW = 0–1 substantive late-life sources opened;
- MEDIUM = 2–4;
- HIGH = 5 or more across at least 2 independent publishers.
Retain raw counts.

Write stage1b/CODEBOOK.md that:
- copies these fixed rules without weakening them;
- resolves foreseeable edge cases direction-blindly;
- defines source tiers, independence of publishers, event dating, co-authorship, edited interviews, retrospective accounts, and conflicting evidence;
- freezes a direction-neutral analysis-date rule for DAY/MONTH/YEAR/bounded-interval event dates and requires earliest/latest sensitivity for any event whose precision can move it across the age-80 or five-year boundary;
- copies the fixed practical thresholds: 10 percentage points for the primary five-year public-function risk difference and 5.0 years for the primary 50-year post-1973 survival RMST difference;
- states that no evidence is unknown rather than impairment;
- includes a blank deviation table for any later coding-rule problem.

Also write stage1b/STAGE_COMPLETE.md attesting that no browsing or person-level outcome collection occurred and that no group outcome rates were examined.

Stop and reply only: STAGE1B_COMPLETE, followed by the two paths and any blocking failure.
```

## STAGE 1C — uniform outcome-evidence collection

Send only after Stage 1B artifacts have been hashed.

```text
Stages 1 and 1B are locked. Do not alter their files. Collect outcome evidence under the locked codebook; do not perform group comparisons.

First generate stage1c/research_worklist.csv for everyone in stage1/cohort.csv. Order people by ascending SHA-256 of the UTF-8 string:
SOL-20260721-EVIDENCE|person_id
The worklist contains research_id,person_id,full_name,search_disambiguator,birth_date,end_date,eligible_age80. Do not include cohort flags in the worklist or in evidence adjudication notes.

For every age-80-eligible person, run and log exactly these six base query families, substituting the person’s name, the precommitted search_disambiguator, and useful year bounds:
1. "<full name>" <search_disambiguator> interview
2. "<full name>" <search_disambiguator> lecture OR talk OR Q&A
3. "<full name>" <search_disambiguator> author OR book OR memoir
4. "<full name>" <search_disambiguator> dementia OR Alzheimer OR "cognitive decline" OR stroke
5. "<full name>" <search_disambiguator> 80th OR 85th OR 90th birthday
6. "<full name>" <search_disambiguator> obituary OR died

Use the runtime’s built-in web search consistently for all people. For every base query, record the first 10 returned results with rank and URL. Open the first two nonduplicate, permitted, person-matching results; if a URL repeats, is prohibited, or is inaccessible, proceed down the ranked list until two eligible pages are opened or the 10 results are exhausted. Complete all six query families even if an event is found early.

After the fixed base budget, at most three additional page opens and at most two additional queries are allowed per person, and only to resolve one of these logged triggers: inaccessible base result, same-name identity ambiguity, event-date ambiguity, conflicting evidence, or a base source that identifies a more-primary source. Do not search extra merely because no positive event was found. Every returned rank, query, opened URL, trigger, and access failure must be logged. Never accept a search snippet alone as positive evidence. Never infer function from the absence of impairment reports.

Continue the contamination rule: do not open group-level Apollo/astronaut mortality, aging, vitality, or cognition analyses. Log encounters without opening.

Write:

1. stage1c/SEARCH_LOG.csv
timestamp,research_id,person_id,query_family,query,result_rank,url,opened,access_result,source_tier,substantive_late_life_source,evidence_candidate,extra_search_trigger,notes

2. stage1c/EVIDENCE_EVENTS.csv
research_id,person_id,event_date,event_date_precision,event_date_earliest,event_date_latest,analysis_event_date,age_at_analysis_event,evidence_type,event_family,source_url,source_publisher,source_tier,direct_or_indirect,qualifies,boundary_sensitive,adjudication_confidence,supporting_paraphrase,notes

3. stage1c/PERSON_OUTCOMES.csv
research_id,person_id,eligible_age80,potential_followup_days,observed_followup_days,death_competing_event_within_five_years,administratively_censored_before_five_years,base_search_complete,base_results_logged,base_pages_opened,extra_queries,extra_pages_opened,substantive_sources_opened,independent_publishers,documentation_depth,first_qualifying_function_date,first_function_date_precision,first_function_days_after_80,first_function_within_five_years,latest_qualifying_function_date,latest_qualifying_function_age,first_qualifying_impairment_date,outcome_state,boundary_sensitive,adjudication_confidence,notes

4. stage1c/DECISIONS_AND_DEVIATIONS.md — apply only the locked codebook; list any unforeseen case and the most direction-neutral resolution before recording its final code.

5. stage1c/VALIDATION.md — verify every eligible person has all six base query families, rank logs, the fixed page-opening budget or an explicit exhaustion/access failure, no untriggered extra search, correct follow-up calculations, every qualifying event inside the evidence-collection window, partial-date rules and boundary flags, mutually exclusive outcome states linked to evidence rows, depth labels matching raw counts, and no group comparison.

6. stage1c/CONTAMINATION.md even if empty.

7. stage1c/STAGE_COMPLETE.md with artifact list and attestation that cohort-level outcome rates were not computed or discussed.

The research worklist plus the seven enumerated outputs are eight required artifacts. Process the entire worklist. Stop after Stage 1C and reply only: STAGE1C_COMPLETE, followed by the eight paths and any blocking failure.
```

## STAGE 2 — reveal questions and analyze locked data

Send only after Stage 1C artifacts have passed validation and been hashed.

```text
Stages 1, 1B, and 1C are locked. Do not alter them. You may now analyze only the dataset and evidence you constructed.

Question 1 — SURVIVAL:
Does APOLLO_FLEW show descriptively unusual all-cause survival or attained age relative to the same-era comparison families and to appropriate U.S. male birth-cohort life-table expectations?

Question 2 — PUBLICLY DOCUMENTED LATE-LIFE FUNCTIONING:
Among people who reached age 80, does APOLLO_FLEW have a different probability of at least one QUALIFYING_FUNCTION_EVENT at age 80+? This is a public-evidence detection endpoint, not a clinical cognitive measure.

Create stage2/analysis.py or stage2/analysis.R and retain all generated tables/figures. Use only your locked person-level data for astronaut comparisons. You may fetch an official U.S. life table for the population comparison; log and cite it.

Required survival analyses:
- group counts, deaths/censoring, attained ages, and exact uncertainty;
- primary 1973-01-01 common-landmark analysis among people alive then: APOLLO_FLEW versus OTHER_ALL, effect measure Apollo-minus-other restricted mean survival over a fixed 50-year horizon; use a stratified nonparametric percentile bootstrap resampling people within groups, 50,000 replicates, seed 20260721, and the 2.5th/97.5th percentiles for the 95% interval;
- age at the landmark and this fixed age-adjusted sensitivity: Cox proportional-hazards model from the landmark with group plus age-at-landmark in years as a linear covariate, Efron ties, conventional two-sided 95% interval, and Schoenfeld-residual PH diagnostic; do not substitute it for the RMST primary;
- Kaplan–Meier from birth as secondary cohort description, explicitly labeled retrospective and future-flight-selected;
- composition sensitivities versus CORE_NASA_NON_APOLLO and MILITARY_ONLY (military flags restricted to apollo_flew=0); do not describe these nested/reused groups as independent replications;
- OTHER_AVAILABLE only in the secondary birth-origin description; verify and state that it is identical to OTHER_ALL after the 1973 landmark rather than presenting a duplicate result as sensitivity evidence;
- official era- and sex-matched U.S. population expectation;
- effect sizes with 95% intervals; p-values only as supplements;
- explicit treatment of future-flight classification, immortal-time/selection, healthy-selectee, and noncausal interpretation.

Required age-80 public-evidence analyses:
- primary APOLLO_FLEW versus OTHER_ALL five-year cumulative incidence of first qualifying function detection after age 80, estimated with Aalen–Johansen and death as a competing event; primary effect is the Apollo-minus-other absolute five-year risk difference; use a stratified nonparametric percentile bootstrap resampling people within groups, 50,000 replicates, seed 20260721, and the 2.5th/97.5th percentiles for the 95% interval;
- composition sensitivities versus CORE_NASA_NON_APOLLO and MILITARY_ONLY, not independent confirmations; verify and state that OTHER_AVAILABLE and OTHER_ALL have the same age-80 risk set rather than presenting a duplicate result;
- secondary crude any-time detection: raw numerator/denominator, exact binomial intervals, risk difference, risk ratio, odds ratio, Fisher exact test, and compatible intervals;
- source-availability descriptions using documentation depth and raw counts; do not present conditioning on MEDIUM/HIGH as adjustment or complete-case correction;
- a separately labeled latent-event worst/best sensitivity for NEITHER_FOUND, explicitly stated to answer a different question from observed detection and not to change the primary estimate;
- earliest/latest plausible-date sensitivity for every boundary-sensitive event;
- latest qualifying-event-age distributions and function/impairment temporal sequences.

Classify SURVIVAL and PUBLIC FUNCTION separately with a strength—ROBUST, SUGGESTIVE, NOT_DETECTED, or INDETERMINATE—and a direction—HIGHER, LOWER, or UNCERTAIN—using the fixed materiality thresholds of 5.0 absolute RMST years and 10 absolute percentage points:
- ROBUST requires the absolute primary effect to be practically material and its primary 95% interval to exclude the null, with no direction reversal in any prespecified composition sensitivity; nested comparator sensitivities are not independent replications;
- SUGGESTIVE permits interval or ascertainment uncertainty but requires coherent direction and practical magnitude;
- NOT_DETECTED means small, unstable, or sensitivity-explained;
- INDETERMINATE means data/provenance failure prevents judgment;
- assign direction from the sign of Apollo minus comparator. Treat a large precise negative anomaly symmetrically; do not force it into NOT_DETECTED.

Write:
- stage2/ANALYSIS_DECISIONS.md before running group models;
- stage2/ANALYSIS_REPORT.md with methods, results, limitations, and plain conclusions;
- stage2/RESULTS_SUMMARY.csv with every prespecified contrast;
- stage2/VALIDATION.md;
- stage2/CONTAMINATION.md;
- stage2/BLIND_CONCLUSION.md containing the two classifications and the narrowest defensible answer to: "Is there an anomaly?"
- stage2/STAGE_COMPLETE.md.

Do not read any parent/sibling project data and do not compare your numbers with a prior result. Stop after Stage 2 and reply only: STAGE2_COMPLETE, followed by the artifact paths and any blocking failure.
```

## STAGE 3 — post-lock reconciliation

This stage is not part of the blind result. Send only after `stage2/BLIND_CONCLUSION.md` and all Stage 2 artifacts are hashed. Before sending, copy the explicitly approved reference datasets into `run/sol_001/stage3/reference/` and record their original hashes.

```text
Your blind Stage 2 conclusion is locked and may not be edited. This is a labeled post-lock reconciliation.

Compare your cohort definitions, rows, evidence, and results with the reference datasets now present under stage3/reference/. Do not assume either construction is correct by authority.

Perform three passes:
1. definition-level comparison of inclusion rules;
2. row-level comparison within shared scope, adjudicating membership/date/flag disagreements from primary sources;
3. harmonized shared-scope reanalysis, while preserving the original blind result verbatim.

Write stage3/RECONCILIATION.md, stage3/ROW_DIFFERENCES.csv, stage3/HARMONIZED_RESULTS.csv, stage3/CONTAMINATION.md, and stage3/STAGE_COMPLETE.md. Any correction to your own prior data is reported here and never back-edited into Stages 1–2.
```
