# Stage 1b public-evidence endpoint codebook

## Status and scope

This codebook is frozen before outcome collection. It operationalizes a public-evidence endpoint; it does **not** define or estimate a clinical cognitive diagnosis, cognitive intactness, or cognitive-intactness prevalence.

All rules are applied identically without reference to cohort, program, exposure, expected direction, or eventual result. Coders must not use group membership to change search depth, source acceptance, event qualification, dating, or adjudication.

## Eligibility and observation windows

A person is eligible if the person reached the 80th birthday on or before death or the fixed censoring date, **2026-06-01**.

- A person who died before the 80th birthday is `NOT_ELIGIBLE_UNDER_80`.
- A person who reached age 80 on the date of death is eligible.
- The evidence-collection window begins on the 80th birthday and ends on the earlier of death or 2026-06-01, inclusive.
- Evidence of activity or impairment before the 80th birthday cannot qualify, although it may be retained as non-endpoint context.
- Evidence after death or after 2026-06-01 cannot itself be an observed event. A later-published retrospective source may document an earlier event only under the retrospective-account rules below.

The primary analytic window is age `[80,85)`: it includes the 80th birthday and excludes the 85th birthday.

Primary follow-up begins on the 80th birthday and ends at the earliest of:

1. the first `QUALIFYING_FUNCTION_EVENT`;
2. death;
3. the 85th birthday; or
4. 2026-06-01.

Death before detected qualifying function is a competing event. Administrative end before age 85 is right censoring. Reaching the 85th birthday without a prior event or death ends primary follow-up without a primary function event.

Collection continues after age 85, when observable, through death or 2026-06-01 for the secondary description of any detected function event at any age 80 or older.

## `QUALIFYING_FUNCTION_EVENT`

A `QUALIFYING_FUNCTION_EVENT` is dated, attributable evidence within the evidence-collection window of substantive self-directed activity in at least one of these families:

1. a substantive interview or unscripted Q&A containing the person’s own responsive answers;
2. original authored or co-authored substantive work with evidence of contemporaneous participation;
3. a lecture, technical presentation, teaching session, or public discussion with substantive participation;
4. active professional, advisory, organizational, civic, artistic, or technical responsibility;
5. verified active piloting, operation of complex equipment, fieldwork, or similarly demanding activity.

Events within five years after age 80 contribute to the primary endpoint. Later events contribute only to secondary descriptions.

The following do **not** qualify alone:

- attendance;
- a photograph;
- an award listing;
- a birthday notice;
- a quotation of unknown date;
- generic praise;
- a signature;
- a reissued old work; or
- absence of an impairment report.

### Substantive and self-directed

“Substantive” requires evidence of content, decisions, duties, instruction, creation, operation, or responsive participation beyond ceremonial presence or passive recognition. “Self-directed” requires evidence that the person supplied responsive answers, content, judgment, performance, or operational action. No inference is made merely from title, reputation, appearance, or physical presence.

A single event can satisfy more than one family. It is stored once as an event with all applicable family flags.

### Interviews and Q&A

- A dated interview qualifies when the person’s own answers are attributable and substantively responsive.
- Live, recorded, written, email, or transcripted interviews can qualify.
- Normal journalistic editing, abridgment, translation, or removal of filler does not disqualify an interview if the source preserves attributable responsive answers.
- A scripted promotional statement, isolated quotation, paraphrase without the person’s answers, press-release boilerplate, or unknown-date quotation does not qualify alone.
- If an interview is published after the evidence window but was demonstrably conducted inside it, the conduct date or bounded conduct interval controls. Publication after the window does not by itself create an event.

### Authorship and co-authorship

- A new substantive book, article, essay, technical report, artistic work, or comparable original work can qualify when there is evidence of the person’s contemporaneous participation.
- Co-authorship is treated the same as sole authorship only when a byline plus contemporaneous source information, contributor statement, interview, acknowledgment, editorial record, or comparable evidence supports actual participation.
- A byline alone is not sufficient when the item is a reissue, compilation of old material, posthumous publication, ghostwritten work, nominal/honorary authorship, or otherwise leaves contemporaneous participation unresolved.
- A new edition qualifies only for documented new substantive contribution made during the evidence window. Reprinting, reformatting, translation, or a new foreword written earlier does not qualify.
- Publication date is the event date only when it reasonably marks contemporaneous completion or release of the new contribution. If contribution timing is reported as an interval, interval dating applies.

