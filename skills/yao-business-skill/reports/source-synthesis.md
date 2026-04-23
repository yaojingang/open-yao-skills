# Source Synthesis

This note records what was extracted from the user's two April 2026 source files:

- `/Users/laoyao/Documents/business_model_research_skill_design_v2.docx`
- `/Users/laoyao/Documents/business_model_skill_taxonomy_v2.xlsx`

## Patterns Carried Into The Skill

- evidence-first business model analysis rather than free-form advice
- multi-label business model classification instead of one-label simplification
- bounded financial estimation with low, base, and high ranges
- direct competitors plus cross-industry analogs
- recommendation logic tied to formulas, effort, risk, and validation actions
- JSON-first reporting with an HTML report rendered from the same structure

## Material Added During This Design Pass

The user added a critical requirement after the initial read:

- business-model advice must account for operating environment and buyer traits
- direction matters: `china_to_china`, `china_to_overseas`, `overseas_to_china`, `overseas_to_overseas`
- recommendations should change when payment, channel, trust, compliance, and service conditions change

That requirement has been promoted into a first-class `market_environment` layer rather than being left as a note.

## Deliberate Packaging Choices

- `SKILL.md` stays compact and routeable
- large taxonomies and scoring details were distilled into `references/` instead of copied inline
- no exhaustive crawler or renderer scripts were added in this first package because the request was still in design phase
- gray and illegal models are preserved only as risk-recognition material

## Next Build Targets

- add a JSON schema file and a validator script
- add competitor-scoring helpers and confidence-score helpers
- add an HTML report template or renderer
- add eval cases for the three main branches and for near-neighbor routing confusion
