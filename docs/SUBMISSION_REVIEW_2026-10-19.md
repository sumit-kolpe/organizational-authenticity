# Submission QA audit — 19 October 2026

> **Current final status (19 October 2026):** The project owner confirms human source review completed with no further changes. The active Part 1 and 2 panel records now carry the completed-review disposition, the 140 usable Part 1 sources have final-selection approval, and Parts 3 and 4 were regenerated with updated hashes. Prior computational findings and their methodological limitations are unchanged. The owner confirmation is not an externally witnessed reviewer log. See `docs/HUMAN_SOURCE_VALIDATION.md`.

**Input:** user-provided `organizational-authenticity.zip`. **Goal:** check assignment fit, correctness, source/data integrity, report quality and packaging without fabricating missing historical observations.

## Verdict

**Conditionally submission-ready as a transparently labeled, exploratory proof of concept.** The existing numeric outputs are internally consistent and 97 automated tests passed. Important substantive limitations remain and cannot be fixed merely by editing code or documentation. The supplied research must not be represented as independently verified evidence of actual corporate conduct.

## Independently executed checks

| Check | Outcome | Meaning / boundary |
|---|---|---|
| Python tests | **97 passed; 23 subtests passed** under Python 3.13 and pytest 9.0.2 | Unit/logic checks; not a validation of LLM labels or historical page relevance. |
| Project's cross-part audit | **Passed** | Matched 450 unique roster/company-year keys and the current Part 1→2→3→4 input provenance chain. |
| Part 1 | **450 inventory rows; 140 eligible; 37 firms** | Remaining 310 company-years are ineligible, missing or require correction; no zero imputation. |
| Part 2 | **443/450 analyzed filings, 50 firms** | All 443 referenced extracted proxy texts were found in the full uploaded working archive and matched the recorded text SHA256 hashes **after Windows newline normalization**. |
| Part 2 independent sample | **35/35 sampled filing metrics matched** | Recomputed lexical topic and language indicators from original extracted text, including repaired BLK, XOM, and TSLA cases; not a manual validation of SEC contents. |
| Part 3 | **137 scores, 36 firms; mean 0.546237342074** | Full score recomputation passed the project's independent cross-part auditor. A fresh offline re-run reproduced every primary score and the aggregate summary. |
| Part 4 | **96 adjacent scored pairs, 79 known labels, 28 firms; contrast +0.0062776293** | A fresh offline re-run reproduced all stored primary pair-level and summary results. |
| Floating-point reproducibility | **Expected last-digit variation in 32 Part 3 sensitivity values** | On Python 3.13, `cosine_log_rates` differs from stored versions by only roughly 1e-16; **primary `score` values, Part 3 summary and all Part 4 results match**. Not a scientific discrepancy. |
| PDF summaries | **1, 2, 2, 2 pages** | Independently checked PDF page counts and rendered each page for a readability/layout review; all comply with max 2 pages per part. |
| Secrets / packaging | **No secrets included in curated archive** | Omit `.env`, `.venv`, `.git`, bulky raw/download caches, intermediate ZIPs, logs and superseded scaffolds. This is a packaging control, not a substitute for a full credential leak audit. |

## Outstanding issues ranked by severity

### Material: requires explicit disclosure or future research repair

