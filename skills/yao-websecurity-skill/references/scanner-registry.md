# Scanner Registry

Scanner use is optional and scope-dependent. Run only tools that are installed, authorized for the target environment, and non-mutating for the audited source tree.

| Domain | Preferred Tools | Use | Safe Default |
| --- | --- | --- | --- |
| Source inventory | `rg`, `git ls-files`, package manager metadata | list files, routes, manifests, generated/vendor areas | read-only |
| SCA/SBOM | OSV-Scanner, Trivy, Dependency-Check, Syft/Grype, package manager audit | dependency and image vulnerabilities | read-only |
| Secrets | Gitleaks, TruffleHog-style scanners, Semgrep secrets | hardcoded keys, private keys, tokens, connection strings | report fingerprints only |
| SAST | Semgrep, CodeQL, Bandit, Brakeman, gosec, ESLint security rules | injection, XSS, SSRF, deserialization, path traversal, dangerous functions | read-only |
| IaC/container | Trivy, Checkov, tfsec, kube-bench, kube-score | Dockerfile, Kubernetes, Terraform, cloud config, RBAC | read-only |
| Passive DAST | OWASP ZAP baseline, crawler, browser inspection, security header checks | headers, cookies, error leaks, CORS, public files | isolated temp runtime or authorized URL only |
| Active DAST | ZAP active scan, Nuclei authorized templates, Burp | controlled validation of injection, known CVEs, path traversal, SSRF signals | isolated temp runtime by default; staging or approved window only |
| API testing | OpenAPI linting, Schemathesis, Postman/Newman, GraphQL schema/depth tools | BOLA, BFLA, object property auth, resource limits, shadow APIs | test accounts/data only |
| Cloud | Prowler, ScoutSuite, cloudsplaining, native security center | IAM, logs, storage, network, KMS, backups | read-only audit role |
| AI/LLM | custom prompt tests, RAG ACL tests, tool-call audit review | prompt injection, data leakage, tool abuse, output safety, cost DoS | synthetic data only |
| Blind/OOB validation | Interactsh-style self-owned endpoint, requestbin-style controlled callback, local DNS/HTTP listener | SSRF reachability, webhook callback, blind injection signal | harmless unique tokens; no secret exfiltration |
| Brute-force resilience | custom capped scripts, ZAP/Burp intruder equivalents, framework auth tests | lockout, throttling, MFA prompts, logging | test accounts, capped attempts, temp runtime by default |
| Destructive/runtime mutation | framework feature tests, API clients, upload probes, migration/reset scripts | file deletion handling, DB writes, resource pressure, upload cleanup | isolated temp runtime only unless separately authorized |

## Fallback Pattern

If a tool is missing:

1. Record the missing scanner in coverage notes.
2. Manually inspect the code/config surfaces that scanner would cover.
3. Mark unresolved runtime-only checks `Unclear` or `Not Checked`.
4. Add the scanner as a follow-up, not a blocker, unless the user required that tool.

## Command Safety

Never run commands that modify the original audited source tree: no code edits, formatting, dependency installation, migrations, generated files, commits, pushes, deletes, moves, or build artifacts inside the original repository. Put reports and temporary files in an external workdir. For dynamic modes, first copy/clone into a fresh temp `target-source`, then install dependencies, build, migrate, and run services only there.

Avoid commands that mutate runtime data, send traffic, brute force, create accounts, delete records, or upload payloads unless the user has explicitly authorized that exact class of test in a safe environment. Prefer offline and passive commands for the first pass. For `dynamic-active`, destructive classes are allowed only inside the isolated temp deployment unless the user has separately authorized a named online target, test data boundary, stop condition, and rollback owner.
