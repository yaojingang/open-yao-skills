# Kelly Skill Iteration Log

Append only. Log every package-level change.

## 2026-04-26T17:41:56+08:00
- Summary: Scaffolded the Kelly skill, added multi-turn readiness logic, conservative sizing rules, canonical calculation scripts, and persistent logging contracts.
- Reason: The default init package did not yet own the real recurring job of turning uncertain allocation questions into conservative Kelly application reports.
- Files: `SKILL.md`, `agents/interface.yaml`, `manifest.json`, `references/intake-contract.md`, `references/multi-turn-kelly-loop.md`, `references/kelly-sizing-playbook.md`, `references/output-contract.md`, `references/logging-contract.md`, `references/safety-and-scope.md`, `scripts/kelly_allocation_report.py`, `scripts/append_iteration_log.py`, `reports/design-summary.md`, `reports/example-brief.json`, `reports/example-output.json`, `history/CHANGELOG.md`, `logs/README.md`
- Assumptions: `Default total_exposure_cap stays conservative at 0.25 when the user does not provide one.`, `Default min_cash_reserve_ratio stays conservative at 0.50 when the user does not provide one.`
- Checks: `python3 scripts/kelly_allocation_report.py --input reports/example-brief.json --output reports/example-output.json`, `python3 /Users/laoyao/AI Coding/03-Development/Skills/yao-meta-skill/scripts/validate_skill.py /Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill`, `python3 /Users/laoyao/AI Coding/03-Development/Skills/yao-meta-skill/scripts/governance_check.py /Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill --require-manifest`
- Next steps: `Add route and near-neighbor eval cases for formula tutoring vs real allocation sizing.`, `Add explicit correlated-opportunity examples and stronger friction handling.`

## 2026-04-26T17:50:18+08:00
- Summary: Added standalone HTML report generation and updated the Kelly skill workflow to support JSON plus HTML report artifacts.
- Reason: The user asked for an optimized HTML report style and a new sample output based on the Kelly sizing logic.
- Files: `SKILL.md`, `README.md`, `manifest.json`, `references/output-contract.md`, `scripts/kelly_allocation_report.py`, `scripts/generate_html_report.py`, `reports/example-brief.json`, `reports/example-output.json`, `reports/example-html-report.html`, `history/CHANGELOG.md`
- Assumptions: `JSON remains the canonical audit source while HTML is the human-readable report artifact.`
- Checks: `python3 scripts/kelly_allocation_report.py --input reports/example-brief.json --output reports/example-output.json`, `python3 scripts/generate_html_report.py --input reports/example-output.json --output reports/example-html-report.html`, `python3 /Users/laoyao/AI Coding/03-Development/Skills/yao-meta-skill/scripts/validate_skill.py /Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill`, `python3 /Users/laoyao/AI Coding/03-Development/Skills/yao-meta-skill/scripts/governance_check.py /Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill --require-manifest`
- Next steps: `Add route evals and a screenshot-based visual check if this report becomes a published artifact.`

## 2026-04-26T18:01:29+08:00
- Summary: Added public sync rule and prepared the skill for publication into yao-open-skills.
- Reason: The user asked to push the Kelly skill into the GitHub yao-open-skills repository and keep future iterations auto-published.
- Files: `README.md`, `references/logging-contract.md`, `history/CHANGELOG.md`
- Assumptions: `The public copy should keep the package iteration log but exclude local caches and private runtime logs.`
- Checks: `Manual review of yao-open-skills publishing rules and registry schema.`
- Next steps: `Sync cleaned public copy into yao-open-skills/skills/yao-kelly-skill, update registry and README, then commit and push.`

## 2026-04-26T18:16:32+08:00
- Summary: Added two new scenario reports and resource-unit aware HTML rendering.
- Reason: The user asked for two completely different example use cases and report outputs.
- Files: `README.md`, `scripts/kelly_allocation_report.py`, `scripts/generate_html_report.py`, `reports/marketing-budget-brief.json`, `reports/marketing-budget-output.json`, `reports/marketing-budget-report.html`, `reports/engineering-hours-brief.json`, `reports/engineering-hours-output.json`, `reports/engineering-hours-report.html`, `history/CHANGELOG.md`
- Assumptions: `Resource allocation reports should support non-currency units such as engineering-hours while preserving the same Kelly sizing logic.`
- Checks: `python3 scripts/kelly_allocation_report.py --input reports/marketing-budget-brief.json --output reports/marketing-budget-output.json`, `python3 scripts/kelly_allocation_report.py --input reports/engineering-hours-brief.json --output reports/engineering-hours-output.json`, `python3 scripts/generate_html_report.py --input reports/marketing-budget-output.json --output reports/marketing-budget-report.html`, `python3 scripts/generate_html_report.py --input reports/engineering-hours-output.json --output reports/engineering-hours-report.html`, `python3 /Users/laoyao/AI Coding/03-Development/Skills/yao-meta-skill/scripts/validate_skill.py /Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill`
- Next steps: `Add a brief gallery section if more example reports are added.`
