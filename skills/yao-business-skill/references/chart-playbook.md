# Chart Playbook

Use the report JSON to produce a chart layer that is readable, comparable, and auditable. Prefer charts that can be derived directly from existing structured fields instead of one-off hand-built visuals.

## Minimum Chart Standard

For `model_diagnosis` and `company_case_study`, target at least `10` chart modules whenever the source data is sufficient. Each chart module should include:

- `id`
- `chart_type`
- `title`
- `subtitle`
- `insight`
- structured `data`

Every chart must answer a decision question, not just decorate the page.

## Standard Chart Catalog

1. `environment_radar`
- Input: `market_environment.*_fit`
- Goal: show the six-dimension operating-environment shape

2. `environment_heatmap`
- Input: `market_environment.*_fit`
- Goal: surface weakest operating dimensions quickly

3. `evidence_tier_distribution`
- Input: `evidence_items.source_tier`
- Goal: show whether the report relies on strong or weak evidence

4. `evidence_recency_timeline`
- Input: `evidence_items.source_date`
- Goal: show whether the report is anchored in current evidence

5. `model_confidence_ranking`
- Input: `current_business_models[].confidence`
- Goal: compare certainty across monetization layers

6. `financial_range_comparison`
- Input: `financial_estimates[].range`
- Goal: show low/base/high bands instead of false precision

7. `financial_mix_share`
- Input: `financial_estimates[].range.base`
- Goal: show the relative weight of each disclosed or inferred revenue line

8. `direct_competitor_ranking`
- Input: `direct_competitors[].score`
- Goal: show the most important direct threats

9. `cross_industry_analog_ranking`
- Input: `cross_industry_analogs[].score`
- Goal: show the strongest migration patterns from other categories

10. `benchmark_gap`
- Input: `benchmark.scorecard`
- Goal: show which dimensions are above or below the peer median

11. `upgrade_impact_effort`
- Input: `upgrade_recommendations[].impact`, `effort`, `risk`
- Goal: prioritize what to do first

12. `risk_severity_map`
- Input: `risk_flags[].severity`
- Goal: keep downside visible beside upside

13. `ai_leverage_balance`
- Input: `ai_fit.leverage_points`, `ai_fit.disruption_risks`
- Goal: balance AI upside against AI pressure

## Display Rules

- Use the same color semantics everywhere: strong or positive as dark/green, caution as amber, risk as red.
- Show the chart insight directly under the title instead of burying interpretation in a distant paragraph.
- If precision is weak, use intervals, counts, or ordinal heatmaps instead of fake exact charts.
- If a chart cannot be supported by the available data, skip it and fall back to a simpler chart from the catalog.
