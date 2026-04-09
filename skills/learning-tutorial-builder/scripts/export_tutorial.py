#!/usr/bin/env python3
"""Export one markdown tutorial to docx, html, and pdf.

The script assumes markdown is the canonical source. It uses pandoc for docx and
html generation, then prints the html to pdf with headless Chromium.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required tool: {name}")
    return path


def find_pdf_browser() -> str:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if os.access(candidate, os.X_OK):
            return candidate

    for name in ["google-chrome", "chromium", "chromium-browser", "msedge", "brave"]:
        path = shutil.which(name)
        if path:
            return path

    raise SystemExit("Missing PDF browser: install Google Chrome, Microsoft Edge, Brave, or Chromium.")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def export_docx(pandoc: str, source: Path, target: Path, reference_doc: Path | None, title: str | None) -> None:
    cmd = [pandoc, str(source), "-o", str(target)]
    if reference_doc:
        cmd.append(f"--reference-doc={reference_doc}")
    if title:
        cmd.extend(["-M", f"title={title}"])
    run(cmd)


def export_html(
    pandoc: str,
    source: Path,
    target: Path,
    title: str | None,
    css: Path | None,
) -> None:
    cmd = [
        pandoc,
        str(source),
        "--embed-resources",
        "--standalone",
        "--toc",
        "-o",
        str(target),
    ]
    if title:
        cmd.extend(["-M", f"title={title}"])
    if css:
        cmd.extend(["-c", str(css)])
    run(cmd)


def export_pdf(browser: str, html_file: Path, pdf_file: Path) -> None:
    html_uri = html_file.resolve().as_uri()
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=3000",
        f"--print-to-pdf={pdf_file}",
        html_uri,
    ]
    run(cmd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a tutorial markdown file to docx, html, and pdf.")
    parser.add_argument("source", help="Path to the tutorial markdown file.")
    parser.add_argument("output_dir", help="Directory for exported artifacts.")
    parser.add_argument("--title", default=None, help="Optional document title override.")
    parser.add_argument("--basename", default=None, help="Optional base filename for exported files.")
    parser.add_argument("--reference-doc", default=None, help="Optional pandoc reference docx.")
    parser.add_argument("--css", default=None, help="Optional CSS file for html export.")
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=["docx", "html", "pdf"],
        default=["docx", "html", "pdf"],
        help="Which formats to generate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"Source file not found: {source}")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    base = args.basename or source.stem
    title = args.title or source.stem.replace("-", " ").replace("_", " ").title()
    reference_doc = Path(args.reference_doc).resolve() if args.reference_doc else None
    css = Path(args.css).resolve() if args.css else None

    pandoc = require_tool("pandoc")
    browser = find_pdf_browser() if "pdf" in args.formats else ""

    html_target = output_dir / f"{base}.html"

    if "docx" in args.formats:
        export_docx(pandoc, source, output_dir / f"{base}.docx", reference_doc, title)

    if "html" in args.formats or "pdf" in args.formats:
        export_html(pandoc, source, html_target, title, css)

    if "pdf" in args.formats:
        export_pdf(browser, html_target, output_dir / f"{base}.pdf")

    print(f"Export complete for {source.name}")
    for fmt in args.formats:
        print(f"- {fmt}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode)
