# Final Compliance Audit

این سند وضعیت واقعی clean branch را ثبت می‌کند. هر شکاف بحرانی انتشار را مسدود می‌کند.

| الزام بحرانی | وضعیت | شاهد/شکاف |
|---|---|---|
| جدایی معماری از Legacy | PASS | `LEGACY_BOUNDARY.md`; root commit مستقل؛ آزمون الگوهای ممنوع |
| Authority/hash/data baseline | PASS | بازخوانی مستقیم workbook: ۲۲۵ / ۳۵۰ / ۱۵۱ / ۵۰۱، بدون overlap/duplicate |
| Raw provenance | PASS | ۸۴٬۶۱۸ cell غیرتهی با منبع، مختصات و fingerprint |
| Registry | PASS | ۱۵۳ کلید: ۱۰۶ mapped، ۳۱ reference-only و ۱۶ unresolved audit-only برای سلول‌های خارج جدول بدون heading؛ raw evidence محفوظ است |
| Typed canonical domains | PASS | مدل‌های رابطه‌ای و migrations؛ JSON فقط برای پیکربندی/ممیزی است |
| Design system/navigation/dossier | PASS | token enforcement، Vazirmatn محلی، navigation افقی و dossier یکپارچه |
| Historical contracts/beneficiaries/appraisals/auctions | PASS | import رابطه‌ای با provenance |
| Appraisal fees/utilities/workflow | PASS | ثبت تراکنشی، سند، override، تاریخچه، Audit، گزارش Excel و dossier با تست |
| Commission lifecycle | PASS | UI ایجاد، پیوند چند فضا، شرکت‌کنندگان/سند، اقدام بعدی، transition و Audit با تست |
| File movement/current holder | PASS | ثبت ممیزی‌شده و current-holder مشتق از آخرین movement باز |
| Documents/alerts/audit | PASS | upload امن server-side و checksum؛ اقدام هشدار و audit موجود |
| Advanced filters/saved views | PASS | operatorهای متنی، خالی/ناخالی، ranges، multi-select/sort، AND/OR، column chooser و نمای ذخیره‌شده |
| Auction engine | PASS | موتور نسخه‌دار fail-safe، snapshot، تست مرزی و UI ارزیابی/دوره/lot |
| Official exports | PASS | XLSX/DOCX/PDF واقعی server-side، فیلتر/ستون جاری و header رسمی |
| RBAC/user administration | PASS | مدیریت بومی create/reset/activate، اجبار تعویض رمز، staff enforcement و audit |
| Backup/restore | PASS | DB/media/config manifest، lock نوشتن، pre-restore، integrity/FK و rollback tests |
| Browser/print/concurrency/security | PASS | Chromium واقعی و screenshot، PDF ساختاری، login throttle، پنج read/report و پنج write هم‌زمان پاس |
| Windows portable/release asset | PASS | اجرای Windows با شناسه [`36741689560`](https://github.com/sazmantehkarimian-wq/sama-1405/actions/runs/36741689560) روی commit `af531ae` پاس شد؛ release رسمی `v5.0.0-uat.4` شامل runtime، پایگاه canonical و launcherهاست. ZIP منتشرشده ۴۶٬۹۶۸٬۰۸۵ بایت است و SHA-256 آن پس از دانلود مستقل برابر `557ff5e9524b716ae48a55ccd927dfe4a22570ea768e36c0cb751acbeed9b164` تأیید شد. |

هیچ Critical FAIL یا Gate باز باقی نمانده است. workflow کیفیت خط پاک و workflow ساخت Windows برای commit یکسان `af531ae` پاس شده‌اند و asset منتشرشده نیز از بیرون workflow بازخوانی و از نظر hash و وجود runtime، پایگاه canonical و launcherها راستی‌آزمایی شده است؛ بنابراین Definition of Done خط پاک تکمیل است.
