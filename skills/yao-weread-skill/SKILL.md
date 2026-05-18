---
name: yao-weread-skill
description: 当用户需要分析微信读书阅读历史、生成读书报告、可视化阅读统计、笔记、书架、词云、热力图、雷达图，或导出精排 HTML 报告时使用。也适用于创建 AI 创业者示例阅读报告。不用于通用图书推荐，或不生成报告的原始微信读书 API 查询。
---

<!--
Copyright © 2026 姚金刚. All rights reserved.
Project: yao-weread-skill
Created by: 姚金刚
Date: 2026-05-16
X: https://x.com/yaojingang
-->

# Yao WeRead Skill

从微信读书账号数据生成精排中文 HTML 报告。默认范围为截至今天的最近 24 个月。

## 输入

- 环境变量 `WEREAD_API_KEY`，格式遵循微信读书 skill 的要求。
- 可选报告范围：`--years`、`--start` 或 `--end`。
- 可选笔记深度：`--max-note-books`；省略或传 `0` 时处理微信读书返回的全部笔记书籍。
- 可选输出目录。
- 可选示例模式：`--sample-ai-founder --sample-scale 5`，不需要 `WEREAD_API_KEY`。

## 输出

流程会生成：

- `weread-report.html`：参考 kami 排版风格的交互式 HTML 报告。
- `weread-report-data.json`：聚合后的图表数据。
- `weread-raw-summary.json`：不含密钥的 API 结构和计数摘要，便于复核。

报告还会生成一个读者画像模块：顶部诗性总结、1 条画像金句，以及从近两年划线中筛选出的最多 20 条高价值句子。原始划线和想法仅用于聚合分析与画像筛选。除非用户明确要求分享或发布，否则报告产物应视为私有内容。

## 工作流

1. 调用 API 前先阅读微信读书 skill 文档：
   - `shelf.md`：书架计数、公开/私密规则。
   - `readdata.md`：阅读时长单位、周期规则、年度/月度字段。
   - `notes.md`：笔记分页、笔记数计算、划线/想法文本。
   - `book.md`：仅在需要书籍详情或阅读进度时使用。
2. 运行 `scripts/generate_weread_report.py`。
3. 检查生成的 HTML 至少包含 20 个图表面板，没有 `TODO`、占位文本或内嵌 API key。
4. 检查矩形树图、热力图、横向条形图等高密度图表没有被默认边距压缩，没有右侧空白导致标签截断。
5. 检查读者画像模块：金句必须来自画像划线清单第一条；真实账号模式不得编造划线，划线不足 20 条时如实少展示。
6. 如果用户要求视觉验证，或报告排版有实质变化，使用浏览器打开生成的 HTML，并检查桌面、平板宽度和窄屏宽度。

## 命令

```bash
python3 scripts/generate_weread_report.py --output reports/generated
```

常用选项：

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --max-note-books 0 \
  --output reports/generated
```

AI 创业者示例报告：

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --sample-ai-founder \
  --sample-scale 5 \
  --output reports/generated/ai-founder-sample
```

## 报告设计

- 视觉系统遵循 `references/report-design.md`。
- 图表模块遵循 `references/chart-catalog.md`。
- API 字段语义和降级规则遵循 `references/data-contract.md`。
- 高密度图表必须显式设置容器占满、标签换行/隐藏策略和 resize 监听，避免 ECharts 默认布局留下空白。
- 内容画像必须基于真实划线文本生成，顶部总结可以使用统计口径生成温暖、诗性但不冒充用户原文的描述。

## 边界

- 真实账号模式下，不编造微信读书响应中不存在的阅读事件、笔记文本、评分或分类。
- AI 创业者示例模式用于在不接入真实账号时生成可复用示例报告。
- 不导出书籍全文；只使用用户自己的划线/想法，以及微信读书 skill 可访问的元数据。
- 不存储或打印 `WEREAD_API_KEY`。
- 无法获得精确滚动日期边界时，必须清楚标注月度或年度近似口径。
