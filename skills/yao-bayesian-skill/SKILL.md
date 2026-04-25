---
name: yao-bayesian-skill
description: Convert uncertain real-world choices into an auditable Bayesian evidence-to-action report. Use when the user wants a hypothesis, reference class, prior, evidence grading, posterior update, sensitivity analysis, expected-value action comparison, a next-information recommendation, and an exported report bundle such as HTML, PDF, or Word. Good fits include Bayesian decision analysis, likelihood-ratio updates, action thresholds, and deciding whether to do X under uncertainty. Do not use for Bayes theorem tutoring, homework, generic brainstorming with no report, or final licensed medical, legal, or financial advice.
---

# Yao Bayesian Skill

## Use This Skill For

- turning a vague decision into one explicit hypothesis, time horizon, success metric, and action set
- separating priors, evidence quality, posterior result, sensitivity, and action choice
- starting from incomplete user input, issuing a weak initial prior plus a preliminary judgment, then guiding the user through multiple follow-up turns
- recording each decision round so the final report can explain how priors, posteriors, and readiness changed over time
- exporting one synchronized report bundle: Chinese-first `markdown/pdf/docx` plus bilingual `html`

## Do Not Route Here

- Bayes theorem tutoring or homework-only calculations
- broad research or brainstorming with no explicit decision report
- final professional medical, legal, or investment advice

## Default Workflow

1. Use `references/intake-contract.md` to convert the request into one structured decision brief.
2. If the input is incomplete, read `references/multi-turn-dialogue-loop.md` and start with a weak prior plus a preliminary judgment instead of pretending certainty.
3. Use `references/evidence-prior-playbook.md` to grade evidence and choose the lightest valid update path.
4. Maintain a structured conversation log for each round: what the user added, what gap remained, how the Bayesian update changed, and whether the case is now ready to decide.
5. Run `scripts/bayesian_decision_report.py` for canonical JSON or `scripts/generate_report_bundle.py` for the full bundle.
6. Read `references/report-export-pipeline.md` before export. The normal bundle is `json + markdown + html + pdf + docx`.
7. Finalize with `references/decision-report-contract.md` and `references/sensitivity-and-safety.md`.

## Output Contract

- Deliver one Bayesian decision report bundle, not a formula dump.
- Mark each number as observed, estimated, or assumed.
- Surface weak evidence, dependence risk, and model limits.
- When the user starts with only a question plus current state, begin with a weak prior and a preliminary action read; then ask the minimum next questions needed to improve the decision.
- For multi-turn use, keep a round-by-round log of the evolving prior, posterior, decision readiness, remaining gaps, and the exact Bayesian formula or update path used in that round.
- Final reports must analyze the dialogue process itself: what changed in each round, which information moved the belief the most, whether the decision is now ready, and what is still missing if it is not.
- If the result is unstable, recommend a lower-cost test before a heavier commitment.
- In high-risk domains, label the output as decision support only.
- Human-facing reports default to Simplified Chinese; HTML must also provide bilingual Chinese/English switching with sticky top navigation.
- The bundle must explicitly state that it was auto-generated from one structured input.
- Put a plain-language executive summary first: what to do now, why, and why not the other options before the technical sections.
- HTML should default to the full professional view while keeping advanced sections collapsible.
- HTML should also show a conversation-process section with a change chart when a multi-turn log is present.
- PDF tables must wrap long CJK or mixed Chinese-English text inside the cell width and must not overflow beyond the right margin.
- When needed, the exporter may also generate an experimental `print.html + browser.pdf` branch so HTML and PDF can share a closer paged-CSS layout.

## Reference Map

- `references/intake-contract.md`: request-to-brief conversion
- `references/multi-turn-dialogue-loop.md`: incomplete-input handling and iterative questioning
- `references/evidence-prior-playbook.md`: evidence tiers, priors, update-path selection
- `references/decision-report-contract.md`: required report sections and schema alignment
- `references/report-export-pipeline.md`: automatic bundle generation and bilingual HTML rules
- `references/sensitivity-and-safety.md`: sensitivity analysis and high-risk disclaimers
- `scripts/bayesian_decision_report.py`: canonical V0/V1 calculation
- `scripts/generate_report_bundle.py`: Chinese-first bundle plus bilingual HTML
