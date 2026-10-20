# Page-selection policy — provisional v1

## Scope
Use the assignment's exact 50-company sample and 2016–2024 window.
Assignment sector labels are retained; they are not a newly verified GICS classification.
This registry documents candidate pages and evidence; it does not select annual snapshots.

## Selection procedure
1. Locate official organizational identity pages (values, mission, purpose, or substantive About pages).
2. Prefer organizational coverage over products, investor news, or vacancies. Assess actual content, not URL names alone.
3. Record competing candidates, their purpose, scope, and reasons for preferring or rejecting them.
4. Verify historical captures and their identity/content before claiming historical suitability. A current official page is only a discovery lead for earlier years.
5. Prefer consistent page purpose across years. Record page-family transitions; do not silently substitute a recruitment page for a values page.
6. Use recruitment pages only as explicit provisional alternatives when they contain substantive organizational values; investigate broader identity pages before final selection.
7. Mark a company mapping reviewed only after documenting candidate research, historical evidence, scope limitations, and a selection rationale. A reviewed mapping can still have missing years.

## Evidence rules
Keep HTTP/HTTPS and trailing-slash variants distinct until archive evidence supports equivalence.
An observed timestamp establishes one capture, not continuous availability between dates.
Keep effective_from/effective_to null unless supported by explicit evidence; null means unknown.
Do not use low keyword counts to reject a page: that would select sources based on the outcome being measured.
Do not follow external links or combine several pages into one observation without documenting a revised unit-of-analysis policy.
Retain rejected candidates and their reasons as the registry grows.

## Pilot evidence
The six seed entries come from inspected pilot captures. Microsoft uses corporate-overview pages; Apple uses recruitment pages containing values language.
They remain provisional candidates, with selected_for_annual_collection=false.
An engineering-quality extraction is not a final page-selection decision.

## Completion criteria for Step 3.1
All 50 companies must have documented candidate research and an explicit outcome: reviewed mapping, unresolved case, or unavailable after documented searches.
Record evidence URLs/timestamps and historical-domain/URL transitions where supported.
Unresolved and unavailable cases must remain visible, not be filled with guessed URLs.
Annual CDX discovery, snapshot selection, and collection belong to later steps.

## Registry fields
- companies: one tracking record per assignment company; pilot_evidence_only or pending_research at initialization.
- candidates: one record per exact candidate URL; multiple candidates per company are allowed.
- page_type/page_family: source-purpose labels, not thematic classifications.
- historical_evidence: observed captures, their raw hash, and traceable pilot artifacts.
- effective_from/effective_to: unknown unless evidence establishes an interval.
- selection_status/selection_rationale: explicit provisional or reviewed selection decision.
- alternative_candidates_reviewed: initially false; the seed is not a complete discovery log.
- selected_for_annual_collection: initially false for every candidate.

## Next research batch
Revisit Microsoft and Apple alternatives first to resolve the pilot's source-purpose mismatch. Then research remaining companies in small batches, recording unsuccessful searches too.
