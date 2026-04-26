# Intake Contract

Turn a natural-language request into one structured Kelly brief before sizing.

## 1. First classify the request

- `binary-bet`
  - one opportunity
  - clear win or lose structure
  - user can provide a win probability and odds, or information that can be translated into those
- `scenario-sizing`
  - one opportunity
  - outcome is better described with `2-5` scenarios instead of simple win or lose
  - each scenario needs a probability and the net return on each `1` unit committed
- `multi-opportunity-allocation`
  - several opportunities compete for one capital or resource pool
  - each opportunity still needs its own scenario or odds model
  - dependence between opportunities must be stated or explicitly marked as unknown

## 2. Minimum brief fields

Every brief should contain:

- `objective`
  - examples: long-term growth, capped drawdown, exploratory test, fixed budget allocation
- `capital_base`
  - the money or resource pool that this recommendation is allowed to touch
- `constraints`
  - reserve cash, total exposure cap, single-opportunity cap, max loss tolerance, minimum ticket size, or lockup limits
- `opportunities`
  - one or more candidate opportunities
- `confidence_level`
  - `high`, `medium`, `low`, or `very_low`

## 3. Required fields by case type

### `binary-bet`

Required:

- `win_probability`
- `odds`
  - `net`: profit multiple on a win
  - `decimal`: total payout multiple including stake
- optional `loss_fraction`
  - defaults to `1.0` when the full stake is at risk

### `scenario-sizing`

Required:

- `scenario_returns`
  - each scenario must include:
    - `name`
    - `probability`
    - `return_multiple`
- `return_multiple` is the net change per `1` unit committed
  - `0.50` means gain `0.50`
  - `-0.30` means lose `0.30`
  - `-1.00` means lose the full committed unit

### `multi-opportunity-allocation`

Required:

- every opportunity must be a valid `binary-bet` or `scenario-sizing` opportunity
- `dependence`
  - recommended values: `independent`, `low`, `medium`, `high`, `unknown`, `exclusive`
- `total_exposure_cap`
  - if the user does not provide one, use a conservative default and label it as assumed

## 4. High-leverage follow-up questions

Ask only the questions that can change the sizing result:

- objective is unclear:
  - `这次你更想要长期增长、控制回撤，还是固定预算内的最优试探？`
- capital base is missing:
  - `这次真正允许参与的资金或资源总盘子是多少？有没有必须保留、完全不能动的部分？`
- scenario model is missing:
  - `如果不是标准赔率，请给我最好 / 基准 / 最差几种结果、各自概率，以及每投入 1 单位后的净收益或净亏损。`
- probabilities are missing:
  - `你认可的胜率或各场景概率是多少？如果不确定，可以给 best / base / bear 三档。`
- constraints are missing:
  - `单次上限、总暴露上限、最大可接受亏损、最少保留现金分别是多少？`
- multiple opportunities but dependence is missing:
  - `这些机会是独立、相关、互斥，还是你现在也不确定？`

## 5. Canonical Kelly brief

```json
{
  "case_type": "multi-opportunity-allocation",
  "objective": "long-term growth with capped drawdown",
  "capital_base": 100000,
  "constraints": {
    "total_exposure_cap": 0.25,
    "min_cash_reserve_ratio": 0.50,
    "fractional_kelly_mode": "auto"
  },
  "opportunities": [
    {
      "name": "Opportunity A",
      "win_probability": 0.57,
      "odds": {"format": "decimal", "value": 2.0},
      "confidence_level": "medium",
      "max_fraction_cap": 0.15,
      "dependence": "independent"
    },
    {
      "name": "Opportunity B",
      "scenario_returns": [
        {"name": "best", "probability": 0.25, "return_multiple": 1.40},
        {"name": "base", "probability": 0.50, "return_multiple": 0.30},
        {"name": "bear", "probability": 0.25, "return_multiple": -0.50}
      ],
      "confidence_level": "low",
      "max_fraction_cap": 0.12,
      "dependence": "unknown"
    }
  ]
}
```
