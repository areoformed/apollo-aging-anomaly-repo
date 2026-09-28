# Fable Replication — Frozen Prompts

**Frozen:** June 9, 2026. These are the exact prompts delivered to the replication instance, in the order and isolation described in `preregistration.md` §2. Each stage's output is saved to disk before the next stage is sent. Any post-freeze change is a protocol deviation.

---

## STAGE 1 — cohort construction (no analytic question disclosed)

You are constructing a reference dataset for a survival-analysis exercise. You don't need
to know the purpose of the analysis, and you should not speculate about it — your only
job is to build the cleanest, best-documented dataset you can.

**Task:** Construct a dataset covering:
(a) every NASA astronaut who flew on an Apollo program mission, and
(b) a comparison set of American astronauts of the same era who met the same selection
requirements as the Apollo astronauts but never flew an Apollo mission.

**Requirements:**

1. **Decision log first.** Before any data, write a DECISIONS section documenting every
   cohort-definition judgment call you make, each with a one-line rationale. At minimum:
   - What counts as "flew Apollo" (which missions are in/out — and why)
   - How you handle the Apollo 1 crew
   - How you handle Skylab and Apollo-Soyuz
   - How you handle astronauts selected in the Apollo era who never flew at all
   - How you bound the comparison group: what you treat as "the same selection
     requirements" (requirements evolved across selection groups — decide which standard
     is operative and document it) and who meets it — which selection programs and
     groups are in or out, and why
   - Any individual edge cases (e.g., people who fit multiple categories)
   Make your own calls. There are defensible answers on multiple sides; what matters is
   that your reasoning is explicit.

2. **Fixed censoring date: June 1, 2026.** Anyone alive on that date is recorded as ALIVE.

3. **Per-row provenance.** For every person, cite a source URL for the birth date and (if
   dead) the death date. Prefer primary/roster sources: NASA biography pages, official
   obituaries, agency releases. **Do not copy cohort tables or membership lists from any
   existing study of astronaut mortality or longevity.** If you encounter such a study
   while searching, do not read its tables; record the encounter in a CONTAMINATION
   section and continue from primary sources.

4. **Output format — strict CSV**, one row per person, sorted by last name, with exactly
   these columns:
   `full_name, cohort, nasa_group, birth_date, death_date, vital_status_20260601, apollo_missions, first_spaceflight_year, birth_source_url, death_source_url, confidence, notes`
   - `cohort`: your own labels, defined in the decision log
   - dates in YYYY-MM-DD; `death_date` empty if alive
   - `vital_status_20260601`: ALIVE or DEAD
   - `confidence`: HIGH / MEDIUM / LOW — flag any row where sources conflict or a date is
     approximate, and explain in `notes`

5. **Completeness over speed.** If you are unsure whether someone belongs, include them
   with a note rather than silently dropping them. Silent exclusions are the one
   unrecoverable error.

Deliver: DECISIONS section → CONTAMINATION section (even if empty) → CSV.

---

## STAGE 1b — blind outcome coding (sent only after Stage 1's CSV is saved)

For every person in your dataset, add two coded fields, with the same per-row provenance
discipline as before:

1. `cognitive_status_20260601` — one of:
   - `IMPAIRED_DOCUMENTED` — a published diagnosis or credible public report of dementia
     or major cognitive decline (cite it)
   - `INTACT_DOCUMENTED` — affirmative public evidence of intact cognition late in life
     (recent interviews, flying, public talks, published work — cite the most recent)
   - `NO_EVIDENCE_EITHER_WAY`
   - `DIED_EARLY` — died before late-life cognition could be assessed (choose and
     document your own age cutoff)
2. `documentation_depth` — HIGH / MEDIUM / LOW: how much public coverage exists about
   this person at all, independent of what it says. A person can be LOW depth with
   NO_EVIDENCE — that combination is informative; record it honestly.

Rules: code from sources, not from fame or general impressions. Do **not** infer
intactness from the absence of impairment reports — that is exactly what
NO_EVIDENCE_EITHER_WAY is for. Log every judgment call in a STAGE-1b DECISIONS section.

---

## STAGE 2 — analysis (sent only after Stage 1 and 1b outputs are saved)

Using only the dataset you constructed, assess two questions:

1. **Mortality:** do the astronauts who flew Apollo missions show mortality that differs
   from (a) your comparison astronaut group and (b) era- and sex-matched US population
   expectations (e.g., SSA cohort life tables)?
2. **Late-life cognitive outcomes:** define an endpoint you consider fair (justify it),
   and assess whether Apollo-flown astronauts differ from comparison astronauts. State
   explicitly how your `documentation_depth` codings affect the strength of any
   conclusion — i.e., quantify or bound the ascertainment problem rather than waving at it.

Choose your own methods and justify them. Report effect sizes with confidence intervals,
not just p-values. State conclusions plainly, including "no detectable difference" if
that is what your analysis shows — a null is an acceptable answer for either question
independently. Document any additional judgment calls (index date for time-at-risk,
reference population construction, endpoint definition) in the same decision-log style.
