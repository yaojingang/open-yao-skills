# Kelly Sizing Playbook

Use the lightest valid Kelly path for the case at hand.

## 1. Binary opportunity

Use the standard closed form when the opportunity is a simple win or lose bet and the full stake is at risk.

Formula:

`f* = (b * p - q) / b`

Where:

- `f*` is the full Kelly fraction
- `b` is the net profit multiple on a win
- `p` is win probability
- `q = 1 - p`

If the user gives decimal odds `O`, convert with:

`b = O - 1`

Equivalent decimal-odds form:

`f* = (p * O - 1) / (O - 1)`

## 2. Scenario-based opportunity

When payoffs are not naturally binary, use discrete scenarios.

Optimize:

`argmax_f Σ p_i * log(1 + f * r_i)`

Where:

- `p_i` is the probability of scenario `i`
- `r_i` is the net return multiple per `1` unit committed in scenario `i`

Valid `f` must satisfy:

- `1 + f * r_i > 0` for every scenario

If the user only has rough intuition, ask for best / base / bear scenarios before going deeper.

## 3. Multiple opportunities

When the user wants to split one pool across several opportunities:

1. compute standalone Kelly for each opportunity
2. convert full Kelly into fractional Kelly
3. apply a dependence haircut
4. apply single-opportunity caps
5. scale down again if the sum exceeds the total exposure cap

This is intentionally conservative. Do not pretend to have a precise joint Kelly solution when correlation data is weak.

## 4. Fractional Kelly defaults

Default to these conservative multipliers unless the user explicitly wants another rule:

- `high` confidence: `0.50 Kelly`
- `medium` confidence: `0.25 Kelly`
- `low` confidence: `0.10 Kelly`
- `very_low` confidence: `0.00 - 0.05 Kelly`

If the user wants a different multiplier, state it explicitly and keep both the full Kelly and conservative Kelly visible.

## 5. Dependence haircuts

Use these when more than one opportunity is present:

- `independent`: `1.00`
- `low`: `0.85`
- `medium`: `0.65`
- `high`: `0.50`
- `unknown`: `0.50`
- `exclusive`: prefer ranking and staged allocation; if a simultaneous answer is unavoidable, keep the same `0.50` haircut and state the limitation

## 6. Capital preservation rules

Always keep reserve logic visible:

- if the user gives `min_cash_reserve_ratio`, honor it
- if no total exposure cap exists, assume a conservative cap and label it as assumed
- if the full Kelly fraction is very large but the estimate quality is weak, cap the recommendation hard instead of repeating the raw Kelly number as if it were actionable

## 7. No-allocation triggers

Default to `skip`, `observe`, or `cheap test first` when:

- expected edge is non-positive
- the sign of the edge depends on one fragile assumption
- downside is not bounded or not modeled
- fees, slippage, taxes, or liquidity probably erase the edge
- the user is sizing against emergency funds or critical operating cash
