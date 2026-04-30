#!/usr/bin/env python3
"""Validate a generated tutorial package before delivery."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    status: str
    message: str


class Validator:
    def __init__(self, package_dir: Path, basename: str, formats: list[str], check_deps: bool, strict: bool) -> None:
        self.package_dir = package_dir
        self.basename = basename
        self.formats = formats
        self.check_deps = check_deps
        self.strict = strict
        self.checks: list[Check] = []
        self.chapter_numbers: list[int] = []
        self.markdown_image_refs: list[str] = []

    def add(self, status: str, message: str) -> None:
        self.checks.append(Check(status, message))

    def pass_(self, message: str) -> None:
        self.add("PASS", message)

    def warn(self, message: str) -> None:
        self.add("WARN", message)

    def fail(self, message: str) -> None:
        self.add("FAIL", message)

    def run(self) -> int:
        if not self.package_dir.exists():
            self.fail(f"Package directory not found: {self.package_dir}")
            return self.finish()

        if self.check_deps:
            self.validate_dependencies()

        self.validate_package_files()
        self.validate_markdown()
        self.validate_visuals()
        self.validate_html()
        self.validate_docx()
        self.validate_pdf()
        self.validate_no_absolute_paths()
        self.validate_public_provenance_hygiene()

        return self.finish()

    def finish(self) -> int:
        failures = [check for check in self.checks if check.status == "FAIL"]
        warnings = [check for check in self.checks if check.status == "WARN"]
        for check in self.checks:
            print(f"[{check.status}] {check.message}")
        print(f"\nSummary: {len(failures)} failures, {len(warnings)} warnings, {len(self.checks)} checks")
        if failures:
            return 1
        if self.strict and warnings:
            return 2
        return 0

    def validate_dependencies(self) -> None:
        if shutil.which("pandoc"):
            self.pass_("pandoc is available")
        else:
            self.fail("pandoc is missing; DOCX and HTML export will fail")

        browser = find_browser()
        if browser:
            self.pass_(f"Chromium-family browser is available: {browser}")
        else:
            self.warn("No Chrome/Edge/Brave/Chromium browser found; screenshots and PDF fallback may fail")

        if can_import("PIL"):
            self.pass_("Pillow is available for exact screenshot cropping")
        else:
            self.warn("Pillow is missing; screenshot cropping cannot be validated or performed exactly")

        if can_import("weasyprint"):
            self.pass_("WeasyPrint is available for clean PDF export")
        else:
            self.warn("WeasyPrint is missing; PDF export will rely on browser fallback")

        if can_import("docx"):
            self.pass_("python-docx is available for default Word reference generation")
        else:
            self.warn("python-docx is missing; default Word reference style generation may be skipped")

    def validate_package_files(self) -> None:
        required = [
            "brief.json",
            "tutorial.md",
            "outline.md",
            "research/evidence-map.md",
            "visuals/visual-spec.json",
            "visuals/index.html",
        ]
        for relative in required:
            path = self.package_dir / relative
            if path.exists():
                self.pass_(f"Found {relative}")
            else:
                self.fail(f"Missing {relative}")

        source_register = self.package_dir / "research/source-register.md"
        user_register = self.package_dir / "research/user-materials-register.md"
        if source_register.exists() or user_register.exists():
            self.pass_("Found at least one research register")
        else:
            self.warn("No source register or user material register found")

        exports_dir = self.package_dir / "exports"
        if "html" in self.formats:
            self.require_file(exports_dir / f"{self.basename}.html", "HTML export")
        if "docx" in self.formats:
            self.require_file(exports_dir / f"{self.basename}.docx", "DOCX export")
        if "pdf" in self.formats:
            self.require_file(exports_dir / f"{self.basename}.pdf", "PDF export")

    def require_file(self, path: Path, label: str) -> None:
        if path.exists() and path.stat().st_size > 0:
            self.pass_(f"{label} exists")
        elif path.exists():
            self.fail(f"{label} exists but is empty: {path.relative_to(self.package_dir)}")
        else:
            self.fail(f"{label} missing: {path.relative_to(self.package_dir)}")

    def validate_markdown(self) -> None:
        tutorial = self.package_dir / "tutorial.md"
        if not tutorial.exists():
            return
        text = read_text(tutorial)

        h1_count = len(re.findall(r"^#\s+", text, flags=re.M))
        if h1_count == 1:
            self.pass_("tutorial.md has one H1 title")
        else:
            self.warn(f"tutorial.md should have one H1 title; found {h1_count}")

        chapter_matches = list(re.finditer(r"^##\s+第\s*(\d+)\s*章\b", text, flags=re.M))
        chapters = [match.group(0) for match in chapter_matches]
        self.chapter_numbers = [int(match.group(1)) for match in chapter_matches]
        if chapters:
            self.pass_(f"Found {len(chapters)} numbered chapters")
        else:
            self.fail("No numbered chapter headings found; expected H2 headings like '## 第1章 标题'")

        h3_headings = re.findall(r"^###\s+(.+)$", text, flags=re.M)
        non_decimal = [heading for heading in h3_headings if not re.match(r"\d+\.\d+\s+", heading)]
        if h3_headings and not non_decimal:
            self.pass_("All H3 headings use decimal numbering")
        elif non_decimal:
            self.warn(f"{len(non_decimal)} H3 headings do not use decimal numbering")

        images = markdown_images(text)
        self.markdown_image_refs = images
        if images:
            missing = [image for image in images if is_local_image(image) and not (self.package_dir / image).exists()]
            if missing:
                self.fail(f"Missing {len(missing)} local markdown images")
            else:
                self.pass_(f"All {len(images)} markdown image references resolve or are remote")
        else:
            self.warn("No markdown images found; each chapter should normally include a visual")

        source_ids = public_source_markers(text)
        if source_ids:
            self.fail(
                "tutorial.md exposes internal source markers: "
                + ", ".join(sorted(set(source_ids))[:8])
            )
        else:
            self.pass_("tutorial.md contains no public bracket source markers")

        self.validate_specific_h3_headings(h3_headings)

    def validate_visuals(self) -> None:
        spec_path = self.package_dir / "visuals/visual-spec.json"
        if not spec_path.exists():
            return
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.fail(f"visual-spec.json is invalid JSON: {exc}")
            return

        chapters = spec.get("chapters") or spec.get("modules") or []
        if not isinstance(chapters, list) or not chapters:
            self.fail("visual-spec.json must contain a non-empty chapters array")
            return
        self.pass_(f"visual-spec.json contains {len(chapters)} chapter visual specs")
        visual_ids = {
            str(chapter.get("id") or f"chapter-{index:02d}")
            for index, chapter in enumerate(chapters, start=1)
            if isinstance(chapter, dict)
        }
        self.validate_chapter_visual_coverage(chapters, visual_ids)

        for index, chapter in enumerate(chapters, start=1):
            if not isinstance(chapter, dict):
                self.fail(f"Visual spec item {index} is not an object")
                continue
            visual_id = str(chapter.get("id") or f"chapter-{index:02d}")
            if not chapter.get("title"):
                self.warn(f"{visual_id} has no title")
            if not chapter.get("caption"):
                self.warn(f"{visual_id} has no caption")

            svg = self.package_dir / "visuals" / f"{visual_id}.svg"
            png = self.package_dir / "assets/screenshots" / f"{visual_id}.png"
            if svg.exists():
                self.pass_(f"SVG exists for {visual_id}")
            else:
                self.fail(f"Missing SVG for {visual_id}")
            if png.exists():
                self.pass_(f"PNG screenshot exists for {visual_id}")
                self.validate_png_size(png, visual_id)
            else:
                self.warn(f"Missing PNG screenshot for {visual_id}; SVG fallback may be used")

    def validate_chapter_visual_coverage(self, chapters: list[object], visual_ids: set[str]) -> None:
        if not self.chapter_numbers:
            return

        expected_ids = [chapter_visual_id(number) for number in self.chapter_numbers]
        missing_specs = [visual_id for visual_id in expected_ids if visual_id not in visual_ids]
        extra_specs = sorted(visual_ids - set(expected_ids))

        if len(chapters) == len(self.chapter_numbers):
            self.pass_("Visual spec count matches numbered chapter count")
        else:
            self.fail(
                f"Visual spec count does not match numbered chapters: "
                f"{len(chapters)} specs for {len(self.chapter_numbers)} chapters"
            )

        if missing_specs:
            self.fail(f"Missing visual specs for chapters: {', '.join(missing_specs)}")
        else:
            self.pass_("Every numbered chapter has a matching visual spec ID")

        if extra_specs:
            self.warn(f"Visual spec has extra IDs not matched to numbered chapters: {', '.join(extra_specs)}")

        embedded_ids = local_image_stems(self.markdown_image_refs)
        missing_embeds = [visual_id for visual_id in expected_ids if visual_id not in embedded_ids]
        if missing_embeds:
            self.fail(f"Tutorial markdown is missing embedded visuals for: {', '.join(missing_embeds)}")
        else:
            self.pass_("Every numbered chapter has an embedded visual reference")

    def validate_png_size(self, png: Path, visual_id: str) -> None:
        try:
            from PIL import Image
        except ImportError:
            return
        try:
            with Image.open(png) as image:
                width, height = image.size
        except Exception as exc:
            self.fail(f"Cannot open PNG for {visual_id}: {exc}")
            return
        ratio = width / height if height else 0
        if width >= 1600 and 1.65 <= ratio <= 1.9:
            self.pass_(f"PNG for {visual_id} is high-resolution 16:9-ish ({width}x{height})")
        else:
            self.warn(f"PNG for {visual_id} may be low resolution or wrong aspect ratio ({width}x{height})")

    def validate_html(self) -> None:
        if "html" not in self.formats:
            return
        html_path = self.package_dir / "exports" / f"{self.basename}.html"
        if not html_path.exists():
            return
        html = read_text(html_path)

        if 'class="report-shell"' in html and 'class="article-body"' in html:
            self.pass_("HTML has centered report-shell and article-body layout")
        else:
            self.fail("HTML missing report-shell/article-body layout wrapper")

        if 'id="TOC"' in html:
            self.pass_("HTML has a generated TOC")
        else:
            self.warn("HTML has no nav#TOC; long tutorials should include a sticky anchor menu")

        if 'class="doc-date"' in html:
            self.pass_("HTML has document date below title")
        else:
            self.warn("HTML has no document date line")

        h1_count = len(re.findall(r"<h1\b", html, flags=re.I))
        if h1_count == 1:
            self.pass_("HTML has one visible H1")
        else:
            self.warn(f"HTML should normally have one H1; found {h1_count}")

        table_positions = [match.start() for match in re.finditer(r"<table\b", html, flags=re.I)]
        unwrapped = 0
        for position in table_positions:
            prefix = html[max(0, position - 120):position]
            if 'class="table-wrap"' not in prefix:
                unwrapped += 1
        if table_positions and not unwrapped:
            self.pass_(f"All {len(table_positions)} HTML tables are wrapped")
        elif unwrapped:
            self.fail(f"{unwrapped} HTML tables are not wrapped in .table-wrap")

        if "file:///" in html or "/Users/" in html:
            self.fail("HTML contains a local absolute path")
        else:
            self.pass_("HTML contains no local file URL or /Users path")

    def validate_docx(self) -> None:
        if "docx" not in self.formats:
            return
        docx_path = self.package_dir / "exports" / f"{self.basename}.docx"
        if not docx_path.exists():
            return
        try:
            with zipfile.ZipFile(docx_path, "r") as archive:
                names = archive.namelist()
                header_footer_files = [
                    name for name in names
                    if name.startswith("word/header") or name.startswith("word/footer")
                ]
                document_xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
        except Exception as exc:
            self.fail(f"Cannot inspect DOCX: {exc}")
            return

        if header_footer_files:
            self.fail(f"DOCX still contains header/footer files: {', '.join(header_footer_files[:4])}")
        elif "headerReference" in document_xml or "footerReference" in document_xml:
            self.fail("DOCX document.xml still references a header or footer")
        else:
            self.pass_("DOCX has no header/footer parts or references")

        if "/Users/" in document_xml or "file:///" in document_xml:
            self.fail("DOCX document XML contains a local absolute path")
        else:
            self.pass_("DOCX document XML contains no local absolute paths")

    def validate_pdf(self) -> None:
        if "pdf" not in self.formats:
            return
        pdf_path = self.package_dir / "exports" / f"{self.basename}.pdf"
        if not pdf_path.exists():
            return
        size = pdf_path.stat().st_size
        if size > 10_000:
            self.pass_(f"PDF exists and is non-trivial ({size} bytes)")
        else:
            self.warn(f"PDF exists but is very small ({size} bytes)")

    def validate_no_absolute_paths(self) -> None:
        text_files = [
            self.package_dir / "tutorial.md",
            self.package_dir / "exports" / f"{self.basename}.html",
        ]
        leaks: list[str] = []
        for path in text_files:
            if not path.exists():
                continue
            text = read_text(path)
            if "file:///" in text or "/Users/" in text:
                leaks.append(str(path.relative_to(self.package_dir)))
        if leaks:
            self.fail(f"Local absolute paths found in final text outputs: {', '.join(leaks)}")
        else:
            self.pass_("No local absolute paths found in final text outputs")

    def validate_specific_h3_headings(self, h3_headings: list[str]) -> None:
        if not h3_headings:
            return
        generic_labels = {
            "你要做的事",
            "你要注意什么",
            "示例",
            "检查点",
            "小结",
            "练习",
            "what to notice",
            "example",
            "checkpoint",
            "summary",
        }
        repeated: dict[str, int] = {}
        for heading in h3_headings:
            label = re.sub(r"^\d+\.\d+\s+", "", heading).strip()
            label = re.sub(r"[：: ].*$", "", label).strip()
            if label.lower() in generic_labels:
                repeated[label] = repeated.get(label, 0) + 1
        offenders = [f"{label} x{count}" for label, count in repeated.items() if count > 1]
        if offenders:
            self.fail(
                "H3 headings repeat generic labels instead of outline-specific section titles: "
                + ", ".join(offenders)
            )
        else:
            self.pass_("H3 headings are specific, not repeated generic labels")

    def validate_public_provenance_hygiene(self) -> None:
        public_texts: list[tuple[str, str]] = []
        tutorial = self.package_dir / "tutorial.md"
        html_path = self.package_dir / "exports" / f"{self.basename}.html"
        docx_path = self.package_dir / "exports" / f"{self.basename}.docx"
        pdf_path = self.package_dir / "exports" / f"{self.basename}.pdf"

        if tutorial.exists():
            public_texts.append(("tutorial.md", read_text(tutorial)))
        if html_path.exists():
            public_texts.append((f"exports/{self.basename}.html", read_text(html_path)))
        if docx_path.exists():
            public_texts.append((f"exports/{self.basename}.docx", docx_visible_text(docx_path)))
        if pdf_path.exists() and shutil.which("pdftotext"):
            text = extract_pdf_text(pdf_path)
            if text:
                public_texts.append((f"exports/{self.basename}.pdf", text))

        marker_leaks = []
        provenance_leaks = []
        for label, text in public_texts:
            markers = sorted(set(public_source_markers(text)))
            if markers:
                marker_leaks.append(f"{label}: {', '.join(markers[:8])}")
            phrases = public_provenance_phrases(text)
            if phrases:
                provenance_leaks.append(f"{label}: {', '.join(phrases[:6])}")

        if marker_leaks:
            self.fail("Public outputs expose internal source markers: " + "; ".join(marker_leaks))
        else:
            self.pass_("Public outputs contain no internal bracket source markers")

        if provenance_leaks:
            self.fail("Public outputs expose internal provenance wording: " + "; ".join(provenance_leaks))
        else:
            self.pass_("Public outputs do not describe themselves as based on supplied material")


def can_import(module: str) -> bool:
    try:
        __import__(module)
    except Exception:
        return False
    return True


def find_browser() -> str:
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
    return ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def public_source_markers(text: str) -> list[str]:
    return re.findall(r"\[(?:U|P|G|A|X|L)\d+\]", text)


def public_provenance_phrases(text: str) -> list[str]:
    patterns = [
        r"用户粘贴",
        r"用户提供",
        r"用户给(?:到|的)",
        r"基于[^。\n]{0,30}(?:文章|原文|资料|材料)",
        r"根据[^。\n]{0,30}(?:文章|原文|资料|材料)(?:整理|生成|改写)",
        r"参考原文",
        r"原文(?:中|里|作者)",
        r"X Article",
        r"user-supplied",
        r"pasted (?:article|note|material)",
        r"based on (?:the )?(?:article|source|supplied material|original text)",
    ]
    found: list[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            found.append(match.group(0))
    return found


def docx_visible_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            chunks = []
            for name in archive.namelist():
                if name == "word/document.xml" or name.startswith("word/header") or name.startswith("word/footer"):
                    chunks.append(archive.read(name).decode("utf-8", errors="ignore"))
            return "\n".join(chunks)
    except Exception:
        return ""


def extract_pdf_text(path: Path) -> str:
    import subprocess

    try:
        completed = subprocess.run(
            ["pdftotext", str(path), "-"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=30,
        )
    except Exception:
        return ""
    return completed.stdout if completed.returncode == 0 else ""


def markdown_images(markdown: str) -> list[str]:
    return [
        normalize_markdown_target(match.group(2))
        for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", markdown)
    ]


def normalize_markdown_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            return target[1:end].strip()
    return target.split()[0].strip("\"'")


def is_local_image(path: str) -> bool:
    return not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path)


def local_image_stems(paths: list[str]) -> set[str]:
    stems: set[str] = set()
    for path in paths:
        if not is_local_image(path):
            continue
        clean_path = path.split("#", 1)[0].split("?", 1)[0]
        stems.add(Path(clean_path).stem)
    return stems


def chapter_visual_id(number: int) -> str:
    return f"chapter-{number:02d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a generated yao-tutorial-skill output package.")
    parser.add_argument("package_dir", help="Generated tutorial package directory, usually outputs/yao-tutorials/<topic-slug>.")
    parser.add_argument("--basename", default="tutorial", help="Base export filename. Defaults to tutorial.")
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=["docx", "html", "pdf"],
        default=["docx", "html", "pdf"],
        help="Expected export formats.",
    )
    parser.add_argument("--check-deps", action="store_true", help="Also check local export dependencies.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code when warnings exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validator = Validator(
        package_dir=Path(args.package_dir).resolve(),
        basename=args.basename,
        formats=args.formats,
        check_deps=args.check_deps,
        strict=args.strict,
    )
    return validator.run()


if __name__ == "__main__":
    raise SystemExit(main())
