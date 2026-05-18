<!--
Copyright © 2026 姚金刚. All rights reserved.
Project: yao-weread-skill
Created by: 姚金刚
Date: 2026-05-16
X: https://x.com/yaojingang
-->

# Yao WeRead Skill

`yao-weread-skill` 用来把微信读书账户数据生成一份完整的个人阅读可视化报告。

它不是简单导出阅读时长，而是把阅读节律、书架资产、分类偏好、作者与出版社偏好、笔记密度、划线长度和高频笔记短语汇总到一份中文 HTML 报告中，便于做年度复盘、知识管理回顾和阅读画像展示。

## 输出内容

- `weread-report.html`：带 KPI 卡片、叙事分区、表格和图表的交互式 HTML 报告。
- `weread-report-data.json`：已经聚合好的图表数据。
- `weread-raw-summary.json`：不含密钥的覆盖范围和关键指标摘要，用于复核生成结果。

标准报告包含 20 个以上可视化模块，并额外生成读者画像内容。当前图表目录覆盖月度阅读时长、阅读天数、星期节律、累计阅读小时、读得最久的书、分类雷达、分类矩形树图、偏好作者、偏好出版社、文字阅读与听书拆分、书架构成、笔记类型构成、阅读进度与笔记量散点图、词云、笔记时间线和划线长度分布。画像内容包含顶部诗性总结、1 条金句，以及最多 20 条与报告特征相关的高价值划线。

## 快速开始

真实微信读书账号报告：

```bash
export WEREAD_API_KEY="<你的_WEREAD_API_KEY>"

python3 scripts/generate_weread_report.py \
  --years 2 \
  --max-note-books 0 \
  --workers 6 \
  --output reports/generated/latest
```

AI 创业者示例报告：

```bash
python3 scripts/generate_weread_report.py \
  --years 2 \
  --sample-ai-founder \
  --sample-scale 5 \
  --output reports/generated/ai-founder-sample
```

生成后用浏览器打开 `weread-report.html`。

## 工作逻辑

1. 通过已安装的微信读书 skill 网关读取数据。
2. 从 `/readdata/detail` 获取月度和年度阅读统计。
3. 从 `/shelf/sync` 获取书架结构。
4. 从 `/user/notebooks` 获取有笔记的书籍概览。
5. 从 `/book/bookmarklist` 和 `/review/list/mine` 获取划线和想法。
6. 从划线中切句、去重、打分，生成读者画像金句和 20 条画像划线清单。
7. 将接口数据聚合成稳定的 JSON 数据契约。
8. 使用 ECharts 和确定性的中文短语抽取逻辑渲染独立 HTML 报告。

## 设计说明

- 报告采用 `kami` 风格的中文长报告视觉系统：暖纸底、墨蓝强调、编辑式层级和紧凑证据卡片。
- 图表按叙事分区组织：时间节律、阅读偏好、书架资产、笔记与语义。
- 高密度图表会显式占满容器，树图标签优先中文折行，小块隐藏标签并保留 tooltip，避免右侧留白和边缘裁切。
- 顶部读者总结使用统计数据生成，不伪装成用户原文；金句和清单只来自用户自己的划线。
- 词云优先保留领域词，并过滤常见中文短语碎片。
- 书籍阅读时长使用 `readLongest[].readTime`，不从书架更新时间推断。
- 没有真实书名或专辑名的匿名 `readLongest` 记录会被过滤。

## 隐私说明

- 脚本从环境变量读取 `WEREAD_API_KEY`，不会把它写入磁盘。
- 真实生成的报告可能包含个人划线和想法，不要把 `reports/generated/latest` 直接提交到公开仓库。
- 仓库内置的 `examples/ai-founder-report/weread-report.html` 是公开示例报告。
