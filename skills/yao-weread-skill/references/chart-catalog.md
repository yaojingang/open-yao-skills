# Chart Catalog

The HTML report should expose more than 20 chart modules. Use available data first and degrade visibly when a module lacks source fields.

## Core Modules

1. KPI strip: total read time, read days, books touched, note count.
2. Monthly read time bar/line.
3. Monthly reading days line.
4. Reading-day duration distribution.
5. Weekday by month heatmap.
6. Cumulative read time area.
7. Monthly read-stat stacked bars.
8. Annual read-time comparison.
9. Top books by read time.
10. Category radar.
11. Category read-time bar.
12. Category treemap.
13. Preferred authors bar.
14. Preferred publishers bar.
15. Reading vs listening donut.
16. Shelf composition donut.
17. Shelf category treemap.
18. Finished vs unfinished shelf pie.
19. Public/private shelf pie.
20. Archive/booklist bar.
21. Recent shelf activity timeline.
22. Notebook top books bar.
23. Note type stacked bar.
24. Notebook progress scatter.
25. Highlight/thought word cloud.
26. Note timeline.
27. Highlight length histogram.

## Interpretation Rules

- Use `readLongest[].readTime` as book-level reading time; never infer book time from shelf recency.
- Drop anonymous `readLongest` rows where neither book nor album metadata contains a real title.
- Use `preferCategory[].readingTime` and `readingCount` for category modules.
- Use `preferAuthor[].readTime` only as display text unless a numeric seconds field exists.
- Use shelf category strings for shelf asset distribution; use annual preference categories for actual reading preference.
- Label `mp` as article-collection entry, not a book.
- Do not render notebook category distribution when WeRead notebook overview only returns `未分类`.
- For word clouds, prefer known domain terms and cap the rendered terms to a smaller high-signal set when deterministic segmentation would otherwise create phrase fragments.
