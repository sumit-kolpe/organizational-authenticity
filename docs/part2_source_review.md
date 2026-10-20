# Part 2 source review: initial 426-document run

The baseline contains 450 company-year records, 426 analyzed documents (94.7%), 48 companies, 376 adjacent-year pairs and 45 complete pandemic-window company comparisons. Review used uploaded output tables and selected official SEC filings; raw local documents were not included in the upload. This earlier targeted model-supported assessment preceded the owner-confirmed completion of human source review. It was not intended to replace the full dataset review.

## Corrections

* BLK: historical CIK 1364742 replaces the current ticker mapping for the 2016–2024 retrieval window. The official 2024 DEF 14A identifies BlackRock Inc. under that CIK: https://www.sec.gov/Archives/edgar/data/1364742/0001193125-24-087282-index.htm
* XOM: historical CIK 34088 replaces the current ticker mapping for that window. Official 2024 proxy: https://www.sec.gov/Archives/edgar/data/34088/000119312524092545/0001193125-24-092545-index.htm
* TSLA 2018: select annual proxy accession 0001564590-18-009339, replacing the earlier special-meeting proxy. Annual source: https://www.sec.gov/Archives/edgar/data/1318605/000156459018009339/tsla-def14a_20180606.htm . Original special meeting: https://www.sec.gov/Archives/edgar/data/1318605/000119312518035345/d524719ddef14a.htm

The repair keeps all original candidate metadata, a copy of replaced baseline rows, separate v2 outputs and the unchanged lexicon. Other years continue using earliest DEF 14A by filing calendar year. The CIK override is a documented retrieval decision, not a general assertion that corporate boundaries never changed.

## Remaining limitations

The other six missing records are AAPL 2018, AVGO 2016–2018, MCD 2022 and SBUX 2024. They remain missing, not zero. AAPL has two 2017 filings, including one dated December 27 for a February 2018 meeting; the filing-year policy must not silently shift this document into 2018. Predecessor histories and other gaps need separate evidence before filling.

Four baseline company-years have multiple candidates: AAPL 2017, NVDA 2022, TSLA 2018 and TJX 2018. Only the demonstrated Tesla mismatch is overridden here. Annual-meeting text markers are heuristics, not validation.

Full-document lexical counts mix management statements, shareholder proposals, board composition, compensation and repeated tables of contents. Evidence excerpts show board diversity and geographic diversity can contribute to the same inclusion category; climate proposals opposed by management can still contribute environment mentions. Rates describe mention frequency and cannot establish endorsement, behavioral authenticity, or validated sentiment. No dictionary is changed retrospectively in this repair.

Pandemic comparisons are descriptive paired changes, not causal estimates. Part 3 must account for the differing genres and coverage of Part 1 and Part 2, and avoid coding missing observations as zero.

## Assistance-reference tracking

New authored references occur in `START_PROXY_REPAIR.md`, `docs/part2_source_review.md`, and `part2_disclosed_priorities/src/proxy_review.py`. Generated v2 coverage_summary.json and run_report.md also describe the method/validation status. Run the included scanner on the merged project for a current inventory; the scanner itself mentions these terms. This list does not claim an exhaustive review of older PDFs.
