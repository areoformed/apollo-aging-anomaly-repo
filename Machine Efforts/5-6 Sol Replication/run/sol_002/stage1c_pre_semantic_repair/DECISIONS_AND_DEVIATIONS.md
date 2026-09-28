# Stage 1C decisions and deviations

## Governing rule

All adjudication applied the locked `stage1b/CODEBOOK.md` without changing the endpoint. No cohort flags were used in the research worklist or person-level evidence notes. “NEITHER_FOUND” means that the fixed public-evidence budget detected neither qualifying function nor qualifying impairment; it is unknown, not impairment.

## Direction-neutral resolutions recorded before final coding

| Case | Foreseeable or unforeseen issue | Direction-neutral resolution |
|---|---|---|
| R001 | The first four base-family result streams were technically merged, and two remaining base streams were inaccessible. | Preserve every returned rank and access result, mark the technical deviation, and use only the two allowed extra queries and three allowed extra page attempts under the inaccessible-base-result trigger. Do not impute missing result streams. |
| R037 | Function evidence and death occur on the same day. | A same-day function event is detected before no earlier competing death; retain both dates and do not code death as preceding function. |
| R056 | The only opened positive source is a low-tier specialty publisher. | Retain the qualifying dated Q&A because it meets the fixed content rule, and assign LOW event confidence rather than changing qualification by expected direction. |
| R058 | Family allegations described decline or dementia, while Aldrin disputed them and no clinical diagnosis was published. | Retain the allegation as a dated nonqualifying impairment row. Do not code qualifying impairment without the locked clinical or credible persistent-impairment threshold. |
| R060 and R092 | Edited interview pages supplied publication dates but not recording dates. | Apply the locked edited-interview proxy: use the page publication date and explain the proxy in notes. |
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
