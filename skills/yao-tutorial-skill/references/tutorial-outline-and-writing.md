# Tutorial Outline And Writing

The tutorial must feel like a guided learning path for a beginner, not a research report.

Read `references/input-adaptation.md` and `references/course-design-principles.md` before outlining. If the user supplied notes, drafts, URLs, or examples, the outline should preserve the user's core angle and only add external structure where it improves teaching quality.

Final public copy must read as a standalone tutorial, not as a summary of supplied references. Do not write phrases such as "based on the article", "the user supplied", "the pasted note says", or "this tutorial is organized from the original text".

## Outline Shape

Use this structure unless the topic clearly needs another order:

1. Hook: a concrete problem, surprising contrast, or relatable scene.
2. Promise: what the learner will be able to understand or build by the end.
3. Roadmap: the smallest useful path through the topic.
4. Chapter 1: the beginner mental model.
5. Chapter 2: the first concrete example.
6. Chapter 3: how the pieces connect.
7. Chapter 4: practical workflow or implementation.
8. Chapter 5: real cases, mistakes, and tradeoffs.
9. Practice: tasks that reinforce the path.
10. Human-readable reference or further-reading section when useful, plus next learning path.

For a short tutorial, use `3-5` chapters. For a textbook-like guide, use `6-10` chapters, but keep each chapter scoped to one learner question.

## User-Material Adaptation

When the user gives substantial material:

- start the outline from the user's strongest claim, case, or teaching angle
- keep user examples as the running example when they are clear enough
- convert loose notes into chapter questions instead of replacing them with generic chapters
- add external theory only where it helps the learner understand or verify the user's point
- mark unsupported user claims as claims to verify before drafting
- do not tell readers which parts came from user material; convert the material into polished teaching structure

When the user gives only a topic:

- use the default beginner path
- choose one running example during research
- make the first chapter solve the most common beginner confusion

When the user gives URLs or named references:

- create at least one chapter, section, visual, or source note that explains how those references matter
- avoid turning the tutorial into a link summary; the references should become teaching structure

## Length Contract

Default to a complete tutorial, not a short article:

- Chinese body target: `5000-10000` Chinese characters, excluding source appendix, source tables, and raw research notes.
- English body target: roughly `3500-7000` words, excluding source appendix.
- Default chapter count: `6-10`.
- Each Chinese chapter should usually be `600-1200` characters.
- Each English chapter should usually be `450-900` words.
- Opening hook should usually be `300-600` Chinese characters or `200-400` English words.
- Final practice section should include a concrete exercise, a checkpoint, and a small self-review rubric.

Use a shorter target only when the user explicitly asks for a sample, preview, brief, or one-pager. If the topic is very narrow, keep the tutorial shorter but say why.

## Opening Rules

The opening should:

- start with a real situation or pain point
- avoid fake urgency and empty hype
- show why the topic matters before naming too much theory
- make the learner feel the path is doable
- state the outcome plainly

Good opening patterns:

- "You have seen X, but Y is the part that usually makes it confusing."
- "Imagine you need to do X tomorrow. The hard part is not A; it is B."
- "Most explanations start from the formula. We will start from the moment you actually need it."

## Chapter Contract

Each chapter must use this numbering pattern:

- H2: `## 第1章 章节标题`
- H3: `### 1.1 小节标题`, `### 1.2 小节标题`, continuing within the chapter
- Final practice can be a numbered chapter when it is part of the learning path.
- H3 headings must be specific to the outline item. Avoid repeated generic headings such as `你要做的事`, `你要注意什么`, `示例`, `检查点`, or `小结`.

Each chapter must include:

- chapter goal
- plain-language concept
- chapter visual with caption
- one guided example or walkthrough
- `what to notice` callouts
- common pitfall
- practice task
- checkpoint question
- source traceability in internal research notes; no visible bracket source IDs in the public tutorial

Recommended chapter rhythm:

1. Start from a concrete scene challenge or learner question.
2. Name the failed old approach and why it does not work.
3. Introduce the new method or mental model.
4. Show the visual and tell the reader what to notice.
5. Walk through one concrete example, table, or template.
6. Give one small behavior prompt or practice task.
7. End with a specific checkpoint.

## Beginner-Friendly Rules

- Introduce terms only when they are needed.
- Define a term the first time it appears.
- Use one running example across chapters when possible.
- Prefer concrete nouns and visible steps.
- Separate must-know from nice-to-know.
- Put formulas, APIs, and jargon after a simple mental model.
- Use analogies only when they reduce confusion; say where the analogy breaks.
- End each chapter with a small success state.

## Evidence-To-Teaching Translation

For every important source-backed claim:

1. State the claim in plain language.
2. Explain why it matters to the learner.
3. Show it in an example or visual.
4. Keep the source ID in `research/evidence-map.md`, not in public prose.
5. Mention limits when the source is narrow, old, or context-specific.

For user-provided claims:

1. Preserve the intent.
2. Verify or qualify the factual part.
3. Keep the user's example when it teaches well.
4. Keep user material IDs in `research/user-materials-register.md`, not in public prose.
5. Add external source IDs in internal research notes when the claim needs authority beyond the user's note.

## Exercises

Include a mix of:

- recognition: identify the concept in a real example
- transformation: convert raw material into the learned structure
- application: solve a small realistic task
- reflection: explain a tradeoff in the learner's own words

Avoid exercises that require tools or accounts the learner has not been prepared to use.

## Final Tutorial Checklist

- The first page answers "why should I care?"
- The body length is within the requested or default range.
- The chapter order has no hidden prerequisites.
- Every chapter has a visual and a source-backed purpose.
- The tutorial includes theory, practice, and case material.
- User-provided material has been used as the spine when it is strong enough, and external material is added only where it improves support.
- The source appendix is audit-friendly.
- Public prose contains no bracket source markers like `[U1]`, `[X1]`, `[A2]`, `[P3]`, or `[G4]`.
- Public prose does not expose internal provenance such as "user supplied material" or "based on the original article".
- Chapter and section headings match the learner path and do not repeat generic labels.
- The conclusion gives the next concrete learning step.
