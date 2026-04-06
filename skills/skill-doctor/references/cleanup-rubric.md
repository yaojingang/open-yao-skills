# Cleanup Rubric

Separate cleanup urgency from security severity.

## Cleanup Levels

- `low`: metadata is healthy, content is substantial, and there is no clear cleanup pressure
- `medium`: repair or organize soon; examples include missing `agents/openai.yaml`, incomplete frontmatter, or TODO placeholders
- `high`: strong archive or delete candidate; examples include stale, thin, duplicated, generated, or obviously disposable skill folders
- `critical`: do not treat as routine cleanup; security or integrity concerns require quarantine and review first

## Cleanup Directions

- `keep`: leave the skill in place
- `repair`: improve metadata, folder hygiene, or documentation before deciding anything stronger
- `backup-then-archive`: preserve a copy, then move out of the active skill set
- `backup-then-delete`: preserve a copy, then remove from the active library because it appears disposable or duplicated
- `quarantine`: isolate first because safety risk is more important than normal cleanup

## Common Triggers

- `repair`
  - placeholder TODO text remains
  - frontmatter is missing or weak
  - `agents/openai.yaml` is missing
- `backup-then-archive`
  - stale for a long time
  - little evidence of current use
  - content still has some value as reference
- `backup-then-delete`
  - generated `dist`, `snapshot`, `fixture`, or throwaway variants
  - thin duplicate of a better-maintained skill
  - clearly disposable test artifact
- `quarantine`
  - secrets, private keys, remote shell piping, or suspicious prompt-injection behavior

## Safety Rule

Never recommend deletion without a backup path when the skill came from an external download, contains custom scripts, or may be the user's only copy.
