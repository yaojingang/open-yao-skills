# Skill Doctor

## What It Does

`skill-doctor` audits local skill libraries for hygiene and security issues, then generates local reports that help decide which skills to keep, repair, archive, delete, or quarantine.

## When To Use It

Use `skill-doctor` when you need to:

- scan a directory of local skills
- inventory what each skill does
- estimate which skills are active or stale from local evidence
- flag risky patterns such as hardcoded secrets, unsafe shell execution, and suspicious prompt-injection language

## Main Workflow

1. Run the doctor against one or more local roots.
2. Review the generated HTML, Markdown, and JSON reports.
3. Inspect cleanup and security recommendations before taking action.
4. Only run backup, archive, quarantine, or delete actions after explicit confirmation.

## Commands

Basic scan:

```bash
python3 skills/skill-doctor/scripts/run_skill_doctor.py /path/to/skills-root
```

Multiple roots:

```bash
python3 skills/skill-doctor/scripts/run_skill_doctor.py /path/one /path/two
```

## Outputs

By default, the runner generates local artifacts under:

```text
skills/skill-doctor/_skill_doctor_reports/<timestamp>/
```

Artifacts include:

- `report.html`
- `report.json`
- `report.md`
- `actions/*.command`

## Publishing Rule

Those generated reports are local runtime outputs. They should not be committed back into `open-yao-skills` unless you intentionally create a sanitized public sample.

