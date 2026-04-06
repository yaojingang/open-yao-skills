---
name: skill-doctor
description: Scan local skill folders to inventory purpose, usage signals, cleanup priority, and safety risks, then generate a visual HTML audit report. Use when Codex needs to audit a skill library, organize or deduplicate skills, recommend backup, archive, or delete actions, or review downloaded third-party skills for prompt injection, token leakage, hardcoded secrets, risky shell execution, and suspicious network-fetch patterns before the user installs or runs them.
---

# Skill Doctor

## Boundary

Own this recurring job: audit local skill folders, estimate usage from local evidence, recommend cleanup direction, and flag security risks before install, execution, archive, or deletion.

Do not route here for:

- generic code security review outside a skill library
- one-off file cleanup with no skill audit
- creating a brand-new skill from scratch
- real destructive cleanup unless the user explicitly authorizes it

## Default Workflow

1. Run `scripts/run_skill_doctor.py <root> [more-roots]`.
2. Generate `_skill_doctor_reports/<timestamp>/` with `report.html`, `report.json`, `report.md`, and clickable `.command` actions.
3. Use [Usage Evidence](references/usage-evidence.md), [Cleanup Rubric](references/cleanup-rubric.md), and [Security Rubric](references/security-rubric.md) to interpret the scan.
4. Return the HTML report path first, then summarize inventory, usage, cleanup, and security.

## Operating Rules

- Stay read-only unless the user explicitly asks for cleanup actions.
- Treat usage frequency as an estimate derived from local evidence such as modification time and top-level inventory mentions.
- Do not present inferred frequency as telemetry or exact run counts.
- Escalate to `quarantine` for secret leakage, remote shell piping, private keys, or suspicious prompt injection or exfiltration behavior.
- Prefer precise path-based evidence over generic statements.
- Separate hygiene issues from security issues. A stale skill is not automatically unsafe, and a recently modified skill can still be dangerous.
- Treat generated reports as local runtime artifacts. Do not commit `_skill_doctor_reports/` back into the public repo unless the user explicitly wants a sanitized sample.

## Outputs

Primary artifact:

- visual HTML report with summary cards, charts, recommendation modules, and per-skill action buttons

For each skill, provide inside the report:

- absolute path
- declared skill name and one-line purpose summary
- usage estimate: `active`, `warm`, `cold`, or `unknown`
- usage confidence: `low`, `medium`, or `high`
- cleanup level: `low`, `medium`, `high`, or `critical`
- cleanup direction: `keep`, `repair`, `backup-then-archive`, `backup-then-delete`, or `quarantine`
- security level: `none`, `low`, `medium`, `high`, or `critical`
- top evidence and findings that justify the recommendation

Order cleanup plans by security severity, cleanup level, and confidence that the skill is stale or disposable.

## Resources

- [Usage Evidence](references/usage-evidence.md)
- [Cleanup Rubric](references/cleanup-rubric.md)
- [Security Rubric](references/security-rubric.md)
- `scripts/run_skill_doctor.py`
- `scripts/scan_skills.py`
- `scripts/skill_actions.py`
- `evals/trigger_cases.json`
- `evals/semantic_config.json`
