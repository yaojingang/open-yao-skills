# Reference Synthesis

The package uses a Production mode shape because the workflow is reusable, security-sensitive, and benefits from deterministic report rendering.

## Borrowed

- OWASP/CWE/CISA/FIRST baselines for risk categories, weakness taxonomy, exploited-vulnerability priority, and severity context.
- User source report for `V001-V275`, module sequencing, evidence schema, risk overrides, and report requirements.
- Yao meta-skill resource boundaries: keep `SKILL.md` small, move domain guidance to `references/`, and put report generation in `scripts/`.

## Not Borrowed

- No exploit payload library or offensive playbook.
- No mandatory dependency on a paid scanner or a single platform.
- No active scanning by default.
- No large benchmark prose inside `SKILL.md`.

## First Iteration Boundary

This version provides a reusable audit workflow, ontology, JSON schema, isolated environment preparation, and XLSX/HTML/Markdown/PDF renderer. It does not run dynamic or online checks without user-provided authorization, URLs, accounts, rate limits, rollback/reset plans, and safe test data.
