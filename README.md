# Organizational Authenticity & Corporate Value Alignment

Wharton–TAU Lab research-assistant recruitment assignment | 50 companies | 2016–2024

## What this project does

This project compares the themes organizations state in archived corporate-identity pages with themes mentioned in annual SEC proxy statements (Form DEF 14A). It constructs a provisional textual-alignment index, then explores whether changes to website text coincide with larger movements in that index.

Important interpretation: Proxy statements are corporate disclosures, not independent observations of behavior. The score must not be presented as verified organizational authenticity, fulfillment of promises, a ranking of ethical performance, or a causal effect.

## Current results and required deliverables

| Part | Implemented directory | Primary data / results | Written summary | Coverage |
|---|---|---|---|---|
| 1. Stated values | `part1_stated_values/` | `outputs/review_v2/part1_values_reviewed.csv` (and JSON) | `Part1_Summary.pdf` | 450 inventory rows; 140 accepted usable records, 37 firms |
| 2. Lived/disclosed values | `part2_disclosed_priorities/` | `outputs/proxy_v2/disclosure_metrics.csv` (and JSON) | `outputs/proxy_v2/Part2_Summary.pdf` | 443 analyzed proxy statements, 50 firms |
| 3. Alignment measure | `part3_alignment/` | `outputs/alignment_v1/alignment.csv` (and JSON) | `outputs/alignment_v1/Part3_Summary.pdf` | 137 nonmissing index scores, 36 firms |
| 4. Additional analysis | `part4_exploration/` | `outputs/exploration_v2/pairs.csv` (and JSON) | `outputs/exploration_v2/Part4_Summary.pdf` | 79 pairs with known text-change labels, 28 firms |

Every implemented directory includes its own `README.md`, source code in `src/`, and versioned output files in `outputs/`. Each PDF is one or two pages. `part2_disclosed_priorities/DATA_DICTIONARY.md` explains the Part 2 columns. The authoritative assignment company list is `config/companies.csv`.

The similarly named `part2_lived_values/`, `part3_authenticity_index/`, and `part4_research_proposal/` directories in the full working archive are outdated initial scaffolds; the implemented directories above are the ones to assess. These outdated scaffolds are excluded from the compact submission ZIP.

## Key descriptive findings

1. Mean scored Part 3 alignment: 0.546 on a zero-to-one cosine scale. The available historical website sample is selective; only 137/450 company-years can be scored.
2. Same-sector/year negative controls score only approximately 0.015 lower on average than the matching company, indicating weak company-specific separation.
3. Part 4's changed-minus-unchanged difference in mean absolute annual score movement is +0.0063. The sign can reverse when one company is excluded, so the result is not robust.

Source review completed: The project owner confirmed on October 19, 2026 that human review was complete and no further changes were needed. The source-review decisions have been recorded in the Part 1 and Part 2 company-year datasets. Missing and excluded observations remain excluded; the index results are unchanged. See `docs/HUMAN_SOURCE_VALIDATION.md`.

## Quick verification (offline)

Use Python from the project root, without changing the provided data files:

```bash
python -m pip install -r requirements.txt -r requirements-final.txt
python -m unittest discover -s tests -v
python -m shared.final_audit --part4-version exploration_v2
```

A local environment may also run `python -m pytest -q tests` if `pytest` is installed. The audit checks the required 50-company/year panels, index mathematics, source/output hash chain, primary Part 4 calculations, README availability, and PDF page counts. It does not independently validate historical source selection or the model's coding accuracy. See `docs/FINAL_AUDIT.md` and `docs/SUBMISSION_REVIEW_2026-10-19.md`.

To regenerate Part 3 and Part 4 without overwriting frozen outputs:

```bash
python -m part3_alignment.src.analyze_alignment --output scratch_alignment
python -m part4_exploration.src.explore_changes --alignment scratch_alignment/alignment.json --output scratch_exploration
```

For report rendering, run `python -m part3_alignment.src.render_report --output scratch_alignment` and `python -m part4_exploration.src.render_report --output scratch_exploration`. Input byte hashes are part of the provenance guards. Avoid altering line endings or reformatting input JSON while attempting exact replay.

## Collection and missingness

Part 1: Archived candidate mission, About, values, or similar pages, discovered through Wayback CDX and coded with Gemini-based evidence validation. Historical captures, model calls and review judgments are not reproducible without the original raw-source caches and external API access. Some extracted text includes navigation or marketing content even after review; the primary dataset records final selection of 140/450 usable observations. The other 310 inventory entries remain unavailable, excluded, or analytically invalid.

Part 2: Historical SEC DEF 14A proxy filings, dictionary-based topic and language-marker analysis. Seven company-years have no qualifying filing under the documented form/entity/year selection policy. A special-meeting filing was replaced with a verified annual filing for Tesla 2018; historical identifiers were repaired for BlackRock and ExxonMobil. Full raw proxy documents and retrieval caches are excluded from the compact submission archive, so Part 2 cannot be fully re-executed offline from that archive alone. The processed datasets, source URLs and analytical code are included.

Parts 3–4: The provided processed data can be used to reproduce the analysis offline. Missing values remain missing, never zero. Consecutive years are compared only when both endpoints are available.

## Method choices and limitations

Nine overlapping theme categories are used across the two data sources: innovation, integrity, people, inclusion, customer, environment, community, security/privacy, and performance. Part 3 computes the cosine similarity between Part 1's binary theme vector and Part 2's theme-mention-rate vector. The choice is transparent and scale-invariant but it does not distinguish management endorsement from legally required or shareholder-originated proxy language.

Important unresolved issues include source-genre mismatch, web-page boilerplate, incomplete and changing coverage, model-coding inconsistency for several text pairs, document-year/capture-date misalignment, and weak discriminant validity. See `docs/FINAL_AUDIT.md`. No source text, theme labels, or scores were changed during the final human-review status update. Subsequent research corrections should be versioned and followed by regeneration of downstream outputs and reports.

Part 1 uses Gemini-based LLM coding with exact-source evidence checks, followed by source-review decisions confirmed by the project owner. Part 2 uses transparent dictionary counts. Automated consistency testing is separate from the owner-confirmed source review; neither turns textual alignment into a behavioral authenticity assessment.

## Repository layout

- `config/` — fixed company roster, page registry and research configuration.
- `part1_stated_values/src/` — Wayback collection, extraction, LLM coding and review utilities.
- `part2_disclosed_priorities/src/` — SEC collection, PDF/HTML or text cleaning, metrics and reporting.
- `part3_alignment/src/` — measure construction, negative controls and sensitivity analyses.
- `part4_exploration/src/` — original exploratory question, influence diagnostics and attribution.
- `shared/` — shared validation, utilities and final package/audit command.
- `tests/` — offline unit and regression tests.
- `docs/` — decision log, dataset/source review, technical audits and limitations.

A GitHub repository was not published or connected during the audit; the supplied ZIP is a portable repository export. For all four parts' assumptions, alternative methods, and future improvements, read each implemented part's README.
