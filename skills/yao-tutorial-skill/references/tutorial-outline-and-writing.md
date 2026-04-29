# Tutorial Outline And Writing

The tutorial must feel like a guided learning path for a beginner, not a research report.

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
10. Source appendix and next learning path.

For a short tutorial, use `3-5` chapters. For a textbook-like guide, use `6-10` chapters, but keep each chapter scoped to one learner question.

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

Each chapter must include:

- chapter goal
- plain-language concept
- chapter visual with caption
- one guided example or walkthrough
- `what to notice` callouts
- common pitfall
- practice task
- checkpoint question
- source IDs

Recommended chapter rhythm:

1. State the learner question.
2. Explain the mental model.
3. Show the visual and tell the reader what to notice.
4. Walk through one concrete example.
5. Name the common mistake.
6. Give one small practice task.
7. End with a checkpoint.

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
4. Cite the source ID.
5. Mention limits when the source is narrow, old, or context-specific.

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
- The source appendix is audit-friendly.
- The conclusion gives the next concrete learning step.
