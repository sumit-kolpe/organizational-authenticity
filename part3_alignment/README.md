# Part 3: provisional textual alignment

## Inputs and sample

Uses the reviewed Part 1 `outputs/review_v2/part1_values_reviewed.json` and Part 2 `outputs/proxy_v2/disclosure_metrics.json`. Joins exact ticker and calendar year across the fixed 450-row panel. Part 1 must explicitly mark a row eligible; Part 2 must have a downloaded, analyzed proxy. No imputation, forward filling or conversion of missing values into zero. The supplied outputs have 137 scored company-years across 36 companies and 313 unscored rows. Exclusion reasons can overlap.

## Index specification

The fixed nine dimensions are innovation, integrity, people, inclusion, customer, environment, community, security_privacy and performance. The stated-values vector s uses 1 for a theme present in Part 1 and 0 otherwise. The disclosure vector d uses dictionary mentions per 1,000 proxy words. The primary index is:

`alignment = sum(s[t]*d[t]) / (sqrt(sum(s[t]^2)) * sqrt(sum(d[t]^2)))`

Scores range from 0 to 1. Zero means disjoint nonzero theme vectors; one means proportional vectors. A zero vector is unscorable and recorded as null. Part 1 provides theme presence rather than intensities, so stated themes receive equal weight. Dividing every proxy dimension by word count does not alter cosine: the score measures the relative theme profile, not absolute disclosure volume. This is textual alignment, not a percentage of promises fulfilled or evidence of authentic behavior. Scores use no fitted parameters or threshold tuned to the observed results.

## Validation and sensitivity

Tests cover mathematical boundaries, scale invariance, missingness, duplicate keys, unknown themes, bad rates and timing. Actual input checks require matching 450-row panels, 50 companies, 2016–2024, matching sectors and identical theme vocabularies. Input hashes and a policy file prevent silent overwriting with changed inputs; use `--output` for a new run.

Negative controls compare each eligible stated vector with every other available proxy in its year, and separately in its sector and year, excluding its own ticker. The control pool includes proxies whose Part 1 is unavailable. The reported own-minus-other mean is descriptive, not a p-value or proof of validity. Repeated firm-years are dependent. An average close to zero indicates limited company-specific discrimination.

Sensitivity checks use log(1+rate) cosine; binary Jaccard with at least one or at least three dictionary hits; cosine excluding integrity and inclusion; exclusion of specifically scope-flagged Part 1 sources; and the subset with an archive capture on or before the proxy filing date. The last two subsets change sample composition, so their differences cannot be attributed solely to measurement. The generic extraction warning applies to all eligible Part 1 rows and is retained rather than used to exclude the entire sample. Excluding integrity and inclusion tests reliance on two governance-related categories, but cannot remove all governance content. Thresholded Jaccard is length-sensitive and typically saturates in long proxies. Sensitivity scores are alternatives, not interchangeable validated measures.

Source review queue selects the lowest, middle and highest score deterministically and preserves both URLs. The project owner confirmed review completion with no additional changes. The three queued cases are marked as reviewed with no changes; their scores and limitations are unchanged. Computational and negative-control checks are also completed. See `docs/HUMAN_SOURCE_VALIDATION.md`.

## Threats and interpretation

1. Selection: historical values coverage is sparse and rises over time; the 137 observations cannot represent all 450 company-years. Year and sector means have changing company composition.
2. Genre and voice: recruitment pages, founding letters and values pages differ from full proxies. Shareholder proposals, compensation, mandated governance and repeated contents contribute mentions; mentions do not establish endorsement.
3. Coding asymmetry: model-derived Part 1 presence is compared with Part 2 dictionary frequency. Synonyms, polysemy, negation and broad theme sets can change scores without substantive alignment changes.
4. Timing and entity scope: archive captures and filing dates differ within a calendar year. Corporate restructuring, historical CIK mappings and filing-form restrictions affect coverage. XOM 2021 DEFC14A remains outside the baseline's DEF 14A rule.
5. Construct validity: both sources describe communications, not actual conduct. The weak negative-control separation limits claims about company-specific authenticity. No causal event effects are estimated.

Group summaries report observation-weighted statistics and sample sizes. The overall company-equal-weight mean gives each represented company equal weight. Within-company changes use adjacent years only. Variance of company means and mean squared within-company deviations describe an unbalanced sample; they are not an additive variance decomposition or model-based components. No arbitrary high/low authenticity classifications are assigned.

## Reproduction

From the project root, run the commands in START_PART3.md. Analysis requires only Python's standard library and no API credentials. Rendering the supplied charts and two-page summary requires matplotlib and reportlab. All current results and figures are included in the package. Changing source inputs requires a new output directory and corresponding report regeneration.

The active output carries completed source-review status, a dated owner-confirmation basis, original Part 1 flags, and input-byte hashes. The numerical index is reproducible; its limited behavioral validity remains an explicit substantive limitation.
