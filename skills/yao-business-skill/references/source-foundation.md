# Source Foundation

This package is derived from the user's April 2026 business model design materials. The package uses those materials as seed references, not as a giant inline knowledge dump.

## Core Inputs

- `website_url`: a company or product site
- `brand_or_company`: a company, brand, or ticker
- `product_name`: a product or offering to diagnose
- `new_idea`: a startup or monetization idea

If the prompt is under-specified, ask only for missing fields that materially change the model:

- target buyer
- target market or region
- existing assets or constraints
- whether the goal is design, diagnosis, or study

## Shared Objects

- `EvidenceItem`: `source_url`, `source_tier`, `source_date`, `quote`, `extracted_fields`
- `BusinessModelLine`: `model_label`, `payer`, `pricing_unit`, `revenue_basis`, `status`, `confidence`
- `Competitor`: `type`, `name`, `url`, `category`, `model_tags`, `scores`, `evidence_ids`
- `FinancialEstimate`: `formula`, `variables`, `low`, `base`, `high`, `gross_margin`, `confidence`
- `Recommendation`: `title`, `mechanism`, `impact`, `effort`, `risk`, `validation`, `formula`
- `MarketEnvironment`: `company_origin`, `target_market`, `delivery_direction`, buyer and operating-environment fields

## Evidence Tiers

- `S`: audited filings, exchange disclosures, formal segment reporting, accounting standards
- `A`: company site, IR, pricing, product docs, terms, official blogs
- `B`: software directories, app stores, plugin markets, GitHub, technology-stack tools
- `C`: SEO signals, ad libraries, hiring signals, social and community evidence
- `D`: comparable-company inference, interviews, bounded analyst assumptions

Use `S` and `A` sources for summary claims whenever possible. `C` and `D` can support estimates, not hard facts.

## Required Analysis Sequence

1. Resolve the entity and the exact analysis target.
2. Build the market-environment profile.
3. Collect evidence and product or monetization signals.
4. Classify the business model with multiple labels when needed.
5. Map revenue lines to disclosed figures or bounded formulas.
6. Generate direct competitors and cross-industry analogs.
7. Produce recommendations or idea options with environment fit.
8. Run risk and quality gates before final output.

## Core Pattern Families

Use combinations rather than forcing a single label. Common families include:

- one-time sale
- subscription
- usage-based or AI credits
- marketplace commission
- ads or retail media
- license or ecosystem take rate
- services or managed delivery
- hardware plus attach services
- data products
- financial or payment add-ons
- outcome-based pricing

## Confidence Model

Use the weighted confidence formula from the source materials:

`confidence = 0.28*source_quality + 0.22*direct_observability + 0.18*triangulation + 0.12*benchmark_fit + 0.10*recency + 0.10*accounting_clarity - risk_penalty`

Recommended interpretation:

- `85-100`: high confidence; can enter the summary directly
- `70-84`: fairly strong; include assumptions inline
- `50-69`: moderate; keep it as bounded estimate
- `30-49`: weak; move to appendix or hypothesis
- `<30`: too weak; do not present as a conclusion

## Guardrails

- Never turn GMV, TPV, ARR, AUM, or user counts into recognized revenue without a clear basis.
- Never fabricate private-company numbers as facts.
- Gray or illegal models can appear only inside the risk section, never as recommendations.
- Separate current-state analysis from future AI-era speculation.
