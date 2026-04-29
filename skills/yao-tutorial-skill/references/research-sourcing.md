# Research Sourcing

Use this guide to gather enough evidence to teach the topic without turning research into an endless crawl.

## Source Ladder

1. Primary authority: official docs, standards, specifications, maintainer docs, regulator guidance, university or lab pages.
2. Scholarly evidence: peer-reviewed papers, preprints from known venues, paper platform metadata, citations, surveys, benchmark papers.
3. Implementation evidence: GitHub repositories, examples, issues, releases, docs folders, notebooks, demos, and tests.
4. Practitioner discussion: X.com posts, long threads, conference slides, engineering blogs, podcasts with transcripts, and respected expert notes.
5. Secondary explainers: only use them to fill teaching gaps after stronger sources are in place.

Do not give social posts the same weight as papers, official docs, or working code. Use them to find names, cases, failure modes, debates, and current language.

## Minimum Research Set

For a full tutorial, aim for `10-18` source records:

- `2-5` papers or paper-platform records
- `2-5` GitHub records
- `2-4` official or first-party authority records
- `2-5` practitioner discussion or case records, including X.com when accessible

For niche topics, use fewer sources but state the gap. For high-stakes topics, broaden primary sources and avoid unsupported claims.

## Search Recipes

### X.com

Use X for current discourse and practitioner signals:

- `"<topic>" (tutorial OR guide OR thread OR "case study") has:links -is:retweet lang:<target-language>`
- `"<topic>" (mistake OR lessons OR "what I learned") has:links -is:retweet`
- `from:<expert_handle> "<topic>"`
- `"<topic>" (paper OR repo OR demo) has:links`

Use `lang:zh-CN` for Simplified Chinese, `lang:zh-TW` for Traditional Chinese, and `lang:en` for English. When the target language has weak results, search both the target language and English, then write the tutorial in the requested language.

Record the author handle, post URL, date, author credibility, linked source, and the claim you can safely use. If X is blocked by login, rate limits, or search instability, use scoped web search such as `site:x.com "<topic>" "repo"` and report the limitation.

### Papers And Paper Platforms

Use Semantic Scholar, arXiv, PubMed, ACM Digital Library, IEEE Xplore, SSRN, Google Scholar, Papers With Code, or domain-specific indexes.

Search patterns:

- `"<topic>" survey`
- `"<topic>" tutorial`
- `"<topic>" benchmark`
- `"<topic>" application case study`
- `"<topic>" limitations`

Capture title, authors, year, venue, URL or DOI, abstract-level relevance, citation or influence signals when visible, and what the tutorial should borrow.

### GitHub

Use GitHub search and repository pages for implementation and examples:

- `"<topic>" in:name,description,readme stars:>100 pushed:>2025-01-01`
- `topic:<topic-slug> stars:>50`
- `"<topic>" "example" language:<language>`
- `"<topic>" "notebook" OR "demo"`
- inspect `README`, `docs/`, `examples/`, `tests/`, releases, issues, and discussions

Do not treat stars as proof. Check recency, maintainer activity, license, examples, issue quality, and whether code matches the current API.

### Authority Sharing Sites

Look for:

- official product docs and blogs
- research lab posts
- engineering blogs from reputable teams
- conference talks and slide decks
- standards bodies and specifications
- university lecture notes or lab tutorials
- public notebooks from credible maintainers

Use these to translate theory into approachable teaching language, but keep claims traceable.

## Source Record Schema

Each source record should include:

- `id`: short stable ID such as `P1`, `G2`, `X3`, `A4`
- `title`
- `url`
- `source_type`: paper, official, GitHub, X, talk, engineering blog, standard, course note
- `date_accessed`
- `published_or_updated`
- `authority_reason`
- `use_for`: theory, practice, case, terminology, failure mode, example, visual
- `key_takeaway`
- `limits_or_cautions`

## Evidence Map

Before drafting, map each chapter to source IDs:

- chapter title
- learner question answered
- source IDs supporting theory
- source IDs supporting example or case
- visual idea
- claims to avoid or qualify

## Stop Rule

Stop research when:

- the tutorial outline can be supported chapter by chapter
- the central claims have primary or scholarly support
- examples have working-code or first-party evidence
- no chapter depends only on social posts

Continue research when:

- sources contradict each other
- the topic changed recently
- a tool/API/version matters
- a chapter has no credible source backing

## Citation And Copyright Rules

- Cite exact URLs in the source appendix.
- Use short quotes only when wording is essential.
- Paraphrase source material in beginner-friendly language.
- Never copy long passages, proprietary slides, paywalled text, or full social threads.
- If evidence is weak, label it as a practitioner signal rather than a fact.
