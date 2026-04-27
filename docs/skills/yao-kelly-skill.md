# Yao Kelly Skill

`yao-kelly-skill` turns uncertain investment, betting, and resource-allocation questions into conservative Kelly sizing reports.

It is not a formula tutor. Its job is to help answer:

- should I allocate at all
- how much should I allocate
- how conservative should the raw Kelly number become
- what assumptions still matter
- why the skill stopped asking follow-up questions

## When To Use It

Use this skill when the user has a bounded opportunity and needs a disciplined sizing recommendation:

- a single bet with win probability and odds
- one investment or resource allocation with best/base/bear scenarios
- several competing opportunities that share one capital or resource pool
- an incomplete request where the assistant should ask only the few questions that can change the action

Do not use it for:

- guaranteed-return claims
- martingale or all-in escalation
- pure Kelly formula homework
- final licensed investment, legal, or tax advice

## Workflow

1. Classify the case as `binary-bet`, `scenario-sizing`, or `multi-opportunity-allocation`.
2. Build a structured Kelly brief from the user's objective, capital base, payoff model, probabilities, constraints, confidence, and dependence assumptions.
3. If information is incomplete, score `decision_readiness` and ask only the top `1-3` missing questions.
4. Stop asking when readiness reaches the threshold or the action class is already stable.
5. Compute full Kelly, then apply fractional Kelly, dependence haircuts, caps, reserve rules, and total exposure scaling.
6. Output canonical JSON plus a polished standalone HTML report.
7. Append every package-level iteration to `history/CHANGELOG.md`.

## Outputs

The public version includes:

- `scripts/kelly_allocation_report.py`: canonical JSON calculation
- `scripts/generate_html_report.py`: standalone HTML renderer
- `reports/example-brief.json`: sample structured input
- `reports/example-output.json`: sample calculation output
- `reports/example-html-report.html`: sample HTML report with print/save-PDF support
- `reports/marketing-budget-report.html`: quarterly customer-acquisition budget allocation example
- `reports/engineering-hours-report.html`: non-financial engineering-capacity allocation example
- `history/CHANGELOG.md`: append-only iteration log

## HTML Report

The HTML report is designed as an operational decision artifact. The first viewport shows:

- action class
- recommended total exposure
- capital base
- recommended amount
- decision readiness
- total exposure cap

Each opportunity then shows raw full Kelly next to conservative Kelly so the haircut is visible. Scenario tables remain available for auditability.

The latest report format also includes a `普通人版结论` section before the technical details. It explains:

- what to do now
- how much to commit
- why the raw Kelly number was reduced
- when the user should recalculate instead of continuing with the old allocation

Reports now also open with a narrative framing section:

- background: what is happening
- tension: why the choice is hard
- user question: what the user is really unsure about
- solution path: how the report will turn the situation into a conservative allocation

After that, the report introduces the Kelly principle in plain language before showing the detailed scenario tables and sizing calculations.

## Example Reports

### Customer-acquisition budget

This case allocates a quarterly budget between proven search retargeting and a riskier KOL seeding campaign.

The sample conclusion is:

- total recommended exposure: `9.5%`
- total recommended budget: `¥28,425`
- search retargeting: `¥25,500`
- KOL seeding campaign: `¥2,925`

The point of this example is to show how the skill handles paid growth allocation where one channel is more proven and another has higher upside but weaker confidence.

### Engineering capacity allocation

This case allocates `120` monthly engineering hours between retention automation and an experimental AI triage assistant.

The sample conclusion is:

- total recommended exposure: `6.2%`
- total recommended capacity: `7.5 engineering-hours`
- retention automation: `6.4 engineering-hours`
- AI triage assistant: `1.1 engineering-hours`

The point of this example is to show that the same Kelly sizing logic can support non-currency resources when the user can define payoff scenarios and downside.

## Iteration And Publishing Rule

This skill is mirrored from the local source:

`/Users/laoyao/AI Coding/03-Development/Skills/yao-kelly-skill`

Future accepted iterations should:

- update the source skill
- append `history/CHANGELOG.md`
- refresh this public copy under `skills/yao-kelly-skill`
- update the registry and README when metadata changes
- commit and push `yao-open-skills` to GitHub
