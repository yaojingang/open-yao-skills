---
name: yao-websecurity-skill
description: Use when auditing an authorized website, SaaS, API, AI app, local code path, GitHub repo, staging URL, or owned runtime for security risks, vulnerability checklist scoring, static review, dynamic review, active validation, or Chinese security reports.
---

# Yao Websecurity Skill

## Use

Use when the user gives a local path, archive, GitHub repo, staging URL, or owned runtime and wants a defensive website security audit, vulnerability checklist review, scorecard, remediation plan, static review, dynamic review, active validation, or Excel/HTML/Markdown/PDF report.

Do not use for unauthorized targets, exploit development, credential theft, stealth, malware, third-party public-target scanning, or bypass instructions.

## Required Reading

- `references/security-audit-method.md`
- `references/report-contract.md`
- `references/review-modes.md`
- `references/vulnerability-ontology.csv`
- `references/scanner-registry.md`

## Workflow

1. Confirm mode, scope, authorization, environment, intensity, forbidden actions, test accounts, rate limits, rollback/reset plan, and whether online targets are allowed. Without active-test authorization, use `static`.
2. Prepare an isolated workdir before review: `python3 scripts/security_audit_report.py prepare-env --source "<path-or-url>" --workdir "<fresh-temp-workdir>" --project "<name>" --mode "<mode>"`. Local and GitHub targets must be copied or cloned into this fresh temp directory; never install, build, migrate, write reports, or mutate the original source tree.
3. For `dynamic-safe`, `dynamic-active`, `hybrid`, or `online-authorized`, configure only temporary secrets, test DB, synthetic accounts/data, loopback or isolated containers, OOB endpoint if authorized, and stop conditions. Destructive file operations, DB writes, brute-force resilience, resource pressure, and blind SSRF/OOB tests default to the isolated temp deployment.
4. Inventory the isolated `target-source` with `rg --files`, manifests, routes/API definitions, auth/session modules, data models, configs, Docker/IaC, CI/CD, and AI/LLM integrations. Record unreadable, generated, vendor, or excluded paths.
5. Create the review skeleton: `python3 scripts/security_audit_report.py init --project "<name>" --source "<fresh-temp-workdir>/target-source" --mode "<mode>" --intensity "<intensity>" --out "<fresh-temp-workdir>/security_review.json"`.
6. Triage `V001-V275` by observed attack surface. Mark irrelevant items `Not Applicable` with a short reason; deep-audit only applicable or unclear items, grouped by domain and priority. Do not spend review budget testing vulnerability families that are not represented in the code, framework, runtime, or deployment model.
7. Execute only the selected mode. Static means code/config/passive review. Dynamic-safe means runtime and passive DAST against temp deployment. Dynamic-active may run blind/OOB, capped brute-force, file mutation, DB writes, and resource-pressure tests only inside temp deployment unless explicit online authorization states otherwise. If a runtime gate is missing, mark affected checks `Unclear` or `Deferred`, not `Safe`.
8. Render artifacts: `python3 scripts/security_audit_report.py render --review "<workdir>/security_review.json" --out-dir "<workdir>/security-audit-report"`.
9. Return the absolute `.xlsx`, `.html`, `.md`, and `.pdf` paths, selected mode, selected risk domains, P0/P1 findings, unclear items, coverage gaps, runtime assumptions, and active-test evidence.

## Output Contract

Default outputs are `安全审查评分表.xlsx`, `安全审查报告.html`, `安全审查报告.md`, `安全审查报告.pdf`, and `security_review.sanitized.json`, written outside the audited source tree. Report content is Simplified Chinese by default. Excel must use Chinese labels and Chinese row-level interpretations for verdict, evidence, finding, impact, and remediation, while preserving code identifiers and paths as-is. HTML must include a right-side language toggle with Chinese as the default view and English as the alternate view, plus a sticky top navigation menu for major sections. Markdown is generated from the same Chinese scorecard/report content used by Excel. PDF is a Chinese-first browsing copy optimized for quick review and should use browser/HTML print rendering when available for stable typography and page breaks. Follow `references/report-contract.md` for review-mode, isolation, and presentation standards. Evidence must be sanitized: no plaintext secrets, cookies, reusable tokens, personal data dumps, or destructive proof steps.

## Reference Map

- `scripts/security_audit_report.py`: prepare-env/init/extract/render.
- `templates/review-template.json`: review shape.
- `evals/`: route boundaries.
- `reports/`: reference, output-risk, artifact profiles.
