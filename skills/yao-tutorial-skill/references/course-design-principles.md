# Course Design Principles

Use these rules when turning evidence into a tutorial or course-like document. They come from the local course marketing reference packet and should be treated as durable design constraints, not visible source notes.

## Public Artifact Rule

The final tutorial is a formal public-facing teaching product. It should not say it is based on a pasted article, user notes, source packet, X thread, draft, or original text. Absorb user references silently into the structure, examples, and teaching angle.

Keep source IDs such as `[U1]`, `[X1]`, `[A2]`, `[P3]`, or `[G4]` only in `research/` files. Public `tutorial.md`, HTML, DOCX, and PDF must not display these IDs. If references are useful to readers, write a human-readable `参考资料` or `延伸阅读` section with titles and links, not internal IDs.

## Title Design

A tutorial title should work like a compact value proposition, not a neutral file name.

Use at least one of these title forces:

- user benefit: make the outcome obvious
- tension or contrast: name the misunderstanding the tutorial fixes
- visual concreteness: create a memorable picture or action
- attachment: connect a new idea to a familiar frame
- authority: use credible scope, framework, or experience when available

Preferred title shape:

```text
主题/领域 + 时代或场景 + 方法动作 + 用户结果
```

If a title must be short, preserve the user-facing result before the professional category. A good title makes the reader think "this is for my problem", not just "this is about a topic".

## Outline Design

Avoid the knowledge curse. Most weak outlines are organized around what the author wants to teach; strong outlines are organized around what the learner wants to solve.

Use this formula:

```text
Outline item = professional content + learner pain or desired outcome
```

When space is limited, keep the learner-facing pain/outcome and hide the professional term inside the section body.

Build the outline with the `point-line-surface-system` method:

1. `Point`: list key knowledge points, user questions, pain points, examples, terms, and mistakes.
2. `Line`: merge related points into learner-facing section questions or tasks.
3. `Surface`: group sections with a clear logic such as process, cause-effect, comparison, or category.
4. `System`: make the chapters form one coherent method, not a bag of tips.

Scope rules:

- Choose what the author can explain well, what the learner truly needs, and what forms a self-consistent path.
- Do not pursue "big and complete" if it weakens learning certainty.
- Every H2 chapter and H3 section should map to a distinct outline item.
- Avoid repeating generic H3 labels such as `你要做的事`, `你要注意什么`, `示例`, or `检查点` across chapters. Make section headings specific, e.g. `3.2 用熟悉场景降低听力负担`.

## Section Content Design

Do not default to `concept + explanation + example`. That structure often starts too abstractly and fails to create need.

For important sections, use the experience formula:

```text
Content = scene challenge + failed old approach + new solution + new result
```

Each teaching unit should move through three levels:

1. `Transfer knowledge`: explain the concept with clear logic.
2. `Change cognition`: expose why the old mental model fails and why the new model matters.
3. `Awaken behavior`: give a low-friction action the learner can perform.

Use behavior design when a section asks the learner to act:

- motivation: show the benefit, contrast, or emotional reason to act
- ability: reduce the first action to a small feasible step
- prompt: provide a clear trigger, checklist, template, or practice moment

Good sections usually contain:

- a concrete scene or learner problem
- one method, model, or principle
- a short case or walkthrough
- a visible artifact such as table, checklist, diagram, or template
- one small action or reflection prompt

## Material And Memory

Strong tutorials need material, not only explanation. Use stories, cases, diagrams, tables, short formulas, memorable lines, and before/after comparisons to create recognition and memory.

Use `method + case + reusable template` as the default rhythm when the tutorial teaches a repeatable workflow. The template can be a checklist, prompt, worksheet, decision table, or experiment plan.

Avoid fake marketing hype. The goal is not to sell inside the tutorial; the goal is to make the value, path, and next action obvious.

