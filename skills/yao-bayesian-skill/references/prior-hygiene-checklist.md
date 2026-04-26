# Prior Hygiene Checklist

Use this checklist as a judgment-audit layer before finalizing a Bayesian decision report. These items are not numeric priors by themselves; they are default assumptions that help prevent bad priors, weak evidence, overconfident conclusions, and unsafe action recommendations.

## How To Use

1. Run this checklist after the decision brief, prior, evidence, and actions are known.
2. Treat the principles as updateable defaults, not doctrine.
3. Show only the 3-5 principles most relevant to the current decision in the final report.
4. Prefer concrete decision effects: how the principle changes the prior, discounts evidence, raises an action threshold, or changes the next information step.
5. Do not use the checklist to block action by default. Use it to choose safer action intensity under uncertainty.

## Core Five

These five checks should be considered for every report:

- I may be wrong: state uncertainty and what would change the judgment.
- Base rates first: start from the reference class before the individual story.
- Evidence has grades: independent, repeatable, verifiable evidence updates more.
- Strong claims need strong evidence: raise the evidence threshold for surprising or high-impact conclusions.
- Avoid ruin risk: do not let expected value hide irreversible downside.

## Full Checklist

| ID | Principle | Core sentence | Decision effect |
|---|---|---|---|
| fallibility | 我可能错 | 任何判断先给自己留一条退路。 | Mark uncertainty, alternative explanations, and update triggers. |
| base_rate | 基础率优先 | 先看一般规律，再看个别故事。 | Require a reference class before using vivid individual evidence. |
| evidence_grade | 证据有等级 | 独立、重复、可验证的证据更强。 | Grade evidence and scale the likelihood-ratio update by quality. |
| strong_evidence | 强结论需要强证据 | 越惊人的说法，证据门槛越高。 | Raise thresholds for large commitments or strong recommendations. |
| small_sample | 小样本很吵 | 一两个案例不能代表整体。 | Treat small samples as directional only and ask for more observations. |
| incentives | 动机和激励很重要 | 人常常被利益、环境、压力推动。 | Check who benefits if the user believes the claim. |
| ruin_risk | 避免毁灭性风险 | 先避免输光，再追求赢很多。 | Prefer conservative or staged action when downside is irreversible. |
| absence_evidence | 缺证据有时也是证据 | 该出现的证据没出现，值得下调信念。 | Lower confidence when expected evidence is absent. |
| causality | 相关不等于因果 | 两件事一起发生，不代表一件导致另一件。 | Separate correlation, mechanism, timing, and intervention evidence. |
| mean_reversion | 极端会回归 | 特别好或特别坏之后，常会向平均水平靠近。 | Avoid over-updating from one extreme outcome. |
| simplicity | 简单解释优先 | 证据相当时，先考虑较少假设的解释。 | Prefer simpler explanations until complex ones predict more. |
| reversibility | 保留可逆选项 | 不确定时，优先选择还能调整的路。 | Recommend pilots, staged commitments, or reversible tests. |
| local_rationality | 人有局部理性 | 多数行为背后都有某种处境逻辑。 | Interpret behavior through incentives, constraints, and context. |
| confidence_layers | 置信度要分层 | 别只说信或不信，要说有多大把握。 | Express belief as probability, interval, and confidence tier. |
| disconfirming | 反面证据最珍贵 | 能改变你看法的证据，最值得看。 | Name what evidence would reverse the recommendation. |
| recency_emotion | 近因和情绪会放大判断 | 刚发生、很吓人、很生动的事会被高估。 | Discount vivid anecdotes unless long-run rates confirm them. |
| second_order | 系统会产生副作用 | 一个改变常常带来二阶后果。 | Check downstream incentives, side effects, and delayed costs. |
| individual_difference | 个体差异真实存在 | 平均规律有用，个人情况也要看。 | Start with base rates, then adjust for the user's specific context. |
| graded_trust | 信任要分级 | 可以善意起步，同时逐步验证。 | Increase trust through staged exposure and repeated reliability. |
| stale_prior | 先验会过期 | 世界变了，旧经验要重新校准。 | Re-check whether older reference-class data still applies. |

## Report Language

Use plain language in the final report:

```text
本次触发的贝叶斯先验原则：

1. 基础率优先：先看类似项目的常见成功率，再看当前个案。
2. 小样本很吵：当前用户访谈样本偏少，不能直接代表市场。
3. 保留可逆选项：证据还不稳定，优先选择低成本试点。
4. 强结论需要强证据：当前证据不足以支持直接重投入。
```

The checklist should make the report easier to trust and easier to act on. It should not become a long philosophical appendix unless the user explicitly asks for the full list.
