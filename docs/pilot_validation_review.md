> Historical collection-stage notes. For the completed human source-review decision and final active outputs, see `docs/HUMAN_SOURCE_VALIDATION.md` and the project README.

# Pilot content review

Review date: 2026-10-17 (America/New_York; corresponding UTC date 2026-10-18).
Validation run reviewed: `2026-10-18T02:11:34.003257+00:00`; validator `pilot_validation_v1`.

## Scope and decision

All six captures are acceptable for the limited engineering pilot, with the limitations below. This does not approve them as final annual observations, establish historical completeness, validate LLM classifications, or authorize an unattended 450-observation extraction run.
Technical result: five passes, one warning, no failures. Source HTML and extracted text were inspected during Step 2.6. This record binds those reviews to the current report hashes. Checkmarks document inspection and recording of concerns, not proof that no unknown content is missing.
Five cleaned-text uploads were directly hashed and matched to this report. Apple 2024 was regenerated from its uploaded raw HTML using bs4_main_baseline_v3: the normalized text hash and the hash after Windows CRLF serialization both matched the report. Its original download JSON was not supplied for this regeneration; a minimal extraction input containing the report source hash and snapshot URL was used only for that check.
No signed human approval is inferred from running the validator. Researcher acknowledgement appears at the end.

## MSFT_20160101214549

Reviewed clean-file SHA-256: `1b63500b99e487809dd08034e70546c452818255b608ec51d82032f616c94940`
Normalized-newline text SHA-256: `7b1d125589ef4eb5d21c438e0c95e551121f5221a01eeddcc4abb6174a9a72f8`
Raw HTML SHA-256: `63f10acf4619006f22483223cd56318c9f37f0707dedb824b0796af29953a6a2`
Cleaned text: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20160101214549.txt`
Extraction metadata: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20160101214549.json`
Source: https://web.archive.org/web/20160101214549/http://www.microsoft.com/en-us/about
Extraction version: `microsoft_pilot_cleanup_v1`; characters: 2778; technical status: `pass`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved the mission, strategy, ambitions, all linked section labels, and descriptions, including Trustworthy Computing and Global diversity and inclusion. The automatic candidate lost contextual section labels.
Cleanup and remaining content: No additional main-region text was deleted. Directory content, investor/contact prompts, and mixed promotional descriptions remain intentionally. This is a broad corporate overview, not a values-only page.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

## MSFT_20200102053409

Reviewed clean-file SHA-256: `f67c122bc91e46ac6181fc77e17357a25f2724a4e97b7dd510448910126a1789`
Normalized-newline text SHA-256: `c6854b277d565cfb5f13df7fce118b08c0cdcc3e8551bc04a76a8ca1d2ca22b9`
Raw HTML SHA-256: `095f32b7f64c18b4898e5419edbbfade3a41560876329de96c065ca6df54b893`
Cleaned text: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20200102053409.txt`
Extraction metadata: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20200102053409.json`
Source: https://web.archive.org/web/20200102053409/https://www.microsoft.com/en-us/about
Extraction version: `microsoft_pilot_cleanup_v1`; characters: 1264; technical status: `pass`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved the mission, company/people/value headings, corporate-social-responsibility passage, Story Labs description, and AI passage.
Cleanup and remaining content: Removed seven standalone call-to-action labels, the contact/support block, and the social-follow block. Remaining overview and project descriptions mix substantive and promotional language. Scope differs from 2016.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

## MSFT_20240101141329

