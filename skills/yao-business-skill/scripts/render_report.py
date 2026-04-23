#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


PLACEHOLDER = "__REPORT_JSON__"


def render_html(template_path: Path, report_path: Path, output_path: Path) -> None:
    template = template_path.read_text(encoding="utf-8")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if PLACEHOLDER not in template:
        raise ValueError(f"Template missing placeholder: {PLACEHOLDER}")
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = template.replace(PLACEHOLDER, payload, 1)
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Yao Business Skill HTML report from a JSON payload.")
    parser.add_argument("report_json", help="Path to the report JSON file")
    parser.add_argument(
        "--template",
        default=None,
        help="Optional HTML template path. Defaults to templates/report-skeleton.html beside this script.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output HTML path. Defaults to the JSON path with .html suffix.",
    )
    args = parser.parse_args()

    report_path = Path(args.report_json).resolve()
    script_dir = Path(__file__).resolve().parent
    template_path = Path(args.template).resolve() if args.template else script_dir.parent / "templates" / "report-skeleton.html"
    output_path = Path(args.output).resolve() if args.output else report_path.with_suffix(".html")

    render_html(template_path, report_path, output_path)
    print(json.dumps({"ok": True, "output_html": str(output_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
