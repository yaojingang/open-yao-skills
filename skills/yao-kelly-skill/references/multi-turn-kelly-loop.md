# Multi-turn Kelly Loop

Use this when the user starts with an incomplete allocation question instead of a clean Kelly brief.

## Goal

Move from vague intent to a documented Kelly decision process:

1. identify the case type
2. produce a provisional first answer
3. ask only the highest-leverage missing questions
4. update the Kelly view after each round
5. stop once readiness is high enough or the action class is already stable
6. return the final report with a round log

## Decision-readiness score

Score the current brief from `0.00` to `1.00`.

Recommended weights:

- `0.12`: objective is explicit
- `0.14`: capital base and reserve rule are explicit
- `0.22`: payoff or return model is explicit
- `0.18`: probability estimate is explicit
- `0.12`: exposure caps or loss constraints are explicit
- `0.10`: confidence in the estimates is explicit
- `0.07`: dependence across opportunities is explicit when needed
- `0.05`: friction, fees, or execution limits are explicit

## Readiness bands

- `0.00 - 0.44`
  - too early for firm sizing
  - give a provisional view and keep asking
- `0.45 - 0.77`
  - enough for a useful provisional range
  - ask only the questions that can still change the action class
- `0.78 - 1.00`
  - ready by default
  - stop asking unless one missing item can plausibly flip the sign of the edge or more than double the recommended size

## Additional stop rules

Stop asking and return a final answer when any of these is true:

- `decision_readiness >= 0.78`
- all remaining unknowns are low impact and do not change the action class
- the current best answer is already clearly `skip`, `observe`, or `run a cheap test first`
- the user has given the maximum detail they can provide and the model is already conservative enough

## Action classes

Use stable action classes so the stop rule is practical:

- `<= 0.00`: `skip`
- `0.00 - 0.02`: `observe-or-tiny-test`
- `0.02 - 0.10`: `small`
- `0.10 - 0.25`: `medium`
- `> 0.25`: `large`

If plausible remaining information cannot move the recommendation into a different class, stop asking.

## Round discipline

After every round record:

- what the user added
- which uncertainty gap it resolved
- current case type
- formula path used this round
- readiness before and after
- current full Kelly view
- current conservative recommendation
- next questions, or why questioning stopped

Ask only `1-3` questions in a round. Do not turn this into a questionnaire.

## Round log template

```json
{
  "round": 2,
  "case_type": "scenario-sizing",
  "user_input_summary": "The user added a capital base, a reserve rule, and base/bear probabilities.",
  "resolved_gap": [
    "capital base is now explicit",
    "scenario probabilities are now explicit"
  ],
  "formula_path": "scenario-log-growth-grid-search",
  "decision_readiness_before": 0.46,
  "decision_readiness_after": 0.79,
  "full_kelly_fraction": 0.183,
  "conservative_fraction": 0.046,
  "action_class": "small",
  "next_questions": [],
  "stop_reason": "readiness threshold reached and remaining unknowns no longer change the action class"
}
```
