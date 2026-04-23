---
name: yao-business-skill
description: Design, diagnose, and study business models from ideas, product websites, or company names. Use when asked to create options for a new idea, audit an existing product's monetization and competitors, or analyze a mature company's model and AI-era upgrade paths. Adjust for market, buyer, and operating environment, then output JSON plus HTML.
---

# Yao Business Skill

Evidence-based business model analysis. Separate facts, estimates, hypotheses, and recommendations.

## Use This Skill For

- turning a new idea into `3-5` viable business model options
- diagnosing an existing product, website, or company
- comparing direct competitors and cross-industry analogs
- proposing business model upgrades with formulas, risks, and validation
- studying a mature company to separate reusable from environment-specific patterns

## Do Not Route Here

- generic marketing ideation without business model analysis
- standalone legal, tax, accounting, or valuation advice
- pure financial model builds that do not need business model diagnosis
- gray or illegal monetization design; those belong only in risk recognition and avoidance

## Workflow

1. Choose the branch: `idea_to_model`, `model_diagnosis`, or `company_case_study`.
2. Build a `market_environment` profile before recommending pricing, channels, or sales motion.
3. Gather evidence by tier and mark what is confirmed, estimated, assumed, or unknown.
4. Analyze the current or proposed model, including AI as cost driver and monetization lever.
5. Produce branch-appropriate JSON, HTML, and a short narrative summary.

## Branch Rules

- For new ideas, generate `3-5` options and include one lower-friction, one higher-margin, and one higher-barrier path.
- For existing products, map current monetization, competitors, analogs, upgrade ideas, and environment fit.
- For mature companies, separate environment advantages from reusable patterns so the reader does not copy context-specific advantages blindly.

## Output Contract

- Always distinguish `fact`, `estimate`, `hypothesis`, and `recommendation`.
- Every revenue line or new monetization path needs formula, low/base/high range, and confidence.
- When competitor benchmarking applies, target at least `10` direct competitors and `10` cross-industry analogs; if not possible, explain the gap.
- Include a `market_environment_fit` section and an `AI leverage and AI disruption` section.
- Final artifacts are a concise narrative, a structured JSON payload, and an HTML report.

## Reference Map

- Read `references/source-foundation.md` first for shared objects, evidence tiers, and confidence logic.
- Read `references/scenario-playbooks.md` for the three analysis branches.
- Read `references/market-environment.md` before giving region-sensitive advice.
- Read `references/report-contract.md` before drafting JSON or HTML output.
- Read `references/chart-playbook.md` before building visual analysis modules.
- Use `templates/report.schema.json` as the output schema target.
- Use `templates/report-skeleton.html` as the HTML report base.
- Use `scripts/render_report.py` when turning report JSON into HTML.
- Read `reports/source-synthesis.md` only if you need the distilled design rationale from the user's attachments.
