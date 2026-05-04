# Yao Kelly Skill

## What It Does

`yao-kelly-skill` owns one recurring job:

> Turn an uncertain invest, bet, or allocate question into a conservative Kelly application report that decides whether to allocate, how much to allocate, why that number is disciplined, and what assumptions still matter.

## How To Use

1. Load the routing and workflow from `SKILL.md`.
2. Use `references/intake-contract.md` to turn the request into a Kelly brief.
3. If input is incomplete, use `references/multi-turn-kelly-loop.md` to ask the minimum next questions and stop when readiness is high enough.
4. Use `references/kelly-sizing-playbook.md` to choose the correct formula path.
5. Run `python3 scripts/kelly_allocation_report.py --input reports/example-brief.json --output reports/example-output.json` for the canonical calculation path.
6. Run `python3 scripts/generate_html_report.py --input reports/example-output.json --output reports/example-html-report.html` for the polished report artifact.
7. Use `references/output-contract.md` and `references/logging-contract.md` to finalize the user-facing report and the logs.

## Package Map

- `SKILL.md`: trigger and workflow entrypoint
- `agents/interface.yaml`: portable interface metadata
- `manifest.json`: lifecycle and packaging metadata
- `references/`: intake, multi-turn loop, sizing rules, output contract, logging contract, and safety boundaries
- `scripts/kelly_allocation_report.py`: canonical Kelly sizing calculator
- `scripts/generate_html_report.py`: standalone HTML report renderer
- `scripts/append_iteration_log.py`: append-only skill change logger
- `reports/design-summary.md`: boundary and deliverable summary
- `reports/example-brief.json`: sample calculation input
- `reports/example-output.json`: sample calculation output
- `reports/example-html-report.html`: sample HTML report
- `reports/marketing-budget-report.html`: customer-acquisition budget allocation example
- `reports/engineering-hours-report.html`: non-financial engineering-capacity allocation example
- `reports/internet-product-sprint-report.html`: practical internet product sprint allocation example
- `history/CHANGELOG.md`: package iteration log
- `logs/`: session log location

## Publication

This skill is mirrored to `yao-open-skills/skills/yao-kelly-skill`. Future accepted iterations should append `history/CHANGELOG.md`, refresh the public copy, and push `yao-open-skills` to GitHub.
