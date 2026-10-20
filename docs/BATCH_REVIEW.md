> Historical collection-stage notes. For the completed human source-review decision and final active outputs, see `docs/HUMAN_SOURCE_VALIDATION.md` and the project README.

# Batch review and next actions

The uploaded archive has 215 HTML/metadata/text triplets. All HTML SHA-256 hashes
match their metadata. All 193 selected texts match their inventory hashes after
normalizing Windows line endings and removing the writer's terminal newline.
These checks establish file integrity, not substantive suitability.

The 450-row inventory has 180 screened candidates, 13 flagged candidates,
223 rows with no records for queried URLs, 7 without eligible captures, 18 replay
failures, and 9 unresolved source choices. The 193 selections have 158 exact
unique texts. Do not treat duplicated statements as independently written each year.

Focused content inspection (not a full manual review):
- Microsoft 2016: values paragraphs are present, but product menus and footer links
  contaminate the extract. Its clean-body extraction still needs correction.
- Apple 2016 and 2024: substantive corporate/recruitment content; source scope and
  changing page emphasis limit historical comparability.
- NVIDIA 2019 and 2022: substantive culture paragraphs followed by navigation.
- Amazon 2020 and 2024: primarily article-link hubs, with a short Day 1 statement.
  Leadership Principles links must not be coded as if the linked content was read.
- Alphabet 2016 and 2024: founding-letter language remains on the captured pages.
  Capture year measures displayed content, not original authorship or fresh commitments.

Priority repairs, grounded in saved evidence:
1. Broadcom: failed replays in 2019–2024 report redirects to
   https://www.broadcom.com/company/about-us/ (also without a terminal slash).
   Discover these exact variants as NEW source candidates in a versioned collection;
   preserve the original failed attempts. Do not silently follow to a different year.
2. Amazon: extract the actual Leadership Principles href from archived HTML and
   discover that destination; compare body content before preferring it.
3. Microsoft/NVIDIA: improve body-region extraction using actual HTML structure.
4. Target, Phillips 66 and Lilly: investigate empty extractions before more LLM calls.
5. Early years: broaden historically evidenced URLs; absence for current URLs is
   not evidence that a company had no values page.

No repaired captures have been downloaded in this package. No registry decision
or final annual selection has been changed. The collection manifest hash guard
is intentional: do not edit the existing manifest and rerun over batch_v1.

# Pilot method

The pilot deliberately samples contaminated navigation, recruitment, a link hub,
a repeated historical letter and a nontechnology observation. It is diagnostic,
not a representative accuracy evaluation. The nine-category taxonomy is a proposed
coding framework, chosen to cover recurring organizational priorities. Categories
may overlap. Absence of a code means no supported statement in this source, not
absence of a real organizational value. It is not yet frozen for Parts 1 and 2.

The program verifies exact source quotations and allowed labels. This does NOT
verify semantic correctness: a human must check whether each quote actually supports
the category and comes from corporate content rather than navigation. Review all
six responses; record corrections before scaling. The source text is deliberately
not silently rewritten for this diagnostic pilot.

Cache keys include model, complete prompt/taxonomy and text. Raw responses are
retained. Failed validations are not automatically resubmitted. No API key is
written to disk. Six generation requests maximum per first run, at ten-second
intervals; model listing uses separate metadata requests. No automatic paid-model
fallback or billing change. The program cannot verify your billing settings: keep
your confirmed free-tier project unchanged. Model availability does not prove
free-tier eligibility; use the exact model tied to your displayed free quota.

API implementation reference: https://ai.google.dev/api/generate-content
and https://ai.google.dev/api (accessed October 19, 2026 UTC).

This is only a content-classification pilot. Prior-year change and linguistic-shift
analysis, final body cleaning, coverage repair, full LLM coding, Parts 2–4, and the
four submission summaries remain outstanding. Do not submit pilot outputs as the
completed assignment.
