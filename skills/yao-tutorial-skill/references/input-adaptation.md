# Input Adaptation

Use this guide before research. The user may provide only a topic, or they may provide a full packet of notes, URLs, drafts, papers, repos, examples, and style references. The skill should adapt its research effort to the evidence already provided.

## Priority Rule

User-provided material is the first-order reference for:

- intent and angle
- audience assumptions
- examples, cases, and terminology
- required claims or arguments
- style, tone, and output constraints
- URLs, named people, repos, papers, or projects the user explicitly wants considered

External research exists to verify, complete, update, and challenge the user material. Do not replace the user's angle with a generic web-research angle unless the user material is clearly wrong, unsafe, stale, or too thin to support the tutorial.

## Material Intake

Classify each item into one of these buckets:

- `must_use`: central material the tutorial should preserve or build around
- `supporting`: useful detail, example, data point, or source
- `style_reference`: layout, writing, visual, or tone reference
- `caution`: material that may be wrong, stale, promotional, unsupported, or out of scope
- `exclude`: material the user says not to use

Record the classification in `research/user-materials-register.md`.

Suggested schema:

```markdown
| id | type | title_or_label | user_priority | use_for | key_takeaway | limits_or_cautions |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | pasted note | ... | must_use | angle, examples | ... | user-authored, verify factual claims |
```

Use `U1`, `U2`, `U3` for user material. External sources should keep `P`, `G`, `A`, `X`, or other source prefixes.

## Sufficiency Tiers

After intake, choose a research tier.

### Rich User Packet

Use this when the user provides at least one of:

- a substantial draft, transcript, or notes packet
- `5+` relevant URLs or files with a clear angle
- specific must-use papers, repos, cases, or benchmark projects
- enough examples and claims to support most chapters

Research behavior:

- use user material as the tutorial spine
- add only `3-8` external records for verification, freshness, missing theory, missing implementation, and counterexamples
- do not over-research familiar background if the user packet already supports the chapter

### Moderate User Packet

Use this when the user provides:

- a topic plus a few notes or URLs
- a clear angle but incomplete evidence
- examples but weak theory
- theory but weak practice

Research behavior:

- preserve the user's angle and examples
- add `6-12` external records
- fill only the missing source layers, such as papers, GitHub, official docs, or practitioner cases

### Thin User Packet

Use this when the user provides:

- only a topic
- one vague paragraph
- weak or mostly stylistic references
- unsupported claims with no source trail

Research behavior:

- preserve the user's wording and implied intent
- run the full source ladder from `references/research-sourcing.md`
- target `10-18` external records for a full tutorial

## Conflict Handling

When user material conflicts with external evidence:

- keep the user's goal visible
- separate opinion, practitioner signal, and supported fact
- cite the stronger source for factual claims
- explain the limitation briefly in the tutorial if it affects learning
- do not silently erase the user's idea; reshape it into a safer, source-backed version

When the user provides many references but no topic, infer the topic from the repeated pattern and state that assumption before writing.

When the user provides style references, extract rules rather than copying surface decoration.

## Personalization Hooks

Use supplied details to personalize:

- audience role: founder, engineer, teacher, student, operator, creator
- learning objective: understand, build, decide, teach, evaluate, sell, or operate
- domain context: business, education, software, AI, design, finance, healthcare, legal, or another field
- tone: formal textbook, practical playbook, narrative tutorial, internal manual
- output depth: sample, complete tutorial, deep manual

If the user gives none of these, default to a beginner practical tutorial with concrete examples and restrained document design.

## Research Budget Rule

External research should shrink when user material is strong and expand when user material is weak. It should never disappear entirely for current, factual, technical, legal, medical, financial, or tool/version-dependent topics.

Minimum external check even for rich packets:

- one authority or primary source for core definitions
- one implementation or case source when practice is involved
- one freshness check when tools, APIs, laws, prices, benchmarks, or public figures are involved
