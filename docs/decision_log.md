# Decision log

Dates use America/New_York. Preserve prior decisions when revising them; record the reason and affected outputs.

| ID | Date | Status | Decision and reason |
| --- | --- | --- | --- |
| D001 | 2026-10-16 | Fixed requirement | Preserve the PDF's exact 50 firms and supplied sector labels; do not rebuild the sample. |
| D002 | 2026-10-16 | Adopted interpretation | Measure website–disclosure alignment, not directly observed behavior or ethics. |
| D003 | 2026-10-16 | Adopted architecture | Four part folders, shared reusable code, separate raw/processed/output layers. |
| D004 | 2026-10-16 | Provisional | Latest usable in-year website capture; verify on the archive pilot. |
| D005 | 2026-10-16 | Provisional | Prefer annual proxy statements, pending cross-sector availability and content checks. |
| D006 | 2026-10-16 | Provisional | Match by publication calendar year, preserve fiscal period, and require disclosure availability by capture date for primary scoring. |
| D007 | 2026-10-16 | Adopted rule | Missing data and unavailable prior-year comparisons remain missing, never automatically zero or unchanged. |
| D008 | 2026-10-16 | Provisional | Start from ten proposed themes; freeze definitions after a representative pilot. |
| D009 | 2026-10-16 | Provisional | Use Jaccard as the transparent index starting point; assess alternatives before full scoring. |
| D010 | 2026-10-16 | Deferred | Select LLM, budget and provider-specific settings at the model pilot. |
| D011 | 2026-10-19 | Completed — owner-confirmed | Project owner confirms human source review complete with no further changes; current source inventory fields record all 450 reviewed dispositions and 140 accepted final Part 1 selections. See `docs/HUMAN_SOURCE_VALIDATION.md`. |
| D012 | 2026-10-19 | Implemented | Part 4 exploratory question: compare absolute annual textual-alignment movements between changed and unchanged recorded company messaging, with firm influence and decomposition checks. |

The implemented additional analysis and the raw-download omission policy for the compact submission are documented in the Part 4 README and `README_SUBMISSION.md`, respectively.
