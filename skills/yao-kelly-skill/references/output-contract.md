# Output Contract

Return one Kelly application report that lets the user act immediately. The preferred artifact pair is:

- `JSON`: canonical calculation and audit source
- `HTML`: polished human-readable report, suitable for review, print, and save-as-PDF

## Required sections

0. `背景、矛盾和问题`
   - explain the situation in story form
   - name the user's real confusion
   - state the tension between opportunity and downside
1. `建议动作`
   - one sentence first
   - include `skip / observe-or-tiny-test / small / medium / large`
   - explain the action in plain language before showing formulas
2. `建议投入`
   - conservative Kelly fraction
   - translated amount from the stated capital base
   - total exposure cap and reserve rule
3. `公式路径`
   - binary closed form, scenario log-growth search, or multi-opportunity conservative scaling
4. `关键假设`
   - mark each key number as `observed`, `estimated`, or `assumed`
5. `为什么停止追问`
   - readiness threshold reached, action class stable, or best current action already clear
6. `敏感性与风险`
   - which variable can change the answer most
   - when the recommendation should be cut further or abandoned
7. `轮次日志`
   - append each round in chronological order

## HTML report UI rules

- first viewport must show action class, total recommended exposure, capital base, recommended amount, readiness, and exposure cap
- before the calculation details, include a narrative background section that explains:
  - what is happening
  - what the conflict or tension is
  - what the user is unsure about
  - what solution path the report recommends
- immediately after the first viewport, include a `普通人版结论` section with:
  - what to do now
  - how much to commit
  - why the recommendation is conservative
  - when to recalculate
- repeated opportunities can use cards, but do not put nested cards inside them
- label full Kelly as theory and conservative Kelly as the execution ceiling so non-technical readers do not over-use the raw number
- introduce the Kelly principle in plain language before the detailed method and scenario tables
- keep tables for scenario probabilities and return multiples
- include a sticky top bar with `Print / Save PDF`
- make the page responsive and printable
- avoid treating the HTML report as a marketing landing page; it is an operational decision artifact

## Output style

- action first, math second
- short, concrete, and auditable
- show both `full Kelly` and `conservative Kelly`
- if `capital_base` is missing, still provide fractions but say the amount cannot yet be translated
- if the recommendation is `skip`, explain why a zero or near-zero allocation is the disciplined Kelly result

## Minimum final hand-back template

```markdown
## 建议动作
建议：使用保守版 Kelly，投入比例 `4.6%`，动作级别为 `small`。

## 建议投入
- 资金口径：`100000`
- Full Kelly：`18.3%`
- Conservative Kelly：`4.6%`
- 建议投入金额：`4600`
- 总暴露上限：`25%`
- 现金保留：`50%`

## 公式路径
- 路径：`scenario-log-growth-grid-search`
- 原因：回报结构不是简单二元赔率

## 关键假设
- base scenario probability：`estimated`
- fee drag：`assumed`

## 为什么停止追问
- `decision_readiness = 0.79`
- 剩余未知项已不会改变动作级别

## 敏感性与风险
- 如果 bear scenario 概率从 `25%` 升到 `35%`，建议应下调到 `observe-or-tiny-test`

## 轮次日志
- Round 1: ...
- Round 2: ...
```
