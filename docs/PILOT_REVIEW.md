> Historical collection-stage notes. For the completed human source-review decision and final active outputs, see `docs/HUMAN_SOURCE_VALIDATION.md` and the project README.

# Offline pilot correction

Merge this package into the project. Run from your project root:

    python -m part1_stated_values.src.review_pilot

No new packages, API key, network access or generation requests are required.
The original gemini_pilot.py is included unchanged for reproducibility. Original
cache and pilot_results.json are not overwritten. The included review outputs
were generated against the uploaded cache and source texts; rerunning reproduces
them locally. No need to send the same outputs back unless the command errors.

## Diagnosis

NVIDIA: one quote omitted a source space before a period. JPMorgan: seven quotes
added punctuation or combined separately extracted bullets/headings; the integrity
quote also omitted the heading number 11. None of these eight failures was caused
by the minimum quote length. Exact matching correctly rejected them.

The offline reviewer applies eight explicit source-specific replacements, retains
all original coding, logs every edit, and reruns the unchanged strict validator.
This is not fuzzy matching. A source mismatch stops processing. For JPMorgan the
replacement is a shorter exact passage; original extended claims are not silently
presented as verbatim evidence. Supporting rationales are marked as assistant review.

Apple's customer label is removed: its evidence is an employee quotation attributed
to Ehsan, Engineering Manager in the archived HTML. Amazon remains excluded as a
link-heavy source. Microsoft, Apple, NVIDIA, Alphabet and JPMorgan are conservatively
marked mixed because cleaning, source scope or historical-letter limitations remain.
All final annual selections remain false; independent human review remains pending.

## What this establishes

The API works. The model can locate relevant themes, but exact-quote and semantic
checks are both necessary. Six purposefully selected cases are not a representative
accuracy sample, and assistant review is not independent human validation. Do not
report the repaired results as six successful unassisted model responses.

## Required design for the scaled pipeline

Use deterministic paragraph/block IDs and ask the LLM to select IDs, not regenerate
quotations. Copy evidence text from the selected blocks locally. Validate IDs against
the actual input and still check theme semantics, speaker attribution and suitability.
Preserve heading and speaker context. Do not universally strip punctuation or use
fuzzy matching to pass unsupported quotes. Freeze the taxonomy only after evaluation.

This source-specific repair is intentionally not a general full-dataset classifier.
Coverage repair, body extraction, block-ID coding, prior-year changes and Parts 2–4
remain outstanding. Collection and model caches should be reused wherever applicable.
