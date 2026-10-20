> Final version: use outputs/proxy_v2. BLK uses historical CIK 1364742 and XOM uses 34088 for the study window; TSLA 2018 uses annual accession 0001564590-18-009339. All other years keep the filing-calendar-year selection rule. The v1 description below records the original design; these explicit overrides supersede its current-CIK and earliest-filing defaults. See docs/FINAL_AUDIT.md and DATA_DICTIONARY.md.

# Part 2: disclosed priorities in definitive proxy statements

## Why this source
The assignment permits one consistent type among ESG, sustainability, DEI and proxy
reports. This pipeline chooses SEC Form DEF 14A definitive proxy statements. Official
2024 filings were verified for Microsoft, JPMorgan and Chevron. Public SEC submissions
history covers recent and older index files without an API key. This supports one
consistent collection procedure across the roster. It does NOT establish complete
historical coverage for all 50 companies before the run.

## Selection and dates
Read the assignment's existing config/companies.csv unchanged. Resolve current ticker
to SEC CIK (normalize BRK.B to BRK-B for mapping only), then retrieve recent submissions
and all historical index files overlapping 2016-2024. Select exact form DEF 14A, not
DEFA14A, PRE 14A, amendments or other types. Deduplicate by accession number. Select
the earliest filing in each calendar year, breaking ties by accession; retain every
candidate in inventory/discovery JSON. The fixed rule avoids cherry-picking based on
content but can select a special-meeting statement rather than the annual proxy.
Multiple candidates and lack of verified annual-meeting status are review flags.
The annual_meeting_marker is a text heuristic, NOT verified document classification.

`year` is filing calendar year. `report_date` is preserved but NOT treated as a fiscal
year. Proxy language frequently discusses preceding fiscal periods. Part 3 must check
filing date against website capture date or report same-year mismatch as a limitation.
Do not describe the whole panel as contemporaneous fiscal-year priorities.

Current CIK mapping does not reconstruct reorganizations or predecessor entities.
Broadcom, BlackRock and other entity-history gaps may require manual research. A year
without a matching filing for the queried CIK is not proof that the economic firm had
no disclosure. The collector does not invent predecessor mappings or silently splice
entities. Mapping-unresolved and unsupported-format rows remain missing.

## Collection and reproducibility
One request per second; bounded 5xx/network retries; stop on access restrictions.
Contact identification is required through SEC_USER_AGENT. URLs, raw response hashes,
retrieval timestamps, response type and archive accessions are preserved. Successful
files are cached and reused. Raw HTML/text and cleaned text get separate hashes.
The run policy hashes the fixed roster and lexicon. Changed inputs require a versioned
new run directory; do not edit policy hashes to force mixed runs. Completed downloaded
rows are not repeatedly fetched. Discovery/download failures can retry on resume.

## Extraction
BeautifulSoup removes scripts/styles and hidden iXBRL metadata; remaining visible text
is extracted, INCLUDING plain div content (important after the Part 1 Chevron omission).
Full proxy documents and tables are retained, not only ESG sections. Numeric tables,
repeated headings, footnotes and complex formatting may affect rates. Documents under
1,000 extracted word-like tokens are flagged. Extraction is not claimed perfect.
PDF primary documents are marked unsupported rather than silently converted or omitted.

## Lexical method
No LLM calls are needed. A versioned, hand-specified dictionary operationalizes the nine
Part 1 theme labels. Specific phrases reduce ambiguity: e.g., environmental rather than
generic sustainable growth; customer satisfaction rather than every occurrence of client.
Case-insensitive word-boundary matching is applied after whitespace normalization, with
longest alternatives first inside each category. Matches can overlap across categories.
No stemming, negation, speaker attribution or semantic disambiguation is performed.

Each theme receives a count, mentions per 1,000 alphabetic word tokens, and share of all
theme hits. Zero means no dictionary match in an available document; unavailable text
is missing. The full document length is the denominator, including table words. Five
matched excerpts per theme per document are exported for checking. They are diagnostic
examples, not a representative sample of all theme occurrences.

Proxy statements combine management statements, shareholder proposals, opposition to
proposals, legal requirements, biographies and compensation discussion. These metrics
measure lexical disclosed attention, NOT managerial endorsement, spending, behavior or
authenticity. Performance/governance language is structurally prominent in proxies.
Part 1 LLM coding and Part 2 lexical measures have different error profiles: alignment
needs explicit method-sensitivity checks rather than treating them as identical measures.

## Language and change analyses
Commitment, uncertainty and obligation word rates provide limited language/tone proxies.
They are NOT validated positive/negative sentiment measures; terms such as may can have
other meanings. COVID markers are counted separately. Adjacent calendar years are
compared within firms only when both documents are available. Company-level metrics
support cross-company comparisons; sector-year means are unweighted document means,
with denominators reported. Changes in sample composition can confound pooled trends.

The event comparison uses WHO's 11 March 2020 pandemic characterization as background:
compare firm means for 2018-2019 versus 2021-2022, excluding transition year 2020 and
requiring all four years. Report lexical change and COVID-marker change, not causal
effects. Other trends, reporting changes, proxy topics and timing are uncontrolled.

## Output dictionary
inventory.json: all 450 roster rows; status, current CIK/entity, candidate filings,
selection warnings, dates, accession, URLs, raw/text paths and hashes.
disclosure_metrics.json/csv: roster identifiers plus word_count, character_count,
themes (count/rate/share), language markers (count/rate), total_theme_hits and analysis
status. Nested values are JSON strings in CSV and proper objects in JSON.
theme_evidence.csv: category, matched term, offset in lowercased normalized text,
context excerpt and source URL; offsets do not refer to original HTML.
within_company_changes: adjacent-year theme and language-rate differences.
sector_year_themes.csv: theme mean rate, sector/year, number of available documents.
pandemic_paired_comparison: firm-level post-minus-pre theme and COVID rates; requires
2018, 2019, 2021, 2022. Empty output means insufficient matched coverage, not no effect.
coverage_summary.json: collection statuses, analyzed counts and comparison denominators.
run_report.md: factual short report generated only from actual outputs; final submission
narrative and figures will follow substantive review of the actual results.

## Validation and remaining work
Ten offline tests cover boundaries, whitespace, empty-text missingness, div/hidden text,
column lengths, historical-file reading/deduplication, contact/budget/host checks and
no bridging of missing years. The user completed collection and uploaded proxy_v2 outputs; 443 documents were analyzed. Raw proxy files were not supplied for this audit.
Results remain provisional pending source identity, extraction and lexical precision
review. Manually inspect excerpts from several sectors, multi-candidate years, and
predecessor gaps. Document dictionary false positives/negatives and report sensitivity
to source selection and dictionary definitions. Do not treat missing observations as
zero in the alignment index.

## Official references (checked 19 October 2026)
- SEC API documentation: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC fair access: https://www.sec.gov/about/developer-resources
- Microsoft 2024: https://www.sec.gov/Archives/edgar/data/789019/000119312524242883/0001193125-24-242883-index.html
- JPMorgan 2024: https://www.sec.gov/Archives/edgar/data/19617/000001961724000273/0000019617-24-000273-index.htm
- Chevron 2024: https://www.sec.gov/Archives/edgar/data/93410/000119312524091327/0001193125-24-091327-index.html
- WHO event: https://www.who.int/news-room/speeches/item/who-director-general-s-opening-remarks-at-the-media-briefing-on-covid-19---11-march-2020


## With more time
Separate management voice from proposals and boilerplate, validate dictionaries on stratified samples, verify annual-meeting status, and resolve predecessor/form gaps. Build semantic measures only after source selection and timing are reliable.
