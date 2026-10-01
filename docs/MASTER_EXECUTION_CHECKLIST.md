# Master Execution Checklist — Zero-Data

این جدول فقط وضعیت خط جاری `work/zero-data-foundation` را ثبت می‌کند. «PASS» فقط برای مواردی استفاده می‌شود که شاهد خودکار روی همین معماری Zero-Data دارند. هیچ نتیجه‌ای از بسته‌های Import محور یا UAT قبلی به‌عنوان شاهد این خط محسوب نمی‌شود.

| Gate | وضعیت | شاهد / توضیح |
|---|---|---|
| Fresh migration با داده عملیاتی صفر | PASS | Quality workflow پس از migration شمار املاک مادر، فضا، قرارداد، بهره‌بردار، کارشناسی، مزایده، مصرف، گردش و Timeline را صفر کنترل می‌کند. |
| حذف Import Excel/CSV از Runtime | PASS | `import_pipeline` حذف شده؛ schemaهای `ImportBatch/SourceFile/RawCell` از Runtime حذف شده‌اند؛ Release بسته‌های Authority را حمل نمی‌کند. |
| کد فضا به‌عنوان Business Key | PASS | فقط عدد مثبت بدون صفر ابتدایی، unique و immutable؛ Validation فرم + trigger دیتابیس + تست. |
| استقلال املاک مادر و فضای تجاری | PASS | ارتباط اجباری/استنتاجی حذف شده؛ هر Entity فرم و شناسه مستقل دارد. |
| ورود دستی فضای تجاری | PASS | فرم کنترل‌شده، normalization، validation، Audit و ویرایش با کد ثابت. |
| ورود دستی ملک مادر | PASS | فرم مستقل، شناسه ثابت، Audit و کنترل مقادیر عددی. |
| Reference Data منطقه / مرکز | PASS | تعریف کنترل‌شده توسط مدیر و استفاده در فرم‌های عملیاتی. |
| تفکیک فضاهای فعال / خارج از چرخه | PASS | Route و View مستقل، Scope جست‌وجو، پیام هدایت به گروه صحیح؛ تست lifecycle اضافه شده و باید در آخرین CI سبز باقی بماند. |
| نمایش بهره‌بردار مستقل از قرارداد | PASS | `BeneficiaryAssignment` مستقل، ثبت بهره‌بردار بدون قرارداد و تاریخچه تغییر؛ تست جاری در Quality Gate آخر. |
| پرونده مستقل بهره‌بردار | PASS | شخص حقیقی/حقوقی، شناسه هویتی، کنترل Duplicate، Completeness، پرونده و Audit. |
| تغییر بهره‌بردار بدون overwrite | PASS | ارتباط قبلی خاتمه می‌یابد، علت و تاریخ حفظ می‌شود و ارتباط جدید ساخته می‌شود؛ تست جاری در Quality Gate آخر. |
| قرارداد با بهره‌بردار ثبت‌شده | PASS | ایجاد قرارداد فقط با Beneficiary موجود، بدون ساخت ضمنی نام آزاد. |
| ممنوعیت قرارداد هم‌پوشان | PASS | سرویس قرارداد overlap را قبل از ثبت رد می‌کند؛ قرارداد متوالی مجاز است. |
| مدت / وضعیت زمانی / بلندمدت قرارداد | PASS | از تاریخ‌ها محاسبه می‌شود؛ مدت دستی وجود ندارد؛ بیش از 365 روز Long-term است. |
| الحاقیه | PASS | رکورد مستقل، شماره یکتا در قرارداد، Audit/Timeline؛ قرارداد قبلی overwrite نمی‌شود. |
| پرونده مستقل کارشناس | PASS | `Appraiser` با کد سیستمی، شناسه حرفه‌ای، Duplicate control، وضعیت همکاری و Audit. |
| پرونده کارشناسی ساختاری | PASS | کد `APR`، کارشناس ثبت‌شده، ابلاغ 1:N، جواب، تاریخ خود کارشناسی و مبلغ مستقل. |
| یک کارشناسی مرجع جاری + تاریخچه | PASS | unique conditional DB constraint + سرویس تغییر مرجع؛ سابقه قبلی حفظ می‌شود. |
| تاریخ‌های کارشناسی مستقل | PASS | تاریخ ابلاغ، تاریخ جواب و تاریخ خود کارشناسی فیلدهای جدا و Validation مستقل دارند. |
| حق‌الزحمه کارشناسی | CORE PASS | گردش FROZEN شامل مبلغ دستی مستقل، وضعیت‌های کنترل‌شده، ارسال به مالی با نامه/تاریخ، پرداخت کامل با شرط برابری مبلغ، اصلاح مبلغ با Audit، Batch گروهی با عضویت فعال یکتا، KPI/Filter/Drill-down و XLSX رسمی پیاده و تست شد. PDF/Print اختصاصی این گزارش در Gate خروجی نهایی باز می‌ماند. |
| مزایده — Candidate / Instruction / Period Selection | CORE PASS | موتور deterministic و fail-safe، Rule سالانه نسخه‌دار، کارشناسی مرجع جاری، کنترل اعتبار در تاریخ مزایده، Reason Code/Snapshot، دستورات هم‌تراز مدیر/کمیسیون، تعارض رسمی، Manual Include/Exclude، جلوگیری از حضور هم‌زمان فضا در چند دوره باز، انتخاب از Candidate و افزودن دستی مجاز با علت/مرجع/Audit پیاده و تست شد. Golden Master اسناد رسمی، Readiness کامل Lot و خروجی‌های جلسه هنوز Gate جدا دارند. |
| کمیسیون معاملات | CORE PASS | اعضای مستقل، Snapshot اعضای جلسه، جلسه/موضوع، ارتباط صریح با فضا/قرارداد/بهره‌بردار/مزایده، تصمیم، مسئول/مهلت، Follow-up append-only، وضعیت اجرا و Audit/Timeline پیاده و تست شد. صورتجلسه Golden Master و بسته اسناد/چاپ تخصصی هنوز Gate جدا دارد. |
| برق — Bill / Allocation / Measurement / Snapshot | PASS | مدل FROZEN برق روی Zero-Data پیاده شد: UtilityUnit، ElectricityBill، Allocation، Measurement، Category، Rule Registry، اولویت داده واقعی، Override مجاز، کنترل ۱۰۰٪، کنترل ریالی، Final/Reopen و Snapshot نسخه‌دار. |
| آب / گاز — Connection / Bill / Measurement | PASS | معماری مستقل آب و گاز بدون استفاده از فرمول برق پیاده شد؛ اشتراک، قبض، دوره، مبلغ، مصرف، Measurement، پرداخت و Audit پوشش داده شده‌اند. |
| گزارش‌ها و فیلترهای تخصصی آب / گاز | PASS | داشبورد مستقل آب/گاز/سایر، فیلتر نوع/پرداخت/Measurement/منطقه/مرکز/دوره/مبلغ، مقایسه با دوره قبلی همان اشتراک، سند قبض و خروجی رسمی Excel 2019 پیاده و تست شد. |
| گردش پرونده / «الان دست کیه» | PASS | فقط یک تحویل باز برای هر فضا مجاز است؛ تحویل جدید قبلی را می‌بندد، بازگشت مستقل Audit/Timeline دارد و محل، دارنده، تحویل‌گیرنده، زمان، مدت در دست، امضا، اقدام بعدی و مهلت در پرونده نمایش داده می‌شود. |
| اسناد و مدارک | موجود / نیازمند بازبینی | Upload امن، checksum و download کنترل‌شده موجود؛ اتصال تخصصی به Entityهای جدید باید تکمیل شود. |
| هشدارها / Workflow | موجود / نیازمند بازبینی | سرویس‌های Auditدار موجود؛ Reference Status و UI نهایی باقی است. |
| Search / Filter | PARTIAL PASS | کد فضا، بهره‌بردار، قرارداد، Appraiser و Appraisal توسعه یافته‌اند؛ فیلترهای تخصصی هر ماژول هنوز کامل نشده‌اند. |
| گزارش XLSX/PDF/DOCX | موجود / نیازمند بازبینی | موتور خروجی رسمی موجود؛ باید با schema Zero-Data و ستون‌های جدید بازآزمایی شود. |
| Hard delete policy | PASS در معماری | روابط عملیاتی با `PROTECT` و تاریخچه طراحی شده‌اند؛ UI حذف عادی برای رکوردهای اصلی ارائه نمی‌کند. |
| Audit / Timeline | PASS برای جریان‌های بازطراحی‌شده | Space, MotherProperty, Beneficiary, Contract, Appraisal و تغییرات اصلی Audit/Timeline دارند. |
| Security / Authentication | PASS در تست‌های جاری | CSRF، password hashing، login throttle، مدیریت کاربران و UAT policy توسط تست‌ها پوشش داده می‌شود. |
| Backup / Restore | موجود / نیازمند Gate نهایی Zero-Data | سازوکار integrity/hash/rollback موجود است؛ بعد از تثبیت schema نهایی دوباره تست Release لازم است. |
| Portable Windows/LAN | روش تثبیت‌شده، Build جدید PENDING | روش `START_SAMA.bat`، Waitress و پورت 8765 حفظ شده؛ هنوز بسته Windows جدید بر مبنای Zero-Data منتشر نشده است. |
| Windows Zero-Data UAT package | PENDING | فقط بعد از تثبیت schema و عبور کامل CI ساخته می‌شود. |
| Owner UAT | PENDING | نیازمند بسته جدید و پذیرش انسانی Owner است. |
| Production/LAN-ready | NOT APPROVED | تا Windows gate و Owner UAT نباید Production/LAN-ready اعلام شود. |

## ترتیب ادامه اجرا

1. سبز نگه‌داشتن Quality Gate پس از هر تغییر Schema/Workflow.
2. تکمیل بهره‌بردار مستقل از قرارداد و نمایش Current/History.
3. تکمیل قرارداد، کارشناسان و کارشناسی بر اساس اسناد FROZEN.
4. تکمیل اسناد تخصصی، هشدارها و Workflow؛ سپس Readiness کامل Lot و Golden Masterهای مزایده/کمیسیون.
5. تکمیل خروجی‌های PDF/Print تخصصی، از جمله حق‌الزحمه و انشعابات.
6. بازآزمایی Search/Filter/Report/Print روی schema نهایی.
7. Backup/Restore و Security regression.
8. ساخت Portable Windows Zero-Data، UAT واقعی و سپس تصمیم Owner.
