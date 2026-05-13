# Validation Results

Checked on 2026-05-13.

## Structure

- `validate_skill.py`: pass, no warnings.
- `resource_boundary_check.py`: pass, initial-load estimate `989/1000` tokens, no unused resource directories.
- `trigger_eval.py`: pass at threshold `0.45`, precision `1.0`, recall `1.0` on 18 route cases.

## Artifact Smoke Test

- Extracted `275` checklist rows into `references/vulnerability-ontology.csv`.
- Initialized a sample review JSON with `275` checks.
- Regression test confirms local paths, cookies, bearer tokens, API keys, passwords, private keys, cloud keys, and long token-like values are sanitized from rendered artifacts.
- Report schema now includes attack-surface triage, selected risk domains, applicability reason, verification mode, scan depth, active-test prerequisites, and test-safety notes.
- Report helper refuses to write review JSON, sanitized JSON, XLSX, HTML, Markdown, PDF, or prepared environment artifacts inside the original audited local source directory.
- `prepare-env` smoke test confirms a local source is copied into an isolated `target-source`, ignored dependency directories are not copied, `.env.audit` is created in the temp copy, and mode metadata records `dynamic-active`/`destructive` gates.
- `init` smoke test confirms selected runtime mode, intensity, `allowed_dynamic_tests`, runtime URL, and OOB endpoint are written into the review ledger.
- Rendered sample artifacts:
  - `security_review.sanitized.json`
  - `安全审查评分表.xlsx`
  - `安全审查报告.html`
  - `安全审查报告.md`
  - `安全审查报告.pdf`
- `unzip -t` passed for the generated `.xlsx`.
- HTML/XLSX/Markdown/sanitized JSON redaction checks passed for sensitive fixtures.

## Ontology Distribution

- `P0`: 95
- `P1`: 125
- `P2`: 53
- `P3`: 2