Reviewed clean-file SHA-256: `2dbfb31ff9df8a4e252148fc768a509838c6323c9b0374290f8116e394aed450`
Normalized-newline text SHA-256: `030980b25b7cbec230f4c6f9683fdfc857ac2148a1e05b7798488f5be23c85ec`
Raw HTML SHA-256: `dd360d099732a862ff764aae9898cbcd9247d5340f445b74868d72fc24be484a`
Cleaned text: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20240101141329.txt`
Extraction metadata: `part1_stated_values/data/processed/microsoft_pilot_cleanup/MSFT_20240101141329.json`
Source: https://web.archive.org/web/20240101141329/https://www.microsoft.com/en-us/about/
Extraction version: `microsoft_pilot_cleanup_v1`; characters: 1225; technical status: `pass`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved the mission, corporate-social-responsibility passage, Stories and AI descriptions, and the carbon-negative-by-2030 statement as a historical corporate claim, not verified performance.
Cleanup and remaining content: Removed seven standalone call-to-action labels, the contact/support block, and the social-follow block. Remaining overview and project descriptions mix substantive and promotional language. Scope differs from 2016.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

## AAPL_20160101124138

Reviewed clean-file SHA-256: `e1224793863183aa02ed36cb7feff786a1e5edc4bdf9bc80d193e9886b1dd700`
Normalized-newline text SHA-256: `2f13b2c1d85b1bac9be55a969238214b37a712d823fd3dee5ffa1be4b59a23a6`
Raw HTML SHA-256: `815fc3f793039ed335db686664a4b3e447adab9a9249d0a0fe63b6ac6a3a209e`
Cleaned text: `part1_stated_values/data/processed/apple_2016_cleanup/AAPL_20160101124138.txt`
Extraction metadata: `part1_stated_values/data/processed/apple_2016_cleanup/AAPL_20160101124138.json`
Source: https://web.archive.org/web/20160101124138/https://www.apple.com/jobs/us/
Extraction version: `apple_2016_narrow_cleanup_v1`; characters: 924; technical status: `pass`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved the opening diversity/innovation/environment paragraph, Corporate/Retail/Student Programs headings and descriptions, retail culture language, and closing inclusion statement. Automatic extraction omitted relevant culture language.
Cleanup and remaining content: Removed one job-search banner and four Learn more labels. Kept meaningful descriptions embedded in nav and linked cards. Recruitment framing remains; do not treat all retained text as a value assertion.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

## AAPL_20200115042328

Reviewed clean-file SHA-256: `d9d36aa73802ac5b05ab6fc08ddc096ba72625c2fe4af4f4bd8145d631bc8946`
Normalized-newline text SHA-256: `a1e4f5d3884b9a33d152235ed315846c71ffff4e8bf9b04f8c4f908f5b26c2a8`
Raw HTML SHA-256: `5e36c8eda5b74172200bd754da85395c79ed3f59ba2e86de48a520965e1f28be`
Cleaned text: `part1_stated_values/data/processed/apple_2020_cleanup/AAPL_20200115042328.txt`
Extraction metadata: `part1_stated_values/data/processed/apple_2020_cleanup/AAPL_20200115042328.json`
Source: https://web.archive.org/web/20200115042328/https://www.apple.com/jobs/us/about.html
Extraction version: `apple_2020_narrow_cleanup_v1`; characters: 4906; technical status: `pass`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved main paragraphs and headings, three quotation attributions and roles, the 800+ engineers claim, closing diversity and employment claims, benefits eligibility footnote, and one copy of each of six employee captions.
Cleanup and remaining content: Removed one gallery-navigation copy only after matching its six labels to retained captions; removed two Learn more labels; inserted a space at the inspected products.They HTML boundary. Retained gallery/location captions and promotional claims are context, not automatically thematic evidence.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

## AAPL_20240319041941

Reviewed clean-file SHA-256: `197f72872b4bb6d53624949ae313210ed1c9b382b484ff609db817223d2f8884`
Normalized-newline text SHA-256: `e789d93b37324bdbaa2ad0df363491d8bf82a31bc0570b017c1abc5d6ed7da33`
Raw HTML SHA-256: `0a8d4ba2456a51c34910a9c4d6ebc4f9252e36783f51df5873db5685361f7953`
Cleaned text: `part1_stated_values/data/processed/extraction_baseline/AAPL_20240319041941.txt`
Extraction metadata: `part1_stated_values/data/processed/extraction_baseline/AAPL_20240319041941.json`
Source: https://web.archive.org/web/20240319041941/https://www.apple.com/careers/us/
Extraction version: `bs4_main_baseline_v3`; characters: 1491; technical status: `pass_with_warnings`.

- [x] Source HTML region and cleaned text compared through inspection and code-assisted preservation checks.
- [x] Relevant statements, headings, attributions, and qualifying notes checked for this capture.
- [x] Implemented removal rules inspected; remaining irrelevant or mixed-purpose text noted below.
- [x] Missing/truncated/dynamic-content concerns recorded below.
Outcome: acceptable for pilot, with limitations.
Preservation evidence: Preserved seven values headings and descriptions, culture statements, employee quotations, and their attributions. Automatic extraction omitted attributions and retained values-card navigation.
Cleanup and remaining content: Removed 14 navigation/video labels and two inspected vacancy/category blocks. Kept surrounding recruitment/culture prose. Exclusion of job-listing blocks differs from older Apple pages, which retain descriptions containing culture language; scope harmonization is still needed.
Archive limitation: available HTML only. No JavaScript execution, CSS visibility assessment, complete rendered-page audit, or proof that all original content was archived. Recorded checksum consistency cannot resolve those gaps.

Warning disposition: the original extraction metadata lacks output_sha256. The current content was corroborated by regeneration and both reported hashes, but no retroactive claim is made about earlier file integrity. Keep the warning in the technical report. Add output hashing to the future common extractor; the current reviewed hash provides a reference for this artifact.

## Pilot-wide decisions

- [x] Page-purpose and extraction-scope differences documented: Apple uses recruitment pages; Microsoft uses corporate overview pages. Apple URL families and content structures change across the pilot years. Microsoft 2016 retains directory content that later cleanup excludes in part.
- [x] Review identified as source inspection assisted by code, not independent blind validation. Rules and diagnostic phrases were developed on the inspected examples, so this is in-sample engineering verification.
- [x] Required refinements before broad scaling identified below. Capture-specific scripts remain prototypes.

### Next actions and limits

1. At Phase 3 page mapping, record page purpose, URL family, effective dates where verified, and selection rationale. Investigate more comparable identity/values pages before freezing a company-wide policy.
2. Define a common inclusion policy for substantive value/culture passages and contextual text. Preserve the broad cleaned layer; apply later thematic coding consistently. Do not interpret differing word counts as changes in values.
3. Consolidate proven rules into a configurable extractor with explicit per-layout exceptions and review flags, rather than adding a separate script for every future capture. Save output hashes and source evidence consistently.
4. Finalize and document annual snapshot reference-date, tie-breaking, retry, fallback, and no-usable-capture rules before selecting final annual observations. All six current captures remain discovery-pilot selections.
5. Add an adjacent-year example before validating changed_from_prior. The 2016/2020/2024 pilot cannot establish consecutive-year behavior.
6. Evaluate the common extraction policy on previously uninspected pages from additional companies/layouts before unattended scaling. Include manual review; do not claim accuracy from these six tuned examples.
7. Keep communications/disclosures distinct from actual behavior. These texts support claims about messaging, not verified ethical or environmental performance.

### Status bookkeeping

The JSON validator intentionally reports manual review as not_assessed_by_script and Step 2.7 as pending sign-off. This Markdown is the separate review record; editing it does not change JSON fields. Do not edit generated JSON to manufacture a pass. Regenerating the validator preserves this worksheet. If cleaned text changes, compare hashes and renew the affected review.
Step 2.7 evidence: technical validation and code-assisted content review documented. Researcher acknowledgement of this review and its limited pilot scope remains pending. Broader methodological refinements are explicitly carried forward; they are not represented as completed.

### Researcher acknowledgement

- [x] I have read this record, checked it against the work performed, and accept its limited pilot conclusion and outstanding actions.
Researcher name: Sumit Pradeep Kolpe
Acknowledgement date: 2026-10-17 
