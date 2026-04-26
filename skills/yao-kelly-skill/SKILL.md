---
name: yao-kelly-skill
description: "Convert betting, investment, and resource-allocation requests into conservative Kelly sizing reports with multi-turn clarification, readiness thresholds, scenario-based allocation, fractional Kelly defaults, and append-only round plus iteration logs. Use when a user wants to decide whether to allocate and how much to allocate under uncertainty. Do not use for pure formula tutoring, guaranteed-return claims, martingale escalation, or final licensed investment, legal, or tax advice."
---

# Yao Kelly Skill

## Use This Skill For

- turn "should I invest, bet, or allocate, and how much?" into an actionable Kelly application report
- start with incomplete input, give a provisional view early, then ask only the minimum high-impact follow-up questions
- size a single bet or opportunity, or conservatively split a pool across several opportunities
- keep a round-by-round log for the current case and an append-only change log for future edits to this skill

## Do Not Route Here

- pure formula tutoring, homework solving, or generic finance education
- requests for guaranteed returns, sure-win systems, or martingale-style escalation
- final licensed investment, legal, or tax advice
- leverage sizing with no bounded downside model

## Default Workflow

1. Use `references/intake-contract.md` to classify the request as `binary-bet`, `scenario-sizing`, or `multi-opportunity-allocation`.
2. If the input is incomplete, read `references/multi-turn-kelly-loop.md`:
   - ask only `1-3` questions that can materially change the result
   - recalculate `decision_readiness` after every round
   - stop asking when the threshold is met or the action class is already stable
3. Use `references/kelly-sizing-playbook.md` to choose the formula path:
   - binary opportunity: standard Kelly closed form
   - scenario-based opportunity: maximize `E[log(1 + f * r)]`
   - multiple opportunities: compute standalone Kelly first, then apply fractional Kelly, dependence haircuts, and total exposure scaling
4. Run `scripts/kelly_allocation_report.py` for canonical JSON sizing output.
5. Run `scripts/generate_html_report.py` when the user wants a polished standalone HTML report or PDF-ready artifact.
6. Use `references/output-contract.md` to produce a Kelly application report that gives the action first, then the math, assumptions, sensitivity, and remaining risk.
7. Use `references/logging-contract.md` to maintain:
   - the case round log for the current user request
   - the append-only iteration log in `history/CHANGELOG.md` whenever this skill package changes
8. Apply `references/safety-and-scope.md` before finalizing.

## Core Rules

- default to `fractional Kelly`, not `full Kelly`
- mark each key number as `observed`, `estimated`, or `assumed`
- if correlation across opportunities is unknown, shrink exposure instead of assuming independence
- if the edge is negative, fragile, or mostly assumption-driven, recommend `no allocation`, `observe`, or `run a cheap test first`
- stop asking once more questions are unlikely to change the action class
- every future edit to this skill must append a dated note to `history/CHANGELOG.md`

## Output Contract

- deliver a Kelly application report, not just a formula
- prefer `HTML + JSON` when the user wants a report artifact; use JSON as the audit source and HTML as the readable hand-back
- the report must include:
  - recommendation summary and action class
  - current capital or resource base and translated amount
  - full Kelly fraction and conservative Kelly fraction
  - formula path and key assumptions
  - exposure caps, reserve rules, and sensitivity
  - why the questioning stopped
  - round log
