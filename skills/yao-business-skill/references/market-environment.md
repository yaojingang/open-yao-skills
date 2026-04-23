# Market Environment

Every analysis must pass through a market-environment layer before recommendations are made. A strong business model in one region can fail in another because channels, trust, payment, delivery, and compliance conditions differ.

## Required Fields

- `company_origin`: `china`, `overseas`, or a named market
- `target_market`: `china`, `overseas`, `global_multi_region`, or named market clusters
- `delivery_direction`: `china_to_china`, `china_to_overseas`, `overseas_to_china`, `overseas_to_overseas`
- `primary_buyer`: consumer, SMB, enterprise, developer, merchant, channel partner, public sector
- `payment_environment`
- `channel_environment`
- `compliance_environment`
- `trust_environment`
- `service_environment`
- `competition_environment`

Do not treat `overseas` as one market when the distinction matters. Split `US`, `EU`, `SEA`, `Middle East`, or other regions when pricing, data rules, or channel behavior change materially.

## Direction Archetypes

### `china_to_china`

Common traits:

- stronger role for local platforms, ecosystems, and relationship-based distribution
- more demand for integrated service, implementation, and local support in many B2B contexts
- payment, invoicing, and procurement behavior often differ from Western self-serve defaults

### `china_to_overseas`

Common traits:

- trust-building, localization, and foreign channel fit become first-order problems
- PLG, self-serve onboarding, app-market distribution, and standard pricing often matter more
- cross-border tax, data, and support design can break an otherwise solid model

### `overseas_to_china`

Common traits:

- global product logic may need local deployment, local partners, or local ecosystem integration
- compliance, procurement, and trust expectations often change the sales motion
- imported pricing and packaging may not map cleanly to the local market

### `overseas_to_overseas`

Common traits:

- standard SaaS, subscription, platform, or advertising logic often applies
- but regional splits still matter for privacy, enterprise buying, local language, and channel density

## Fit Dimensions

Score the current or proposed model on these dimensions:

- `channel_fit`
- `payment_fit`
- `compliance_fit`
- `trust_fit`
- `service_fit`
- `competition_fit`

Recommended aggregate:

`environment_fit_score = 0.22*channel_fit + 0.20*payment_fit + 0.20*compliance_fit + 0.15*trust_fit + 0.13*service_fit + 0.10*competition_fit`

Use the score to explain fit, not as a black box. The narrative matters more than the number.

## How Environment Changes Recommendations

This layer should directly reshape:

- pricing and packaging
- sales motion and distribution
- localization and deployment
- partner or ecosystem strategy
- AI monetization approach
- regulatory and trust requirements

Examples:

- `china_to_overseas` often favors clearer packaging, self-serve trial or PLG motion, global payment support, and stronger documentation.
- `overseas_to_china` often increases the need for partner channels, local deployment options, and stronger localization before enterprise monetization works.

## AI-Specific Questions

For every branch, answer:

- Is AI mainly a cost reducer, a differentiator, or a new billable unit?
- Does AI strengthen the moat or make the product easier for a suite player to absorb?
- Should AI be priced as an add-on, as usage, inside the base plan, or by outcome?

## Report Requirement

Include a `market_environment_fit` module with:

- the direction and target-buyer profile
- the biggest environment constraints
- the main environment advantages
- fit score and explanation
- recommended business-model adjustments for that environment
