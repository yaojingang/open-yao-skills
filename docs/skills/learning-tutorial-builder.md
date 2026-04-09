# Learning Tutorial Builder

## 中文说明

`learning-tutorial-builder` 面向“要做教程成品”的场景，不只是做搜索或写稿。

它会先引导用户说明学习目标、背景、当前水平、时间预算和期望输出，再从官方文档、标准规范、维护者文档、监管资料等权威来源中提炼内容，最终生成一份个性化学习教程。默认以 markdown 为源稿，按需导出 `docx`、`pdf`，并且可以在教程确认后继续扩展成学习网页。

### 适合什么时候用

- 你想把某个主题做成系统化教程
- 你希望内容有权威来源支撑
- 你希望内容能因学习者画像不同而变化
- 你希望最后得到文档成品，而不只是对话答案

### 主流程

1. 收集学习者画像和目标
2. 筛选权威来源
3. 写出个性化教程
4. 导出为 `docx`、`html`、`pdf`
5. 如有需要，再继续做个性化学习网页

### 输出物

- 教程 markdown
- 来源附录
- 可选 `docx`
- 可选 `pdf`
- 可选学习网页扩展

## English Usage

`learning-tutorial-builder` is for producing a finished learning packet, not just answering questions or collecting links.

Use it when you need to:

- clarify the learner profile before writing
- research authoritative or official sources first
- generate a personalized tutorial or study guide
- export the result to `docx` and `pdf`
- optionally extend the approved tutorial into a learner-facing webpage

### Main Workflow

1. Capture learner context and target outcome.
2. Gather primary or official sources.
3. Write the tutorial in markdown.
4. Export the tutorial into requested formats.
5. Offer the webpage branch only after the tutorial is accepted.

### Command

```bash
python3 skills/learning-tutorial-builder/scripts/export_tutorial.py tutorial.md out/
```

### Important Boundary

Do not use this skill for:

- one-off factual answers
- generic web research summaries
- export-only file conversion
- webpage-only requests with no tutorial packet behind them
