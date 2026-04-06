# Operating Rules

This reference is the short operational summary for maintaining `open-yao-skills`.

## Source of truth

- Public skill content lives in `skills/<slug>/`
- Skill state lives in `registry/skills.json`
- README catalog is generated from the registry

## Intake rule

Only add a skill when it is suitable for public release:

- useful beyond one private session
- understandable without private context
- clean of secrets, logs, caches, and output artifacts

Generated local outputs should stay local by default.

## Sync rule

Use these `sync_status` values:

- `local-only`: registered locally, not yet published
- `staged`: public copy prepared, awaiting final publication step
- `published`: already available on GitHub
- `needs-update`: GitHub copy exists but local source changed

## Required maintenance steps

1. Import or update the public skill copy
2. Upsert `registry/skills.json`
3. Add or update `docs/skills/<slug>.md`
4. Regenerate `README.md`

## Paths

- Repo root: the repository root that contains `README.md`, `registry/`, `scripts/`, and `skills/`
- Skill collection root: `skills/` under the repo root
