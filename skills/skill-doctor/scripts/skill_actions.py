#!/usr/bin/env python3

import argparse
import shutil
import tarfile
from datetime import datetime
from pathlib import Path


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def unique_destination(dest_root, name):
    candidate = dest_root / name
    if not candidate.exists():
        return candidate
    return dest_root / f"{name}_{timestamp()}"


def backup_skill(skill_path, backup_root):
    backup_root.mkdir(parents=True, exist_ok=True)
    archive_path = backup_root / f"{skill_path.name}_{timestamp()}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as handle:
        handle.add(skill_path, arcname=skill_path.name)
    return archive_path


def confirm(prompt):
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def move_skill(skill_path, dest_root):
    dest_root.mkdir(parents=True, exist_ok=True)
    destination = unique_destination(dest_root, skill_path.name)
    shutil.move(str(skill_path), str(destination))
    return destination


def command_backup(args):
    skill_path = Path(args.skill_path).expanduser().resolve()
    backup_root = Path(args.backup_root).expanduser().resolve()
    archive_path = backup_skill(skill_path, backup_root)
    print(f"Backup created: {archive_path}")


def command_move(args, action_label):
    skill_path = Path(args.skill_path).expanduser().resolve()
    backup_root = Path(args.backup_root).expanduser().resolve() if args.backup_root else None
    dest_root = Path(args.dest_root).expanduser().resolve()

    backup_path = None
    if backup_root:
        backup_path = backup_skill(skill_path, backup_root)
        print(f"Backup created: {backup_path}")

    if not confirm(f"{action_label} {skill_path} -> {dest_root}?"):
        print("Cancelled.")
        return

    destination = move_skill(skill_path, dest_root)
    print(f"Moved to: {destination}")
    if backup_path:
        print(f"Backup kept at: {backup_path}")


def main():
    parser = argparse.ArgumentParser(description="Apply Skill Doctor actions to a skill folder.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("skill_path")
    backup_parser.add_argument("--backup-root", required=True)

    archive_parser = subparsers.add_parser("backup-archive")
    archive_parser.add_argument("skill_path")
    archive_parser.add_argument("--backup-root", required=True)
    archive_parser.add_argument("--dest-root", required=True)

    quarantine_parser = subparsers.add_parser("quarantine")
    quarantine_parser.add_argument("skill_path")
    quarantine_parser.add_argument("--backup-root", required=True)
    quarantine_parser.add_argument("--dest-root", required=True)

    delete_parser = subparsers.add_parser("backup-delete")
    delete_parser.add_argument("skill_path")
    delete_parser.add_argument("--backup-root", required=True)
    delete_parser.add_argument("--dest-root", required=True)

    args = parser.parse_args()

    if args.command == "backup":
        command_backup(args)
    elif args.command == "backup-archive":
        command_move(args, "Archive")
    elif args.command == "quarantine":
        command_move(args, "Quarantine")
    elif args.command == "backup-delete":
        command_move(args, "Soft-delete")


if __name__ == "__main__":
    main()
