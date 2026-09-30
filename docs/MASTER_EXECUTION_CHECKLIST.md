# Master Execution Checklist

| Gate | وضعیت | شاهد |
|---|---|---|
| Authority/Data Inventory | PASS | `tests/test_import.py` و گزارش import |
| Canonical Field Registry | PASS | `CanonicalField`, `RawCell` و tests |
| Canonical Domain Schema | PASS | migrations و model tests |
| Design System | PASS | token/component drift tests |
| Shared UI Components | PASS | templates و UI tests |
| Horizontal Navigation | PASS | design enforcement/browser tests |
| 501 Space / 225 Property baseline | PASS | import acceptance tests |
| Dossier and history | PASS | dossier integration tests |
| Contracts / beneficiaries / appraisal / auction | PASS | typed import and dossier tests |
| Appraisal fee / utilities / commission | IN PROGRESS | typed schema complete; operational UI/process tests pending |
| File movement/current holder | IN PROGRESS | derivation service passes; movement UI pending |
| Documents / alerts / audit | IN PROGRESS | typed schema complete; operational hooks pending |
| Search/filter/saved views | IN PROGRESS | shared space query complete; saved-view UI pending |
| Official PDF/XLSX/DOCX reports | IN PROGRESS | structures pass; Persian PDF/print QA pending |
| RBAC/user provisioning | IN PROGRESS | secure provisioning works; management workflows pending |
| Backup/restore | IN PROGRESS | scripts complete; controlled-write round-trip pending |
| Browser/print QA | IN PROGRESS | CI browser gate |
| Five-user concurrency | IN PROGRESS | application concurrency gate |
| Clean release | NOT STARTED | blocked until all critical gates PASS |
