# Design Summary

## Owned job

`yao-kelly-skill` owns one recurring job:

Turn an uncertain invest / bet / allocate question into a conservative Kelly application report that tells the user whether to allocate, how much to allocate, why that number is disciplined, and what assumptions still matter.

## Primary hand-back

The finished deliverable is a Kelly application report with:

- action class
- full Kelly and conservative Kelly
- translated amount from the stated capital base
- key assumptions and caps
- why questioning stopped
- round log

## Deliberate boundaries

This skill does not own:

- generic Kelly tutoring
- guaranteed-return language
- martingale or all-in escalation
- final licensed investment, legal, or tax advice

## Why the workflow is conservative

- default output is fractional Kelly, not raw full Kelly
- multi-opportunity sizing uses dependence haircuts and total-cap scaling
- if edge quality is weak, the skill should prefer `skip`, `observe`, or `cheap test first`
- when more questioning cannot change the action class, the skill stops and delivers

## Logging model

Two logs are required:

- user-case round log
- package iteration log in `history/CHANGELOG.md`
