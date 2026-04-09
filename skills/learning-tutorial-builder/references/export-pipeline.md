# Export Pipeline

Use markdown as the single editable source of truth. Generate distribution formats from that source rather than maintaining separate copies by hand.

## Local Environment Notes

This workspace currently has:

- `pandoc` at `/opt/homebrew/bin/pandoc`
- browser app binaries detected for Google Chrome and Microsoft Edge
- no `soffice`, `xelatex`, `pdflatex`, or `typst` detected in the quick scan

## Recommended Pipeline

1. Write the tutorial in markdown.
2. Export `docx` with `pandoc`.
3. Export HTML with `pandoc`.
4. Print the HTML to PDF with a detected headless browser.

## Why This First Pass

- `pandoc` is reliable for markdown to `docx`.
- A local browser can print the same HTML to PDF without needing a LaTeX stack.
- The same HTML can later seed a learning webpage.

## Command Shape

```bash
python3 scripts/export_tutorial.py tutorial.md out/
```

Optional reference document for Word styling:

```bash
python3 scripts/export_tutorial.py tutorial.md out/ \
  --reference-doc templates/tutorial-reference.docx
```

## When To Escalate

- If the user needs advanced Word-only layout, custom headers, tracked changes, or strict corporate templates, route the export phase through the local `docx` skill.
- If the user needs form-heavy, merge-heavy, or post-processing PDF work, route the export phase through the local `pdf` skill.
- If the user wants the HTML export turned into a reusable frontend family, use the local `skill-pageforge` patterns once reference HTML exists.
