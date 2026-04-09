---
name: learning-tutorial-builder
description: Create personalized learning tutorials from a learner profile and authority-first research. Use when the user wants a guided intake to clarify goals, background, constraints, and desired outcomes, then wants a structured tutorial or study guide assembled from official docs, standards, maintainer docs, regulator guidance, or other primary sources. Also use when the user wants the tutorial exported to Word or PDF, or wants to extend the finished tutorial into a personalized learning webpage. Do not use for one-off factual answers, generic blog writing, broad web research without a tutorial deliverable, or standalone webpage design with no learning packet.
---

# Learning Tutorial Builder

## Own The Following Job

- Turn a vague learning request into one clear learner-specific tutorial brief.
- Gather the minimum learner context before doing deep research.
- Prefer authoritative sources over blogs, reposts, or anonymous summaries.
- Assemble one tutorial packet with explicit citations, exercises, and next steps.
- Export the tutorial to `docx` and `pdf` when requested.
- Offer an optional personalized webpage only after the tutorial content is approved.

## Inputs

Expect one or more of:

- the topic or skill the learner wants to master
- the learner's current level, role, and target outcome
- a time budget, learning style, or deadline
- required or forbidden sources and domains
- existing notes, outlines, bookmarks, or source lists
- an explicit request for `docx`, `pdf`, or webpage output

## Do Not Route Here

- requests that only need a short answer or explanation
- generic research with no tutorial or study guide deliverable
- unsourced opinion writing or marketing copy
- document export requests where the tutorial is already written and no learning workflow is needed
- pure webpage design work with no learning packet behind it

## Default Workflow

1. Start with the sharp intake in `reports/intent-dialogue.md`. Ask only the questions that change scope, sourcing, or output shape.
2. Convert the answers into the schema in `input/learner_profile_template.json`. If key inputs are missing, list the blockers before researching.
3. Read `references/authority-research.md` and build an authority-first source list. Prefer primary sources and record why each source is trusted.
4. Read `references/tutorial-assembly.md` and draft one tutorial in markdown. Keep the tutorial aligned to the learner profile, not to the source order.
5. If `docx` or `pdf` output is requested, read `references/export-pipeline.md` and use `scripts/export_tutorial.py`. In this workspace, prefer markdown as the canonical source.
6. If the user wants a personalized webpage after reviewing the tutorial, read `references/webpage-extension.md` and generate that as a second deliverable, not as a substitute for the tutorial packet.
7. Validate the final artifact set:
   - the learner goal is explicit
   - key claims are backed by cited authority sources
   - exercises and next steps match the learner level
   - requested output files were actually produced
   - optional webpage work did not replace the core tutorial deliverable

## Output Contract

The normal output set is:

- one learner-specific tutorial in markdown
- one compact source appendix with URLs, source dates, and trust rationale
- one `docx` export when requested
- one `pdf` export when requested
- one optional webpage plan or static learning page only after user confirmation

## Validation Checklist

- The brief captures topic, learner state, target outcome, and constraints.
- The research set is authority-first and not padded with weak sources.
- The tutorial is personalized enough that a different learner profile would change the content.
- The export pipeline starts from markdown instead of maintaining separate source documents by hand.
- The webpage branch is clearly optional.

## Reference Map

- Read `reports/intent-dialogue.md` before doing deep work.
- Read `reports/reference-scan.md` to understand the initial borrow plan.
- Read `references/authority-research.md` for source selection rules.
- Read `references/tutorial-assembly.md` for the tutorial content contract.
- Read `references/export-pipeline.md` for `docx` and `pdf` generation.
- Read `references/webpage-extension.md` before offering the personalized webpage branch.
- Inspect `evals/trigger_cases.json` when tightening route boundaries.