### Lectures, teaching, and public discussion

- A lecture, class, technical presentation, panel, or public discussion qualifies when a recording, transcript, detailed contemporaneous account, or equivalent evidence shows substantive participation.
- A schedule, program, speaker listing, photograph, or attendance report alone does not qualify.
- A prerecorded presentation qualifies if the recording date is within the window; if only a release date is known and contemporaneous creation is supported, the release date is used and marked as a publication-date proxy.

### Active responsibility

- A professional, advisory, organizational, civic, artistic, or technical role qualifies only when dated evidence shows active duties, decisions, work product, leadership action, advice, or comparable responsibility.
- Holding an honorary title, being listed on a board without evidence of activity, receiving an award, or having a biography state that the person “remained active” does not qualify alone.
- A role spanning an interval may generate an event at the earliest dated, documented substantive action in that interval. The appointment date alone qualifies only if accepting or beginning the role itself entailed a documented substantive responsibility.

### Piloting, equipment operation, and fieldwork

- Piloting, operation of complex equipment, fieldwork, or similarly demanding activity qualifies when the person, activity, and date are verified by a contemporaneous record or credible attributable account.
- Ownership, licensure, a posed cockpit photograph, or an undated claim of continued operation does not qualify alone.

## `QUALIFYING_IMPAIRMENT_EVIDENCE`

`QUALIFYING_IMPAIRMENT_EVIDENCE` requires either:

1. a published clinical diagnosis of persistent major cognitive impairment; or
2. a credible, attributable report of persistent major cognitive impairment.

The impairment must be dated within the evidence-collection window, either exactly or by a defensible bounded interval.

Qualifying reports must identify persistent, major cognitive dysfunction rather than invite inference from circumstances. Potential examples include an attributable diagnosis of dementia or major neurocognitive disorder, or a credible report describing persistent major loss of memory, orientation, comprehension, judgment, or independent cognitive functioning.

The following do **not** qualify without cognitive detail:

- frailty;
- physical disability;
- stroke;
- seclusion or privacy;
- retirement;
- reduced travel or public appearances;
- reliance on assistance for physical tasks;
- transient delirium, anesthesia effects, or acute confusion;
- lack of interviews; or
- absence of public function evidence.

Function and impairment evidence may coexist. Neither automatically invalidates the other. Impairment does not censor later function-event detection; only death, the relevant administrative boundary, or detection of the first function event ends primary function follow-up.

## Full-window person-level state

Using all qualifying evidence from age 80 through death or 2026-06-01, assign exactly one mutually exclusive and exhaustive state:

- `FUNCTION_ONLY`
- `IMPAIRMENT_ONLY`
- `FUNCTION_THEN_IMPAIRMENT`
- `IMPAIRMENT_THEN_FUNCTION`
- `BOTH_ORDER_INDETERMINATE_OR_SAME_DATE`
- `NEITHER_FOUND`
- `NOT_ELIGIBLE_UNDER_80`

Assignment is mechanical:

- Function evidence and no impairment evidence: `FUNCTION_ONLY`.
- Impairment evidence and no function evidence: `IMPAIRMENT_ONLY`.
- Both, with the earliest function event before the earliest impairment evidence: `FUNCTION_THEN_IMPAIRMENT`.
- Both, with the earliest impairment evidence before the earliest function event: `IMPAIRMENT_THEN_FUNCTION`.
- Both on the same analysis date, or with date intervals that do not establish a stable order: `BOTH_ORDER_INDETERMINATE_OR_SAME_DATE`.
- Eligible, with neither form found: `NEITHER_FOUND`.
- Did not reach age 80 by death or censor: `NOT_ELIGIBLE_UNDER_80`.

`NEITHER_FOUND` means that neither qualifying form was detected in the searched public record. It is not evidence of impairment, absence of function, or absence of unpublished evidence.

## Endpoint definitions

### Primary endpoint

The primary endpoint is the five-year cumulative incidence of first `QUALIFYING_FUNCTION_EVENT` after age 80, with death as a competing event.

