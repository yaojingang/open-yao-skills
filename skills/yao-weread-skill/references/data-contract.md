<!--
Copyright © 2026 姚金刚. All rights reserved.
Project: yao-weread-skill
Created by: 姚金刚
Date: 2026-05-16
X: https://x.com/yaojingang
-->

# 数据契约

本报告依赖已安装的微信读书 skill 暴露的数据。

## API 数据源

| 数据源 | 接口 | 用途 |
|---|---|---|
| 阅读统计 | `/readdata/detail` | 月度和年度阅读时长、阅读天数、阅读统计、Top 书籍、分类、作者、出版社，以及可用时的阅读/听书拆分 |
| 书架 | `/shelf/sync` | 书籍、有声专辑、文章收藏入口数量，书架分类，近期阅读/更新信号，归档数量，公开/私密状态 |
| 笔记总览 | `/user/notebooks` | 有笔记的书、笔记总量、划线、想法、书签、阅读进度 |
| 划线文本 | `/book/bookmarklist` | 用户划线，用于词云、长度分布、划线时间线、画像金句和 20 条画像划线清单 |
| 想法/书评 | `/review/list/mine` | 用户想法和书评，用于词云和笔记时间线 |

## 必须遵守的语义

- 阅读时长单位为秒，只在展示层转换为小时或分钟。
- 书架总数为 `books.length + albums.length + (mp exists ? 1 : 0)`。
- 笔记总数为 `reviewCount + noteCount + bookmarkCount`。
- 笔记分页使用 `count` 和顶层 `lastSort`；不要使用 `params`、`offset` 或 `limit`。
- `/review/list/mine` 需要小写 `bookid`。
- `readTimes` 是明细数据；完整周期汇总使用 `totalReadTime`，日/月可视化使用 `readTimes`。
- `readerPortrait.quotes` 只允许使用用户划线文本，不允许从书籍正文、想法点评或统计摘要中编造。
- `readerPortrait.goldenQuote` 必须等于画像划线清单第一条。

## 默认范围

默认范围为执行日期当天向前 24 个月，时区为 `Asia/Shanghai`。

实现方式：

1. 查询与目标范围有交集的每个自然月。
2. 当存在每日 `readTimes` 明细时，用它过滤精确开始/结束日期。
3. 如果范围结束在当前自然月内，则将当前自然月作为部分数据使用。
4. 偏好模块查询范围覆盖到的每个自然年的年度数据。

## 回退规则

- 如果偏好字段缺失，图表面板应显示明确空状态。
- 如果某本书的划线/想法文本拉取失败，保留笔记总览数据，并记录拉取错误数量。
- 如果中文分词不可用，使用确定性短语抽取，结合中文停用词、领域词优先和 n-gram 过滤。
- 如果有效划线不足 20 条，画像划线清单按实际数量展示；不要补写虚构句子。
- 如果图表库加载失败，报告仍应展示 KPI 卡片、表格和文字摘要。

## AI 创业者示例模式

`--sample-ai-founder --sample-scale 5` 可在不调用微信读书 API、也不需要 `WEREAD_API_KEY` 的情况下生成 AI 创业者阅读报告示例。

- 示例模式使用内置读者画像数据，覆盖所有报告模块。
- 示例输出必须设置 `meta.sampleReport=true`。
- 真实账号模式必须继续只使用微信读书 skill 返回的数据。
