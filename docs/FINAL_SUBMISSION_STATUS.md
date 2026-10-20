# Submission status — 19 October 2026

**Completed:** Four assignment parts, structured source and analytical files, 1–2 page reports, datasets and methodological explanations. The project owner confirms **completed human source review with no additional corrections**. The existing usable inputs have been accepted without changing historical text, themes or scores. Source gaps, genuine computational failures and research validity limitations remain transparently identified.

## Data and review summary

| Area | Final recorded status |
|---|---|
| Required inventory | 50 companies × 9 years = 450 company-years |
| Part 1 | 140 source selections accepted after review; 310 source years unavailable/invalid/excluded |
| Part 2 | 443 proxy documents retained; 7 years missing under source policy |
| Part 3 | 137 reproducible textual-alignment scores across 36 companies; mean 0.546237 |
| Part 4 | 96 matched-year score pairs; 79 with known website-text change decision; difference +0.006278 |
| Human review | Project-owner-confirmed complete, no new source/coding corrections; decisions recorded in active inputs |
| QA | Unit tests and cross-part numerical audit pass; 1-, 2-, 2-, 2-page PDFs |

## Scientific interpretation

The index estimates **textual similarity** between self-reported values and proxy-disclosure vocabulary. It does not independently observe conduct or prove organizational authenticity. Source quality, uneven historical coverage and low company-specific discriminant validity remain important limitations. An owner-confirmed review decision must not be conflated with an independent external re-verification of every archived page.

## Reproduce

Install both `requirements.txt` and `requirements-final.txt`, run `python -m unittest discover -s tests -v`, then `python -m shared.final_audit --part4-version exploration_v2`. The archival raw retrieval caches are held outside this compact submission and source recollection requires network/model access.
