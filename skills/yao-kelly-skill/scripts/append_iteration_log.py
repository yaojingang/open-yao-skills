#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append one iteration entry to the Kelly skill change log."
    )
    parser.add_argument(
        "--log-file",
        default="history/CHANGELOG.md",
        help="Path to the markdown log file.",
    )
    parser.add_argument("--timestamp", help="Optional ISO timestamp override.")
    parser.add_argument("--summary", required=True, help="One-line summary.")
    parser.add_argument("--reason", default="", help="Why this iteration was made.")
    parser.add_argument("--file", action="append", dest="files", default=[], help="Changed file.")
    parser.add_argument(
        "--assumption",
        action="append",
        default=[],
        help="Assumption made during the iteration.",
    )
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        help="Verification step or check performed.",
    )
    parser.add_argument(
        "--next-step",
        action="append",
        dest="next_steps",
        default=[],
        help="Suggested follow-up step.",
    )
    return parser.parse_args()


def format_list(label: str, items: list[str]) -> list[str]:
    if not items:
        return [f"- {label}: none"]
    joined = ", ".join(f"`{item}`" for item in items)
    return [f"- {label}: {joined}"]


def main() -> int:
    args = parse_args()
    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = args.timestamp or datetime.now().astimezone().isoformat(timespec="seconds")
    lines: list[str] = [f"## {timestamp}", f"- Summary: {args.summary}"]
    if args.reason:
        lines.append(f"- Reason: {args.reason}")
    lines.extend(format_list("Files", args.files))
    lines.extend(format_list("Assumptions", args.assumption))
    lines.extend(format_list("Checks", args.check))
    lines.extend(format_list("Next steps", args.next_steps))
    entry = "\n".join(lines) + "\n"

    if log_path.exists():
        current = log_path.read_text(encoding="utf-8").rstrip() + "\n\n"
    else:
        current = "# Kelly Skill Iteration Log\n\nAppend only. Log every package-level change.\n\n"
    log_path.write_text(current + entry, encoding="utf-8")

    print(
        json.dumps(
            {"ok": True, "log_file": str(log_path), "timestamp": timestamp},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
