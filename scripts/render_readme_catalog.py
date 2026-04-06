#!/usr/bin/env python3

import json
from pathlib import Path


START_MARKER = "<!-- catalog:start -->"
END_MARKER = "<!-- catalog:end -->"


def format_source_path(source_path: str, repo_root: Path) -> str:
    source = Path(source_path)
    try:
        relative = source.resolve().relative_to(repo_root.resolve())
        return "[{path}]({path})".format(path=relative.as_posix())
    except ValueError:
        return "`external-local-source`"


def render_table(skills, repo_root: Path):
    lines = [
        START_MARKER,
        "| Skill | Guide | Lifecycle | Sync | Collection Path | Source Path | GitHub |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for skill in skills:
        collection = "[{path}]({path})".format(path=skill["collection_path"])
        source = format_source_path(skill["source_local_path"], repo_root)
        guide = (
            "[guide]({path})".format(path=skill["guide_path"])
            if skill.get("guide_path")
            else "pending"
        )
        github = (
            "[link]({url})".format(url=skill["github_url"])
            if skill["github_url"]
            else "pending"
        )
        lines.append(
            "| [{slug}]({collection_path}/SKILL.md) | {guide} | `{lifecycle}` | `{sync}` | {collection} | {source} | {github} |".format(
                slug=skill["slug"],
                guide=guide,
                lifecycle=skill["lifecycle"],
                sync=skill["sync_status"],
                collection=collection,
                collection_path=skill["collection_path"],
                source=source,
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
    table = render_table(skills, repo_root)

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
