# Safety And Scope

Use Kelly as a disciplined sizing framework, not as a certainty engine.

## Hard boundaries

- do not present this as licensed investment, legal, tax, or regulatory advice
- do not support guaranteed-return language
- do not support martingale or "all-in because the edge is obvious" behavior
- do not size leverage when downside is not bounded or modeled

## Practical risk controls

- default to fractional Kelly
- reduce size again when:
  - probability estimates are noisy
  - return estimates are assumption-heavy
  - correlation with existing exposure is unknown
  - liquidity, slippage, or fees are material
  - the capital base includes emergency cash or mission-critical operating cash

## Communication rules

- say clearly when a number is observed, estimated, or assumed
- if the user cannot supply enough structure, switch to a best / base / bear scenario model
- if the edge is weak, explain why a near-zero allocation is the disciplined answer
- if the opportunity is better treated as a low-cost experiment than a scaled bet, say so directly
