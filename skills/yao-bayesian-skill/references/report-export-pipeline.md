# Report Export Pipeline

## Default Artifact Set

The recommended final output is:

- `markdown`
- `html`

Language default:

- `markdown` should default to Simplified Chinese
- `html` should be bilingual and allow one-click switching between Chinese and English

## Why This Exists

Different review contexts need different report shapes:

- `html` for visual review and internal sharing
- `markdown` for readable source, copy, versioning, and lightweight collaboration
- bilingual `html` for mixed-language teams that want the same calculation result in two display languages

## Export Rule

Prefer one command that generates the HTML + Markdown pair from the same request input.

Use:

```bash
python3 scripts/generate_report_bundle.py input_file.json output_dir
```

The exporter should:

1. build the canonical decision result in memory
2. render the readable markdown report in Simplified Chinese
3. render the visual HTML report with bilingual Chinese/English switching

## Required Sections In Rendered Reports

Each human-facing format should include:

- a plain-language conclusion that a non-technical user can read first
- a clear action recommendation and the next 1 to 3 steps
- a short explanation of why the recommendation beats the other options
- a prior-hygiene section that shows only the 3-5 everyday Bayesian principles most relevant to the case
- when a multi-turn session exists, a process section that explains how the judgment changed across rounds
- when a multi-turn session exists, a round-by-round log of what new information was added and how the Bayesian update changed
- one-sentence conclusion
- decision question
- prior setup
- evidence summary
- Bayesian update
- action comparison
- sensitivity analysis
- next-information recommendation
- warnings and caveats
- skill workflow
- skill capabilities
- an explicit note that the reports were generated automatically from the same structured input

## HTML-Specific UX Rule

The HTML report should also include:

- a sticky top navigation bar that remains visible while scrolling
- section anchor links for the main report sections
- a one-click Chinese / English language toggle
- top-right actions for `Print` and `Save as PDF`
- an executive-summary style top section that ordinary users can understand without reading the full Bayesian details
- a prior-hygiene section near the top so users can see which judgment principles constrained the recommendation
- the professional view as the default presentation
- collapsible advanced sections so evidence, prior, sensitivity, and appendix stay closed until requested
- a conversation-process section with a change chart when the input includes multi-turn dialogue rounds
- automatic expansion of collapsible sections before the user prints or saves the page as PDF
- the same workflow and capability summary as the Markdown version

## HTML Print Rule

The HTML report should be printable as-is. When the user clicks `Print` or `Save as PDF`:

- folded sections should open automatically before the print dialog appears
- the print layout should hide sticky navigation and interactive controls
- the user should be able to use the browser print dialog to save the page as PDF without needing a separately generated PDF file

## Automation Rule

The rendered reports are not hand-written examples. They should be generated automatically from the same input request so the output stays reproducible.