It must be called **public-evidence detection**. It must never be called cognitive-intactness prevalence or interpreted as a clinical cognitive endpoint.

An event exactly on the 85th birthday is outside the primary age `[80,85)` window but remains eligible for the secondary age-80-plus description.

If a function event and death have the same exact calendar date, the event precedes death only when evidence establishes that the activity occurred while the person was alive on that date. If time order cannot be established, preserve the tie and run the required earliest/latest or tie-order sensitivity; do not resolve it according to cohort or expected direction.

### Secondary endpoint

The secondary crude endpoint is any detected `QUALIFYING_FUNCTION_EVENT` at any age 80 or older, within the evidence-collection window.

This is also a public-evidence detection description, not a clinical prevalence measure.

## Source tiers

Source tier describes provenance and evidentiary strength; it does not replace the event definition.

### Tier 1: direct or primary evidence

- full or substantially complete contemporaneous video, audio, transcript, interview text, authored work, lecture material, official minutes, operational record, or technical record;
- an official clinical publication or directly attributable public statement from the treating institution or clinician, when lawfully public;
- a first-party institutional record that documents the person’s dated action or responsibility.

### Tier 2: credible attributable reporting

- major national, regional, or specialist news reporting;
- reputable institutional, university, museum, professional-society, publisher, or organizational reporting;
- a family-authorized obituary or attributable report;
- a detailed contemporaneous account by an identified witness or responsible organization.

### Tier 3: secondary leads and corroboration

- derivative biographies, aggregators, unsourced institutional summaries, reposts, social-media items, search snippets, and other secondary references.

Tier 3 material can locate stronger evidence and can corroborate identity or date. It does not qualify an otherwise ambiguous event merely by repeating a claim. A Tier 3 item containing an authentic embedded primary artifact may be coded to the embedded artifact’s publisher and provenance, with the hosting source also retained.

A single clear Tier 1 source can establish a qualifying event. Tier 2 evidence can establish an event when it is attributable, specific, dated, and directly supports the fixed definition. Source tier, qualification decision, and documentation depth are stored separately.

## Publisher independence

Publisher independence is evaluated at the level of editorial or record-producing control:

- Syndicated copies, mirrors, excerpts, transcripts, clips, or reposts of one original item count as one publisher family.
- Different imprints, channels, websites, or archives under the same controlling organization are not independent unless they produced separate original reporting or records.
- A press release and news stories that merely repeat it are one underlying evidence chain.
- A video host and the organization that produced the video are one chain unless the host added independent reporting.
- Two outlets are independent when each produced its own reporting, interview, record, or verification rather than copying a common source.
- Co-produced material counts as one evidence chain for independence.

Independence affects the `HIGH` documentation-depth threshold, not whether a clearly qualifying event occurred.

## Documentation depth

Documentation depth is mechanical:

- `LOW` = 0–1 substantive late-life sources opened.
- `MEDIUM` = 2–4 substantive late-life sources opened.
- `HIGH` = 5 or more substantive late-life sources opened across at least 2 independent publishers.

Retain:

- the raw number of substantive late-life sources opened;
- the raw number of independent publishers;
- the assigned depth category; and
- the source-to-publisher-family mapping.

A substantive late-life source is an opened source that contains event-relevant late-life content, impairment-relevant content, or specific dated information needed to adjudicate such content. Search-result snippets, duplicate mirrors, inaccessible pages, and sources containing only excluded evidence do not inflate the substantive-source count, although all search and access attempts remain in the source log.

Documentation depth measures research depth, not function, impairment, source quality, or confidence. `LOW` and `NEITHER_FOUND` must never be converted to impairment.

## Event attribution and dating

Each candidate event or impairment record must retain:

- person identifier;
- evidence type and applicable function-family flags;
- source URL and publisher family;
- publication date, when known;
- activity or impairment date as reported;
- `date_precision`;
- `event_date_lower`;
- `event_date_upper`;
- main `analysis_date`;
- attribution text or a concise paraphrase;
- qualification decision and reason;
- source tier;
- whether the date can cross age 80, the 85th birthday, death, or censor under sensitivity; and
- links to duplicate, corroborating, conflicting, or retrospective records.

The activity date controls when it is stated. Publication date is used only when the source itself is the contemporaneous event or work, or when it is a justified proxy for contemporaneous creation and that proxy is flagged. A later report does not shift an earlier activity to the report date.

