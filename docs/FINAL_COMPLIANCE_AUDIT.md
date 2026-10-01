# Final Compliance Audit

## وضعیت جاری: UAT REMEDIATION IN PROGRESS

پذیرش UI/UX و Design System در UAT مالک رد شده است. وضعیت‌های PASS زیر شواهد فنی پیشین را ثبت می‌کنند و به معنی آمادگی Production/LAN یا مجوز ادغام نیستند. انتشار جدید فقط پس از تکمیل اصلاحات، بازبینی واقعی مرورگر و تأیید دوباره همه Gateها مجاز است.

| الزام بحرانی | وضعیت | شاهد/شکاف |
|---|---|---|
| جدایی معماری از Legacy | PASS | `LEGACY_BOUNDARY.md`; root commit مستقل؛ آزمون الگوهای ممنوع |
| Authority/hash/data baseline | PASS | بازخوانی مستقیم workbook: ۲۲۵ / ۳۵۰ / ۱۵۱ / ۵۰۱، بدون overlap/duplicate |
| Raw provenance | PASS | ۸۴٬۶۱۸ cell غیرتهی با منبع، مختصات و fingerprint |
| Registry | PASS | ۱۲۴ کلید: ۷۷ mapped، ۳۱ reference-only و ۱۶ unresolved audit-only برای سلول‌های خارج جدول بدون heading؛ raw evidence محفوظ است |
| Typed canonical domains | PASS | مدل‌های رابطه‌ای و migrations؛ JSON فقط برای پیکربندی/ممیزی است |
| Design system/navigation/dossier | PASS | token enforcement، Vazirmatn محلی، navigation افقی و dossier یکپارچه |
| Historical contracts/beneficiaries/appraisals/auctions | PASS | import رابطه‌ای با provenance |
| Appraisal fees/utilities/workflow | PASS | ثبت تراکنشی، سند، override، تاریخچه، Audit، گزارش Excel و dossier با تست |
| Commission lifecycle | PASS | UI ایجاد، پیوند چند فضا، شرکت‌کنندگان/سند، اقدام بعدی، transition و Audit با تست |
| File movement/current holder | PASS | ثبت ممیزی‌شده و current-holder مشتق از آخرین movement باز |
| Documents/alerts/audit | PASS | upload امن server-side و checksum؛ اقدام هشدار و audit موجود |
| Advanced filters/saved views | PASS | operatorهای متنی، خالی/ناخالی، ranges، multi-select/sort، AND/OR، column chooser و فیلتر ذخیره‌شده |
| Auction engine | PASS | موتور نسخه‌دار fail-safe، snapshot، تست مرزی و UI ارزیابی/دوره/lot |
| Official exports | PASS | XLSX/DOCX/PDF واقعی server-side، فیلتر/ستون جاری و header رسمی |
| RBAC/user administration | PASS | مدیریت بومی create/reset/activate، اجبار تعویض رمز، staff enforcement و audit |
| Backup/restore | PASS | DB/media/config manifest، lock نوشتن، pre-restore، integrity/FK و rollback tests |
| Browser/print/concurrency/security | PASS | Chromium واقعی و screenshot، PDF ساختاری، login throttle، پنج read/report و پنج write هم‌زمان پاس |
| Windows portable/prerelease asset | PASS | workflow [`36850270141`](https://github.com/sazmantehkarimian-wq/sama-1405/actions/runs/36850270141) روی runtime commit `9fd74aa` پاس شد. `v5.0.0-uat.7` prerelease دارای ZIP ۵۴٬۵۳۶٬۰۹۴ بایتی است؛ SHA-256 دانلود مستقل `5aa2d3c402c49e6c42c62c6927baaa92e8f5c88c30405fda6c6ef32fac89d0bb` است. |

اصلاحات فنی UAT.6 شامل نگاشت semantic قرارداد/بهره‌بردار/کارشناسی، timeline، ارائه مرکزی، خروجی رسمی RTL و بازبینی Chromium واقعی است. وضعیت تا پذیرش انسانی مالک همچنان UAT REMEDIATION IN PROGRESS می‌ماند؛ PR شماره ۲ نباید ادغام شود و این نسخه آماده Production/LAN نیست.


## قفل حساب مالک در UAT

در بسته UAT، `SAMA_UAT_FIXED_ADMIN` تنها مرجع فعال‌سازی است. حساب `admin` با گذرواژه `admin` در هر راه‌اندازی به‌صورت idempotent بازنشانی می‌شود؛ تغییر گذرواژه، بازنشانی، غیرفعال‌سازی، تغییر نام کاربری و حذف آن از رابط مدیریتی ارائه نمی‌شود. این استثناء در حالت Production غیرفعال است و سیاست امن کاربران عملیاتی را تغییر نمی‌دهد.


یادداشت زنجیره انتشار UAT.7: runtime و ورودی‌های build دقیقاً از commit `9fd74aa` ساخته شده‌اند. commitهای پس از آن فقط شواهد workflow و جای‌گذاری آزمون مرورگر در Gate صریح CI را ثبت می‌کنند؛ هیچ کد یا ورودی بسته‌شده runtime تغییر نکرده و بازسازی بسته لازم نیست.
