## Reproduce existing processed-data analysis

Install the original requirements and requirements-final.txt in a virtual environment. Run tests for the relevant modules, then the Part 3 and Part 4 analysis commands documented in their READMEs. For changed input bytes, choose a fresh output directory and regenerate the matching report; do not delete hash guards. Windows newline differences can change byte hashes even where JSON values agree. The local final audit checks the actual on-disk provenance chain.

Part 1 collection/coding and Part 2 collection require external access and their own configuration. Part 3/4 and report rendering are offline. The submission archive includes processed data and code, but omits raw HTML/download caches and credentials. The full local working project retains those caches; raw-source regeneration requires collection or a separately supplied raw-data bundle. Do not claim that a processed-only archive independently reproduces the original downloads without network access.

## Scalability and next work

Cached retrieval, explicit row statuses, versioned prompts/dictionaries, fixed join keys and per-document provenance make the pipeline extensible. Scale source quality assurance before increasing sample size: verify annual source selection, remove navigation/promotional blocks, separate proxy voices, consistently recode repeated values text, and validate sampled matches and nonmatches. Preserve all old outputs when producing revised versions.

Known findings are exploratory: average alignment is about 0.546, with weak own-company separation from same-sector/year controls. Part 4's text-change contrast is about +0.0063 and can reverse when individual companies are omitted. Neither supports a strong behavioral or causal claim.
