# Stage 1C decisions and deviations

## Governing rule

All adjudication applied the locked `stage1b/CODEBOOK.md` without changing the endpoint. No cohort flags were used in the research worklist or person-level evidence notes. “NEITHER_FOUND” means that the fixed public-evidence budget detected neither qualifying function nor qualifying impairment; it is unknown, not impairment.

## Direction-neutral resolutions recorded before final coding

| Case | Foreseeable or unforeseen issue | Direction-neutral resolution |
|---|---|---|
| R001 | The first four base-family result streams were technically merged, and two remaining base streams were inaccessible. | Preserve every returned rank and access result, mark the technical deviation, and use only the two allowed extra queries and three allowed extra page attempts under the inaccessible-base-result trigger. Do not impute missing result streams. |
| R006 and R011 | Later sources identify earlier interviews without a defensible conduct date. | Do not substitute the episode, book, or later source date; without a defensible bounded conduct date, do not qualify the candidate. |
| R022, R056, and R092 | Derived notes described plausible substantive conduct, but the locally retained opened content does not preserve enough substantive responsive material to verify it. | Insufficient stored evidence is nonqualifying; do not search for replacement evidence during repair. |
| R037 | The stored obituary reports the crash of Crossfield's aircraft but does not explicitly identify him as its operator. | Do not infer active piloting from aircraft ownership, reputation, or the circumstances of death. |
| R039 and R076 | A caption says that the person speaks at an event. | A caption or isolated “speaks” statement does not establish substantive participation. |
| R058 | A museum page is a future-tense announcement; the later ABC source contains both a detailed attributable family impairment report and Aldrin's substantive answers. | Exclude the announcement, qualify the detailed credible persistent-impairment report despite the dispute, independently qualify the later function interview, and retain their order. |
| R060 | An edited interview page presents multiple current substantive answers and describes the interview as recent without identifying an earlier recording date. | Use the page publication date under the frozen edited-interview proxy rule. |
| R071 | A source identified an as-told-to memoir that appeared posthumously, but it did not date the subject's participation. | Use the permitted more-primary-source query; because participation could not be dated inside the evidence window, do not qualify the work. |
| R077 | A university page announced a future substantive lecture, and the linked occurrence record was inaccessible. | A prospective announcement alone does not prove substantive participation. Retain the accesses and code no event. |
| R078 | A substantive memoir had month-level dating. | Use MONTH bounds and the locked midpoint analysis date; retain earliest/latest dates and test both boundaries. |
| R081 | A 2010 reprint contained a Dana foreword, but the official NASA record dated the original work to 2007. | Treat the 2010 edition as a reissue of old work, which cannot qualify alone. |
| R090 | An obituary linked attributed statements from 2003 and 2016 and separately listed later responsibilities without dates. | Exclude the pre-age-80 statements and do not turn undated service descriptions into events. |

## Collection-process deviations

- R001 is the only base-query stream-format deviation. The six required query families were issued, but four base families share one result stream in the raw technical record and two had inaccessible base streams. Its allowed extras are fully logged.
- When an already-opened base page had to be re-opened to expose a date or article body, the re-open was conservatively counted as an additional page open.
- All other extra queries or page opens have one of the locked triggers in `SEARCH_LOG.csv`. No extra search was run merely because a positive event was absent.

## Coding-rule deviations

No coding rule was changed.

## Controller-gate consistency re-audit

Unforeseen consistency issue: the initial adjudication did not apply every already-frozen exclusion uniformly to analogous candidate sources. In particular, some positive coding relied on a future event listing or speaker caption, substituted a later source or episode date for earlier conduct, treated retrospective publication wording as a conduct date, inferred operation from context, or relied on a derived paraphrase when the locally retained opened content did not itself preserve the necessary substantive evidence.

Direction-neutral resolution recorded before revised final coding:

- Require the locally stored opened source content itself to establish attributable substantive conduct and a defensible conduct date or bounded interval. A future listing, program, schedule, speaker label, photograph, caption, isolated quotation, or reputation does not satisfy that requirement alone.
- The documented conduct date controls. A later episode, page, book, or report date cannot substitute for an earlier interview or activity that the source identifies as earlier. Unbounded retrospective wording receives no analysis date.
- Qualify authorship only when the source supports both a new substantive work and contemporaneous participation; a reissue or later edition does not qualify alone.
- If the retained local source does not contain the content needed to verify a candidate, code the candidate nonqualifying even if an earlier derived note described it as plausible.
- Apply the impairment rule independently of function. A detailed, attributable report of persistent major cognitive impairment may qualify even when disputed; preserve a later qualifying function event and order both by their defensible dates.
- Apply these checks to every event row and closest locally stored analogues, including the schedule/caption, retrospective-date, reissue, incomplete-content, stroke-without-cognitive-detail, and disputed-impairment cases. Do not search for replacement evidence.

This is consistent enforcement of the locked codebook, not a new coding rule.
