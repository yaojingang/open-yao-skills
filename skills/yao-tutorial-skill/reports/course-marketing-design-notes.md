# Course Marketing Design Notes

Source reviewed: `/Users/laoyao/Downloads/《课程营销学：AI时代，如何快速做出爆品课》 .pdf`.

This report records the distilled principles integrated into `yao-tutorial-skill`. It is an internal design note, not public tutorial content.

## Sections Prioritized

- Opening method: every section should close the loop from method to case to reusable template.
- `2.1 名称`: course title design and five title attraction methods.
- `2.2 大纲`: "say human words" outline design, knowledge curse, and point-line-surface-system.
- `2.3 内容`: three levels of course content and the experience formula.
- `2.4 材料`: use stories, models, diagrams, tables, memorable lines, and emotional material to improve retention.

## Integrated Rules

1. Public tutorials must not expose internal source markers such as `[U1]`.
2. Final copy should be standalone, as if it were a finished public tutorial, not a note saying it was based on a reference article.
3. Titles should communicate user benefit, contrast, visual action, attachment, or authority.
4. Outlines should combine professional content with learner pain or desired outcome.
5. H3 headings should be specific learning items, not repeated generic labels.
6. Chapter structure should move from concrete scene to failed old approach, new method, result, and practice.
7. Content should not stop at knowledge transfer; it should change cognition and prompt a small action.
8. The default teaching rhythm is method, case, reusable checklist/template when appropriate.

## Validation Added

`scripts/validate_package.py` now fails packages that:

- expose `[U1]`, `[X1]`, `[A1]`, `[P1]`, `[G1]`, or similar source markers in `tutorial.md`, HTML, DOCX, or PDF text
- use public provenance wording such as `用户粘贴`, `基于...文章`, `根据...原文整理`
- repeat generic H3 labels such as `你要做的事`, `你要注意什么`, `示例`, or `检查点` across chapters

