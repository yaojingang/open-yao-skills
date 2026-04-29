# Reference Scan

## Current Skill Anchor

Create a reusable production-style skill that turns any topic into a beginner tutorial package using multi-source research, a verified outline, per-chapter visuals, and DOCX/PDF/HTML exports.

## Scan Focus

- `method`: how to preserve tutorial pedagogy instead of dumping research notes
- `execution`: how to search X, papers, GitHub, and authority sources reliably
- `structure`: how to keep the package lean while still supporting visuals and exports

## External Benchmark Objects

1. Diataxis tutorials
   - URL: `https://diataxis.fr/tutorials/`
   - Pattern borrowed: a tutorial is a guided learning experience with meaningful learner action, small steps, and visible results.
2. X API Search Posts and Search Operators docs
   - URLs: `https://docs.x.com/x-api/posts/search/introduction`, `https://docs.x.com/x-api/posts/search/integrate/operators`
   - Pattern borrowed: use explicit search operators and treat access limits as part of the evidence record.
3. Semantic Scholar Academic Graph API
   - URL: `https://www.semanticscholar.org/product/api`
   - Pattern borrowed: paper search should capture metadata, source links, and rate/access caveats rather than relying on memory.
4. GitHub Docs: Searching for repositories
   - URL: `https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories`
   - Pattern borrowed: use repository qualifiers such as `in:readme`, `stars`, `pushed`, `language`, and `topic`, then verify quality manually.
5. Local `learning-builder`
   - URL: local skill package
   - Pattern borrowed: markdown as canonical source, authority-first research, and export as a downstream step.
6. Local `kami`
   - URL: local skill package
   - Pattern borrowed: warm-paper editorial design, serif-led hierarchy, ink-blue accent discipline, bilingual document typography, and tight document spacing.
7. Local `frontend-slides`
   - URL: local skill package
   - Pattern borrowed: viewport awareness, content density limits, distinctive typography, and anti-generic visual guidance.
8. Local `yao-ppt-skill`
   - URL: local skill package
   - Pattern borrowed: editorial rhythm, image-first planning, quality gates, and guizang-inspired magazine/e-ink constraints.

## User-Supplied References

The user supplied the target workflow in Chinese:

- arbitrary topic input
- research from X.com, papers and paper platforms, authoritative sharing sites, and GitHub
- theory, practice, cases, and related information
- beginner-friendly tutorial outline
- attractive opening
- detailed tutorial content
- one visual per chapter through HTML visual pages
- final PDF, Word, and HTML outputs

## Local Fit Constraints

- The workspace already contains `learning-builder`, `docx`, `pdf`, `kami`, and page-generation skills. This skill should orchestrate document export and visual generation without becoming a full layout engine.
- The requested `guizang-ppt-skill` was not present as a standalone local directory in this workspace. The available `yao-ppt-skill` explicitly borrows guizang-style magazine/e-ink constraints, so this iteration uses `yao-ppt-skill` as the local PPT design reference.
- The new skill should be routeable separately from `learning-builder` because it emphasizes arbitrary-topic research breadth, visual HTML generation, and full publishing artifacts.
- Scripts should use stdlib Python where possible and rely on `pandoc` plus a Chromium-family browser only for export.

## What To Borrow

- From Diataxis: tutorial as learning path, not reference dump.
- From X docs: operator-based social search with access limitation notes.
- From Semantic Scholar: source metadata discipline.
- From GitHub docs: qualifier-driven repository discovery.
- From local `learning-builder`: markdown source of truth and export pipeline.
- From local `frontend-slides`: primary layout discipline, density control, `clamp()` responsiveness, and anti-generic visual standards.
- From local `kami`: document typography, restrained ink-blue use, and Word/PDF polish.
- From local `yao-ppt-skill`: guizang/e-ink-inspired rhythm, quality gates, and diagram restraint.

## What Not To Borrow

- Do not duplicate a full LMS or curriculum operations system.
- Do not treat social posts as authoritative evidence.
- Do not make visuals decorative or separate from the chapter learning goals.
- Do not build a heavyweight publishing platform in v1.
- Do not force slide rules onto long-form tutorials; borrow their rhythm and quality gates only.

## Borrow Plan

1. Keep `SKILL.md` as the route and operator flow.
2. Put search rules, writing rules, visual rules, and export rules in references.
3. Add one visual-generation script and one export script because they directly support the requested recurring job.
4. Add trigger evals because this skill has near-neighbor confusion with generic research, learning guides, document conversion, and webpage design.
5. Add an editorial production reference, sticky HTML TOC styling, high-resolution screenshot capture, and default DOCX reference generation for polished deliverables.
6. Revise the visual priority to `frontend-slides` first: remove decorative-only paper texture, duplicate title blocks, helper copy, heavy shadows, and visual-pack boilerplate from formal outputs.
