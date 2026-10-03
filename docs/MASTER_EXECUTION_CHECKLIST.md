# Master Execution Checklist — Zero-Data

این جدول فقط وضعیت خط جاری `work/zero-data-foundation` را ثبت می‌کند. «PASS» فقط برای مواردی استفاده می‌شود که شاهد خودکار روی همین معماری Zero-Data دارند. هیچ نتیجه‌ای از بسته‌های Import محور یا UAT قبلی به‌عنوان شاهد این خط محسوب نمی‌شود.

| Gate | وضعیت | شاهد / توضیح |
|---|---|---|
| Fresh migration با داده عملیاتی صفر | PASS | Quality workflow پس از migration شمار املاک مادر، فضا، قرارداد، بهره‌بردار، کارشناسی، مزایده، مصرف، گردش و Timeline را صفر کنترل می‌کند. |
| حذف Import Excel/CSV از Runtime | PASS | `import_pipeline` و schemaهای `ImportBatch/SourceFile/RawCell` حذف شده‌اند؛ Release فایل‌های Excel/Authority را حمل نمی‌کند. |
| کد فضا به‌عنوان Business Key | PASS | فقط عدد مثبت بدون صفر ابتدایی، unique و immutable؛ Form + Server + DB trigger + تست. |
| استقلال املاک مادر و فضای تجاری | PASS | هیچ رابطه اجباری/استنتاجی وجود ندارد؛ هر Entity فرم، پرونده و گزارش مستقل دارد. |
| ورود دستی فضای تجاری / ملک مادر | PASS | فرم کنترل‌شده، normalization، validation، Audit و Business Key ثابت. |
| Reference Data منطقه / مرکز | PASS | تعریف کنترل‌شده مدیر و استفاده در فرم‌های عملیاتی. |
| تفکیک فعال / خارج از چرخه | PASS | View مستقل، Scope صحیح، هدایت جست‌وجو و حفظ آخرین سوابق تاریخی. |
| بهره‌بردار مستقل از قرارداد | PASS | `BeneficiaryAssignment` مستقل؛ بهره‌بردار بدون قرارداد مجاز، تغییر با خاتمه رابطه قبلی و بدون overwrite. |
| قرارداد | PASS | Beneficiary ثبت‌شده، سازگاری با بهره‌بردار جاری، منع overlap، وضعیت زمانی/مدت مشتق‌شده و الحاقیه مستقل. |
| گردش قرارداد قبل از قرارداد رسمی | PASS | گردش، امضاها، تحویل/بازگشت، تأیید و تبدیل به Contract رسمی مستقل از خود Contract ثبت می‌شود. |
| کارشناسان / کارشناسی | PASS | `EXP` و `APR`، Duplicate control، ابلاغ 1:N، تاریخ‌های مستقل، یک Reference Appraisal جاری و تاریخچه کامل. |
| حق‌الزحمه کارشناسی | CORE PASS | مبلغ، وضعیت، ارسال مالی، پرداخت، اصلاح Auditدار، Batch، KPI/Filter/Drill-down و XLSX/PDF پیاده شده‌اند؛ بازبینی چاپ نهایی در Gate خروجی سراسری باقی است. |
| مزایده | CORE PASS | Rule نسخه‌دار، Candidate/Review/Readiness، Snapshot/Reason Code، Instruction، Period/Lot و Manual Include/Exclude Auditدار. Golden Master نهایی اسناد جلسه هنوز Gate خروجی رسمی است. |
| کمیسیون معاملات | CORE PASS | اعضا، Snapshot جلسه، Case/Decision/Follow-up و Audit/Timeline پیاده شده‌اند؛ Golden Master صورتجلسه هنوز Gate خروجی رسمی است. |
| برق | PASS | Bill/Allocation/Measurement/Category/Rule/Snapshot، اولویت داده واقعی، Override، کنترل ۱۰۰٪ و ریال، Final/Reopen. |
| آب / گاز | PASS | Connection/Bill/Measurement مستقل از فرمول برق، پرداخت و Audit. |
| گزارش‌های آب / گاز | PASS | فیلتر، مقایسه دوره، سند قبض، Excel 2019 و PDF. |
| گردش پرونده / «الان دست کیه» | PASS | فقط یک تحویل باز مجاز است؛ **تحویل دوم تا بازگشت صریح پرونده Block می‌شود**؛ بازگشت Audit/Timeline مستقل دارد. |
| اسناد و مدارک | PASS | Upload کنترل‌شده، metadata، SHA-256، محدودیت نوع/حجم، Archive بدون Hard Delete، Audit/Timeline و checksum مجدد قبل از Download؛ دستکاری فایل Fail-Closed است. |
| هشدارها / Workflow / Action Center | PASS | Create/Transition/Resolve Auditدار، Action Center دامنه‌پذیر، Priority/Overdue/Search و Drill-down دقیق. |
| داشبورد مدیریتی / Global Scope | PASS | Region/Center/Usage/Status Scope، KPI از Query مرکزی، KPI=Drill-down، Action Center و Auction latest-evaluation drill-down؛ status scope روی KPIهای Active-only نیز اعمال می‌شود. |
| Search / Filter | PARTIAL PASS | کلیدهای اصلی فضا، بهره‌بردار، قرارداد، کارشناس، کارشناسی و Utility پوشش دارند؛ بازبینی نهایی یکپارچگی همه Domain filterها مانده است. |
| گزارش رسمی XLSX/PDF/DOCX | CORE PASS | موتور مشترک RTL، لوگوی رسمی و فقط هویت سازمانی؛ Excel 2019/PDF/DOCX و گزارش‌های scoped موجودند. Golden Masterهای مزایده/کمیسیون و Regression نهایی مانده است. |
| Hard delete policy | PASS | روابط اصلی `PROTECT`، تاریخچه/Archive و نبود حذف عادی در UI. |
| Audit / Timeline | PASS | جریان‌های اصلی Business با Audit و Timeline/History پوشش داده شده‌اند. |
| Security / Authentication | PASS در تست جاری | Password hashing، CSRF، session hardening، Login throttle، fixed accounts، force-password-change و document integrity. |
| Backup / Restore | CORE PASS — latest CI pending | DB+Media manifest/hash، SQLite integrity/FK، pre-restore backup، maintenance write lock و rollback موجود است؛ Startup schema guard و startup-safety backup نیز اضافه شده و آخرین CI آن در حال اجراست. |
| Startup schema safety | CORE PASS — latest CI pending | DB دارای migration ناشناخته/جدیدتر Fail-Closed می‌شود؛ دیتابیس موجود قبل از migrate Backup verified می‌گیرد. |
| Portable Windows/LAN | روش FROZEN، Build جدید PENDING | `START_SAMA.bat` → First Start/Preflight → Waitress، پورت 8765؛ بسته Windows نهایی هنوز ساخته نشده است. |
| Windows Zero-Data UAT package | PENDING | فقط پس از بسته‌شدن Gateهای خروجی و سبز بودن head نهایی ساخته می‌شود. |
| Owner UAT | PENDING | نیازمند بسته نهایی و پذیرش انسانی Owner. |
| Production/LAN-ready | NOT APPROVED | تا Windows/LAN UAT و پذیرش Owner ممنوع است. |

## ادامه اجرا

1. تثبیت CI پس از Startup schema/backup guard.
2. Golden Master خروجی‌های مزایده و کمیسیون و Regression هویت رسمی گزارش‌ها.
3. بازآزمایی سراسری Search/Filter/Print/Excel/PDF/DOCX و Browser RTL.
4. Security + Backup/Restore + crash/restart regression نهایی.
5. ساخت Portable Windows Zero-Data و اجرای Windows/LAN UAT.
6. تحویل یک‌جای بسته نهایی برای پذیرش Owner.
