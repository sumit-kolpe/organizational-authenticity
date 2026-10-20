# Historical website collection pilot

## Objective
Test page discovery, archived capture retrieval, text extraction,
and provenance tracking before expanding to all 50 companies.

## Companies
- MSFT — Microsoft
- AAPL — Apple

These companies are engineering test cases, not a representative
sample of all assignment sectors.

## Initial target years
2016, 2020, and 2024.

This produces six target company-year observations.
Archive availability and extraction quality are not yet verified.

## Page-selection requirement
Identify an official corporate About Us, mission, values, or
equivalent identity page. Record why each candidate is suitable.
Do not assume that a current URL existed throughout 2016–2024.

## Evidence to retain
- Original page URL and selection rationale
- CDX discovery results
- Capture timestamp and archive URL
- Retrieval outcome and redirect information
- Extracted text and quality-review notes
- Reasons for missing or rejected observations

## Pilot completion criteria
Available captures must be traceable to their sources, and extracted
text must be manually compared with archived content.
Unavailable or unusable captures must have documented reasons.

Finding all six captures is not required. The pilot must establish
whether the collection method is usable and what limitations remain.

## Later extension
Add an adjacent year where available to test consecutive-year
change detection. Broaden the sample across sectors before
finalizing the thematic coding method.

## Current status
Pilot scope defined. Historical page candidates have not yet
been selected or verified.

### Apple: inspected historical fallback candidate

- Company: Apple (AAPL)
- Original URL: https://www.apple.com/jobs/us/
- Snapshot URL: https://web.archive.org/web/20160101124138/https://www.apple.com/jobs/us/
- Snapshot timestamp (UTC): 2016-01-01 12:41:38
- Page type: recruitment / organizational culture
- Discovery route: archived Apple About page → Jobs Overview
- Inspection method: manual browser inspection
- Visible content: statements about innovation, diversity,
  inclusion, environmental efforts, and broader social purpose.
- Status: provisional fallback; not final annual selection.
- Limitation: recruitment messaging may differ systematically
  from messaging on an investor values page.
- Pending: programmatic retrieval, extraction validation,
  and assessment of page comparability across pilot years.

The Apple About capture at timestamp 20160101050609 was
inspected but not selected: it primarily contains news headlines,
contact information, and navigation links.

These observations describe website statements, not verified
corporate behavior. No LLM classification has been performed.

### Apple: 2020 About page candidate

- Original URL: https://www.apple.com/jobs/us/about.html
- Snapshot URL: https://web.archive.org/web/20200115042328/https://www.apple.com/jobs/us/about.html
- Snapshot timestamp (UTC): 2020-01-15 04:23:28
- CDX metadata: HTTP 200; text/html.
- Browser check: final URL and toolbar confirm the 2020 capture.
- Visible introduction discusses diversity, innovation,
  shared commitment, and learning from colleagues.
- Introduction visually matches the inspected December 2019
  capture; full-text equality has not been tested.
- Status: relevant organizational-culture candidate within
  a recruitment website; not final annual selection.
- Pending: extraction validation and cross-year comparability.

### Apple: 2024 careers page candidate

- Original URL: https://www.apple.com/careers/us/
- Snapshot URL: https://web.archive.org/web/20240319041941/https://www.apple.com/careers/us/
- Snapshot timestamp (UTC): 2024-03-19 04:19:41
- Discovery: following the archived redirect from
  /jobs/us/about.html at timestamp 20240319083808.
- Browser inspection: destination date and relevant text confirmed.
- Content: explicit values descriptions covering accessibility,
  education, environment, inclusion and diversity, privacy,
  racial equity and justice, and supplier responsibility.
- Status: provisional candidate for the recruitment/culture
  page family; not final annual selection.
- Comparability limitation: page structure and content scope
  differ from the 2016 jobs and 2020 About pages.
- Extraction rule: preserve substantive values descriptions;
  do not automatically collect linked pages.
- Pending: destination CDX metadata and extraction validation.

### Microsoft: inspected pilot candidates

- 2016: http://www.microsoft.com/en-us/about
  Snapshot timestamp: 20160101214549
- 2020: https://www.microsoft.com/en-us/about
  Snapshot timestamp: 20200102053409
- 2024: https://www.microsoft.com/en-us/about/
  Snapshot timestamp: 20240101141329

All three candidates were manually inspected and contain
organizational mission language. CDX records report HTTP 200
and text/html. Full-page extraction quality remains untested.

### Pilot page-selection policy

Prefer official pages containing substantive organizational
mission, purpose, values, or culture statements.

Prefer consistent page purpose across years. Record URL changes,
redirects, audience differences, and changes in content scope.
Recruitment pages are provisional fallbacks with a comparability
flag, not automatically equivalent to corporate values pages.

Exclude pages dominated by news, contact information, or navigation
when they lack substantive organizational identity statements.
Do not automatically combine text from linked pages.

A capture must fall within its target calendar year.
Verify the final replay URL and timestamp after redirects.
These manually inspected captures are discovery examples;
the reproducible annual selection rule remains to be finalized.

### Initial quality inspection: Apple 2024

- Capture: AAPL_20240319041941
- Provenance: requested URL, final URL, capture timestamp,
  and Memento-Datetime agree.
- Integrity: cached HTML checksum and byte count verified.
- Content spot-check: environmental statement found in a
  paragraph beneath the Environment heading within main content.
- Archive interface: Wayback toolbar insertion confirmed,
  including wm-ipp-base and wm-ipp elements.
- Extraction requirement: exclude archive toolbar content;
  preserve corporate headings and substantive descriptions.
- Status: initial checks passed; broader content review and
  extraction validation remain pending.

### Step 2.5: initial pilot quality assessment

All six pilot captures passed the local integrity and provenance
audit without warnings. Results are recorded in:
part1_stated_values/outputs/pilot_download_audit.json

Relevant body text was manually spot-checked in every capture:
- Microsoft 2016, 2020, 2024: organizational mission.
- Apple 2016: diversity and innovation introduction.
- Apple 2020: human-rights statement.
- Apple 2024: environmental statement.

All six contain a Wayback toolbar marker.
Raw HTML remains unchanged.

Decision: proceed to extraction trials.
These checks establish content presence, not full-page completeness.
Broader content review and extraction validation remain pending.
Apple's changing recruitment-page scope remains a comparability
limitation. Pilot captures are not final annual selections.