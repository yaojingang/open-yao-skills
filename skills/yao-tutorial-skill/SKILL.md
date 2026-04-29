---
name: yao-tutorial-skill
description: Create source-backed beginner tutorials from any topic through multi-source research, outline design, chapter-by-chapter writing, HTML/SVG visuals, and export to Markdown, DOCX, PDF, and HTML. Use when the user asks to turn an arbitrary topic into a beginner-friendly textbook, course, tutorial, or teaching document using X.com, papers, authoritative sharing sites, and GitHub references. Do not use for short factual answers, unsourced blog posts, pure web research with no tutorial deliverable, or file conversion when the tutorial is already finished.
---

# Yao Tutorial Skill

## Own The Following Job

- Turn any topic into a source-backed beginner tutorial package.
- Search across timely discussion, scholarly theory, practical repositories, and authority explainers.
- Convert research into a clear beginner outline before drafting.
- Write a complete tutorial with a strong opening, numbered chapter learning path, examples, exercises, and citations.
- Generate one visual artifact for every chapter through local HTML/SVG, then place the captured image in the tutorial.
- Export the final package to Markdown, DOCX, PDF, and standalone HTML when requested.

## Inputs

Minimum input: one topic. If the topic is broad, make a low-risk assumption and state it briefly.

Useful optional inputs:

- target audience, role, and current level
- desired language, depth, and length
- user-provided reference notes, URLs, files, examples, drafts, transcripts, papers, repos, posts, or named exemplars
- must-use, nice-to-use, and do-not-use reference material
- required source types, domains, authors, papers, or repositories
- forbidden sources, regions, or technologies
- required output formats
- visual style or document template constraints

Use `templates/topic-brief-template.json` when the request is thin or the project will span many chapters.

## Do Not Route Here

- one-off explanations or quick answers
- generic web research where no tutorial will be produced
- marketing articles, SEO listicles, or opinion essays
- pure diagram generation with no tutorial body
- document conversion or formatting work where the source tutorial is already complete
- advanced curriculum design for a known cohort when the user is asking for instructional operations, grading, or live teaching plans instead of a written tutorial package

## Default Workflow

1. Confirm the topic, audience, target outcome, language, requested formats, and any user-provided reference material. Ask at most two questions only when these choices change the package materially.
2. Read `references/input-adaptation.md`, then normalize the request into `brief.json`. Treat user-provided material as the primary spine unless the user says it is only optional inspiration.
3. Create a dated output folder under `outputs/yao-tutorials/<topic-slug>/`.
4. Triage user material before external research:
   - rich user material: use it as the main evidence spine; use external research for gap checks, freshness, and counterexamples
   - moderate user material: keep it as the spine; add targeted external sources where claims, examples, or visuals are under-supported
   - thin user material: preserve the user's intent, then run the full external source ladder
5. Record user material in `research/user-materials-register.md` with source IDs such as `U1`, `U2`, and classify each item as must-use, supporting, style reference, or caution.
6. Read `references/research-sourcing.md`, then build an adaptive search plan covering only the source layers needed:
   - X.com posts or threads for current discussion and practitioner signals
   - papers and paper platforms for theory and evidence
   - GitHub repositories, issues, examples, and READMEs for implementation patterns
   - authoritative sharing sites such as official docs, research labs, engineering blogs, conference talks, standards bodies, and university materials
7. Record external sources in `research/source-register.md`. Treat X posts and social threads as leads or case material unless the author and claim can be verified elsewhere.
8. Create `research/evidence-map.md` that maps user and external evidence to tutorial chapters. Stop research when the outline can be supported, not when every search path is exhausted.
9. Read `references/tutorial-outline-and-writing.md`, then write `outline.md` before drafting. The outline must be beginner-friendly, sequential, action-oriented, and use chapter numbering.
10. Read `references/editorial-production.md`, then set the tutorial length, visual direction, and output polish level. Unless the user asks for a short sample, target a substantial tutorial of `5000-10000` Chinese characters or `3500-7000` English words.
11. Draft `visuals/visual-spec.json` with one visual spec per chapter. Read `references/visual-html-workflow.md` and `references/visual-board-benchmarks.md`, then run:

   ```bash
   python3 <skill-dir>/scripts/build_visual_pack.py visuals/visual-spec.json visuals/
   ```

