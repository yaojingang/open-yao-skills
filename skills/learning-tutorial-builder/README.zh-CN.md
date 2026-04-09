# Learning Tutorial Builder

## 中文说明

`learning-tutorial-builder` 用来把一个模糊的学习需求，整理成一份可交付、可追溯、可导出的学习教程包。

它的核心流程是：

1. 先通过简短问答明确学习目标、用户背景、当前水平、时间预算和输出格式。
2. 再优先从官方文档、标准规范、维护者文档、监管指南等权威来源收集资料。
3. 基于用户画像写出个性化教程，而不是简单堆砌搜索结果。
4. 以 markdown 作为单一源稿，按需导出 `docx`、`html`、`pdf`。
5. 在教程内容确认后，再决定是否继续生成个性化学习网页。

## 适用场景

- 想把某个主题做成系统化学习教程
- 希望教程内容有权威来源支撑
- 希望根据不同学习者背景定制内容深度和示例
- 希望最终得到 Word、PDF，或进一步扩展成网页

## 不适用场景

- 只想问一个事实性问题
- 只想做泛泛的资料汇总
- 只需要把现成文档转成 PDF
- 只想做网页，不需要教程内容本身

## 关键文件

- `SKILL.md`：路由与主流程
- `input/learner_profile_template.json`：用户画像模板
- `references/authority-research.md`：权威来源研究规则
- `references/tutorial-assembly.md`：教程结构规则
- `references/export-pipeline.md`：导出链路说明
- `scripts/export_tutorial.py`：导出脚本

## 英文使用说明入口

See [README.md](README.md) for the English usage guide.
