# Output Risk Profile

## Top Risks

1. **False precision in date ranges**  
   `/readdata/detail` works by natural periods. The script must use daily `readTimes` when available and label approximations when it cannot.

2. **Miscounting shelf size**  
   Shelf total must include books, albums, and the article-collection entry when present.

3. **Weak word cloud quality**  
   Chinese segmentation is not guaranteed. The script uses deterministic phrase extraction and stopwords; the report labels the result as a note/highlight phrase cloud.

4. **Privacy leakage**  
   User highlights and thoughts can be personal. Reports are local artifacts and should not be shared unless the user asks.

5. **Over-dashboarding**  
   More than 20 charts can become noisy. The report groups charts by narrative section and gives each chart a caption.

## Gates

- At least 20 chart panels are present.
- Generated HTML has no `WEREAD_API_KEY`, `TODO`, or unresolved template token.
- Aggregated data JSON is valid.
- Empty charts have visible captions rather than fabricated values.
