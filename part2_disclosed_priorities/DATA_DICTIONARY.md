# Part 2 output schema

JSON is authoritative for nested structures. CSV stores nested dictionaries/lists as JSON strings. Missing analyzed fields on unavailable documents mean unavailable, not zero. All rates use alphabetic word tokens from the full extracted proxy. Counts mean dictionary matches, not unique propositions.

## disclosure_metrics.json / disclosure_metrics.csv: every column

| Column | Type / interpretation | Why retained |
|---|---|---|
| ticker | string, assignment ticker | Stable join key; BRK.B retained |
| company_name | string | Readable assignment identity |
| sector | string, assignment sector | Sector comparison |
| year | integer, filing calendar year | Annual join; not fiscal year |
| status | string, downloaded or missing/failure reason | Separate availability from zero mentions |
| filing_date | ISO date or null | Document timing |
| report_date | SEC report/meeting date or null | Preserve source metadata; not silently used as year |
| accession | SEC accession string or null | Unique filing provenance |
| source_url | SEC document URL or null | Retrieve and inspect evidence |
| cik | integer SEC entity identifier or null | Entity resolution and history |
| candidate_count | integer or null | Detect ambiguous source selection |
| annual_meeting_marker | Boolean or null | Heuristic annual-meeting phrase flag; not verification |
| selection_warning | string or null | Record source-selection caveats/override |
| entity_scope_warning | string or null | Current versus historical CIK limitations |
| word_count | integer, available documents only | Rate denominator |
| character_count | integer | Extraction size diagnostics |
| themes | mapping of nine theme names to metrics | Shared dimensions for Parts 1-3 |
| language | mapping of commitment, uncertainty, obligation, covid to metrics | Limited language/tone/event indicators |
| total_theme_hits | integer, sum of theme counts | Profile normalization and diagnostics |
| extraction_warning | string | Full-document voice/boilerplate limits |
| text_sha256 | SHA-256 string | Detect changed cleaned source text |
| analysis_status | string | Lexically analyzed pending review versus unavailable |

For every theme, `count` is a nonnegative integer, `per_1000_words` is `1000*count/word_count`, and `share_of_theme_hits` is `count/total_theme_hits` (null if the total is zero). Theme names: innovation, integrity, people, inclusion, customer, environment, community, security_privacy, performance. Every language category has `count` and `per_1000_words`, without a share field.

## Supporting data tables

* `theme_evidence.csv`: ticker and year identify a document; source_url gives provenance; theme identifies the dictionary category; matched_term gives the literal normalized match; normalized_character_offset is the starting character in lowercased whitespace-normalized text, not raw HTML; excerpt gives nearby normalized text. At most the first five matches per theme are retained, not a random validation sample.
* `within_company_changes`: ticker, sector, year and previous_year identify an adjacent pair; theme_rate_changes and language_rate_changes map categories to current minus prior rates; interpretation records the descriptive/noncausal scope.
* `sector_year_themes.csv`: sector, year and theme identify a cell; n_documents is the denominator; mean_per_1000_words is the unweighted document mean, null when none are available.
* `pandemic_paired_comparison`: ticker and sector identify a firm; pre_years and post_years specify 2018,2019 and 2021,2022; theme_rate_changes contains post-period mean minus pre-period mean per theme; covid_marker_change applies the same subtraction to COVID rates; caveat records timing and confounding. All four filings are required.
* `coverage_summary.json`: total_company_years is panel size; statuses counts inventory states; analyzed_documents and analyzed_companies count successful analysis; adjacent_year_pairs counts consecutive available pairs; pandemic_complete_company_pairs counts companies with all four event-window years; multiple_proxy_candidate_years counts inventory rows with more than one candidate; missing_is_not_zero states missingness policy; method describes the lexical and review scope.

## Collection inventory and policy

`inventory.json` includes identifiers above plus form (DEF 14A), manual_review_status (pending), sec_entity_name, candidates, raw_file/text_file (project-relative saved paths), raw_sha256/text_sha256, characters, and annual_meeting_marker. Candidate entries preserve accessionNumber, filingDate, reportDate, form and primaryDocument from SEC submissions. Optional notes/error explain unresolved mapping or failed retrieval. repair_reason describes targeted v2 correction. Paths may contain Windows backslashes and are normalized by analysis code when read.

`replaced_baseline_rows.json` preserves the 19 inventory records selected for the repair, including the XOM year that remained missing. `discovery/*.json` retains cik, sec_name, former_names and the eligible filing list. `run_policy.json` records version, roster/lexicon hashes, baseline inventory hash, CIK overrides, annual proxy override and selection policy. These support reproducibility; they are not analysis variables. `run_report.md` is a generated narrative, and Part2_Summary.pdf is the nontechnical summary.
