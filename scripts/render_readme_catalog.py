#!/usr/bin/env python3

import json
from pathlib import Path


START_MARKER = "<!-- catalog:start -->"
END_MARKER = "<!-- catalog:end -->"


def render_table(skills):
    lines = [
        START_MARKER,
        "| Skill | Lifecycle | Sync | Collection Path | Source Path | GitHub |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for skill in skills:
        github = skill["github_url"] or "pending"
        lines.append(
            "| `{slug}` | `{lifecycle}` | `{sync}` | `{collection}` | `{source}` | `{github}` |".format(
                slug=skill["slug"],
                lifecycle=skill["lifecycle"],
                sync=skill["sync_status"],
                collection=skill["collection_path"],
                source=skill["source_local_path"],
                github=github,
            )
        )

    lines.append(END_MARKER)
    return "\n".join(lines)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    registry_path = repo_root / "registry" / "skills.json"
    readme_path = repo_root / "README.md"

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    skills = sorted(registry.get("skills", []), key=lambda item: item["slug"])
    table = render_table(skills)

    readme = readme_path.read_text(encoding="utf-8")
    if START_MARKER not in readme or END_MARKER not in readme:
        raise SystemExit("README catalog markers not found.")

    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER) + len(END_MARKER)
    updated = readme[:start] + table + readme[end:]
    readme_path.write_text(updated, encoding="utf-8")
    print(f"Rendered catalog for {len(skills)} skill(s).")


if __name__ == "__main__":
    main()

