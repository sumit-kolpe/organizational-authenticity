# Assignment requirements

Authority: uploaded “Research Assistant Recruitment Task - Wharton-TAU Lab 2026 (3).pdf”, reviewed during planning. This checklist is a summary; the PDF remains authoritative.

## All parts
- [ ] Use the supplied 50-company roster and assignment sector labels.
- [ ] Design methods that can scale beyond the proof of concept.
- [ ] Provide all code, fully commented, in a structured repository (GitHub preferred).
- [ ] Provide one README per part: what, why, assumptions, limitations, and improvements with more time.
- [ ] Provide output data files.
- [ ] Provide one nontechnical written summary per part, at most 1–2 pages.

## Part 1
- [ ] Use Wayback CDX for annual About Us or equivalent mission/values snapshots, 2016–2024.
- [ ] Document page selection, missingness and redirect handling.
- [ ] Extract body text without navigation, footer or boilerplate.
- [ ] Use an LLM-based pipeline for prior-year change, justified value categories and linguistic shifts.
- [ ] Export ticker, company_name, sector, year, page_text_clean, changed_from_prior, theme_categories and analyst_notes.
- [ ] Document and justify coverage gaps; perfect coverage is not required.

## Part 2
- [ ] Choose one type: ESG report, sustainability report, DEI report or proxy statement.
- [ ] Collect feasible years within 2016–2024; document sources and gaps.
- [ ] Analyze language, tone and thematic changes within companies.
- [ ] Analyze cross-company and cross-sector differences.
- [ ] Examine shifts coinciding with justified external events without claiming causation.
- [ ] Justify methods and document every dataset column.

## Part 3
- [ ] Define and implement alignment using Parts 1 and 2.
- [ ] Allow variation across companies and time; do not manufacture variation.
- [ ] Report distributional properties and at least one validity check.
- [ ] Discuss at least two threats to validity.

## Part 4
- [ ] Propose and implement one additional analysis, even preliminarily.
- [ ] Report observed findings and limitations.

## Our additional safeguards
Evidence-linked coding, versioned prompts, cached calls, unit tests, explicit timing rules, and a complete 450-row inventory are our design choices, not separate verbatim PDF requirements.
