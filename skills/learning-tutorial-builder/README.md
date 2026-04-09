# Learning Tutorial Builder

## What It Does

`learning-tutorial-builder` turns a vague learning request into a source-backed tutorial package.

It guides the user through a short learner intake, prefers authoritative sources, writes a personalized study guide in markdown, and can export the result to `docx` and `pdf`. After the tutorial is approved, it can also extend the content into an optional learning webpage.

## Main Workflow

1. Clarify the learner profile: topic, current level, target outcome, time budget, and output format.
2. Research official or primary sources first.
3. Assemble a personalized tutorial with exercises, examples, and citations.
4. Export the tutorial to `docx`, `html`, and `pdf` when requested.
5. Offer a webpage extension only after the tutorial content is accepted.

## Key Files

- `SKILL.md`: routing and workflow entrypoint
- `input/learner_profile_template.json`: learner brief schema
- `references/authority-research.md`: source selection rules
- `references/tutorial-assembly.md`: tutorial structure contract
- `references/export-pipeline.md`: markdown to `docx` and `pdf` pipeline
- `scripts/export_tutorial.py`: export runner

## Basic Usage

```bash
python3 skills/learning-tutorial-builder/scripts/export_tutorial.py tutorial.md out/
```

## Outputs

- tutorial markdown
- source appendix
- optional `docx`
- optional `html`
- optional `pdf`
- optional learning webpage follow-up

## Notes

- This skill is for building a tutorial packet, not for one-off factual answers.
- It is also not a generic webpage-design skill.
- The current public version uses `pandoc` plus a local browser for PDF generation.
