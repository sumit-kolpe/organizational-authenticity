# Part 4: Do text changes coincide with larger alignment changes?

This exploratory question tests whether the magnitude of annual textual alignment change differs between observations with a recorded Part 1 text change and those recorded as unchanged. It is not a test of whether substantive corporate values, behavior or authenticity changed. The question was chosen after Part 3, before computing this contrast; it is exploratory and not preregistered.

## Design

Use exact adjacent calendar years with non-null Part 3 scores at both endpoints. Of 96 such pairs, 79 have a Boolean Part 1 comparison decision in one of three accepted statuses: identical_extracted_blocks, llm_compared_human_reviewed or llm_repaired_human_reviewed. The other 17 remain unknown and are excluded from the primary contrast. The owner confirmed completing human review of the existing source decisions without further changes; label uncertainties and methodological limitations remain in the analysis. The 79 pairs represent 28 firms, with 49 changed and 30 unchanged comparisons. Firms may contribute to both groups.

The outcome is `abs(score_current - score_previous)`. The primary statistic is its mean among recorded-changed pairs minus its mean among recorded-unchanged pairs. Signed changes are reported separately to distinguish movement magnitude from direction. Company-years are dependent and unevenly distributed; no independent-observation t-test, causal regression or claim of population significance is made.

## Sensitivity and company influence

* Theme-set sensitivity uses all 96 pairs and compares binary stated-theme vectors directly. This changes both classification and sample, and partially overlaps mechanically with how alignment is constructed.
* Scope sensitivity excludes a pair if either Part 1 endpoint has specific source-scope flags. Generic extraction warnings are not used to discard every observation.
* Company-balanced comparison calculates changed-minus-unchanged differences within firms that have both types of observation, then weights those firms equally. This is a different, smaller subset, not a fixed-effects causal estimate.
* Leave-one-company-out recalculates the pooled contrast after removing each represented firm. Its range is an influence diagnostic, not a confidence interval.
* Four pairs are recorded as unchanged text but have different theme sets: AAPL 2017, HAL 2022, HAL 2023 and INTC 2019. This may reflect coding variation or comparison scope. A source-linked review queue records the completed no-change decision. Another sensitivity excludes them; they remain possible sources of coding variation rather than being silently overwritten.

## Exact attribution of score movement

For cosine F(s,d), old/new stated vectors s0/s1 and proxy profiles d0/d1:

`stated_component = ((F(s1,d0)-F(s0,d0)) + (F(s1,d1)-F(s0,d1))) / 2`

`proxy_component = ((F(s0,d1)-F(s0,d0)) + (F(s1,d1)-F(s1,d0))) / 2`

The two signed components sum exactly to the score change (within floating-point precision). This averages both update orders. It is an algebraic attribution of the measure, not a causal decomposition. Absolute components need not add to absolute total change because opposing changes can cancel. When the stated vector is unchanged, its component is zero and all score movement is attributable algebraically to the proxy profile.

## Findings and limits

The primary difference is about +0.0063 on the 0–1 alignment scale: changed mean 0.0963 versus unchanged 0.0900. The leave-one-company-out difference ranges from about -0.0051 to +0.0165, so its sign is not stable to company removal. The company-balanced comparison among 11 firms averages +0.0217. These summaries do not support a strong or robust general claim that recorded text changes lead to larger alignment movements.

Even among 51 pairs with unchanged coded theme sets, mean absolute alignment change is about 0.0753, demonstrating that proxy-profile changes can move the index without a change in stated themes. Broad or boilerplate proxy language, varying source genres, archive timing, selective historical availability and model/dictionary errors remain important. Part 3's weak company-specific negative-control separation also carries forward. No event causality, behavioral performance or verified authenticity is inferred.

## Reproducibility and provenance

The code requires only the standard library, accepts input/output path arguments and makes no network calls. It checks Part 1's hash against Part 3's run policy, unique keys, matching panel size, score/vector consistency and exact decomposition. Run policy hashes prevent mixing different inputs into an existing output directory. Charts and the two-page PDF require matplotlib and reportlab; precomputed versions are included.

The project owner confirmed human source review complete with no additional changes. The four label/theme disagreement cases are retained for transparent sensitivity analysis and their review-queue status is now recorded as completed without changes. Numerical findings are unchanged; see `docs/HUMAN_SOURCE_VALIDATION.md`.
