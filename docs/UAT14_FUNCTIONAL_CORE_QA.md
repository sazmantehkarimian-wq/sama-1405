# UAT.14 — Functional Core Phase 1 QA

Status: **UAT REMEDIATION IN PROGRESS**

## Verified behavior

- The shared Commercial Space picker searches its complete canonical option set, normalizes Persian/Arabic digits for matching only, and ranks exact codes before prefix, substring, and descriptive matches.
- Every Commercial Space dossier section has one compact export control backed by the central report engine; full-dossier browser print remains available and interactive controls are excluded from print.
- Specialist lists reuse the same filtered and sorted queryset for screen pagination and official XLSX/PDF/DOCX output. Appraisal filters preserve the distinction between numeric zero and an unknown amount.
- Region and Center counts identify canonical totals separately from records with confirmed geographic mapping.
- Official outputs contain only the approved organizational identity and omit application branding, account/navigation content, URLs, and developer credit.

## Evidence

- Authority inspection reconciled 225 Mother Properties and 501 Commercial Spaces (350 active and 151 out of cycle), with no overlaps or duplicate source identifiers/codes.
- Imported Authority examples reconcile Commercial Space 347 to one contract and three appraisals, and Commercial Space 497 to one contract and two appraisals.
- Chromium exercised picker queries `37`, `۳۷`, `173`, and `497`, plus all shared picker consumers, at 1366, 1600, and 1920 pixel desktop widths.
- The appraisal-only PDF was visually inspected for Persian shaping, RTL table order, official identity, borders, wrapping, and pagination. XLSX properties and DOCX OOXML were also inspected programmatically.

This evidence is technical QA for an Owner UAT candidate; it is not Production or LAN readiness approval.
