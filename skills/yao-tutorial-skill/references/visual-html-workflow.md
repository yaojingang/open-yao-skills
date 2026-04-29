# Visual HTML Workflow

Every chapter needs one visual artifact. Use visuals to make structure visible, not to decorate.

Read `references/editorial-production.md` and `references/visual-board-benchmarks.md` before choosing the diagram style. The visual system should follow the `frontend-slides`-first rule: strong hierarchy, responsive density, no decorative-only elements, and crisp screenshots. Use `kami` only for restrained document typography and ink-blue discipline.

## Visual Types

Choose the simplest visual that explains the chapter:

- `flow`: process, sequence, pipeline, lifecycle
- `layer`: stack, architecture, abstraction levels
- `comparison`: before/after, option A vs option B
- `cycle`: feedback loop, iteration, reinforcement
- `mindmap`: concept map, vocabulary map, dependency map
- `matrix`: tradeoff grid, decision map, 2x2 model
- `network`: nodes and relationships
- `timeline`: chronological change

If a chapter needs a visual grammar outside these types, create a bespoke SVG/HTML visual rather than forcing the idea into the nearest template. Keep the same artboard, typography, color, caption, and screenshot rules.

## Visual Spec

Create `visuals/visual-spec.json` before generating graphics. Use `templates/visual-spec-template.json` as a starting point.

Each chapter entry should include:

- `id`: stable ID such as `chapter-01`; visible labels must render as `第1章`
- `title`
- `diagram_type`
- `summary`: what this visual teaches
- `nodes`: labels or objects with `label` and `detail`
- `caption`
- optional `center`
- optional `columns` for comparison charts
- optional `quadrants` for matrix charts
- optional `edges` for network/relationship charts
- optional `layout_note`: internal note explaining why this grammar is the clearest choice; do not render it in the final visual

For each chapter, also decide the visual job:

- mental model: explain a concept
- process: show a sequence
- architecture: show parts and relationships
- decision: show tradeoffs
- case: show what happens in practice
- checklist: show evaluation criteria

## Board Design Rules

Borrow the mature patterns from Excalidraw, tldraw, Mermaid, React Flow, Slidev, reveal.js, Markmap, AntV G6, and Observable Plot without copying their UI wholesale:

- Start from a semantic grammar: nodes, edges, groups, axes, marks, or annotations.
- Keep one artboard to one idea. If the chapter needs more than six primary nodes, group or split the visual.
- Use a fixed `16:9` export artboard with a visible safe area and deterministic layout.
- Prefer readable node-edge composition over generic card grids.
- Use Kami-style warm ivory paper instead of pure white slabs; the artboard should feel like a designed teaching canvas, not a browser screenshot.
- Keep the main diagram vertically balanced inside the safe area. Flow diagrams should not leave a large empty lower band after the final row of nodes.
- Give every visual a visible semantic frame: chapter label, title, short teaching summary, one diagram panel, and a small diagram-type label. Avoid a plain row of boxes floating on an empty canvas.
- Use restrained depth only when it improves scanability: subtle shadows, ink-blue emphasis, fine dividers, and warm surfaces. Do not add decorative gradients, blobs, or ornamental shapes.
- For `layer` visuals, split labels like `结构：文件和边界` into a primary concept and a secondary explanation so the learner can scan both levels.
- For `cycle` visuals, prefer curved arrows and a central idea over disconnected straight arrows.
- Use a quiet canvas board page for inspection: sticky text rail on the left, artboards on the right.
- Show only chapter label, title, summary, visual, and caption in the board page.
- Do not put helper copy, placeholder text, marketing copy, or generator labels into the board.
- Do not use background texture unless it encodes layout or canvas context.

## Generate The Visual Pack

From the tutorial output folder, run:

```bash
python3 /path/to/yao-tutorial-skill/scripts/build_visual_pack.py visuals/visual-spec.json visuals/
```

This creates:

- `visuals/index.html`
- one SVG file per chapter

Open `visuals/index.html` in a browser and inspect the layout before screenshotting.

## Screenshot And Embedding

Preferred path:

1. Generate SVG and HTML.
2. Open `visuals/index.html`.
3. Capture each visual into high-resolution `assets/screenshots/<chapter-id>.png`. The capture script should render the SVG inside a temporary zero-margin HTML page, capture a slightly taller browser viewport, then crop back to the exact SVG aspect ratio. This avoids macOS Chrome headless clipping the lower part of the artboard.

   ```bash
   python3 /path/to/yao-tutorial-skill/scripts/capture_visuals.py visuals/ assets/screenshots/
   ```

4. Embed the screenshot in `tutorial.md`:

   ```markdown
   ![第1章：Chapter title](assets/screenshots/chapter-01.png)
   ```

Fallback path:

- If screenshots fail, embed the local SVG path in markdown and keep `visuals/index.html` as the visual deliverable.
- If a diagram is too dense, reduce nodes before styling.
- If the built-in renderer cannot express the chapter's core relationship, manually create a custom SVG or HTML artboard in `visuals/`, document the choice in `visual-spec.json`, and capture it with the same screenshot workflow.

## Visual Quality Gate

- Each visual explains one idea.
- The visual has an explicit grammar and semantic elements, not arbitrary boxes.
- Labels fit inside shapes.
- The caption tells the learner what to notice.
- The visual can stand alone in PDF and Word exports.
- The visual is referenced in the chapter text.
- The visual uses source-backed entities when it represents facts, architecture, or a published model.
- Visuals based on user-provided examples should cite or trace to `U` source IDs in the chapter text or caption.
- PNG screenshots are generated at `2x` scale unless the user asks for lighter files.
- Screenshots should not contain visible browser gutters, pure-white bottom strips, or large unused artboard areas.
- The bottom edge of the visual artboard must be visible in the PNG; if the last rows match the page background instead of the artboard/border, recapture before exporting.
- No visual uses generic decoration as a substitute for structure.
- Repeated visual types are intentional; avoid using the same flow layout for every chapter.
- The visual HTML index must not include helper copy such as "generated visual pack"; it should only show the real title, chapter visuals, and captions.
- The visual HTML index should look like a compact canvas board, not a blog page or a stack of decorative cards.