### Frozen direction-neutral date rule

Allowed `date_precision` values are `DAY`, `MONTH`, `YEAR`, and `BOUNDED_INTERVAL`.

For every non-day date, first define an inclusive lower and upper calendar bound:

- `DAY`: lower = upper = the stated calendar date.
- `MONTH`: lower = the first day and upper = the last day of the stated month.
- `YEAR`: lower = January 1 and upper = December 31 of the stated year.
- `BOUNDED_INTERVAL`: lower and upper are the narrowest defensible inclusive dates explicitly supported by the source and other fixed calendar facts. “At age 82,” for example, is bounded by the 82nd birthday through the day before the 83rd birthday.

The main `analysis_date` is the calendar midpoint:

`event_date_lower + floor((event_date_upper - event_date_lower) / 2)`

When an interval has two central dates, this formula selects the earlier central date. This convention is fixed for all people and evidence directions.

An unbounded expression such as “before,” “after,” “years earlier,” “in his eighties,” or “late in life” receives no analysis date unless defensible lower and upper bounds can be established without person-specific directional judgment. Undated evidence is retained but cannot itself produce a dated endpoint event.

### Mandatory boundary sensitivity

For any candidate event whose date precision can move it across the 80th birthday or the five-year boundary at the 85th birthday:

1. run the main analysis using `analysis_date`;
2. run an earliest-date sensitivity using `event_date_lower`; and
3. run a latest-date sensitivity using `event_date_upper`.

The same earliest/latest sensitivity is required when imprecision can change ordering relative to death, censor, another qualifying function event, or the earliest impairment evidence. Report whether eligibility, primary-event status, first-event ordering, or full-window state changes. Never select a bound based on which result is more favorable.

## Retrospective accounts

- A retrospective source can qualify an earlier function event or impairment only when it provides attributable, substantive, and dateable evidence.
- The documented activity or impairment date/interval, not the later publication date, controls.
- A broad retrospective statement such as “he remained sharp and active” does not qualify.
- A retrospective account identifying a specific lecture, interview, work product, duty, flight, diagnosis, or persistent impairment with a defensible date or bounded interval can qualify at the source tier warranted by its provenance.
- Posthumous publication does not itself create a posthumous event and does not establish contemporaneous authorship without evidence of participation before death.

## Conflicting and overlapping evidence

- Function and impairment evidence are not treated as contradictions; both are retained and ordered when possible.
- Conflicting dates, identities, descriptions, or source claims are all retained with provenance.
- Prefer direct records over derivative accounts, specific dates over unsupported summaries, and corrected versions over superseded versions.
- Do not average conflicting dates.
- If conflict remains material, code the narrowest defensible interval or unresolved status and apply sensitivity.
- Duplicate reporting of one event remains one event, linked to all supporting sources.
- Evidence suggesting inability does not erase a separately qualifying function event, and a function event does not erase qualifying impairment evidence.
- Adjudication must be blind to cohort and expected direction whenever practicable. The same resolution must be applied to every analogous record.

## Absence of evidence

No evidence is **unknown**, not impairment.

Specifically:

- no function event found does not establish impairment;
- no impairment evidence found does not establish normal cognition;
- no interview found does not establish inability to be interviewed;
- seclusion or sparse public record does not establish either endpoint;
- search depth is reported through the mechanical documentation-depth variables, not converted into a person-level clinical conclusion.

## Fixed practical thresholds

These thresholds are copied unchanged and are not estimated or evaluated in Stage 1b:

- Primary five-year public-function risk-difference practical threshold: **10 percentage points**.
- Primary 50-year post-1973 survival restricted-mean-survival-time difference practical threshold: **5.0 years**.

## Deviation control

No coding-rule problem may be resolved silently. A proposed deviation must be entered below before implementation, justified without reference to group direction, approved under the later protocol, applied consistently to every affected record, and accompanied by sensitivity analysis when it could affect eligibility, event qualification, timing, ordering, censoring, or state assignment.

| Deviation ID | Date raised | Coding-rule problem | Affected records | Locked rule implicated | Proposed resolution | Direction-neutral rationale | Approved by | Approval date | Implementation status | Sensitivity required |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
