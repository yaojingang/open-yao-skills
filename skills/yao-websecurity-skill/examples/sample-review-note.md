# Sample Review Note

Run:

```bash
python3 scripts/security_audit_report.py init \
  --project "example-saas" \
  --source "/path/to/example-saas" \
  --out "/tmp/example-security-review.json"

python3 scripts/security_audit_report.py render \
  --review "/tmp/example-security-review.json" \
  --out-dir "/tmp/example-security-audit-report"
```

Then fill the JSON statuses and evidence before rendering the final report. The renderer writes `security_review.sanitized.json`, `安全审查评分表.xlsx`, and `安全审查报告.html`.
