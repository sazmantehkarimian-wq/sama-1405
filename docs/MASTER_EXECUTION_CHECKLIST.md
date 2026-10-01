# Master Execution Checklist

این جدول وضعیت واقعی خط پاک را ثبت می‌کند. «PASS» فقط با شاهد خودکار موجود به‌کار رفته است.

| Gate | وضعیت | شاهد |
|---|---|---|
| Authority SHA/Data Inventory | PASS | `verify_manifest` + `inspect_package` و `tests/test_authority.py`: شمارش مستقیم workbook، یکتایی و نبود overlap |
| Lossless import / 225 + 350 + 151 | PASS | `tests/test_import_pipeline.py`; شمارش مستقیم workbook و همه cellهای غیرتهی |
| Canonical Field Registry | PASS | ۱۵۳ کلید طبقه‌بندی‌شده: ۱۰۶ mapped، ۳۱ reference-only و ۱۶ unresolved audit-only برای سلول‌های خارج جدول با heading خالی؛ هیچ source cell حذف نمی‌شود |
| Canonical typed domain schema | PASS | migrations و `tests/test_domain.py` |
| Design System / local Vazirmatn | PASS | token enforcement، فونت محلی، `tests/test_design_enforcement.py` |
| Shared UI components | PASS | shell، کنترل‌ها، filter، table، column chooser، dossier، timeline، dialog/disclosure و pagination فقط از Design System مشترک استفاده می‌کنند؛ enforcement test |
| Horizontal Navigation | PASS | `ui/templates/ui/base.html`; enforcement test |
| Dossier and imported history | PASS | dossier همه domainهای واردشده را پیوند می‌دهد؛ UI integration test |
| Contracts / beneficiaries / appraisal / auction | PASS | typed import + ثبت عملیاتی، الحاقیه، تغییر وضعیت، timeline و audit؛ `tests/test_operational_flows.py` |
| Decisions / source documents / utility obligations | PASS | typed import از workbook + full import gate |
| Appraisal fee operational process | PASS | مبلغ/پرداخت/نامه/پیگیری/سند، تاریخچه، Audit و Excel رسمی؛ تست عملیاتی و export |
| Utility consumption operational process | PASS | دوره/مصرف/سهم‌ها/پرداخت/سند، override کنترل‌شده، تاریخچه و Excel رسمی |
| Commission operational process | PASS | UI تشکیل تصمیم، فضاها/شرکت‌کنندگان/سند/اقدام بعدی، transition و Audit |
| File movement/current holder | PASS | فرم، تاریخچه، audit و current holder مشتق از آخرین حرکت باز |
| Workflow | PASS | ایجاد فقط با نوع عملیاتی مجاز، transition تراکنشی، تاریخچه و Audit در dossier |
| Documents / alerts / audit | PASS | upload امن server-side، checksum، permission، اقدام/مختومه‌سازی هشدار و Audit |
| Search/filter/saved views | PASS | exact/contains/starts، empty/nonempty، multi-select، ranges، AND/OR، multi-sort، column chooser و نماهای ذخیره‌شده |
| Official PDF/XLSX/DOCX engine | PASS | server-side structures, local Persian PDF font, exact filters/selected columns |
| Report builder / archived snapshot | PASS | تعریف زنده، اجرای مجدد، نسخه ثابت XLSX با query context، تعداد ردیف، SHA-256 و Audit؛ `test_saved_report_and_immutable_snapshot` |
| RBAC/user provisioning | PASS | native create/reset/activate UI، one-time passwords، forced change، staff gate و audit tests |
| Backup/restore | PASS | DB/media manifests، checksum، integrity/FK، global write lock، pre-restore backup، atomic restore و rollback tests |
| Auction candidate rules/lifecycle | PASS | Rule نسخه‌دار، تست مرزها و fail-safe، snapshot، UI ارزیابی، دوره و lot؛ participant/proposal schema |
| Browser/print QA | PASS | Chromium واقعی RTL/login/filter/dossier و screenshot؛ PDF server-side واقعی با صفحه، metadata و نبود URL |
| Five-user application concurrency | PASS | پنج کاربر authenticated در read/search/report و پنج write عملیاتی هم‌زمان با retry محدود SQLite |
| Clean Windows release | PASS | اجرای Windows روی commit `af531ae` با شناسه [`36741689560`](https://github.com/sazmantehkarimian-wq/sama-1405/actions/runs/36741689560) پاس شد؛ release رسمی `v5.0.0-uat.4` شامل ZIP به‌اندازه ۴۶٬۹۶۸٬۰۸۵ بایت و `SHA256SUMS.txt` است و hash دانلود مستقل نیز با مقدار `557ff5e9524b716ae48a55ccd927dfe4a22570ea768e36c0cb751acbeed9b164` تطبیق داده شد. |
| Owner UI/UX and Design System UAT | UAT REMEDIATION IN PROGRESS | پذیرش رابط `v5.0.0-uat.4` رد شده است؛ شواهد release قبلی صرفاً baseline فنی هستند و انتشار UAT جدید تا تکمیل بازبینی مرورگر و Gateهای اصلاحی مجاز نیست. |
