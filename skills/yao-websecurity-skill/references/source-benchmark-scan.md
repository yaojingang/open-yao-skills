# Reference Synthesis

## Anchor

The skill turns the user-supplied website security review method report into a reusable defensive audit workflow with a fixed checklist, score table, and Excel/HTML artifact generation.

## External Benchmarks Checked

- OWASP Top 10:2025 confirms the current web risk baseline and the categories used for access control, misconfiguration, supply chain, cryptographic failures, injection, insecure design, authentication, integrity, logging/alerting, and exceptional conditions: <https://owasp.org/Top10/2025/>
- OWASP API Security Top 10 2023 provides the API-specific authorization, resource, SSRF, inventory, and third-party API consumption baseline: <https://owasp.org/API-Security/>
- OWASP ASVS remains the verification-control standard for web application security requirements: <https://owasp.org/www-project-application-security-verification-standard/>
- MITRE CWE Top 25 2025 provides weakness taxonomy and prioritization context: <https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html>
- CISA KEV should be used as a threat-intelligence priority override: <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
- FIRST CVSS v4.0 supports severity scoring when CVE data exists: <https://www.first.org/cvss/v4.0/specification-document>
- OWASP Top 10 for LLM Applications 2025 supports AI/RAG/agent-specific audit surfaces: <https://genai.owasp.org/llm-top-10/>

## User Reference Intake

The source method report contributes:

- `V001-V275` vulnerability ontology
- conservative scan sequencing: inventory, SCA, secrets, SAST, IaC, passive DAST, controlled active validation, business logic, logs, AI/LLM
- evidence schema and report sections
- priority model with KEV/public RCE/auth bypass/secret exposure overrides
- requirement to output both Excel scorecard and HTML report

## Local Fit Constraints

- The package lives in the local agent-skill format with `SKILL.md`, `agents/interface.yaml`, references, scripts, evals, and reports.
- The renderer must not depend on unavailable Python packages, so the XLSX writer uses Python standard library ZIP/XML.
- Reports should avoid exposing absolute local paths; evidence should use repo-relative paths and redacted values.

## Borrow Plan

Borrow the fixed checklist and module sequence from the user report, the category baselines from OWASP/CWE/CISA/FIRST, and the artifact discipline from the meta-skill references. Do not borrow offensive exploit detail, active-scanning defaults, or bulky prose into `SKILL.md`.
