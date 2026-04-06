# Usage Evidence

Estimate frequency conservatively. This skill does not have true runtime telemetry unless the user provides it.

## Evidence Ladder

Prefer evidence in this order:

1. explicit user-provided run logs or dashboards
2. repository history or automation logs when available
3. recent file modification times inside the skill
4. top-level inventory or registry mentions in the scanned root
5. weak heuristics such as size or folder structure

## Labels

- `active`: strong recent evidence, such as modification within 30 days or repeated top-level mentions
- `warm`: some recent evidence, such as modification within 90 days or at least one top-level mention
- `cold`: stale evidence, such as no mentions and modification older than 180 days
- `unknown`: not enough evidence to estimate responsibly

## Confidence

- `high`: multiple strong signals agree
- `medium`: one strong signal or several weak signals
- `low`: only weak proxies are available

## Reporting Rule

Always report the evidence behind the estimate. Good phrasing:

- `warm, confidence medium: modified 42 days ago and mentioned once in top-level inventory files`
- `cold, confidence low: modified 420 days ago and no top-level references found`

Avoid phrasing that implies exact run counts or telemetry unless the user supplied real usage data.
