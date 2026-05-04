---
name: yao-kelly-skill
description: "Turn uncertain resource-allocation requests into practical action plans using Kelly sizing as a conservative allocation engine. Use when a user needs to decide whether an opportunity is suitable for Kelly, what minimum action package to run, how much resource to cap, when to add or stop, and how to review results. Do not use for pure formula tutoring, guaranteed-return claims, martingale escalation, or final licensed investment, legal, or tax advice."
---

# Yao Kelly Skill

## Use This Skill For

- turn "should I invest, bet, or allocate, and how much?" into a practical resource allocation plan
- decide whether the user's problem is actually suitable for Kelly-style sizing
- translate a percentage into a minimum action package with owner, metric, review window, add condition, and stop condition
- start with incomplete input, give a provisional view early, then ask only the minimum high-impact follow-up questions
- size a single bet or opportunity, or conservatively split a pool across several opportunities
- keep a round-by-round log for the current case and an append-only change log for future edits to this skill

## Do Not Route Here

- pure formula tutoring, homework solving, or generic finance education
- requests for guaranteed returns, sure-win systems, or martingale-style escalation
- final licensed investment, legal, or tax advice
- leverage sizing with no bounded downside model

## Default Workflow

1. Use `references/intake-contract.md` to identify the user's real resource pool, decision question, minimum action unit, review window, and opportunity candidates.
2. If the input is incomplete, read `references/multi-turn-kelly-loop.md`:
   - ask only `1-3` questions that can materially change the result
   - recalculate `decision_readiness` after every round
   - stop asking when the threshold is met or the action class is already stable
3. Decide whether Kelly is suitable:
   - use it when downside is bounded, the opportunity can be tested or repeated, and probabilities can be approximated
   - switch to a test-first or risk-review answer when the decision is irreversible, one-off, or has unbounded downside
4. Use `references/kelly-sizing-playbook.md` to choose the formula path:
   - binary opportunity: standard Kelly closed form
   - scenario-based opportunity: maximize `E[log(1 + f * r)]`
   - multiple opportunities: compute standalone Kelly first, then apply fractional Kelly, dependence haircuts, and total exposure scaling
5. Run `scripts/kelly_allocation_report.py` for canonical JSON sizing output.
6. Run `scripts/generate_html_report.py` when the user wants a polished standalone HTML report or PDF-ready artifact.
7. Use `references/output-contract.md` to produce a practical allocation report:
   - resource snapshot
   - fit assessment
   - minimum action packages
   - Kelly sizing cap
   - add, stop, and review conditions
8. Use `references/logging-contract.md` to maintain:
   - the case round log for the current user request
   - the append-only iteration log in `history/CHANGELOG.md` whenever this skill package changes
9. Apply `references/safety-and-scope.md` before finalizing.

## Core Rules

- default to `fractional Kelly`, not `full Kelly`
- never make the formula the main product; the main product is a resource allocation action plan
- mark each key number as `observed`, `estimated`, or `assumed`
- if correlation across opportunities is unknown, shrink exposure instead of assuming independence
- if the edge is negative, fragile, or mostly assumption-driven, recommend `no allocation`, `observe`, or `run a cheap test first`
- always translate the final fraction into the smallest next action the user can actually do
- include add, stop, and review conditions so the allocation can improve after real feedback
- stop asking once more questions are unlikely to change the action class
- every future edit to this skill must append a dated note to `history/CHANGELOG.md`

## Output Contract

- deliver a Kelly application report, not just a formula
- prefer `HTML + JSON` when the user wants a report artifact; use JSON as the audit source and HTML as the readable hand-back
- the report must include:
  - recommendation summary and action class
  - Kelly fit assessment
  - current capital or resource base, protected reserve, risk budget, and translated amount
  - minimum action package per opportunity
  - full Kelly fraction and conservative Kelly execution cap
  - add, stop, and review conditions
  - formula path and key assumptions
  - why the questioning stopped
  - round log
