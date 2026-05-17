---
name: yao-weread-skill
description: Generate live or sample WeRead visual reading reports from 微信读书 skill data. Use when asked to analyze 微信读书 reading history, create a 读书报告, visualize reading stats, notes, shelves, word clouds, heatmaps, radar charts, export a polished HTML report, or create an AI-founder sample reading report. Do not use for generic book recommendations or raw WeRead API lookup without report generation.
---

# Yao WeRead Skill

Create a polished Chinese HTML report from WeRead account data. The default scope is the most recent 24 months ending today.

## Inputs

- `WEREAD_API_KEY` in the environment, using the format required by the 微信读书 skill.
- Optional report range: `--years`, `--start`, or `--end`.
- Optional note depth: `--max-note-books`; omit or pass `0` to process every notebook returned by WeRead.
- Optional output directory.
- Optional sample mode: `--sample-ai-founder --sample-scale 5`, which does not require `WEREAD_API_KEY`.

## Output

The workflow produces:

- `weread-report.html` — a kami-informed interactive HTML report.
- `weread-report-data.json` — aggregated, chart-ready data.
- `weread-raw-summary.json` — non-secret API shape and count summary for review.

Raw highlights and thoughts are used for aggregation. Treat report output as private unless the user explicitly asks to share or publish it.

## Workflow

1. Read the 微信读书 skill docs before calling APIs:
   - `shelf.md` for shelf counts and public/private rules.
   - `readdata.md` for reading-time units, period rules, and annual/monthly fields.
   - `notes.md` for notebook pagination, note count math, and highlight/thought text.
   - `book.md` only when book-level detail or progress is required.
2. Run `scripts/generate_weread_report.py`.
3. Verify generated HTML has at least 20 chart panels, no `TODO`/placeholder text, and no embedded API key.
4. If visual verification is requested or the report is changed materially, open the generated HTML in a browser and inspect desktop and narrow widths.

## Command

```bash
python3 scripts/generate_weread_report.py --output reports/generated
```

Useful options:

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --max-note-books 0 \
  --output reports/generated
```

AI founder sample report:

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --sample-ai-founder \
  --sample-scale 5 \
  --output reports/generated/ai-founder-sample
```

## Report Design

- Follow `references/report-design.md` for the kami-informed visual system.
- Follow `references/chart-catalog.md` for the chart module catalog.
- Follow `references/data-contract.md` for API field semantics and fallback rules.

## Boundaries

- Do not invent reading events, note text, ratings, or classifications that are not present in WeRead responses.
- The AI founder sample mode is for generating a reusable sample report without requiring a live account.
- Do not export full book content; only user-owned highlights/thoughts and metadata available through the 微信读书 skill.
- Do not store or print `WEREAD_API_KEY`.
- When exact rolling-day boundaries are unavailable, clearly label monthly or annual approximations.
