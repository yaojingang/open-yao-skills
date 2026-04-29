#!/usr/bin/env python3
"""Export one markdown tutorial to docx, html, and pdf."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from html import escape
from xml.etree import ElementTree as ET
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


def has_weasyprint() -> bool:
    try:
        import weasyprint  # noqa: F401
    except Exception:
        return False
    return True


def create_default_reference_doc(target: Path) -> Path | None:
    try:
        from build_reference_doc import build_reference_doc
    except Exception as exc:
        print(f"Skipping default DOCX reference style: {exc}", file=sys.stderr)
        return None

    build_reference_doc(target)
    return target


def export_docx(
    pandoc: str,
    source: Path,
    target: Path,
    reference_doc: Path | None,
    title: str | None,
    document_date: str | None,
) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        export_source = source
        if document_date:
            export_source = Path(tmp_dir) / source.name
            export_source.write_text(insert_markdown_date(source.read_text(encoding="utf-8"), document_date), encoding="utf-8")

        cmd = [pandoc, str(export_source), "--resource-path", str(source.parent), "-o", str(target)]
        if reference_doc:
            cmd.append(f"--reference-doc={reference_doc}")
        run(cmd)
    strip_docx_headers_footers(target)
    style_docx_tables(target)


def export_html(
    pandoc: str,
    source: Path,
    target: Path,
    title: str | None,
    css: Path | None,
    document_date: str | None,
) -> None:
    cmd = [
        pandoc,
        str(source),
        "--resource-path",
        str(source.parent),
        "--embed-resources",
        "--standalone",
        "--toc",
        "-o",
        str(target),
    ]
    if title:
        cmd.extend(["-M", f"pagetitle={title}"])
    if css:
        cmd.extend(["-c", str(css)])
    run(cmd)
    postprocess_html(target, document_date)


def postprocess_html(target: Path, document_date: str | None) -> None:
    html = target.read_text(encoding="utf-8")
    html = wrap_html_tables(html)
    if document_date and 'class="doc-date"' not in html:
        date_html = f'\n<p class="doc-date">更新日期：{escape(document_date)}</p>'
        html = re.sub(r"(<h1\b[^>]*>.*?</h1>)", rf"\1{date_html}", html, count=1, flags=re.S)
    html = wrap_report_shell(html)
    target.write_text(html, encoding="utf-8")


def wrap_html_tables(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        prefix = html[max(0, match.start() - 120):match.start()]
        if 'class="table-wrap"' in prefix:
            return match.group(0)
        return f'<div class="table-wrap">{match.group(0)}</div>'

    return re.sub(r"<table\b[^>]*>.*?</table>", replace, html, flags=re.S | re.I)


def wrap_report_shell(html: str) -> str:
    if 'class="report-shell"' in html:
        return html

    toc_pattern = re.compile(r"(<body\b[^>]*>\s*)(<nav\b[^>]*id=\"TOC\"[^>]*>.*?</nav>\s*)", re.S)
    if toc_pattern.search(html):
        html = toc_pattern.sub(r'\1<div class="report-shell">\n\2<main class="article-body">\n', html, count=1)
        return re.sub(r"\s*</body>", "\n</main>\n</div>\n</body>", html, count=1)

    html = re.sub(r"(<body\b[^>]*>)", r'\1\n<div class="report-shell report-shell--no-toc">\n<main class="article-body">', html, count=1)
    return re.sub(r"\s*</body>", "\n</main>\n</div>\n</body>", html, count=1)


def insert_markdown_date(markdown: str, document_date: str) -> str:
    if "更新日期：" in markdown:
        return markdown
    return re.sub(r"(^# .+?$)", rf"\1\n\n更新日期：{document_date}", markdown, count=1, flags=re.M)


def default_document_date() -> str:
    today = date.today()
    return f"{today.year}年{today.month}月{today.day}日"


def strip_docx_headers_footers(docx_file: Path) -> None:
    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", w_ns)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(docx_file, "r") as archive:
            archive.extractall(tmp_path)

        document_xml = tmp_path / "word" / "document.xml"
        if document_xml.exists():
            tree = ET.parse(document_xml)
            root = tree.getroot()
            for sect_pr in root.findall(f".//{{{w_ns}}}sectPr"):
                for child in list(sect_pr):
                    if child.tag in {f"{{{w_ns}}}headerReference", f"{{{w_ns}}}footerReference"}:
                        sect_pr.remove(child)
            tree.write(document_xml, encoding="UTF-8", xml_declaration=True)

        rels_xml = tmp_path / "word" / "_rels" / "document.xml.rels"
        if rels_xml.exists():
            tree = ET.parse(rels_xml)
            root = tree.getroot()
            for rel in list(root):
                target = rel.attrib.get("Target", "")
                rel_type = rel.attrib.get("Type", "")
                if "header" in target or "footer" in target or rel_type.endswith("/header") or rel_type.endswith("/footer"):
                    root.remove(rel)
            tree.write(rels_xml, encoding="UTF-8", xml_declaration=True)

        for path in list((tmp_path / "word").glob("header*.xml")) + list((tmp_path / "word").glob("footer*.xml")):
            path.unlink(missing_ok=True)

        patched = docx_file.with_suffix(".clean.docx")
        with zipfile.ZipFile(patched, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in tmp_path.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp_path).as_posix())
        shutil.move(patched, docx_file)


def w_tag(name: str) -> str:
    return f"{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{name}"


def ensure_xml_child(parent: ET.Element, tag: str, first: bool = False) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.Element(tag)
        if first:
            parent.insert(0, child)
        else:
            parent.append(child)
    return child


def set_w_attr(element: ET.Element, name: str, value: str) -> None:
    element.set(w_tag(name), value)


def set_cell_shading(cell: ET.Element, fill: str) -> None:
    tc_pr = ensure_xml_child(cell, w_tag("tcPr"), first=True)
    shd = ensure_xml_child(tc_pr, w_tag("shd"))
    set_w_attr(shd, "fill", fill)


def style_docx_tables(docx_file: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(docx_file, "r") as archive:
            archive.extractall(tmp_path)

        document_xml = tmp_path / "word" / "document.xml"
        if document_xml.exists():
            tree = ET.parse(document_xml)
            root = tree.getroot()
            for table in root.findall(f".//{w_tag('tbl')}"):
                tbl_pr = ensure_xml_child(table, w_tag("tblPr"), first=True)
                borders = ensure_xml_child(tbl_pr, w_tag("tblBorders"))
                for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
                    border = ensure_xml_child(borders, w_tag(side))
                    set_w_attr(border, "val", "single")
                    set_w_attr(border, "sz", "6")
                    set_w_attr(border, "space", "0")
                    set_w_attr(border, "color", "E8E5DA")

                cell_mar = ensure_xml_child(tbl_pr, w_tag("tblCellMar"))
                for side in ["top", "left", "bottom", "right"]:
                    margin = ensure_xml_child(cell_mar, w_tag(side))
                    set_w_attr(margin, "w", "120")
                    set_w_attr(margin, "type", "dxa")

                rows = table.findall(w_tag("tr"))
                for row_index, row in enumerate(rows):
                    fill = "EEF2F7" if row_index == 0 else ("FAF9F5" if row_index % 2 else "F7F5EE")
                    for cell in row.findall(w_tag("tc")):
                        set_cell_shading(cell, fill)
                        if row_index == 0:
                            for run_pr in cell.findall(f".//{w_tag('rPr')}"):
                                ensure_xml_child(run_pr, w_tag("b"))
            tree.write(document_xml, encoding="UTF-8", xml_declaration=True)

        patched = docx_file.with_suffix(".tables.docx")
        with zipfile.ZipFile(patched, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in tmp_path.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp_path).as_posix())
        shutil.move(patched, docx_file)


def export_pdf(browser: str, html_file: Path, pdf_file: Path) -> None:
    try:
        from weasyprint import HTML
    except Exception:
        export_pdf_with_browser(browser, html_file, pdf_file)
        return

    HTML(filename=str(html_file), base_url=str(html_file.parent)).write_pdf(str(pdf_file))


def export_pdf_with_browser(browser: str, html_file: Path, pdf_file: Path) -> None:
    if not browser:
        browser = find_pdf_browser()
    html_uri = html_file.resolve().as_uri()
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
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
    parser.add_argument("--date", default=None, help="Date text shown below the HTML/PDF title. Defaults to today's local date.")
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
    document_date = args.date or default_document_date()
    reference_doc = Path(args.reference_doc).resolve() if args.reference_doc else None
    css = Path(args.css).resolve() if args.css else None

    if reference_doc and not reference_doc.exists():
        raise SystemExit(f"Reference doc not found: {reference_doc}")
    if css and not css.exists():
        raise SystemExit(f"CSS file not found: {css}")

    pandoc = require_tool("pandoc")
    browser = find_pdf_browser() if "pdf" in args.formats and not has_weasyprint() else ""
    html_target = output_dir / f"{base}.html"

    if "docx" in args.formats and not reference_doc:
        reference_doc = create_default_reference_doc(output_dir / f"{base}-reference.docx")

    if "docx" in args.formats:
        export_docx(pandoc, source, output_dir / f"{base}.docx", reference_doc, title, document_date)

    if "html" in args.formats or "pdf" in args.formats:
        export_html(pandoc, source, html_target, title, css, document_date)

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