1. **Inconsistent Part 1 source content and non-values material.** The saved WFC 2021 page contains navigation/link blocks, the ABT 2021 page contains product/award material, and some HAL/Apple pages mix company values with promotional/recruitment content. The assignment expects navigation/footer/boilerplate to be removed. Not all eligible inputs meet this fully. **Disposition:** preserve the primary data as provisional, document problematic rows, and recommend recapturing/recleaning and rechecking source suitability before any stronger claim.
2. **Value coding is not uniformly stable given nearly identical source text.** AAPL 2017, HAL 2022 and 2023, and INTC 2019 have unchanged-text comparisons with differing categorical labels. That may reflect source-scope or LLM variation rather than a real change in values. **Disposition:** retain disagreement queue and exclusion sensitivity; do not quietly patch labels, because it would invalidate downstream provenance/reports.
3. **Part 3 construct validity is weak.** Same-sector/year controls are on average only ~0.015 below matched companies, and most analyzed rows pair website captures **after** the year's proxy filing. Both sources are communications rather than independent actions. **Disposition:** label outputs *textual alignment*, not verified corporate authenticity, and explicitly limit claims in the summaries and README.
4. **Historical coverage is selective.** Part 1 has 140 usable cases out of 450, while Part 3 scores only 137. Unequal samples by company, year, and source genre prevent naive population trends or corporate rankings. **Disposition:** report denominators, exclude missing rather than scoring zero, and avoid broad generalization.
5. **Independent human source validation was undocumented at the time of this audit.** The prior source quality review was model-supported and selectively sampled; the primary series originally had `annual_selection_final=false`. **Final disposition:** the project owner subsequently confirmed completing review without new corrections; current source tables record 140 approved Part 1 selections and the review disposition for all 450 inventory rows. Do not claim the package auditor independently verified every source.

### Moderate: submission and reproducibility hazards (corrected or clarified)

6. **Outdated root README:** the uploaded top-level README still described the project as a Step 1.1 scaffold with no data. **Fixed** by replacing it with an accurate guide naming the four active implementation folders, results, offline commands and limitations.
7. **Misleading legacy scaffold directories:** older `part2_lived_values`, `part3_authenticity_index` and `part4_research_proposal` describe unfinished work even though real code lives in parallel directories. **Fixed for delivery** by excluding these abandoned scaffolds from the curated ZIP and listing active names in the root README.
8. **Original ZIP is needlessly large:** it includes a Windows virtual environment, `.git` scaffolding, redundant nested archives, raw retrieval material and intermediates. **Fixed for delivery** with an active-outputs-only compact ZIP and manifest. Keep the original full working ZIP privately if later source re-extraction is needed.
9. **Processed-only submission cannot reproduce raw retrieval offline.** The curated ZIP intentionally omits ~2 GB of downloaded data. **Clarified** with exact statements on which analyses can be replayed offline versus which require original raw source caches and network/API access.
10. **Dependency/environment nuance:** the original dependency files split core collection packages (`requirements.txt`) from reporting/auditing packages (`requirements-final.txt`). **Clarified** by a two-requirements install command. Existing tests pass on Python 3.13; the user's Windows environment was not executed here.

## What was and was not changed

**Final changes:** root and per-part documentation, owner-confirmed row-level review status, final Part 1 selection flags, matching Part 2 status fields, freshly generated Part 3/4 outputs and hashes, and all four summary PDFs. **Preserved:** the underlying research text, theme choices, source URLs, proxy counts, numerical scores and statistical findings. Missing source material remains missing.

This review does not independently verify all 450 historical Wayback pages, the content of all 443 SEC filings, or the LLM's theme decisions. Retrieval and model calls were not reissued. A numeric re-run does not certify historical page selection, behavior, or causal interpretation.

## Recommended submission message

> This submission is a reproducible, provisional research proof of concept for a fixed sample of 50 firms. It provides versioned, source-linked datasets and documented analysis for all four parts. Historical values-page coverage and page quality are incomplete; the resulting index measures **textual alignment between organizational messaging and proxy disclosures**, not independently verified conduct. Known validity threats, sensitivity analyses, coverage gaps and replication instructions are included.

## Most important improvements if time allows

1. Preserve any additional detailed human-review notes if available and prioritize extraction improvements in future releases.
2. Recode recurring values text consistently, validate change-label disagreements, and publish a new Part 1 dataset version; rerun Parts 3–4 and regenerate PDFs after any upstream change.
3. Review proxy source voice (management vs shareholders vs mandated text) and check timing/CIK continuity.
4. Test the index against at least one independent, nontextual measure of organizational conduct.

**Conclusion:** computational checks passed, packaging/documentation problems can be corrected safely, and material scientific limitations must remain visible.
