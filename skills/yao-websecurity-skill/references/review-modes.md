# Review Modes

All modes start from an isolated copy or clone created outside the original source tree. Use:

```bash
python3 scripts/security_audit_report.py prepare-env \
  --source "<local-path-or-git-url>" \
  --workdir "<fresh-temp-workdir>" \
  --project "<name>" \
  --mode static
```

Then initialize the ledger against the isolated `target-source` path:

```bash
python3 scripts/security_audit_report.py init \
  --project "<name>" \
  --source "<fresh-temp-workdir>/target-source" \
  --mode "<mode>" \
  --intensity "<intensity>" \
  --out "<fresh-temp-workdir>/security_review.json"
```

## Modes

| Mode | Use When | Allowed By Default |
| --- | --- | --- |
| `static` | User wants source/config/dependency review only. | Read isolated copy, run non-mutating SAST/SCA/secrets/IaC scans, generate reports. |
| `dynamic-safe` | User authorizes local runtime checks without destructive behavior. | Install deps, configure temp env, start loopback/container runtime, smoke test, crawl, passive DAST, header/cookie checks, synthetic non-destructive data. |
| `dynamic-active` | User authorizes active validation in the temp deployment. | Blind/OOB callbacks, brute-force resilience with test accounts, upload/path traversal probes, DB writes, file mutation, and resource-pressure checks inside the isolated deployment. |
| `online-authorized` | User supplies an owned live/staging URL and authorization. | Probe only named URL(s), named accounts, rate limits, test data, and approved checks. Destructive tests remain off unless separately authorized. |
| `hybrid` | User wants static plus temp runtime tests and optional live confirmation. | Combine isolated static/dynamic checks first; live confirmation only for scoped items. |

## Authorization Gates

Before any dynamic or online action, record in `runtime`:

- `active_test_authorization`
- `allowed_dynamic_tests`
- `test_accounts`
- `rate_limits`
- `rollback_plan`
- `data_reset_plan`
- `destructive_scope`
- `online_target` and `oob_endpoint` when used

If a gate is missing, downgrade the affected checks to `Unclear` or `Deferred`.

## Hard Boundaries

- Never mutate the original local source tree.
- Never run destructive tests against production by default.
- Never use real credential stuffing lists.
- Never exfiltrate secrets through OOB validation; use harmless unique callback tokens.
- Never hide active testing. Evidence must state what was sent, where, rate limits, and reset status.
