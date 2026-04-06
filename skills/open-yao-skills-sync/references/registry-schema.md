# Registry Schema

`registry/skills.json` stores one object per collected skill.

## Top-level shape

```json
{
  "repo_name": "open-yao-skills",
  "updated_at": "YYYY-MM-DD",
  "skills": []
}
```

## Skill record fields

- `slug`: stable kebab-case identifier used as the collection directory name
- `title`: human-facing name
- `summary`: one-line description of why the skill exists in the collection
- `source_local_path`: original local source path outside or inside the collection
- `collection_path`: relative path inside `open-yao-skills`
- `lifecycle`: `active`, `deprecated`, or `archived`
- `sync_status`: `local-only`, `staged`, `published`, or `needs-update`
- `github_repo`: normally `open-yao-skills`
- `github_url`: public GitHub URL when available
- `guide_path`: path to the human-facing usage guide inside `docs/skills/`
- `license`: intended license for the public copy
- `tags`: flat tag list
- `last_synced_at`: `YYYY-MM-DD` or `null`
- `updated_at`: last local registry update date

## Usage rule

When a skill is imported or refreshed:

1. Update the record
2. Keep `collection_path` stable if possible
3. Regenerate README after the registry change
