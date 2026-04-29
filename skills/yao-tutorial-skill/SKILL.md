---
name: yao-tutorial-skill
description: Create source-backed beginner tutorials from a topic or supplied references, with adaptive research, outline design, chapter visuals, and Markdown/DOCX/PDF/HTML exports. Use for textbook-like tutorials, course guides, teaching documents, or long beginner guides backed by user material plus X.com, papers, authoritative sources, and GitHub evidence. Do not use for quick answers, unsourced posts, link summaries, pure diagrams, or finished-document conversion.
---

# Yao Tutorial Skill

## Job

Turn a topic, notes packet, URL list, draft, repo list, or paper set into a reusable tutorial package: `brief.json`, research records, `outline.md`, `tutorial.md`, one visual per numbered chapter, and requested exports.

## Boundary

Use for source-backed tutorial production. Exclude quick explanations, generic research summaries, SEO/opinion posts, standalone diagrams, file conversion, live teaching operations, grading, and cohort management.

## Workflow

1. Normalize topic, audience, outcome, language, formats, user material, style references, and exclusions into `brief.json`.
2. Read `references/input-adaptation.md`; use user material as the spine when sufficient, then add only needed external research.
3. Read `references/research-sourcing.md`; create `research/user-materials-register.md` when needed, `research/source-register.md`, and `research/evidence-map.md`.
4. Read `references/tutorial-outline-and-writing.md`; write `outline.md`, then `tutorial.md` with `第1章` and `1.1` style headings.
5. Read the editorial and visual references; create `visuals/visual-spec.json`, then run `build_visual_pack.py` and `capture_visuals.py`.
6. Read `references/export-workflow.md`; run `export_tutorial.py` and then `validate_package.py`.
7. Report exact failures and fallbacks. Never fabricate X posts, papers, repo details, dates, or citations.

## Quality Gates

- User material controls intent, examples, tone, and constraints when strong enough.
- External evidence prioritizes primary/official, scholarly, implementation, then practitioner sources.
- Every important claim has a source ID or source appendix entry.
- Every numbered chapter has a matching visual spec and embedded visual.
- Default full tutorial length is `5000-10000` Chinese characters or `3500-7000` English words unless requested otherwise.
- HTML uses centered `report-shell`; DOCX/PDF have no visible headers, footers, local paths, or print chrome.
- Delivery passes `scripts/validate_package.py` or names the remaining warnings/failures.

## References

- `references/input-adaptation.md`
- `references/research-sourcing.md`
- `references/tutorial-outline-and-writing.md`
- `references/editorial-production.md`
- `references/visual-html-workflow.md`
- `references/visual-board-benchmarks.md`
- `references/export-workflow.md`
- `scripts/build_visual_pack.py`, `scripts/capture_visuals.py`, `scripts/export_tutorial.py`, `scripts/validate_package.py`
- `templates/topic-brief-template.json`, `templates/visual-spec-template.json`, `templates/tutorial-style.css`
