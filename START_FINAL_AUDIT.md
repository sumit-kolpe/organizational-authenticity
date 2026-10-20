# Reproducibility and final verification

From the repository root, use a Python virtual environment and install `requirements.txt` and `requirements-final.txt`.

```bash
python -m pip install -r requirements.txt -r requirements-final.txt
python -m unittest discover -s tests -v
python -m shared.final_audit --part4-version exploration_v2
```

The 450-row Part 1 and Part 2 panel includes the October 19, 2026 completed-review decision recorded by the project owner. The final 140 Part 1 accepted sources and 443 selected proxy filings remain unchanged in content from the previously audited results. The Part 3 and Part 4 outputs have been recalculated with fresh provenance hashes. This archive supplies processed data, source links and analytical code but excludes the original large raw download caches, so original Wayback/SEC retrieval requires network access and the separately retained working archive.

The independent numerical tests check consistency, not whether company statements accurately represent company behavior. Further details: `README.md`, `README_SUBMISSION.md`, `docs/HUMAN_SOURCE_VALIDATION.md` and each part's README.
