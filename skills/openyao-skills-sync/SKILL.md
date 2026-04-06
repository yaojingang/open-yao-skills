---
name: openyao-skills-sync
description: Manage the openyao-skills public collection. Use this skill whenever the user wants to evaluate whether a local skill should be open sourced, import a local skill into the openyao-skills repository, register which skills are already public, track GitHub sync status, or update the collection README and catalog after adding or refreshing a skill.
---

# OpenYao Skills Sync

Use this skill to manage the public `openyao-skills` collection at:

- `/Users/laoyao/AI Coding/03-Development/Skills/openyao-skills`

This skill is not for creating arbitrary new skills from scratch. It is for intake, governance, sync tracking, and collection maintenance.

## Read First

Before changing the collection, read:

- `references/operating-rules.md`
- `references/registry-schema.md`

Only read repo-wide docs under `../../docs/` if you need more human-facing detail after reviewing the references.

## Primary Responsibilities

- Evaluate whether a local skill is suitable for public release
- Create a clean public copy under `skills/<slug>/`
- Register or update the skill in `registry/skills.json`
- Regenerate the README catalog so the collection homepage stays in sync
- Record whether the skill is only local, staged, published, or needs an update
- Push collection changes to GitHub when the user wants the public repo updated

## Workflow

### 1. Inspect the source skill

Given a local path from the user:

- Confirm the path exists
- Inspect `SKILL.md`
- Identify what should be kept, removed, or rewritten for public release

Watch for:

- `output/`, `downloads/`, `.venv/`, `node_modules/`, caches, logs
- private APIs, tokens, cookies, internal references, customer data
- assets or references that may not be redistributable

### 2. Decide whether it can be public

Use the publishing rules:

- If the skill can be cleaned into a self-contained public version, proceed
- If it mixes public logic with sensitive material, split the public part from the private part
- If it cannot be safely cleaned, stop and explain why it should not be published

### 3. Import the public copy

When approved:

- Copy the public version into `openyao-skills/skills/<slug>/`
- Keep only the files needed for the public skill
- Make the structure self-contained and understandable

### 4. Register the skill

Upsert the registry entry using:

```bash
python3 scripts/register_skill.py \
  --slug <slug> \
  --title "<title>" \
  --summary "<summary>" \
  --source-local-path "<absolute-source-path>" \
  --collection-path "skills/<slug>" \
  --lifecycle active \
  --sync-status <local-only|staged|published|needs-update> \
  --github-repo openyao-skills \
  --github-url "<url-if-known>" \
  --license "<license>" \
  --tags "tag1,tag2"
```

Use `--last-synced-at YYYY-MM-DD` only when the skill has actually been pushed to GitHub.

### 5. Update the README catalog

After every registry change, run:

```bash
python3 scripts/render_readme_catalog.py
```

README is a rendered view. Do not maintain the catalog table manually.

### 6. Publish to GitHub when requested

If the user wants the collection pushed:

- ensure the public files, registry, and README are already consistent
- commit the current repo changes with a clear message
- push to the configured `openyao-skills` GitHub repository
- only after a successful push, mark relevant skills as `published` and set `last_synced_at`

If the public repo exists but the local collection has new unpublished changes, use `needs-update` until the push is complete.

### 7. Report the result

Always report:

- whether the skill was accepted for the public collection
- the final collection path
- the registry status you wrote
- whether GitHub publication is still pending
- what still needs manual confirmation, if anything

## Output Expectations

When this skill completes a sync task, the result should leave the collection in a consistent state:

- public files exist under `skills/<slug>/`
- `registry/skills.json` is up to date
- `README.md` catalog matches the registry
- if a push was requested, the GitHub repo reflects the same state

## Decision Rules

- Prefer stable, explanatory slugs in kebab-case
- Do not publish raw private source directories without cleaning them
- Do not mark a skill as `published` unless it has actually been synced to GitHub
- If a published skill's source has changed locally, set `sync_status` to `needs-update`
