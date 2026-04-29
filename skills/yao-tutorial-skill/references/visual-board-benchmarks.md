# Visual Board Benchmarks

Use this guide before generating `visuals/visual-spec.json` or running `scripts/build_visual_pack.py`.

The visual board should not look like a random collection of generated SVG cards. Treat it as a small teaching canvas system inspired by proven open-source tools, while keeping the final output restrained and `frontend-slides`-first.

## Reference Projects

Checked on 2026-04-28:

| Project | GitHub | Current signal | What to borrow |
| --- | --- | ---: | --- |
| Excalidraw | https://github.com/excalidraw/excalidraw | ~122k stars | visual thinking canvas, reusable shape library, SVG/PNG export, approachable diagrams |
| Mermaid | https://github.com/mermaid-js/mermaid | ~87.7k stars | diagram grammar, deterministic text-to-diagram generation, flow/sequence/state semantics |
| reveal.js | https://github.com/hakimel/reveal.js | ~71.1k stars | HTML-first presentation pages, strong viewport framing, PDF export discipline |
| tldraw | https://github.com/tldraw/tldraw | ~46.6k stars | infinite-canvas mental model, custom shapes, bindings, snapping, exportable canvas primitives |
| Slidev | https://github.com/slidevjs/slidev | ~46.1k stars | Markdown-first authoring, themeable slides, diagrams, icons, PDF/PNG/PPTX export |
| xyflow / React Flow | https://github.com/xyflow/xyflow | ~36.3k stars | explicit nodes/edges, handles, background, controls, graph UI conventions |
| Markmap | https://github.com/markmap/markmap | ~12.7k stars | markdown-to-mindmap hierarchy, readable radial/branch structures |
| AntV G6 | https://github.com/antvis/G6 | ~12.1k stars | graph layout, palettes, interaction patterns, clustered relationships |
| Observable Plot | https://github.com/observablehq/plot | ~5.2k stars | layered marks, scales, compact data visualization grammar |

## Borrowed Principles

### 1. Canvas Before Card

Each visual is an artboard, not a decorative card:

- fixed 16:9 artboard for export
- safe area on all sides
- one dominant teaching model per artboard
- no nested cards unless they represent real nodes
- use a faint canvas surface only when it helps separate the diagram from the document background

### 2. Semantic Elements

Every shape must have a teaching role:

- `node`: concept, decision, actor, step, layer, criterion
- `edge`: dependency, causality, transition, feedback
- `group`: category, phase, system boundary, comparison side
- `axis`: tradeoff dimension or evaluation scale
- `mark`: data point, score, status, evidence
- `annotation`: short reading cue, never a paragraph

Do not add visual furniture that has no semantic role.

### 3. Explicit Diagram Grammar

Before styling, decide the grammar:

- `flow`: ordered transformation
- `layer`: stacked abstraction or maturity levels
- `comparison`: two-sided contrast
- `cycle`: feedback or iteration
- `mindmap`: concept dependencies around a center
- `matrix`: two-dimensional decision model
- `network`: nodes and relationships
- `timeline`: chronological change

If the chapter cannot be mapped to one grammar, rewrite the chapter visual idea before drawing.

### 4. Layout Rules

Use deterministic layouts rather than arbitrary placement:

- align shapes to a clear grid
- keep one focal axis or one focal center
- keep 6 or fewer primary nodes on one artboard; use groups for more detail
- keep node labels under 12 Chinese characters or 4 English words when possible
- keep detail labels under 18 Chinese characters or 9 English words
- use line weight hierarchy: structure `1-2px`, relationships `2-3px`, focal edges `3-4px`
- never let arrows cross labels
- keep at least `24px` between neighboring shapes

### 5. Typography Rules

Use slide-grade hierarchy:

- artboard title: `28-36px`, one or two lines
- node title: `17-22px`
- node detail: `12-15px`
- metadata/kicker: `11-13px`
- captions live outside the SVG unless the visual must stand alone
- no negative letter spacing
- no viewport-scaled font sizes inside SVG exports

### 6. Color Rules

Use color as information:

- one ink-blue focal accent by default
- neutral fills for most nodes
- second accent only for real contrast, such as "before vs after" or "risk vs opportunity"
- background should be quieter than all content
- use warm ivory or parchment surfaces instead of pure white screenshot slabs
- avoid gradients, glassmorphism, heavy shadows, decorative texture, and stock-poster colors

### 7. Board HTML Rules

The `visuals/index.html` page is a working board for inspection:

- left sticky text rail for chapter navigation
- right workspace with one artboard per chapter
- each artboard keeps its exact export aspect ratio
- show only chapter label, title, summary, visual, and caption
- no visible helper copy such as "generated pack", "how to use", or placeholder marketing text
- no duplicate document title blocks

### 8. Export Rules

The board is not finished until:

- every SVG opens directly in a browser
- every PNG screenshot is at least `2x` scale
- labels do not clip or overlap
- the main diagram is vertically balanced, with no large empty lower band or browser gutter in the captured PNG
- every captured PNG shows the complete artboard, including the bottom border or a deliberate bottom safe area
- the HTML board is readable at desktop and mobile widths
- Word/PDF screenshots remain crisp after embedding
