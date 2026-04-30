# Export Workflow

Use markdown as the single editable source of truth. Generate DOCX, PDF, and HTML from `tutorial.md`.

Read `references/editorial-production.md` before exporting. The export phase is not just format conversion; it is where the tutorial becomes a polished reading artifact.

## Folder Convention

Inside `outputs/yao-tutorials/<topic-slug>/`:

```text
brief.json
research/source-register.md
research/evidence-map.md
outline.md
visuals/visual-spec.json
visuals/index.html
visuals/*.svg
assets/screenshots/*.png
tutorial.md
exports/
exports/tutorial-reference.docx
```

## Export Command

Run from the tutorial output folder:

```bash
python3 /path/to/yao-tutorial-skill/scripts/export_tutorial.py tutorial.md exports/ --css /path/to/yao-tutorial-skill/templates/tutorial-style.css
```

The exporter creates a default `tutorial-reference.docx` for Word styling when no `--reference-doc` is provided and `python-docx` is available.

Optional title, basename, date, and reference document:

```bash
python3 /path/to/yao-tutorial-skill/scripts/export_tutorial.py tutorial.md exports/ --title "Beginner Guide To <Topic>" --basename tutorial --date "2026年4月29日" --css /path/to/yao-tutorial-skill/templates/tutorial-style.css
python3 /path/to/yao-tutorial-skill/scripts/export_tutorial.py tutorial.md exports/ --reference-doc custom-reference.docx --css /path/to/yao-tutorial-skill/templates/tutorial-style.css
```

## Dependencies

The default script uses:

- `pandoc` for DOCX and HTML
- `weasyprint` for clean PDF printing without browser URL/page footers
- a local Chromium-family browser for visual screenshots and PDF fallback
- `Pillow` for exact post-capture PNG cropping
- `python-docx` for generating the default Word reference document when available

If the environment lacks these tools:

- still deliver `tutorial.md` and `visuals/index.html`
- use a dedicated local document or PDF skill if available
- report exactly which export target could not be produced

## Formatting Rules

- Keep headings short and hierarchical.
- Do not show internal source IDs in public text. Keep `[U1]`, `[X1]`, `[A2]`, `[P3]`, `[G4]`, and similar audit IDs inside `research/` files only.
- If references are useful to readers, use a human-readable `参考资料` or `延伸阅读` section with names and links, not bracket IDs.
- Public outputs should not say they are based on user notes, pasted source material, a supplied article, or the original text.
- When a source is a local file, use a human-readable label in final deliverables and keep absolute audit paths only in internal research notes.
- Keep image paths relative to `tutorial.md`.
- Use captions directly below images.
- Use high-resolution screenshots for chapter visuals.
- In HTML, render chapter images as clean figures: no browser-default figure indentation, no extra border when the image already has an artboard frame, and no duplicate auto/generated figcaption.
- Chapter headings must stay visible in all formats as `第1章 标题`; chapter subheadings must stay visible as `1.1 标题`, `1.2 标题`.
- In HTML, wrap tables in a scroll-safe table container so wide or dense tables stay readable.
- HTML must include a plain sticky `nav#TOC` anchor menu that remains functional while scrolling. The exporter should wrap `nav#TOC` and the article in a centered `report-shell`, so the menu and reading column align as one balanced layout. The TOC must stay outside the article body; a long TOC must never push the first paragraphs below the fold.
- Put a compact document date directly below the visible H1 title in HTML, PDF, and DOCX. The date is content metadata, not a browser print footer.
- Do not create duplicate visible title blocks; the markdown `H1` is the only visible title, with one optional date line below it.
- PDF should hide sticky UI chrome and render as a clean document.
- PDF must not include browser-generated URL footers, page counters, print dates, or file paths.
- Word output must not include document headers or footers unless the user explicitly asks for them.
- DOCX should use a reference document for heading, body, table, and caption styles.
- Avoid manual page-break hacks unless the user requires print layout.
- Make the HTML readable before printing to PDF.

## Export Quality Gate

Run the package validator before final delivery:

```bash
python3 /path/to/yao-tutorial-skill/scripts/validate_package.py . --formats docx html pdf --check-deps
```

Use `--formats html` or another subset when the user requested fewer formats.

- DOCX opens and contains images.
- PDF opens and images are visible.
- PDF has no visible header, footer, local file URL, browser date, or browser page counter.
- DOCX has no header/footer parts or section header/footer references unless explicitly requested.
- HTML is standalone or has correctly linked local assets.
- HTML has a sticky anchor-text table of contents when the tutorial is longer than three chapters.
- HTML first viewport shows the title, date, and opening text without a large blank area below the title.
- HTML desktop viewport centers the combined `nav#TOC + article-body` layout, leaving visually balanced outer margins.
- HTML does not contain duplicated title blocks or visible generation/helper labels.
- Links are clickable in exported files when the format supports links.
- No chapter is missing its visual.
- HTML tables are readable at desktop and mobile widths.
- HTML image captions are not duplicated.
- No absolute local filesystem paths appear in final HTML, PDF, or DOCX.
- No public output contains bracket source markers or internal provenance wording.
- Output typography, colors, captions, and tables match the editorial production system.
