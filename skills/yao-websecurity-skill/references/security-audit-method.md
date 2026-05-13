# Security Audit Method

This skill is for defensive review of owned or explicitly authorized website systems. It combines full-codebase inventory, attack-surface triage, targeted deep reading, scanner-assisted evidence, controlled verification, and a fixed vulnerability ontology.

## Scope Gate

Before scanning, record:

- target: local path, archive, or GitHub URL
- authorization: owner, purpose, allowed environment, test window
- forbidden actions: active DAST, brute force, destructive uploads, concurrency, state-changing business tests, third-party callbacks
- test accounts: roles, tenants, permissions, data boundaries
- expected outputs: Excel scorecard, HTML report, review JSON

If authorization or scope is unclear, only perform offline repository review and mark runtime-only checks `Not Checked` or `Unclear`.

## Non-Destructive Code Boundary

The target source tree is read-only. Do not edit, format, patch, delete, move, rename, generate files inside, install dependencies into, run migrations against, commit to, or push from the audited repository. All generated artifacts must go to an external workdir. The report helper refuses to write review JSON, sanitized JSON, XLSX, or HTML outputs inside the local target source directory.

Allowed local actions are source reads, inventory, static parsing, passive scanner reads, and writing external reports. Runtime testing must use authorized deployed targets or isolated/staging services and must not mutate production data or source files.

## Codebase Coverage Protocol

1. Record source identity: path or URL, branch, commit SHA, and review timestamp.
2. Build an inventory with `rg --files`, package manifests, lockfiles, route/API files, auth/session modules, data models, migrations, storage code, file upload code, external request clients, webhooks, background jobs, AI/LLM tool calls, Docker/IaC, CI/CD, and environment examples.
3. Classify generated, vendor, binary, large artifact, and excluded files. Do not silently ignore them; add a coverage note.
4. Deep-read all security boundaries: authentication, authorization, tenant filters, request validation, output encoding, SQL/NoSQL access, command execution, template rendering, file handling, SSRF surfaces, secrets/config, logging, payment/order/export workflows, and AI tool permissions.
5. Map findings and safe evidence to `V001-V275`. If a check requires runtime behavior and no safe runtime data exists, mark `Unclear` or `Not Checked`.

## Applicability Triage

Do not deeply test all `V001-V275` items. Use the ontology as a baseline, then classify each item before spending review tokens:

| Applicability | Meaning | Expected Action |
| --- | --- | --- |
| `Applicable` | The codebase contains the relevant surface, technology, data flow, endpoint, dependency, or deployment pattern. | Deep-read code/config and run safe scanner or manual checks. |
| `Possibly Applicable` | The surface likely exists but evidence is incomplete, generated, external, or runtime-dependent. | Inspect high-value files first; mark `Unclear` if runtime/account data is missing. |
| `Not Applicable` | The surface is absent, e.g. no GraphQL, no OAuth, no file upload, no Kubernetes, no LLM/RAG. | Mark `Not Applicable` with a short evidence-backed reason; do not spend tokens on deep testing. |
| `Deferred` | Relevant but needs authorization, test accounts, deployed URL, or safe data. | Mark `Not Checked` or `Unclear` and add active-test prerequisites. |

Triage inputs should include languages/frameworks, route/API inventory, auth model, tenant model, persistence/storage, external request clients, file/media handling, payment/order/workflow code, messaging/webhooks, cloud/container/IaC, CI/CD, observability, and AI/LLM/RAG/tool surfaces.

## Relevance-Driven Scan Plan

Group applicable checks by domain and priority before reviewing:

1. Always inspect universal high-value surfaces: auth/session, authorization/tenant isolation, secrets/config, dependency manifests, input/output handling, data access, logging, and deployment config.
2. Add domain-specific groups only when the code indicates the surface exists: GraphQL, OAuth/OIDC/SAML, WebSocket, file upload, payment/refund, object storage, Kubernetes, Terraform, Redis/Mongo/Elastic, SSRF-prone URL fetchers, template rendering, command execution, AI/RAG/agent tools.
3. For absent surfaces, bulk-mark related checks `Not Applicable` with one shared rationale, e.g. `No GraphQL schema/resolver/dependency found in inventory`.
4. For ambiguous surfaces, sample the most likely files first; do not exhaustively read unrelated modules just to close every checklist row.
5. Preserve the full checklist in the final scorecard so reviewers can see both what was checked and what was ruled out.

