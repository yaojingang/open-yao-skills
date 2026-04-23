# Scenario Playbooks

Use one primary branch per request. Shared evidence and scoring logic still applies across branches.

## `idea_to_model`

Use for a new idea, concept, or rough business direction.

### Inputs

- idea statement
- target buyer and region
- core pain point
- existing assets, constraints, or moat candidates

### Workflow

1. Translate the idea into buyer, job-to-be-done, and economic trigger.
2. Build the market-environment profile.
3. Generate `3-5` business model combinations.
4. Estimate low, base, and high economics for each option.
5. State where AI creates value, cost pressure, or a new chargeable unit.
6. Give the smallest validation action for each option.

### Required Outputs

- one lower-friction option
- one higher-margin option
- one higher-barrier option
- pricing unit, payer, formula, and key assumptions for each option
- `30/60/90 day` validation or test actions

## `model_diagnosis`

Use for an existing product, website, or company that already has some operating signal.

### Inputs

- website, product, or company name
- optional benchmark names supplied by the user

### Workflow

1. Map product lines, pricing, buyer roles, and payment paths.
2. Identify confirmed, latent, and missing monetization layers.
3. Estimate revenue or contribution by line with confidence bands.
4. Generate direct competitors, adjacent threats, and cross-industry analogs.
5. Score fit against the market environment and target buyers.
6. Produce upgrade recommendations with impact, effort, risk, and validation.

### Required Outputs

- current business model map
- direct competitors and cross-industry analogs
- benchmark scorecard
- upgrade recommendations with formulas
- AI leverage and AI disruption section

## `company_case_study`

Use for a mature company the user wants to understand or learn from.

### Inputs

- company, brand, ticker, or website

### Workflow

1. Map the current business model mix and profit pools.
2. Use filings and official disclosures first when available.
3. Explain strengths, weaknesses, dependencies, and environment advantages.
4. Separate transferable patterns from non-transferable local advantages.
5. Explain how AI could reinforce or weaken the model.

### Required Outputs

- multi-line business model breakdown
- profit-pool explanation
- strengths and weakness analysis
- transferable patterns vs environment-dependent advantages
- learning summary for the user's own business

## Shared Fallback Rules

- If public evidence is thin, downgrade to bounded estimates and state the missing data.
- If the request crosses branches, choose the primary branch and treat the rest as secondary modules.
- If the user asks for pure legal or tax advice, stay out of scope and keep only high-level risk framing.
