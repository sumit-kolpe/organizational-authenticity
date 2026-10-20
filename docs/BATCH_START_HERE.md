> Historical collection-stage notes. For the completed human source-review decision and final active outputs, see `docs/HUMAN_SOURCE_VALIDATION.md` and the project README.

# Batch collection update — Phase 3

This is an additive update for your existing Windows project. It preserves the pilot code, `page_registry.json`, and raw data. It is not a completed assignment or final verified URL registry.

## Install

1. Extract the update ZIP to a temporary folder.
2. Copy its `config`, `docs`, `part1_stated_values`, and `tests` folders into your existing project root, alongside `requirements.txt`. Merge folders. The new filenames should not replace earlier pilot scripts.
3. Open the project terminal with the existing `.venv` active. No new dependency is required; this module uses the installed Beautiful Soup and Python's standard library.
4. Run:

```bat
python -m part1_stated_values.src.batch_web --plan
python -m unittest discover -s tests -p "test_batch_web.py"
python -m part1_stated_values.src.batch_web --run
```

`--plan` must report 50 companies × 9 years and no network requests. Tests use synthetic examples, not company observations. The run is resumable: use the same command after an ordinary interruption. Keep the machine awake and the terminal open while collecting. Do not run several collectors simultaneously.

The package includes the real Microsoft 2020 smoke-test cache and its 450-row inventory (one candidate, 449 not attempted), so the full run can reuse that retrieval. These are clearly labeled candidate data, not fabricated placeholders or final research findings.

The full run is budgeted at 1,500 HTTP requests, paced at least three seconds apart, with bounded retries for transient failures. Actual duration depends on archive response times and coverage; no guaranteed completion time. HTTP 403/429 stops the entire run. Investigate restrictions or wait before retrying; do not loop aggressively or change identities to bypass access controls.

For a smaller optional run:

```bat
python -m part1_stated_values.src.batch_web --run --tickers MSFT AAPL NVDA --years 2020 2024
```

After resolving an error, retry unresolved rows with:

```bat
python -m part1_stated_values.src.batch_web --run --retry-failed
```

If the report specifically says `page_cap_reached`, increase `--max-pages`, for example to 40, with `--retry-failed`. A page cap never establishes archive absence. Successful candidate rows are not recomputed. Treat the manifest as frozen for a run: changing URLs, priorities or extraction code requires a separately versioned run directory or explicitly backed-up reset, not silently mixing versions. Contact your implementation partner before changing these settings.

## Files to examine and return

- `part1_stated_values/outputs/batch_v1/coverage_summary.json`
- `part1_stated_values/outputs/batch_v1/company_year_inventory.csv`
- `part1_stated_values/outputs/batch_v1/company_year_inventory.json` (includes replay attempts)
- `part1_stated_values/data/batch_v1/captures/` (downloaded HTML, provenance JSON, candidate TXT)
- `part1_stated_values/data/batch_v1/cdx/` (full paginated discovery responses/checkpoints)

First send the three output reports. If text review is needed, send the relevant capture files, or ZIP the whole `batch_v1` data directory if manageable. Do not send `.env`, API keys or your `.venv`.

## What each function does

- `Client.get`: sends identified, paced archive requests; rejects redirects and access restrictions; retries transient failures within a request budget.
- `parse_cdx`: validates returned rows and continuation tokens. A JSON `[]` is distinct from an empty, undecodable HTTP response.
- `discover`: queries each URL for 2016–2024, follows continuation keys, and checkpoints every successful page. Raw response files remain traceable by hash.
- `ordered_candidates`: restricts a company's candidates to the requested year, excludes known unsuitable captures, and ranks by distance from July 1 at noon UTC (ties favor earlier timestamps). Direct HTML and revisit records may be tried; redirects and known error records are not treated as content.
- `replay`: downloads the archived page frame, validates capture timestamp when supplied in replay/Memento metadata, caches with a URL-specific key, and writes candidate text.
- `extract`: removes archive tools and obvious boilerplate and extracts headings/paragraphs. It retains substantive paragraphs inside navigation containers because the Apple pilot demonstrated these can contain culture statements. It does not yet implement a validated language or topical-relevance classifier.
- `write_outputs`: saves the complete 450-row inventory after each company-year so interrupted work can resume.

## Selection and measurement policy

The existing registry remains authoritative pilot evidence. The separate `batch_page_candidates.json` adds discovery leads for all 50 companies. New URLs were identified from official-site search or inspection; this does NOT establish their historical existence or suitability. See `batch_sources.md`.

MSFT retains its provisional values-overview family. Apple retains its provisional careers family, with documented source/audience differences. The collector ranks URLs within each family first, then timestamps within each URL. It tries at most three captures per company-year, stopping at a candidate without automated flags. This is a resource-bounded candidate policy, not proof the best historical page has been found. Failed attempts and incomplete inventories remain visible.

Berkshire Hathaway's owner-manual lead is disabled because treating that document as an About/values webpage requires a justified source-type decision. Its nine rows remain `source_selection_pending`. NVIDIA's 2016 brand-configuration capture is explicitly excluded. Alphabet parent-company content must not be replaced silently with Google's values. Meta historical Facebook URLs, and other companies' historical page moves, remain repair work if this first pass lacks coverage.

The date reference is a documented implementation choice, not a requirement of the assignment. All rows keep `annual_selection_final=false` and `manual_review_status=pending`. Before LLM scoring, review relevance, extraction completeness, language, page-family consistency and timing against the chosen disclosure-year policy. These snapshots capture a point in time, not full-year messaging.

## Status interpretation

| Status | Meaning |
|---|---|
| `not_attempted` | No company-year processing completed yet. |
| `source_selection_pending` | No enabled suitable URL lead; source review needed. |
| `discovery_unresolved` | No candidate found while discovery remains incomplete or failed. |
| `no_records_for_queried_urls` | Completed queries returned no records for those URLs/year; NOT proof no historical company page exists. |
| `no_eligible_capture_returned` | Records exist but none satisfy direct-HTML/revisit eligibility. |
| `replay_failed` | Attempted eligible captures failed download/validation. |
| `candidate_flagged` | Text or wrapper retrieved but quality concerns need resolution. |
| `candidate_ready` | Candidate passed limited automated screening; manual relevance/quality approval is still pending. |

`discovery_complete=false` remains important even if candidate text was found. The CSV does not contain LLM themes, change labels or authenticity scores. Missing text is not a negative thematic finding. Generic extraction may omit relevant content or retain boilerplate; it does not supersede the manually refined pilot outputs.

## Deadline priorities and next batch

1. Run this collection batch; summarize coverage and repair high-impact URL families with bounded effort. Do not spend hours forcing a single unavailable year.
2. Finalize an interpretable taxonomy and run a small evidence-grounded LLM pilot, then cached Part 1 classification. LLM provider/model and a spending limit still need to be chosen.
3. Implement the chosen disclosure source (proxy statements are provisional), with fiscal/publication dates and matched comparison policy; apply the same theme definitions.
4. Compute an alignment baseline and robustness check, descriptive statistics, and one exploratory analysis. Do not infer behavior or causal effects from language similarity.
5. Produce four READMEs, output datasets and four short substantive summaries, clearly distinguishing missing coverage from findings.

The uploaded code is enough for this batch. The original assignment PDF is still needed for an authoritative final requirements audit if it is not readable in this conversation. An LLM API key must be configured locally, never pasted into chat. SEC access will require a locally configured identifying User-Agent for that later collector.
