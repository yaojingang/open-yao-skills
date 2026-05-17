# Data Contract

This report depends on data exposed by the installed 微信读书 skill.

## API Sources

| Source | Endpoint | Use |
|---|---|---|
| Reading stats | `/readdata/detail` | Monthly and annual read time, read days, read stats, top books, categories, authors, publishers, reading/listening split when available |
| Shelf | `/shelf/sync` | Book, album, article-collection counts, shelf categories, recent reading/update signals, archive counts, public/private state |
| Notebook overview | `/user/notebooks` | Books with notes, note totals, highlights, thoughts, bookmarks, reading progress |
| Highlight text | `/book/bookmarklist` | User highlights for word cloud, length distribution, highlight timeline |
| Thoughts/reviews | `/review/list/mine` | User thoughts and reviews for word cloud and note timeline |

## Required Semantics

- Reading durations are seconds. Convert to hours/minutes only at presentation time.
- Shelf total is `books.length + albums.length + (mp exists ? 1 : 0)`.
- Notebook total notes are `reviewCount + noteCount + bookmarkCount`.
- Notebook pagination uses `count` plus top-level `lastSort`; do not use `params`, `offset`, or `limit`.
- `/review/list/mine` requires lowercase `bookid`.
- `readTimes` is detail data; use `totalReadTime` for complete periods and `readTimes` for daily/monthly visualization.

## Default Range

Default range is the most recent 24 months ending on the execution date in `Asia/Shanghai`.

Implementation:

1. Query every natural month overlapping the range.
2. Use daily `readTimes` entries when available to filter exact start/end dates.
3. Use the current natural month as partial data if the range ends inside it.
4. Query annual data for every calendar year touched by the range for preference modules.

## Fallback Rules

- If a preference field is missing, render the chart panel with an honest empty state.
- If highlight/thought text fetch fails for one book, keep the notebook overview and record the fetch error count.
- If word segmentation is unavailable, use deterministic phrase extraction with Chinese stopwords, domain-term preference, and n-gram filtering.
- If the chart library fails to load, the report must still show KPI cards, tables, and textual summaries.

## AI Founder Sample Mode

`--sample-ai-founder --sample-scale 5` generates an AI-founder reader sample report without calling WeRead APIs or requiring `WEREAD_API_KEY`.

- Sample mode uses bundled reader-profile data to exercise all report modules.
- Sample output must set `meta.sampleReport=true`.
- Live mode must continue to use only data returned by the 微信读书 skill.
