# Decision Report Contract

Every report should follow this structure.

## Required Sections

1. One-sentence conclusion
2. If available, multi-turn dialogue process and decision readiness
3. Decision question
4. Prior setup
5. New evidence table
6. Bayesian update
7. Natural-frequency explanation
8. Action thresholds
9. Expected value comparison
10. Sensitivity analysis
11. Next information to collect
12. Caveats and risks
13. Appendix or calculation note

When export is enabled, the same report should be rendered consistently to:

- `markdown` as the readable source draft
- `html` as the visual report

If the user needs PDF, the HTML version should be printable and saveable as PDF from the browser.

## Mandatory Distinctions

Never mix these categories:

- observed
- estimated
- assumed

The report should let a reviewer tell which numbers came from data, which came from judgment, and which came from policy or utility assumptions.

## Natural-Frequency Rule

Translate the main result into a concrete frequency statement.

Example:

- "Out of 100 similar cases, the prior suggests about 18 successes."
- "After current evidence, the estimate becomes about 47 successes out of 100."

## Output Schema Alignment

Target the JSON layout in `templates/report.schema.json`.

At minimum, fill:

- `summary`
- `prior`
- `evidence`
- `posterior`
- `decision`
- `sensitivity`
- `natural_frequency`
- `warnings`

## Recommendation Rule

Do not stop at posterior probability.

The conclusion must answer:

- what to do now
- why that action is justified
- what evidence would change the recommendation
- when to reopen the decision
- if a dialogue log exists, whether the decision is now mature enough to act on