## Verification Modes

Use the lightest verification that can support the conclusion:

| Mode | When To Use | Constraints |
| --- | --- | --- |
| `code-review` | Offline code/config reasoning is enough. | Prefer repo-relative file/line evidence. |
| `scanner-passive` | SCA, secrets, SAST, IaC, dependency, and passive URL checks. | Read-only; record tool/version when available. |
| `manual-reasoning` | Scanner is unavailable or misses framework-specific logic. | Explain control path and uncertainty. |
| `blind-safe-test` | Behavior can only be confirmed by black-box/blind request testing. | Requires explicit authorization, test accounts/data, low rate, non-destructive payloads, and rollback. |
| `active-controlled` | Injection, BOLA/BFLA, state flow, or abuse checks need active validation. | Prefer staging; never run against production without approved window and limits. |

Blind tests should validate controls, not weaponize exploitation. Store only redacted HTTP summaries, request IDs, hashes, and behavioral observations.

## Execution Order

1. `M00` Scope and authorization protection.
2. `M01` Asset, technology stack, and route/API inventory.
3. `M02` Data classification and threat model.
4. `M04` SCA/SBOM and dependency review.
5. `M05` Secrets review with fingerprints only.
6. `M06` SAST/manual code review.
7. `M07` Config, container, IaC, cloud, TLS, CORS, headers, CI/CD.
8. `M08` Authentication, authorization, session, OAuth/OIDC/SAML.
9. `M09` API security: BOLA, BFLA, object property authorization, resource limits, shadow APIs.
10. `M10` Passive DAST baseline when a deployed URL is authorized.
11. `M11` Active validation only in an approved environment and time window.
12. `M12` Business logic and abuse flows.
13. `M13` Logging, monitoring, auditability, incident visibility.
14. `M14` AI/LLM, RAG, agent/tool, prompt, and output safety.
15. `M15` Report, remediation, owner/SLA, and retest plan.

## Risk Priority Rules

Use override rules before numeric scoring:

- `P0`: public RCE, auth bypass, tenant isolation failure, sensitive data bulk exposure, payment/refund loss, production secret usable for privileged access, CISA KEV hit on reachable asset.
- `P1`: high-confidence privilege issue, SSRF to cloud metadata/internal services, serious dependency or config exposure with plausible reachability, sensitive logging leak, overly broad cloud/IAM permission.
- `P2`: medium impact, complex prerequisites, limited information disclosure, incomplete rate limits, monitoring gaps.
- `P3`: hardening, low-impact disclosure, long-term governance.

When CVSS or EPSS exists, use it as supporting evidence, not as the sole business priority. Business logic and AI-agent issues need impact, automation potential, recoverability, and affected user count.

## Evidence Rules

Keep evidence useful but non-sensitive:

- Use repo-relative file paths and line numbers for code evidence.
- Hash or mask secrets, tokens, cookies, credentials, API keys, customer identifiers, and personal data.
- Store HTTP evidence as method, route, status, request ID, redacted parameter names, and short behavioral summary.
- For active tests, include test account, environment, timestamp, rate limit, non-destructive proof, and rollback note.
- For uncertainty, explain what was missing and what would resolve it.

## Tool Fallback

Prefer structured scanner outputs when tools are present, but never block the review because a scanner is unavailable. If a tool is missing, record `manual-review` and inspect the matching code/config surfaces directly.

## Security Boundary

This skill must not provide exploit weaponization, stealth, persistence, credential theft, malware, third-party scanning, bypass instructions outside authorized scope, destructive testing steps, or source-code modifications to the audited project. It may describe defensive verification at a high level and should recommend safe reproduction only in controlled environments.
