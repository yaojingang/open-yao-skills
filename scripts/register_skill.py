#!/usr/bin/env python3

import argparse
import json
from datetime import date
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Upsert a skill record into registry/skills.json."
    )
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--source-local-path", required=True)
    parser.add_argument("--collection-path", required=True)
    parser.add_argument("--lifecycle", default="active")
    parser.add_argument("--sync-status", default="local-only")
    parser.add_argument("--github-repo", default="openyao-skills")
    parser.add_argument("--github-url", default="")
    parser.add_argument("--license", default="TBD")
    parser.add_argument("--tags", default="")
    parser.add_argument("--last-synced-at", default="")
    return parser.parse_args()


def load_registry(path: Path):
    if not path.exists():
        return {"repo_name": "openyao-skills", "updated_at": "", "skills": []}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    args = parse_args()
    today = date.today().isoformat()
    repo_root = Path(__file__).resolve().parents[1]
    registry_path = repo_root / "registry" / "skills.json"
    registry = load_registry(registry_path)

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    record = {
        "slug": args.slug,
        "title": args.title,
        "summary": args.summary,
        "source_local_path": args.source_local_path,
        "collection_path": args.collection_path,
        "lifecycle": args.lifecycle,
        "sync_status": args.sync_status,
        "github_repo": args.github_repo,
        "github_url": args.github_url,
        "license": args.license,
        "tags": tags,
        "last_synced_at": args.last_synced_at or None,
        "updated_at": today,
    }

    skills = registry.setdefault("skills", [])
    existing = next((item for item in skills if item.get("slug") == args.slug), None)
    if existing is None:
        skills.append(record)
    else:
        existing.update(record)

    registry["repo_name"] = registry.get("repo_name", "openyao-skills")
    registry["updated_at"] = today
    skills.sort(key=lambda item: item["slug"])

    with registry_path.open("w", encoding="utf-8") as handle:
        json.dump(registry, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Updated registry entry: {args.slug}")


if __name__ == "__main__":
    main()

