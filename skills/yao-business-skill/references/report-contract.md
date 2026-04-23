# Report Contract

The final output should be decision-friendly for readers and auditable for operators. Use a structured JSON payload as the source of truth and render the HTML report from that payload.

## Required Deliverables

- concise narrative summary
- structured JSON payload
- HTML report

## JSON Core

Every branch should include:

- `analysis_mode`
- `entity`
- `market_environment`
- `chart_modules`
- `evidence_items`
- `risk_flags`
- `unknowns`
- `next_validation`
- `ai_fit`

### Branch-Specific Keys

For `idea_to_model`:

- `idea_options`
- `scenario_forecast`
- `validation_plan`

For `model_diagnosis`:

- `current_business_models`
- `financial_estimates`
- `direct_competitors`
- `cross_industry_analogs`
- `benchmark`
- `upgrade_recommendations`

For `company_case_study`:

- `current_business_models`
- `profit_pools`
- `strengths`
- `weaknesses`
- `transferable_patterns`
- `environment_dependencies`

## HTML Module Order

1. `meta`
2. `executive_summary`
3. `market_environment_fit`
4. `evidence_map`
5. `current_model` or `idea_options`
6. `financial_estimate` or `scenario_forecast`
7. `direct_competitors`
8. `cross_industry_analogs`
9. `benchmark`
10. `ai_fit`
11. `upgrade` or `learning_takeaways`
12. `risk`
13. `appendix`

## Recommended Chart Set

Use at least `10` chart or visual modules when data allows. Preferred components:

- revenue mix stacked bar
- scenario forecast
- margin waterfall
- competitor score bar
- pricing matrix
- business-model heatmap
- impact-effort matrix
- evidence coverage matrix
- market-environment radar
- environment-fit heatmap
- risk heatmap
- sensitivity tornado
- evidence recency timeline
- upgrade impact-effort matrix
- AI leverage vs disruption balance

`model_diagnosis` should normally render `10-12` chart modules. `company_case_study` should target the same bar when the source data is sufficient.

If data is thin, downgrade cleanly to tables, interval charts, or evidence-gap visuals rather than faking precision.

## Evidence and Display Rules

- Make `facts`, `estimates`, `hypotheses`, and `recommendations` visually distinct.
- Show source tier and source date for major conclusions.
- Every estimate must include formula, variables, range, and confidence.
- Keep gray or illegal models inside the risk section only.

## Quality Gates

- direct competitors `>=10` when diagnosis or case-study benchmarking applies
- cross-industry analogs `>=10` when strategy transfer is part of the ask
- chart modules `>=10` for diagnosis or case study when the report has enough structured data
- every revenue line has a formula
- every estimate has a confidence score
- the report distinguishes revenue from GMV, TPV, ARR, AUM, or other bases
- the report contains a dedicated market-environment section
- the report contains a dedicated AI section
- the summary excludes unsupported low-confidence claims
