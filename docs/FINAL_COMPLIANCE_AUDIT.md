# Final Compliance Audit

## وضعیت جاری: UAT REMEDIATION IN PROGRESS

پذیرش UI/UX و Design System در UAT مالک هنوز نهایی نشده است. وضعیت‌های PASS زیر فقط شواهد فنی همان Gate را ثبت می‌کنند و به معنی آمادگی Production/LAN یا مجوز ادغام نیستند. علاوه بر پذیرش انسانی UI/UX، Golden Master اسناد رسمی مزایده نیز طبق سند FINAL FROZEN به Print QA واقعی نیاز دارد.

| الزام بحرانی | وضعیت | شاهد/شکاف |
|---|---|---|
| جدایی معماری از Legacy | PASS | `LEGACY_BOUNDARY.md`; root commit مستقل؛ آزمون الگوهای ممنوع |
| Authority/hash/data baseline | PASS | بازخوانی مستقیم workbook: ۲۲۵ / ۳۵۰ / ۱۵۱ / ۵۰۱، بدون overlap/duplicate |
| Raw provenance | PASS | ۸۴٬۶۱۸ cell غیرتهی با منبع، مختصات و fingerprint |
| Registry | PASS | Import جاری ۱۲۴ canonical field گزارش می‌کند؛ raw evidence محفوظ است. |
| Typed canonical domains | PASS | مدل‌های رابطه‌ای و migrations؛ JSON فقط برای پیکربندی/ممیزی است |
| Design system/navigation/dossier | PASS | token enforcement، Vazirmatn محلی، navigation افقی و dossier یکپارچه |
| Historical contracts/beneficiaries/appraisals/auctions | PASS | import رابطه‌ای با provenance |
| Appraisal fees/utilities/workflow | PASS | ثبت تراکنشی، سند، override، تاریخچه، Audit، گزارش Excel و dossier با تست |
| Commission lifecycle | PASS | UI ایجاد، پیوند چند فضا، شرکت‌کنندگان/سند، اقدام بعدی، transition و Audit با تست |
| File movement/current holder | PASS | ثبت ممیزی‌شده و current-holder مشتق از آخرین movement باز |
| Documents/alerts/audit | PASS | upload امن server-side و checksum؛ اقدام هشدار و audit موجود |
| Advanced filters/saved views | PASS | operatorهای متنی، خالی/ناخالی، ranges، multi-select/sort، AND/OR، column chooser و فیلتر ذخیره‌شده |
| Auction engine | PASS | موتور نسخه‌دار fail-safe، snapshot، تست مرزی و UI ارزیابی/دوره/lot |
| Official tabular reports | PASS | XLSX/DOCX/PDF واقعی server-side برای گزارش‌های جدولی، فیلتر/ستون جاری و header رسمی |
| Official auction/legal document engine | BLOCKED — GOLDEN MASTER NOT YET APPROVED | سند `MD اسناد رسمی و Golden Master مزایده — FINAL FROZEN.md` TemplateVersion، Snapshot، DocumentInstance، Hash، PDF/DOCX parity، Visual Regression، Atomic Page و Print Test واقعی را الزام می‌کند. مدل فعلی `domains.documents.Document` فقط فایل بارگذاری‌شده را ثبت می‌کند؛ بنابراین PASS گزارش‌های جدولی نباید به Document Engine رسمی تعمیم داده شود. Production coding/finalization این بخش تا تأیید Golden Master چاپی مالک متوقف می‌ماند. |
| RBAC/user administration | PASS | مدیریت بومی create/reset/activate، اجبار تعویض رمز، staff enforcement و audit |
| Backup/restore | PASS | DB/media manifest، lock نوشتن، pre-restore، integrity/FK و rollback؛ مسیر دیتابیس Manifest روی `sama.sqlite3` قفل شده و DB tamper، media tamper و path traversal با تست رد می‌شود. |
| Browser/UI regression | PASS | Chromium واقعی برای UI و گزارش‌های عمومی؛ CI باید screenshotهای واقعی را به‌عنوان artifact ذخیره کند و نبود artifact از این پس Gate را Fail می‌کند. |
| Golden Master physical print QA | NOT PASSED | چاپ واقعی صفحه‌به‌صفحه و تأیید انسانی برای COMMERCIAL / CAFE / SPORT و تمام اسناد الزامی هنوز شاهد تأییدشده ندارد. |
| Concurrency/security | PASS | login throttle، پنج read/report و پنج write هم‌زمان پاس |
| Windows portable/prerelease asset | PASS (UAT ONLY) | workflow Windows و بسته prerelease وجود دارد؛ این شاهد فقط UAT candidate است و مجوز Production/LAN نیست. |

## Current automated evidence

آخرین Gate کامل پیش از اصلاح سخت‌گیری artifact مرورگر:

- `pytest -q`: **55 passed, 2 skipped**
- Chromium gate: **2 passed**
- `python manage.py check --deploy`: **0 issues**
- import inventory: **225 mother properties / 350 active / 151 out-of-cycle / 501 unique spaces / 84,618 raw cells / 124 canonical fields / 1,884 discrepancies**

پس از اصلاح workflow، browser screenshot artifact نیز باید واقعاً وجود داشته باشد؛ سبز بودن job بدون artifact دیگر پذیرفته نیست.

اصلاحات فنی UAT شامل نگاشت semantic قرارداد/بهره‌بردار/کارشناسی، timeline، ارائه مرکزی، خروجی رسمی RTL و بازبینی Chromium واقعی است. وضعیت تا پذیرش انسانی مالک و عبور Golden Master Print QA همچنان UAT REMEDIATION IN PROGRESS می‌ماند؛ PR شماره ۲ نباید به‌عنوان Production/LAN-ready ادغام شود.

## قفل حساب مالک در UAT

در بسته UAT، `SAMA_UAT_FIXED_ADMIN` تنها مرجع فعال‌سازی است. حساب `admin` با گذرواژه `admin` در هر راه‌اندازی به‌صورت idempotent بازنشانی می‌شود؛ تغییر گذرواژه، بازنشانی، غیرفعال‌سازی، تغییر نام کاربری و حذف آن از رابط مدیریتی ارائه نمی‌شود. این استثناء در حالت Production غیرفعال است و سیاست امن کاربران عملیاتی را تغییر نمی‌دهد.

معماری پرونده را نمای ۳۶۰ درجه فقط‌خواندنی و ماژول‌های تخصصی را محل ثبت عملیات می‌داند. تعریف، جمعیت، predicate و drill-down شاخص‌های داشبورد در `docs/DASHBOARD_KPI_CATALOG.md` ثبت شده است.

## Post-UAT remediation

Contract circulation یک aggregate عملیاتی ممیزی‌شده مستقل است و بدون امضاها و تأیید نهایی نباید قرارداد رسمی شود. Custody فقط از رویدادهای append-only تحویل/عودت مشتق می‌شود. قراردادهای تاریخی حفظ می‌شوند و Workflow ساختگی دریافت نمی‌کنند. تعریف گزارش مرکزی layout ترکیبی مرتب از ستون‌های canonical و blank output-only، multi-sort، orientation و filter را در preview/XLSX/PDF/DOCX و snapshot حفظ می‌کند.

## Production/LAN release blockers

تا عبور هر دو مورد زیر، هیچ برچسب Production/LAN-ready معتبر نیست:

1. پذیرش انسانی Owner برای UI/UX و Design System.
2. تأیید Golden Master و Print QA واقعی برای اسناد رسمی مزایده مطابق FINAL FROZEN.
