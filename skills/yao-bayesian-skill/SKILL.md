---
name: yao-bayesian-skill
description: Convert uncertain real-world choices into an auditable Bayesian evidence-to-action report. Use when the user wants a hypothesis, reference class, prior, evidence grading, posterior update, sensitivity analysis, expected-value action comparison, a next-information recommendation, and an exported report output such as bilingual HTML plus Markdown. Good fits include Bayesian decision analysis, likelihood-ratio updates, action thresholds, and deciding whether to do X under uncertainty. Do not use for Bayes theorem tutoring, homework, generic brainstorming with no report, or final licensed medical, legal, or financial advice.
---

# Yao Bayesian Skill

## Use This Skill For

- turning a vague decision into one explicit hypothesis, time horizon, success metric, and action set
- separating priors, evidence quality, posterior result, sensitivity, and action choice
- starting from incomplete user input, issuing a weak initial prior plus a preliminary judgment, then guiding the user through multiple follow-up turns
- recording each decision round so the final report can explain how priors, posteriors, and readiness changed over time
- exporting one synchronized report pair: Chinese-first `markdown` plus bilingual `html`

## Do Not Route Here

- Bayes theorem tutoring or homework-only calculations
- broad research or brainstorming with no explicit decision report
- final professional medical, legal, or investment advice

## Default Workflow

1. Use `references/intake-contract.md` to convert the request into one structured decision brief.
2. If the input is incomplete, read `references/multi-turn-dialogue-loop.md` and start with a weak prior plus a preliminary judgment instead of pretending certainty.
3. Use `references/evidence-prior-playbook.md` to grade evidence and choose the lightest valid update path.
4. Maintain a structured conversation log for each round: what the user added, what gap remained, how the Bayesian update changed, and whether the case is now ready to decide.
5. Run `scripts/bayesian_decision_report.py` for canonical JSON or `scripts/generate_report_bundle.py` for the HTML + Markdown report pair.
6. Read `references/report-export-pipeline.md` before export. The normal output is `markdown + html`.
7. Finalize with `references/decision-report-contract.md` and `references/sensitivity-and-safety.md`.

## Iteration And Implementation Constraints

Apply these constraints when extending or refining this skill itself. They govern implementation choices, not the underlying Bayesian method.

- Think before coding: do not silently choose one interpretation when the decision question, prior basis, or report expectation is ambiguous. State assumptions, surface tradeoffs, and prefer a weak prior plus explicit uncertainty over hidden completion.
- Simplicity first: implement the minimum valid Bayesian workflow that solves the request. Prefer the lightest update path, the smallest report change, and the fewest output formats needed. Do not add speculative modeling complexity, configuration layers, or export branches that the user did not ask for.
- Surgical changes: touch only the files and logic required for the requested improvement. Match the existing structure and remove only the imports, helpers, or output paths made obsolete by your own change. Do not refactor adjacent skill behavior without a direct reason.
- Goal-driven execution: define the success criteria for each iteration before editing. For this skill, success should be stated in user-visible checks such as whether incomplete input now yields a weak prior plus follow-up questions, whether each round is logged, whether the report explains how belief changed, and whether the HTML/Markdown outputs still render the intended decision guidance.

## Output Contract

- Deliver one Bayesian decision report output, not a formula dump.
- Mark each number as observed, estimated, or assumed.
- Surface weak evidence, dependence risk, and model limits.
- When the user starts with only a question plus current state, begin with a weak prior and a preliminary action read; then ask the minimum next questions needed to improve the decision.
- For multi-turn use, keep a round-by-round log of the evolving prior, posterior, decision readiness, remaining gaps, and the exact Bayesian formula or update path used in that round.
- Final reports must analyze the dialogue process itself: what changed in each round, which information moved the belief the most, whether the decision is now ready, and what is still missing if it is not.
- If the result is unstable, recommend a lower-cost test before a heavier commitment.
- In high-risk domains, label the output as decision support only.
- Human-facing reports default to Simplified Chinese; HTML must also provide bilingual Chinese/English switching with sticky top navigation.
- The report output must explicitly state that it was auto-generated from one structured input.
- Put a plain-language executive summary first: what to do now, why, and why not the other options before the technical sections.
- HTML should default to the full professional view while keeping advanced sections collapsible.
- HTML should also show a conversation-process section with a change chart when a multi-turn log is present.
- HTML must expose top-right actions for `Print` and `Save as PDF`; the PDF path should use the browser print dialog instead of a separately generated artifact.
- When the user prints or saves the HTML as PDF, the report should automatically expand folded sections so the exported document is complete.

## Reference Map

- `references/intake-contract.md`: request-to-brief conversion
- `references/multi-turn-dialogue-loop.md`: incomplete-input handling and iterative questioning
- `references/evidence-prior-playbook.md`: evidence tiers, priors, update-path selection
- `references/decision-report-contract.md`: required report sections and schema alignment
- `references/report-export-pipeline.md`: automatic HTML/Markdown generation and bilingual HTML rules
- `references/sensitivity-and-safety.md`: sensitivity analysis and high-risk disclaimers
- `scripts/bayesian_decision_report.py`: canonical V0/V1 calculation
- `scripts/generate_report_bundle.py`: Chinese-first Markdown plus bilingual HTML
