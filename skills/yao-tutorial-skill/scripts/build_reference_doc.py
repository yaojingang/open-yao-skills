#!/usr/bin/env python3
"""Create an editorial Word reference document for tutorial exports."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def ensure_child(parent: ET.Element, name: str) -> ET.Element:
    child = parent.find(w_tag(name))
    if child is None:
        child = ET.SubElement(parent, w_tag(name))
    return child


def set_attr(element: ET.Element, name: str, value: str) -> None:
    element.set(w_tag(name), value)


def patch_style(style: ET.Element, latin: str, east_asia: str, size_half_points: str, color: str = "172033") -> None:
    rpr = ensure_child(style, "rPr")
    rfonts = ensure_child(rpr, "rFonts")
    for attr in ["ascii", "hAnsi", "cs"]:
        set_attr(rfonts, attr, latin)
    set_attr(rfonts, "eastAsia", east_asia)
    sz = ensure_child(rpr, "sz")
    set_attr(sz, "val", size_half_points)
    szcs = ensure_child(rpr, "szCs")
    set_attr(szcs, "val", size_half_points)
    color_node = ensure_child(rpr, "color")
    set_attr(color_node, "val", color)


def patch_reference_docx(target: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        with zipfile.ZipFile(target, "r") as archive:
            archive.extractall(tmp_path)

        styles_path = tmp_path / "word" / "styles.xml"
        tree = ET.parse(styles_path)
        root = tree.getroot()

        doc_defaults = root.find(w_tag("docDefaults"))
        if doc_defaults is not None:
            rpr_default = ensure_child(doc_defaults, "rPrDefault")
            rpr = ensure_child(rpr_default, "rPr")
            rfonts = ensure_child(rpr, "rFonts")
            for attr in ["ascii", "hAnsi", "cs"]:
                set_attr(rfonts, attr, "Georgia")
            set_attr(rfonts, "eastAsia", "Noto Sans CJK SC")

        style_specs = {
            "Normal": ("Georgia", "Noto Sans CJK SC", "22", "172033"),
            "BodyText": ("Georgia", "Noto Sans CJK SC", "22", "172033"),
            "Title": ("Georgia", "Noto Serif CJK SC", "48", "172033"),
            "Heading1": ("Georgia", "Noto Serif CJK SC", "40", "172033"),
            "Heading2": ("Georgia", "Noto Serif CJK SC", "32", "172033"),
            "Heading3": ("Georgia", "Noto Serif CJK SC", "26", "172033"),
            "Caption": ("Arial", "Noto Sans CJK SC", "18", "697083"),
        }

        for style in root.findall(w_tag("style")):
            style_id = style.get(w_tag("styleId"))
            if style_id in style_specs:
                patch_style(style, *style_specs[style_id])

        tree.write(styles_path, encoding="UTF-8", xml_declaration=True)

        patched = target.with_suffix(".patched.docx")
        with zipfile.ZipFile(patched, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in tmp_path.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp_path).as_posix())
        shutil.move(patched, target)


def build_reference_doc_with_pandoc(target: Path) -> None:
    data = subprocess.check_output(["pandoc", "--print-default-data-file", "reference.docx"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    patch_reference_docx(target)


def set_style_font(style, latin: str, east_asia: str, size_pt: float | None = None, bold: bool | None = None) -> None:
    from docx.oxml.ns import qn
    from docx.shared import Pt

    font = style.font
    font.name = latin
    if size_pt:
        font.size = Pt(size_pt)
    if bold is not None:
        font.bold = bold
    style.element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)


def build_reference_doc(target: Path) -> None:
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Cm, Pt, RGBColor
    except Exception:
        build_reference_doc_with_pandoc(target)
        return

    document = Document()
    section = document.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.35)
    section.right_margin = Cm(2.35)
    section.header_distance = Cm(0)
    section.footer_distance = Cm(0)

    styles = document.styles
    set_style_font(styles["Normal"], "Georgia", "Noto Sans CJK SC", 11.0, False)
    styles["Normal"].paragraph_format.line_spacing = 1.48
    styles["Normal"].paragraph_format.space_after = Pt(6)

    for name, size, after in [
        ("Title", 24, 14),
        ("Heading 1", 20, 12),
        ("Heading 2", 16, 10),
        ("Heading 3", 13, 8),
    ]:
        set_style_font(styles[name], "Georgia", "Noto Serif CJK SC", size, True)
        styles[name].font.color.rgb = RGBColor(23, 32, 51)
        styles[name].paragraph_format.space_before = Pt(after)
        styles[name].paragraph_format.space_after = Pt(6)
        styles[name].paragraph_format.keep_with_next = True

    set_style_font(styles["Body Text"], "Georgia", "Noto Sans CJK SC", 11.0, False)
    styles["Body Text"].paragraph_format.line_spacing = 1.48
    styles["Body Text"].paragraph_format.space_after = Pt(6)

    if "Caption" in styles:
        set_style_font(styles["Caption"], "Arial", "Noto Sans CJK SC", 9.0, False)
        styles["Caption"].font.color.rgb = RGBColor(105, 112, 131)
        styles["Caption"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if "Source ID" not in styles:
        source_style = styles.add_style("Source ID", WD_STYLE_TYPE.CHARACTER)
        set_style_font(source_style, "Courier New", "Noto Sans Mono CJK SC", 9.0, False)
        source_style.font.color.rgb = RGBColor(31, 78, 121)

    document.add_paragraph("Reference document for yao-tutorial-skill exports.", style="Normal")
    target.parent.mkdir(parents=True, exist_ok=True)
    document.save(target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an editorial DOCX reference file.")
    parser.add_argument("target", help="Path to write the reference docx.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_reference_doc(Path(args.target).resolve())
    print(f"Reference doc written to {Path(args.target).resolve()}")


if __name__ == "__main__":
    main()
