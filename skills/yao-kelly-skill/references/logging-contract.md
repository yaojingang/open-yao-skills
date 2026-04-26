# Logging Contract

This skill keeps two different logs. Treat both as required.

## 1. Session round log

Every user case must keep a round-by-round process log.

Required fields per round:

- round number
- user input summary
- resolved gap
- case type
- formula path
- readiness before and after
- current full Kelly fraction
- current conservative fraction
- action class
- next questions or stop reason

Default behavior:

- always include the round log in the final answer
- if file writing is available and appropriate, persist the log under `logs/sessions/`

Recommended filename:

- `logs/sessions/YYYY-MM-DD-short-slug.md`

## 2. Skill iteration log

Every future edit to this skill package must append one dated note to:

- `history/CHANGELOG.md`

Use:

- `python3 scripts/append_iteration_log.py`

Required fields:

- summary
- reason
- changed files
- assumptions
- checks
- next steps

Rules:

- append only
- do not rewrite older entries unless they are factually wrong
- log package changes even when the edits are small

## 3. Public sync rule

This skill is mirrored into:

- `/Users/laoyao/AI Coding/03-Development/Skills/yao-open-skills/skills/yao-kelly-skill`

When a package-level iteration is accepted:

- append the source iteration log first
- refresh the public copy under `yao-open-skills/skills/yao-kelly-skill`
- keep `history/CHANGELOG.md` in the public copy
- update `registry/skills.json` and the README catalog when public metadata changes
- commit and push the public repo to GitHub if the user has asked for auto-publish behavior

Do not publish local caches, `__pycache__`, private logs, credentials, or unrelated generated output.

## Example iteration log entry

```markdown
## 2026-04-26T16:20:00+08:00
- Summary: Added conservative multi-opportunity Kelly sizing and persistent iteration logging.
- Reason: The initial scaffold did not yet own the real recurring job.
- Files: `SKILL.md`, `references/kelly-sizing-playbook.md`, `scripts/kelly_allocation_report.py`
- Assumptions: Default total exposure cap remains conservative when the user does not specify one.
- Checks: `validate_skill.py`, sample JSON run
- Next steps: Add eval cases for near-neighbor routing and correlated opportunities.
```
