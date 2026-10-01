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
| Windows portable/prerelease asset | PASS | workflow [`36839370829`](https://github.com/sazmantehkarimian-wq/sama-1405/actions/runs/36839370829) روی runtime commit `5b672c6` پاس شد. `v5.0.0-uat.6` prerelease دارای ZIP ۵۰٬۹۹۰٬۷۴۰ بایتی است؛ SHA-256 دانلود مستقل `1c558b90e04a350576059c6a1ff3f2d92aa051eefb851a2d150c098da23ff6d5` است. |

اصلاحات فنی UAT.6 شامل نگاشت semantic قرارداد/بهره‌بردار/کارشناسی، timeline، ارائه مرکزی، خروجی رسمی RTL و بازبینی Chromium واقعی است. وضعیت تا پذیرش انسانی مالک همچنان UAT REMEDIATION IN PROGRESS می‌ماند؛ PR شماره ۲ نباید ادغام شود و این نسخه آماده Production/LAN نیست.


یادداشت زنجیره انتشار: runtime و محتوای بسته از commit `5b672c6` ساخته شده است. commit بعدی فقط همین شواهد ممیزی را ثبت می‌کند و هیچ ورودی runtime/code/build را تغییر نمی‌دهد؛ بنابراین بازسازی artifact لازم نیست.
