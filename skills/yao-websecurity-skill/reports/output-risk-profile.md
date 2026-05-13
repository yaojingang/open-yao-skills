# Output Risk Profile

## Likely Failure Modes

- Marking checklist items `Safe` without evidence because a scanner produced no finding.
- Spending review budget on irrelevant vulnerability classes instead of first proving applicability.
- Running blind or active tests against risks that were not shown relevant by code or inventory.
- Overstating active-test coverage when only offline code review was authorized.
- Leaving `Not Checked` items hidden in the full table instead of surfacing coverage gaps.
- Including plaintext secrets, cookies, tokens, personal data, or customer records in evidence.
- Treating CVSS as the whole priority model and missing business-logic or tenant-isolation impact.
- Producing a polished HTML report with vague findings, missing file references, or no owner/SLA fields.

## Controls

- Require one status for every `V001-V275` item.
- Require applicability triage before deep scanning; mark absent surfaces `Not Applicable` with evidence-backed rationale.
- Require authorization, test accounts/data, rate limits, and rollback notes before `blind-safe-test` or `active-controlled` verification.
- Keep `Unclear` distinct from `Safe`.
- Calculate coverage separately from reviewed safety score.
- Redact absolute local paths in HTML metadata and require repo-relative evidence.
- Run all rendered HTML, XLSX, and sanitized JSON values through the same report sanitizer.
- Make P0/P1, unclear, and not-checked items visible before the full score table.
- Require remediation, owner, due date, and retest fields for operational follow-through.

## Reviewer Questions

- Does the report clearly say what was authorized and what was not?
- Are all high-risk conclusions backed by code, config, scanner, HTTP, or log evidence?
- Are secrets and personal data masked?
- Can engineering teams turn findings into tickets without re-reading the whole report?
