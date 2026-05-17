# Report Design

Use a kami-informed Chinese long-report style with enough density for visual analytics.

## Visual Direction

- Canvas: warm parchment `#f5f4ed`.
- Surfaces: ivory `#faf9f5` with warm borders.
- Accent: ink blue `#1B365D`, used sparingly for titles, key figures, and chart emphasis.
- Typography: serif-led headings, sans-serif functional labels and chart captions.
- No purple gradients, glass panels, decorative blobs, or cold blue-gray dashboard chrome.

## Structure

1. Cover band with date range and generation time.
2. Executive overview with KPI cards and key findings.
3. Time rhythm section: monthly, daily, weekday, cumulative, annual.
4. Reading preference section: books, categories, authors, publishers, reading/listening split.
5. Shelf asset section: shelf composition, categories, progress, privacy, archives, recent activity.
6. Notes and semantics section: note volume, composition, progress, word cloud, note timeline, highlight length.
7. Appendix with data coverage, caveats, and API source summary.

## HTML Rules

- The page is interactive on screen but printable enough to read as a report.
- Chart cards have stable dimensions and no nested-card layout.
- Every chart has a short caption explaining the data source or fallback.
- Empty states are explicit and quiet.
- Do not embed absolute local file paths.
- Do not embed the API key.
