# Final Compliance Audit

این سند وضعیت واقعی clean branch را ثبت می‌کند و مجوز Release نیست. هر شکاف بحرانی انتشار را مسدود می‌کند.

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
| Windows portable/release asset | NEEDS VERIFICATION | ساخت runtime embedded و انتشار asset فقط داخل GitHub Actions؛ نتیجه اجرای release پیش از تبدیل به PASS باید ثبت شود |

هیچ Critical FAIL باقی نمانده است. تنها Gate خارجی Windows package/GitHub Asset تا اجرای workflow با وضعیت `NEEDS VERIFICATION` باقی می‌ماند و پیش از آن انتشار تکمیل‌شده تلقی نمی‌شود.
