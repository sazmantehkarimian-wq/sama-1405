# Master Execution Checklist

این جدول وضعیت واقعی خط پاک را ثبت می‌کند. «PASS» فقط با شاهد خودکار موجود به‌کار رفته است.

| Gate | وضعیت | شاهد |
|---|---|---|
| Authority SHA/Data Inventory | PASS | `verify_manifest` + `inspect_package` و `tests/test_authority.py`: شمارش مستقیم workbook، یکتایی و نبود overlap |
| Lossless import / 225 + 350 + 151 | PASS | `tests/test_import_pipeline.py`; شمارش مستقیم workbook و همه cellهای غیرتهی |
| Canonical Field Registry | PASS | ۱۵۳ کلید طبقه‌بندی‌شده: ۱۰۶ mapped، ۳۱ reference-only و ۱۶ unresolved audit-only برای سلول‌های خارج جدول با heading خالی؛ هیچ source cell حذف نمی‌شود |
| Canonical typed domain schema | PASS | migrations و `tests/test_domain.py` |
| Design System / local Vazirmatn | PASS | token enforcement، فونت محلی، `tests/test_design_enforcement.py` |
| Shared UI components | IN PROGRESS | shell/filter/table/dossier و فیلتر چندانتخابی موجود؛ modal/column chooser عمومی باقی است |
| Horizontal Navigation | PASS | `ui/templates/ui/base.html`; enforcement test |
| Dossier and imported history | PASS | dossier همه domainهای واردشده را پیوند می‌دهد؛ UI integration test |
| Contracts / beneficiaries / appraisal / auction | PASS | typed import + dossier + full import gate |
| Decisions / source documents / utility obligations | PASS | typed import از workbook + full import gate |
| Appraisal fee operational process | IN PROGRESS | مبلغ/پرداخت/نامه/پیگیری/سند، تاریخچه و Audit پاس؛ گزارش مستقل fee باقی است |
| Utility consumption operational process | IN PROGRESS | دوره/مصرف/سهم‌ها/پرداخت/سند و override کنترل‌شده پاس؛ گزارش اختصاصی باقی است |
| Commission operational process | IN PROGRESS | تصمیم، شرکت‌کنندگان، سند، اقدام بعدی و transition ممیزی‌شده؛ UI تشکیل جلسه باقی است |
| File movement/current holder | IN PROGRESS | derivation service passes؛ movement form/history permissions باقی است |
| Workflow | PASS | ایجاد فقط با نوع عملیاتی مجاز، transition تراکنشی، تاریخچه و Audit در dossier |
| Documents / alerts / audit | PASS | upload امن server-side، checksum، permission، اقدام/مختومه‌سازی هشدار و Audit |
| Search/filter/saved views | IN PROGRESS | exact/contains/starts, empty, multi-select, ranges, multi-sort و نماهای ذخیره‌شده پاس؛ گروه‌بندی صریح AND/OR باقی است |
| Official PDF/XLSX/DOCX engine | PASS | server-side structures, local Persian PDF font, exact filters/selected columns |
| Report builder / archived snapshot | PASS | تعریف زنده، اجرای مجدد، نسخه ثابت XLSX با query context، تعداد ردیف، SHA-256 و Audit؛ `test_saved_report_and_immutable_snapshot` |
| RBAC/user provisioning | PASS | native create/reset/activate UI، one-time passwords، forced change، staff gate و audit tests |
| Backup/restore | PASS | DB/media manifests، checksum، integrity/FK، global write lock، pre-restore backup، atomic restore و rollback tests |
| Auction candidate rules/lifecycle | IN PROGRESS | rule versioned، مرزهای ۰/۱/۹۰/۹۱، fail-safe، snapshot و schema دوره/lot/proposal؛ UI دوره و Golden Master اسناد باقی است |
| Browser/print QA | IN PROGRESS | Chromium list/dossier/filter smoke + screenshots passed؛ print visual gate remains |
| Five-user application concurrency | IN PROGRESS | five authenticated concurrent search/export/dossier reads pass؛ concurrent writes remain |
| Clean release | NOT STARTED | تا رفع همه gateهای بحرانی عمداً مسدود است |