12. Capture each chapter visual into `assets/screenshots/` and embed those images in `tutorial.md`:

   ```bash
   python3 <skill-dir>/scripts/capture_visuals.py visuals/ assets/screenshots/
   ```

   If screenshots cannot be produced, embed the generated SVG files and report the fallback.
13. Write `tutorial.md` from the outline and evidence map. Keep markdown as the canonical source of truth.
14. Read `references/export-workflow.md`, then export requested formats with:

    ```bash
    python3 <skill-dir>/scripts/export_tutorial.py tutorial.md exports/ --css <skill-dir>/templates/tutorial-style.css
    ```

15. Validate the package:

    ```bash
    python3 <skill-dir>/scripts/validate_package.py . --formats docx html pdf --check-deps
    ```

    - every factual claim that matters has a source ID or source appendix entry
    - every chapter has a visual
    - the tutorial length matches the requested or default word-count range
    - the tutorial opens with a concrete hook and avoids unexplained jargon
    - examples and exercises match the beginner audience
    - HTML uses a centered report shell where the left anchor-text menu and right reading column behave as one balanced layout, with no large blank area below the title
    - DOCX, PDF, HTML, and visual HTML files exist and follow the editorial production system when requested

## Output Contract

The normal package contains:

- `brief.json`
- `research/user-materials-register.md` when the user supplied notes, URLs, files, or exemplars
- `research/source-register.md`
- `research/evidence-map.md`
- `outline.md`
- `visuals/visual-spec.json`
- `visuals/index.html`
- `visuals/*.svg`
- `assets/screenshots/*.png` when screenshot capture succeeds
- `tutorial.md`
- `exports/tutorial-reference.docx` when the default Word reference style is generated
- `exports/tutorial.docx`
- `exports/tutorial.pdf`
- `exports/tutorial.html`

If a source class is unavailable, say exactly which layer failed and which substitute was used. Do not fabricate X posts, paper citations, repository details, or publication dates.

## Quality Rules

- Match the output language to the user's request unless they specify otherwise.
- Use short quotations rarely; paraphrase and cite instead.
- Use user-provided material as the first-order source of intent, examples, tone, and constraints; use external sources to verify, extend, or challenge it.
- Prefer primary and official sources for claims. Use social posts as discovery and lived-practice context.
- Teach through small steps, concrete examples, and early wins.
- Put theory after the learner has a reason to care.
- Chapter headings must use `## 第1章 章节标题`. Chapter subheadings must use decimal numbering such as `### 1.1 学习目标`, `### 1.2 示例`, and continue within each chapter.
- Every chapter should include: goal, plain-language concept, visual, guided example, practice task, common pitfall, and checkpoint.
- Keep export formatting downstream of the markdown source.

## Reference Map

- Read `reports/reference-scan.md` for the initial borrow plan.
- Read `references/input-adaptation.md` before deciding how much external research is needed.
- Read `references/research-sourcing.md` before browsing.
- Read `references/tutorial-outline-and-writing.md` before drafting the outline or tutorial.
- Read `references/editorial-production.md` before setting length, visual design, or export polish.
- Read `references/visual-html-workflow.md` before generating chapter visuals.
- Read `references/visual-board-benchmarks.md` before choosing the visual board grammar or layout rules.
- Read `references/export-workflow.md` before producing DOCX, PDF, or final HTML.
- Use `scripts/build_visual_pack.py` to create the visual HTML/SVG pack.
- Use `scripts/capture_visuals.py` to create PNG screenshots for document embedding.
- Use `scripts/build_reference_doc.py` when a standalone Word reference style is needed.
- Use `scripts/export_tutorial.py` to export Markdown to DOCX, PDF, and HTML.
- Use `scripts/validate_package.py` before final delivery.
- Inspect `evals/trigger_cases.json` when tightening route boundaries.
