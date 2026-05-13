# Artifact Design Profile

## Artifact Family

High-trust security report plus operational scorecard.

## Reading Model

Decision makers need risk posture, P0/P1 exposure, and coverage gaps first. Engineers need a sortable row-level table with evidence, file/endpoint references, remediation, owner, SLA, and retest state.

The report must also make the applicability model visible: what attack surfaces exist, which risk domains were selected for deep scanning, and which checklist domains were ruled out to control review cost.

## Visual Direction

- Kami-inspired editorial HTML: parchment background, ivory report surface, ink-blue section hierarchy, warm gray rules, serif-led titles, and tight document spacing.
- Compact metrics in the first screen: overall risk, score, coverage, risk count, unclear count, and not-checked count.
- Evidence-first tables with horizontally scrollable dense layout.
- Priority, status, and severity badges using solid hex fills only.
- Excel workbook styled as an operational triage artifact: frozen headers, fixed column widths, hidden gridlines, wrapped evidence, warm header fill, and conditional styles for status/priority/severity.
- No decorative hero, marketing layout, unsupported screenshots, hard drop shadows, or cold blue-gray palette.

## Non-Negotiables

- HTML, XLSX, and sanitized JSON must not reveal absolute local filesystem paths or reusable secrets.
- Tables must keep priority, status, evidence, remediation, owner, and due date visible.
- `Unclear` and `Not Checked` are first-class report outcomes, not hidden notes.
- `Not Applicable` rows need a visible applicability reason so token-saving triage stays auditable.
- Excel must include the complete checklist baseline so reviewers can audit what was considered.
- Excel and HTML must keep the same status vocabulary and risk ordering so the two outputs are interchangeable for triage.
- No plaintext secrets, cookies, tokens, reusable credentials, or personal data dumps.
