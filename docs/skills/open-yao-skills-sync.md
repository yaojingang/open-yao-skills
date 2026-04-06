# Open Yao Skills Sync

## What It Does

`open-yao-skills-sync` manages the `open-yao-skills` public collection itself.

Use it when you want to:

- decide whether a local skill is suitable for open source release
- import a cleaned public copy into this repo
- update registry metadata and GitHub sync state
- refresh the homepage catalog and navigation after changes

## Main Workflow

1. Inspect the local source skill and identify private or generated outputs.
2. Copy only the public source files into `skills/<slug>/`.
3. Update `registry/skills.json`.
4. Add or update `docs/skills/<slug>.md`.
5. Render the README catalog.
6. Commit and push when the public repo should be updated.

## Important Rule

Generated local outputs should stay local by default. Reports, caches, exported artifacts, and machine-specific helper files should not be committed unless they are intentionally prepared as safe public examples.

