# Part 1: historical stated values, 2016–2024

## Reproduce and active version
Use outputs/review_v2/part1_values_reviewed.json as the active export. It contains
140 eligible observations across 37 companies and 83 known text comparisons.
The earlier model-supported quality check excludes ABT 2020 and invalidates comparisons
whose source text changed during review. See README_AI_REVIEW.md, ai_review_audit.json
and docs/FINAL_AUDIT.md for the review history and newly identified limitations.

In the full working project, apply_ai_review.py generates review_v2 from earlier
review/source artifacts. Collection and model coding use batch_web and analyze_values
and require archive/model access. The compact submission archive includes the final
processed outputs for offline downstream reproduction; older review inputs and raw
retrieval/model caches remain in the working project and are not duplicated. It is not
a standalone offline replay of the original collection/model calls.

## Method
Wayback CDX discovers candidate captures, prioritizing documented URL families and
captures nearest the annual target. Replay metadata and raw HTML hashes preserve
provenance. Missing URLs, failed retrieval, insufficient extracted text and exclusions
are not treated as absence of organizational values. The fixed roster retains its
assignment sectors (including Alphabet's Technology classification).

BeautifulSoup extracts numbered blocks after removing common scripts/navigation/footer
content. Pilot-informed boundaries improve some sources; generic extraction can retain
marketing/news or omit meaningful headings. Blockquotes are separated conservatively.
The nine-category taxonomy covers innovation, integrity, people, inclusion, customer,
environment, community, security/privacy/safety, and performance. Themes may overlap.
Full definitions and prompts are in gemini_pilot.py and analyze_values.py. They measure
public statements, not actual conduct or authenticity.

Gemini 3.1 Flash-Lite selects evidence IDs rather than generates quotes. Code checks
IDs and copies exact body text. Raw responses are cached using model, prompt and input
hashes. Adjacent calendar years are compared only when both are coded. Identical
extracted blocks yield false; other pairs receive LLM change and linguistic-shift
coding. Null is unknown, not unchanged. No missing years are bridged. LLM comparisons
include wording and page-composition changes; they are not pure measures of value change.

## Review decisions and remaining failures
All accepted evidence IDs/text were rechecked against saved blocks. An initial focused model-supported
review inspected ten observations (AAPL 2024, ABT 2020, CVX 2024, JPM 2024, MSFT 2024,
GOOGL 2024, NVDA 2022, WFC 2024, TSLA 2024, COP 2024). That focused earlier step was not, by itself, an independent human accuracy evaluation; the project owner subsequently confirmed completing the broader human review. Four Wells Fargo performance labels (2021, 2022, 2023, 2024) were
removed because their sole evidence was a financial-report navigation pointer. Those removals were recorded in the earlier review stage; later changes are recorded
in review_v2/ai_review_audit.json. Other labels remain model-assisted.

All 23 coding failures involve heading evidence rejected by the body's-only validator.
Examples include Oracle's genuine mission statement and Morgan Stanley's named values;
other headings are awards, amounts or article titles. Blanket acceptance or rejection
by HTML tag is therefore imperfect. These rows remain missing in the primary export;
future repair should classify semantic block roles, not relax all validation.

Ten comparison failures persist after structured regeneration. Nine contain at least
one one-sided evidence item describing an addition/removal; the original validator
required nonempty IDs on both sides. Intel 2023 has a different invalid-evidence case.
These are not proof of fabricated statements. They remain unknown pending a revised,
tested change schema with addition/deletion/substitution types and semantic review.
Neither this review nor a CSV conversion silently recovers them.

## Outputs / data dictionary
- part1_values_reviewed.csv/json: all 450 rows, required assignment fields.
- theme_evidence.csv: accepted theme, exact block text, rationale and snapshot URL.
- comparison_details.json: comparison summaries, linguistic shift, evidence, status.
- coverage_by_year.csv and review_summary.json: counts and coverage diagnostics.
- ai_review_audit.json: later review decisions and provenance.
- invalidated_comparisons.json: comparisons invalidated by source edits.
- ai_quality_review.csv: historical ten-observation model review decisions, preserved for provenance.

`page_text_clean` is candidate extracted text, not a claim of perfect cleaning;
`theme_categories` is null/blank for unusable or failed rows and a JSON list otherwise;
`changed_from_prior` is nullable boolean; `analyst_notes` contains scope, flags, concerns,
qualitative language findings and errors. `status` preserves processing status.
`eligible_for_provisional_analysis` means coding passed and is retained as the original analysis-eligibility rule; `annual_selection_final` separately records the owner-confirmed final acceptance of those 140 existing sources.
`annual_selection_final` is now true for the 140 retained usable observations and false for the 310 unavailable/excluded entries. `independent_human_review` records `completed_no_changes_owner_confirmed` on all 450 inventory rows; the owner confirmation is a review attestation, not a newly rerun model classification.
`year` is capture year, not document-authorship year. Snapshot URLs/timestamps preserve
source timing. Source texts can be displayed unchanged for many years (e.g., Alphabet).

## Findings and limits
Only 31.1% (140/450) of requested observations have validated coding. Coverage rises
from 6/50 in 2016 to 31/50 in 2024. This selection is not random; do not interpret
cross-year counts as population trends. The 83 known comparisons contain 53 changes
and 30 unchanged results (23 exact-block matches). These are observed extracted-text
comparisons; scope changes, news modules and recruitment content may drive differences.
Theme counts are multi-label frequencies, not weighted intensity or validated accuracy.

Recruitment emphasis (Apple/NVIDIA), historical-letter content (Alphabet), product/award
content (Abbott), boilerplate, model omissions and strict heading exclusions are key
validity threats. Parts 2/3 should use only matched nonmissing observations and report
coverage plus sensitivity exclusions for problematic page scopes. Never impute missing
values as zero or label missing disclosure matches as misalignment.

## Before submission / future improvements
For future work, retain any item-level reviewer notes or additional evidence when available. The current owner-confirmed review records no further edits and accepts the 140 existing usable sources. Recheck page-family comparability if new historical materials become available. Prioritize semantic heading handling, addition/deletion comparison
validation, historical URL repair and better boilerplate extraction with more time.
The regenerated one-page summary reflects the completed review status and retains the substantive data-quality limitations. Parts 2-4 use the active reviewed export as documented in README_SUBMISSION.md.


## Final audit findings
The four label/theme disagreements and the WFC/ABT source-scope concerns are detailed
in docs/FINAL_AUDIT.md. Candidate extracted text still contains navigation, footer or
promotional content in some observations, so the extraction requirement is only
partially met. Original text and coding decisions were preserved; reviewer-status fields were updated and all downstream hash-bound outputs were regenerated.
