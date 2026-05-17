# Yao WeRead Skill

`yao-weread-skill` turns WeRead account data into a polished personal reading analytics report.

It is designed for people who want more than a raw reading-time export: the skill collects reading rhythm, shelf assets, category preference, author and publisher bias, note density, highlight length, and high-frequency note terms, then renders them into a single Chinese HTML report.

## What It Produces

- `weread-report.html`: interactive HTML report with KPI cards, narrative sections, tables, and charts.
- `weread-report-data.json`: chart-ready aggregated data.
- `weread-raw-summary.json`: non-secret coverage summary for verification.

The standard report contains more than 20 visual modules. The current chart catalog includes monthly reading time, reading days, weekday rhythm, cumulative reading hours, top books, category radar, category treemap, preferred authors, preferred publishers, reading/listening split, shelf composition, note type composition, notebook progress scatter, word cloud, note timeline, and highlight length distribution.

## Quick Start

Live WeRead account report:

```bash
export WEREAD_API_KEY="<your_api_key>"

python3 scripts/generate_weread_report.py \
  --years 2 \
  --max-note-books 0 \
  --workers 6 \
  --output reports/generated/latest
```

AI founder sample report:

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --sample-ai-founder \
  --sample-scale 5 \
  --output reports/generated/ai-founder-sample
```

Open the generated `weread-report.html` in a browser.

## How It Works

1. Reads WeRead data through the installed 微信读书 skill gateway.
2. Pulls monthly and annual reading stats from `/readdata/detail`.
3. Pulls shelf structure from `/shelf/sync`.
4. Pulls notebook overview from `/user/notebooks`.
5. Pulls highlights and reviews from `/book/bookmarklist` and `/review/list/mine`.
6. Aggregates data into a stable JSON contract.
7. Renders a standalone HTML report with ECharts and a deterministic Chinese phrase extraction fallback.

## Design Notes

- The report uses a warm paper, ink-blue, editorial visual system inspired by `kami`.
- Charts are grouped by narrative section: time rhythm, reading preference, shelf assets, and notes/semantics.
- Word cloud extraction prefers domain terms and filters common Chinese phrase fragments.
- Book-level reading time uses `readLongest[].readTime` and does not infer reading time from shelf recency.
- Anonymous `readLongest` rows without real book or album titles are dropped.

## Privacy Notes

- The script reads `WEREAD_API_KEY` from the environment and does not write it to disk.
- Generated reports may contain personal highlights and thoughts. Do not commit real `reports/generated/latest` output to a public repository.
- The included `examples/ai-founder-report/weread-report.html` is a public sample report.

