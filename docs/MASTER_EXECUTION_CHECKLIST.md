# Master Execution Checklist

این جدول وضعیت واقعی خط پاک را ثبت می‌کند. «PASS» فقط با شاهد خودکار موجود به‌کار رفته است.

| Gate | وضعیت | شاهد |
|---|---|---|
| Authority SHA/Data Inventory | PASS | `verify_manifest` + `inspect_package` و `tests/test_authority.py`: شمارش مستقیم workbook، یکتایی و نبود overlap |
| Lossless import / 225 + 350 + 151 | PASS | `tests/test_import_pipeline.py`; شمارش مستقیم workbook و همه cellهای غیرتهی |
| Canonical Field Registry | IN PROGRESS | پنج وضعیت و metadata ذخیره می‌شود؛ بازبینی معنایی aliasهای reference ادامه دارد |
| Canonical typed domain schema | PASS | migrations و `tests/test_domain.py` |
| Design System / local Vazirmatn | PASS | token enforcement، فونت محلی، `tests/test_design_enforcement.py` |
| Shared UI components | IN PROGRESS | shell/filter/table/dossier موجود؛ modal/multiselect/column chooser باقی است |
| Horizontal Navigation | PASS | `ui/templates/ui/base.html`; enforcement test |
| Dossier and imported history | PASS | dossier همه domainهای واردشده را پیوند می‌دهد؛ UI integration test |
| Contracts / beneficiaries / appraisal / auction | PASS | typed import + dossier + full import gate |
| Decisions / source documents / utility obligations | PASS | typed import از workbook + full import gate |
| Appraisal fee operational process | IN PROGRESS | typed schema/list/dossier؛ create/payment/follow-up UI باقی است |
| Utility consumption operational process | IN PROGRESS | typed billing/share schema/list؛ create/override UI باقی است |
| Commission operational process | IN PROGRESS | typed schema/list/dossier؛ session lifecycle باقی است |
| File movement/current holder | IN PROGRESS | derivation service passes؛ movement form/history permissions باقی است |
| Workflow | IN PROGRESS | typed instance/list/dossier؛ transition service/UI باقی است |
| Documents / alerts / audit | IN PROGRESS | typed schema/list؛ secure upload/action hooks کامل نیست |
| Search/filter/saved views | IN PROGRESS | shared space query؛ advanced operators/multiselect/save UI باقی است |
| Official PDF/XLSX/DOCX engine | PASS | server-side structures, local Persian PDF font, exact filters/selected columns |
| Report builder / archived snapshot | IN PROGRESS | builder preview/export exists؛ save/snapshot actions باقی است |
| RBAC/user provisioning | PASS | native create/reset/activate UI، one-time passwords، forced change، staff gate و audit tests |
| Backup/restore | PASS | DB/media manifests، checksum، integrity/FK، global write lock، pre-restore backup، atomic restore و rollback tests |
| Browser/print QA | IN PROGRESS | Chromium list/dossier smoke + screenshots passed؛ print visual gate remains |
| Five-user application concurrency | IN PROGRESS | five authenticated concurrent search/export/dossier reads pass؛ concurrent writes remain |
| Clean release | NOT STARTED | تا رفع همه gateهای بحرانی عمداً مسدود است |
