# Report Export Pipeline

## Default Artifact Set

The recommended final bundle is:

- `json`
- `markdown`
- `html`
- `pdf`
- `docx`

`json` is the canonical structured result. The other formats are renderings of the same decision output.

Language default:

- `markdown`, `pdf`, and `docx` should default to Simplified Chinese
- `html` should be bilingual and allow one-click switching between Chinese and English

## Why This Exists

Different review contexts need different report shapes:

- `html` for visual review and internal sharing
- `pdf` for fixed-layout circulation
- `docx` for editable executive or client-facing workflows
- bilingual `html` for mixed-language teams that want the same calculation result in two display languages

## Export Rule

Prefer one command that generates the full bundle from the same request input.

Use:

```bash
python3 scripts/generate_report_bundle.py input_file.json output_dir
```

The exporter should:

1. build the canonical decision JSON
2. render the readable markdown report in Simplified Chinese
3. render the visual HTML report with bilingual Chinese/English switching
4. generate the PDF report in Simplified Chinese
5. generate the Word report in Simplified Chinese

## Required Sections In Rendered Reports

Each human-facing format should include:

- a plain-language conclusion that a non-technical user can read first
- a clear action recommendation and the next 1 to 3 steps
- a short explanation of why the recommendation beats the other options
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
- an explicit note that the bundle was generated automatically from the same structured input

## HTML-Specific UX Rule

The HTML report should also include:

- a sticky top navigation bar that remains visible while scrolling
- section anchor links for the main report sections
- a one-click Chinese / English language toggle
- an executive-summary style top section that ordinary users can understand without reading the full Bayesian details
- a `简版 / 专业版` display toggle with `简版` as the default
- collapsible advanced sections so evidence, prior, sensitivity, and appendix stay closed until requested
- a conversation-process section with a change chart when the input includes multi-turn dialogue rounds
- the same workflow and capability summary as the PDF and Word versions

## Automation Rule

The rendered reports are not hand-written examples. They should be generated automatically from the same input request so the bundle stays reproducible.
