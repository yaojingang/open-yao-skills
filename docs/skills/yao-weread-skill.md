# Yao WeRead Skill

## 中文说明

`yao-weread-skill` 用来把微信读书账户数据生成一份完整的个人阅读可视化报告。

它不是简单把阅读时长列出来，而是把近两年的阅读节律、书架资产、内容偏好、笔记密度和划线语义组织成一个可浏览、可复核、可分享的 HTML 报告。报告默认中文排版，适合个人年度复盘、知识管理回顾，也适合作为阅读数据产品的展示样例。

### 适合什么时候用

- 你想复盘自己近两年的微信读书阅读节奏
- 你想知道哪些月份、星期和阶段更容易保持阅读
- 你想看书架里电子书、有声书、书单和私密/公开阅读的结构
- 你想分析读得最久的书、偏好的分类、作者和出版社
- 你想把划线和想法沉淀成词云、时间线和笔记密度图
- 你需要一份可直接打开的 HTML 阅读报告

### 核心亮点

- **26 个图表模块**：覆盖阅读时长、阅读天数、星期节律、累计曲线、分类雷达、分类地图、作者偏好、出版社偏好、书架构成、笔记构成、词云和时间线。
- **近两年默认范围**：默认读取最近 24 个月，也支持 `--start`、`--end` 或 `--years` 自定义。
- **真实书名优先**：读得最久的书来自 `/readdata/detail` 的 `readLongest` 字段；缺少真实标题的匿名记录会被过滤。
- **笔记语义分析**：从划线和想法中抽取高频短语，优先保留阅读、产品、AI、创业、管理等领域词，减少中文 n-gram 碎片。
- **本地 HTML 输出**：生成的报告是独立 HTML 文件，适合本地浏览、截图、归档或继续改造成公开页面。
- **示例画像模式**：不接入真实账号也能生成 AI 创业者版阅读报告，方便快速预览设计、图表和使用体验。
- **隐私边界明确**：真实报告可能包含用户划线和想法，默认只在本地生成，不应直接提交公开仓库。

### 数据逻辑

这个 skill 依赖微信读书 skill 暴露的数据接口，并把它们映射到统一的报告数据契约。

| 数据来源 | 用途 |
|---|---|
| `/readdata/detail` monthly | 月度阅读时长、阅读天数、日级 `readTimes`、读过/读完/笔记统计、每月读得最久的书 |
| `/readdata/detail` annually | 年度阅读偏好、分类、作者、出版社、文字阅读与听书拆分 |
| `/shelf/sync` | 书架条目、电子书、有声/专辑、文章收藏入口、书单、公开/私密状态、最近活动 |
| `/user/notebooks` | 有笔记的书、划线数、想法/点评数、书签数、阅读进度 |
| `/book/bookmarklist` | 用户划线文本、划线时间、划线长度 |
| `/review/list/mine` | 用户想法和点评文本、创建时间 |

聚合逻辑遵循几个关键规则：

- 阅读时长全部按秒聚合，展示时再转为小时和分钟。
- 书架总数为电子书、专辑/有声书和文章收藏入口之和。
- 笔记总数为划线、想法/点评和书签数量之和。
- 月度边界优先使用 `readTimes` 做日级过滤。
- 年度偏好来自自然年接口，因此报告会明确标注年度模块是按触达自然年聚合。
- 词云不导出书籍正文，只使用用户自己的划线和想法文本。

### 使用方法

真实微信读书账号报告：

```bash
cd skills/yao-weread-skill
export WEREAD_API_KEY="<your_api_key>"

python3 scripts/generate_weread_report.py \
  --years 2 \
  --max-note-books 0 \
  --workers 6 \
  --output reports/generated/latest
```

AI 创业者示例报告：

```bash
cd skills/yao-weread-skill

python3 scripts/generate_weread_report.py \
  --years 2 \
  --sample-ai-founder \
  --sample-scale 5 \
  --output reports/generated/ai-founder-sample
```

生成后打开：

```bash
open reports/generated/latest/weread-report.html
```

或查看仓库内置样例：

- [AI 创业者版示例报告](../../skills/yao-weread-skill/examples/ai-founder-report/weread-report.html)

### 输出目录

一次生成通常会得到三个文件：

- `weread-report.html`: 可视化 HTML 报告
- `weread-report-data.json`: 图表数据和聚合结构
- `weread-raw-summary.json`: 覆盖范围、关键 KPI 和图表数量

### 目录入口

- [Skill 入口](../../skills/yao-weread-skill/SKILL.md)
- [目录说明](../../skills/yao-weread-skill/README.md)
- [图表目录](../../skills/yao-weread-skill/references/chart-catalog.md)
- [数据契约](../../skills/yao-weread-skill/references/data-contract.md)
- [报告设计](../../skills/yao-weread-skill/references/report-design.md)
- [生成脚本](../../skills/yao-weread-skill/scripts/generate_weread_report.py)
- [示例报告](../../skills/yao-weread-skill/examples/ai-founder-report/weread-report.html)

### 重要边界

- 不要把真实 `reports/generated/latest` 输出提交到公开仓库。
- 不要把 `WEREAD_API_KEY` 写进脚本、报告、README 或 shell 历史。
- 不要把书籍正文作为报告内容导出。
- 如果某些微信读书字段缺失，报告会保留模块位置并显示空状态，而不是编造数据。

## English Usage

`yao-weread-skill` generates a polished personal reading analytics report from WeRead data.

It collects reading rhythm, shelf structure, category preference, authors, publishers, note density, highlights, thoughts, and phrase-cloud data, then renders a standalone Chinese HTML report with 20+ chart modules.

Use it when you need:

- a local WeRead reading report
- a two-year reading rhythm and preference review
- visual analysis of shelf assets and notes
- a standalone HTML report for personal knowledge review
- a sample AI-founder reading report without connecting a live account

Primary entry points:

- [Skill file](../../skills/yao-weread-skill/SKILL.md)
- [README](../../skills/yao-weread-skill/README.md)
- [Chart catalog](../../skills/yao-weread-skill/references/chart-catalog.md)
- [Data contract](../../skills/yao-weread-skill/references/data-contract.md)
- [Report design](../../skills/yao-weread-skill/references/report-design.md)
- [Sample report](../../skills/yao-weread-skill/examples/ai-founder-report/weread-report.html)

