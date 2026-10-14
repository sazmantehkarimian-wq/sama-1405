# Master Execution Checklist

این جدول وضعیت واقعی خط پاک را ثبت می‌کند. «PASS» فقط با شاهد خودکار موجود به‌کار رفته است.

| Gate | وضعیت | شاهد |
|---|---|---|
| Authority SHA/Data Inventory | PASS | `verify_manifest` + `inspect_package` و `tests/test_authority.py`: شمارش مستقیم workbook، یکتایی و نبود overlap |
| Lossless import / 225 + 350 + 151 | PASS | `tests/test_import_pipeline.py`; شمارش مستقیم workbook و همه cellهای غیرتهی |
| Canonical Field Registry | PASS | Import جاری ۱۲۴ canonical field و ۸۴٬۶۱۸ raw cell را ثبت می‌کند؛ هیچ source cell حذف نمی‌شود. |
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
| Search/filter/saved views | PASS | exact/contains/starts، empty/nonempty، multi-select، ranges، AND/OR، multi-sort، column chooser و فیلترهای ذخیره‌شده |
| Official tabular PDF/XLSX/DOCX reporting | PASS | خروجی server-side گزارش‌های جدولی با فونت فارسی محلی، فیلتر/ستون/چیدمان انتخابی و هویت رسمی سازمان؛ این Gate به معنی Golden Master اسناد حقوقی مزایده نیست. |
| Auction official document Golden Master | BLOCKED — HUMAN PRINT QA REQUIRED | طبق `authority/reference/MD اسناد رسمی و Golden Master مزایده — FINAL FROZEN.md`، سه خانواده مستقل COMMERCIAL/CAFE/SPORT و اسناد مزایده/قرارداد/پاکت‌های الف‌ب‌ج/منع مداخله/صورتجلسه باید Master مستقل، Snapshot، Version، Hash، PDF/DOCX data parity، Visual Regression و Print Test صفحه‌به‌صفحه داشته باشند. مدل فعلی `domains.documents.Document` فقط سند بارگذاری‌شده را نگه می‌دارد؛ تا تأیید Golden Master چاپی مالک، Document Engine رسمی Production نباید PASS یا Production-ready اعلام شود. |
| Golden Master source intake | CONTROLLED | `docs/GOLDEN_MASTER_SOURCE_MANIFEST.md` منابع مرجع را روی commit ثابت `main@ae8a789b...` قفل کرده است. نام «اسناد مزایده فضای تجاری.zip» و «نمونه قراراداد 1.zip» به Blob و اندازه یکسان اشاره می‌کنند و تا Content Verification دو منبع مستقل محسوب نمی‌شوند. |
| Report builder / archived snapshot | PASS | تعریف زنده، اجرای مجدد، نسخه ثابت XLSX با query context، تعداد ردیف، SHA-256 و Audit؛ `test_saved_report_and_immutable_snapshot` |
| RBAC/user provisioning | PASS | native create/reset/activate UI، one-time passwords، forced change، staff gate و audit tests |
| Backup/restore | PASS | DB/media manifests، checksum، integrity/FK، global write lock، pre-restore backup، atomic restore و rollback؛ Manifest دیتابیس روی `sama.sqlite3` قفل است و path traversal/DB tamper/media tamper با تست رد می‌شود. |
| Auction candidate rules/lifecycle | PASS | Rule نسخه‌دار، تست مرزها و fail-safe، snapshot، UI ارزیابی، دوره و lot؛ participant/proposal schema |
| Browser UI regression | PASS WITH ARTIFACT GATE | Chromium واقعی RTL/login/filter/dossier؛ workflow حالا `SAMA_BROWSER_SCREENSHOT_DIR=artifacts/browser` می‌فرستد و `if-no-files-found: error` دارد، بنابراین نبود screenshot باعث Fail می‌شود. |
| Golden Master visual/physical print regression | NOT PASSED | تست PDF عمومی سامانه جایگزین Print Test Golden Master نیست. طبق سند Frozen، تعداد/ترتیب صفحات، Atomic Page، overflow، محل امضا، فونت، RTL و چاپ واقعی باید برای هر Template Version تأیید انسانی شود. |
| Five-user application concurrency | PASS | پنج کاربر authenticated در read/search/report و پنج write عملیاتی هم‌زمان با retry محدود SQLite |
| Automated quality baseline | PASS | آخرین Gate کامل قبل از artifact-hardening: `55 passed, 2 skipped`؛ Chromium جداگانه `2 passed`؛ `check --deploy` بدون Issue. Import: 225/350/151/501، 84,618 raw cells، 124 canonical fields، 1,884 discrepancies. |
| Clean Windows UAT prerelease | PASS (UAT ONLY) | بسته Windows prerelease و SHA verification قبلاً پاس شده‌اند؛ این شاهد صرفاً UAT است و مجوز Production/LAN نیست. |
| Owner UI/UX and Design System UAT | UAT REMEDIATION IN PROGRESS | اصلاح فنی، ردگیری داده واقعی و بازبینی Chromium انجام شده است؛ پذیرش انسانی مالک باز است؛ prerelease ویندوزی مجوز Production/LAN نیست. |

## Release truth

تا زمانی که هر دو Gate زیر PASS نشده‌اند، پروژه فقط UAT candidate است و PR #2 نباید به‌عنوان Production/LAN-ready ادغام یا معرفی شود:

1. Owner UI/UX human acceptance.
2. Golden Master visual + physical print acceptance برای اسناد رسمی مزایده.
