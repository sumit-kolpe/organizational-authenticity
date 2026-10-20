# Final cross-part audit - 19 October 2026

> **Current final status (19 October 2026):** The project owner confirms human source review completed with no further changes. The active Part 1 and 2 panel records now carry the completed-review disposition, the 140 usable Part 1 sources have final-selection approval, and Parts 3 and 4 were regenerated with updated hashes. Prior computational findings and their methodological limitations are unchanged. The owner confirmation is not an externally witnessed reviewer log. See `docs/HUMAN_SOURCE_VALIDATION.md`.

## Verdict

The available data pass fresh numerical cross-part checks. The work is a reproducible **provisional proof of concept**, not a fully source-validated measure of corporate authenticity. This document records the original computational audit, conducted before the project owner confirmed completed human source review. The later review completion and no-change decisions are incorporated in the active datasets. Recalculation checks do not themselves prove that historical text expresses organizational behavior.

**Updated after inspection of the complete uploaded project (19 October 2026).** This review originally examined interim output bundles. The full `organizational-authenticity.zip` was subsequently provided and directly inspected. The 450-row panels and active Part 4 outputs were verified, 97 automated tests passed, all 443 raw proxy text file hashes matched after Windows newline normalization, 35 proxy lexical rows were recomputed, and all four summary PDFs were rendered and checked. A compact package was then extracted and audited independently. Full raw proxy documents exist in the working upload but are intentionally omitted from the final compact submission. These original checks were computational; the later owner-confirmed source review is documented separately. See `docs/SUBMISSION_REVIEW_2026-10-19.md` for the full updated QA record.

## Passed

* The assignment's fixed roster has 450 company-years, 50 companies and nine years. Parts 1-3 have matching unique keys.
* 140 Part 1 observations are eligible; 443 proxies are analyzed; their scorable intersection is 137 observations across 36 companies. Missing observations are not coded as zero.
* All 137 cosine scores were independently recomputed from Part 1 theme membership and Part 2 counts. Mean: 0.5462373420742094.
* All 96 adjacent-year Part 4 changes reproduce. Its 79 known comparisons produce changed-minus-unchanged mean absolute movement of 0.006277629303134025.
* The source repairs to BLK, XOM and TSLA are reflected in proxy_v2. Seven policy-defined proxy gaps remain explicit.
* Part 3 supplies a distribution, negative controls and multiple threats to validity. Part 4 implements an exploratory question and checks company influence. Weak or unstable results are reported rather than suppressed.
* Part 3/4 local reproduction succeeded according to the user's console. A byte-hash difference was handled by a new Part 4 output directory; it was not bypassed by deleting the provenance guard.

## Material source/coding findings

| Case | Evidence inspected | Assessment and disposition |
|---|---|---|
| AAPL 2017 versus 2016 | Full saved extracted texts differ only by adding 'now' in the opening sentence. The later coding adds community. | The extra category is not explained by the text change. Keep flagged; do not interpret as newly adopted community values. A consistent recoding rule is needed before changing the primary dataset. |
| HAL 2022 versus 2021 and 2023 | Guiding Principles text is identical; 2022 adds a product-promotion block before it. People and security_privacy appear only in 2022 coding despite employee well-being and safety already being in the shared principles. | Source-boundary and coding inconsistency. Keep both comparisons flagged. Remove the extraneous block and consistently recode shared text in a new dataset version if correcting the primary series. |
| INTC 2019 versus 2018 | Saved body text differs only in a Twitter handle. Both contain the same sustainability sentence; environment appears only in 2019 coding. | Likely coding variation, not a newly expressed environmental priority. Keep flagged for possible future consistent recoding. |
| WFC 2021, low score 0.072 | Saved values text is largely navigation/link cards, language-selection prompts and footer material; proxy excerpts contain extensive governance and workforce language. | Unsuitable as a clean values-page benchmark. Do not use this low score as face-valid evidence of low authenticity. Exclusion is a documented sensitivity; source replacement or exclusion in a new primary version is recommended. |
| ABT 2021, middle score 0.594 | Saved page centers on product categories, award lists and exit-site boilerplate; proxy excerpts mix governance, compensation and sustainability references. | Source genre is a poor match for explicit stated values. Existing product/award scope warning is justified. Treat the score as provisional and include an exclusion sensitivity. |
| MPC 2024, high score 0.897 | Saved page explicitly names safety/environment, integrity, respect, inclusion and collaboration; proxy snippets include relevant themes plus table-of-contents and board references. | The broad thematic overlap is plausible, but duplicated/mandatory proxy language can raise overlap. This supports textual overlap only, not actual conduct or external validation. |

The four label/theme disagreements are already excluded in a Part 4 sensitivity, changing its contrast to +0.010862. Fresh exclusion of WFC 2021 and ABT 2021 from Part 3 leaves 135 scores with mean 0.549396, versus 0.546237 in the baseline. This targeted sensitivity does not establish that all other sources are suitable. Primary datasets are unchanged so the audit does not silently invalidate reproduced downstream outputs.

## Assignment and deliverable review

Part 1 covers the full inventory with gaps explained, but extraction is not consistently free of navigation/footer material, and several eligible sources are recruitment, product or link-hub pages. This is a material limitation against the extraction/source-selection requirement; it is not a clean full pass. Final annual selection and owner-confirmed review status are now recorded in the active rows. Earlier extraction and classification weaknesses still warrant sensitivity analysis.

Part 2 has source history, a consistent DEF 14A policy, within-company changes, sector summaries and a paired pandemic comparison. Tone is operationalized narrowly using commitment/uncertainty/obligation markers; validated sentiment is not implemented. The audit adds the missing substantive two-page summary and an explicit column dictionary. Its README.md is updated to document the v2 repairs and final state. Part 1's older README counts are also updated to the active reviewed export.

Part 3 meets the computational index/distribution/check requirements, but weak same-sector/year negative-control separation (+0.014724 on average) limits discriminant validity. Only 11 matched captures precede or coincide with filing dates. This should not be presented as a prospective measure.

Part 4 meets the exploratory-analysis requirement. Its pooled difference is small and reverses under some leave-one-company-out checks. The theme-set sensitivity is partly mechanical because those themes construct the index.

Each part needs a README.md, code, data and a 1-2 page summary in the final archive. The local audit checks existence and summary page counts. It does not certify that every historical source file or every line of code was independently reviewed. No GitHub repository has been published by this audit.

## Finalization decisions

1. Preserve the source-reviewed primary outputs as a research proof of concept: review_v2, proxy_v2, alignment_v1, exploration_v2. Include this audit and source limitations with any submission of that version.
2. Do not claim full extraction compliance, validated behavior, causal pandemic effects or **independently audited row-level approval** based solely on the owner-completion declaration.
3. If correcting source selection/coding, create new Part 1 outputs and rerun Parts 3-4 with fresh output directories. Update summaries and audit counts together; never patch only a reported number.
4. Use the local audit/package command to check the user's exact files and collect the active outputs. The archive is labeled provisional and excludes raw download caches by default. Online recollection requires the preserved collector code and its settings; offline analysis uses the included processed outputs.
5. The archive preserves documentation of the source-extraction and model-coding methods, as well as review decisions and evidence records.

Remaining judgment: accept the transparent provisional scope for this proof of concept, or perform a broader source cleanup before submission. Numerical consistency alone cannot resolve that scientific tradeoff.
