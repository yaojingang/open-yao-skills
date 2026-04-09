# Reference Scan

## Current Skill Anchor

Build one production-style skill that can:

- clarify the learner profile with a short guided intake
- gather authoritative sources
- write a personalized tutorial
- export to `docx` and `pdf`
- optionally extend the approved tutorial into a learning webpage

## Scan Focus

- `execution`: how to keep research, asset generation, and export in one operator flow
- `structure`: how to keep the package lean while still export-ready
- `domain`: how tutorial output can become a polished reading artifact

## External Benchmark Objects

1. `joeseesun/qiaomu-epub-book-generator`
   - URL: `https://github.com/joeseesun/qiaomu-epub-book-generator`
   - Why it matters: it packages a full reading-artifact workflow from markdown input through final-format output, including asset handling and output verification.
2. Pandoc User's Guide
   - URL: `https://pandoc.org/demo/example13.pdf`
   - Why it matters: it provides the strongest first-party guidance for markdown-driven `docx` generation and style-reference control.
3. python-docx documentation
   - URL: `https://python-docx.readthedocs.io/en/latest/`
   - Why it matters: it is the authoritative fallback when the tutorial pipeline later needs richer Word-specific editing than plain conversion.
4. ReportLab User Guide
   - URL: `https://www.reportlab.com/docs/reportlab-userguide.pdf`
   - Why it matters: it is a credible fallback path if later iterations need deterministic PDF composition beyond browser print.

## Local Fit Constraints

- The local skill library already has `docx`, `pdf`, and `skill-pageforge`; this skill should orchestrate them rather than duplicate their entire depth.
- The current environment has `pandoc` and `chromium`, but the quick scan did not find `soffice`, `xelatex`, `pdflatex`, or `typst`.
- The package should stay in `production` territory rather than becoming a full document platform in v1.

## What To Borrow

- From `qiaomu-epub-book-generator`: one end-to-end operator flow from source inputs to final reading artifact.
- From Pandoc: markdown as the canonical source and export target control via command-line options.
- From python-docx: a clear escalation path when direct Word manipulation becomes necessary.
- From ReportLab: a future deterministic PDF lane if browser-print PDF becomes too limiting.

## What Not To Borrow

- EPUB-specific complexity in the first version
- output-specific sprawl before the tutorial workflow is stable
- heavy formatting logic that belongs in dedicated `docx` or `pdf` capabilities

## Borrow Plan

1. Keep markdown as the source of truth.
2. Build the skill around learner intake and authority-first research, not around format conversion alone.
3. Use `pandoc` plus Chromium as the default export lane for v1.
4. Keep webpage generation optional and downstream of tutorial approval.
5. Treat `docx`, `pdf`, and page-system work as explicit extension points instead of stuffing all that detail into the core skill entrypoint.
