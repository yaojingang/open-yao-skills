#!/usr/bin/env python3

import argparse
import html
import json
import shlex
import sys
from datetime import datetime
from pathlib import Path

from scan_skills import build_payload, markdown_report, scan_root, sort_reports


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Run Skill Doctor and generate local HTML, JSON, and Markdown reports."
    )
    parser.add_argument("roots", nargs="+", help="Root directories to scan")
    parser.add_argument(
        "--output-root",
        help="Directory used to store generated reports. Defaults to <skill>/_skill_doctor_reports",
    )
    return parser.parse_args(argv)


def command_string(parts):
    return " ".join(shlex.quote(part) for part in parts)


def open_command(target: Path):
    if sys.platform == "darwin":
        return command_string(["open", str(target)])
    if sys.platform.startswith("linux"):
        return command_string(["xdg-open", str(target)])
    if sys.platform.startswith("win"):
        return 'cmd /c start "" "{}"'.format(str(target))
    return command_string(["printf", "%s\\n", str(target)])


def write_command(path: Path, command: str):
    path.write_text(
        "#!/bin/bash\nset -euo pipefail\n\n"
        + f'echo "$ {command}"\n'
        + f"{command}\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def render_html(report_dir: Path, payload: dict, commands: dict):
    skill_cards = []
    for item in payload["skills"]:
        if item["security_findings"]:
            findings = "<ul>" + "".join(
                "<li><strong>{severity}</strong> {category} at <code>{location}</code>: {message}</li>".format(
                    severity=html.escape(finding["severity"]),
                    category=html.escape(finding["category"]),
                    location=html.escape(
                        finding["path"] + (f":{finding['line']}" if finding.get("line") else "")
                    ),
                    message=html.escape(finding["message"]),
                )
                for finding in item["security_findings"][:10]
            ) + "</ul>"
        else:
            findings = "<p>none</p>"

        skill_cards.append(
            """
            <section class="card">
              <h2>{name}</h2>
              <p><strong>Path:</strong> <code>{path}</code></p>
              <p><strong>Purpose:</strong> {purpose}</p>
              <p><strong>Usage:</strong> <code>{usage}</code> / <code>{confidence}</code></p>
              <p><strong>Cleanup:</strong> <code>{cleanup}</code> -> <code>{direction}</code></p>
              <p><strong>Security:</strong> <code>{security}</code></p>
              <p><strong>Usage evidence:</strong> {usage_evidence}</p>
              <p><strong>Cleanup reasons:</strong> {cleanup_reasons}</p>
              <div><strong>Security findings:</strong>{findings}</div>
            </section>
            """.format(
                name=html.escape(item["declared_name"]),
                path=html.escape(item["path"]),
                purpose=html.escape(item["purpose_summary"]),
                usage=html.escape(item["usage_estimate"]),
                confidence=html.escape(item["usage_confidence"]),
                cleanup=html.escape(item["cleanup_level"]),
                direction=html.escape(item["cleanup_direction"]),
                security=html.escape(item["security_level"]),
                usage_evidence=html.escape("; ".join(item["usage_evidence"])),
                cleanup_reasons=html.escape("; ".join(item["cleanup_reasons"])),
                findings=findings,
            )
        )

    actions = "".join(
        '<li><a href="actions/{filename}">{label}</a><br><code>{command}</code></li>'.format(
            filename=html.escape(filename),
            label=html.escape(meta["label"]),
            command=html.escape(meta["command"]),
        )
        for filename, meta in commands.items()
    )

    html_text = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Skill Doctor Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; color: #111; background: #f7f4ee; }}
    h1, h2 {{ margin-bottom: 0.4rem; }}
    .meta, .card {{ background: #fff; border: 1px solid #ddd3c4; border-radius: 14px; padding: 20px; margin: 16px 0; }}
    code {{ background: #f2eee6; padding: 2px 6px; border-radius: 6px; }}
    ul {{ padding-left: 20px; }}
  </style>
</head>
<body>
  <h1>Skill Doctor Report</h1>
  <div class="meta">
    <p><strong>Generated at:</strong> {generated_at}</p>
    <p><strong>Scanned roots:</strong> {roots}</p>
    <p><strong>Skills found:</strong> {count}</p>
  </div>
  <div class="meta">
    <h2>Actions</h2>
    <ul>{actions}</ul>
  </div>
  {cards}
</body>
</html>
""".format(
        generated_at=html.escape(payload["generated_at_utc"]),
        roots=html.escape(", ".join(payload["scanned_roots"])),
        count=html.escape(str(payload["skill_count"])),
        actions=actions,
        cards="".join(skill_cards),
    )
    (report_dir / "report.html").write_text(html_text, encoding="utf-8")


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    roots = [Path(root).expanduser().resolve() for root in args.roots]
    script_path = Path(__file__).resolve()
    skill_root = script_path.parents[1]
    output_root = (
        Path(args.output_root).expanduser().resolve()
        if args.output_root
        else skill_root / "_skill_doctor_reports"
    )
    report_dir = output_root / timestamp()
    actions_dir = report_dir / "actions"
    actions_dir.mkdir(parents=True, exist_ok=True)

    all_reports = []
    for root in roots:
        if not root.exists():
            print(f"[ERROR] Root does not exist: {root}", file=sys.stderr)
            return 1
        all_reports.extend(scan_root(root))

    sort_reports(all_reports)
    payload = build_payload(roots, all_reports)
    (report_dir / "report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (report_dir / "report.md").write_text(markdown_report(roots, all_reports) + "\n", encoding="utf-8")

    commands = {
        "rescan.command": {
            "label": "Rescan the same roots",
            "command": command_string([sys.executable, str(script_path), *[str(root) for root in roots]]),
        },
        "open-report-folder.command": {
            "label": "Open the report folder",
            "command": open_command(report_dir),
        },
        "raw-json.command": {
            "label": "Open raw JSON report",
            "command": open_command(report_dir / "report.json"),
        },
    }

    for filename, meta in commands.items():
        write_command(actions_dir / filename, meta["command"])

    render_html(report_dir, payload, commands)
    print(report_dir / "report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
