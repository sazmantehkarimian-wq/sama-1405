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
| حق‌الزحمه کارشناسی | موجود / نیازمند بازبینی نهایی | فرآیند قبلی تراکنشی و Auditدار باقی است؛ باید با پرونده جدید Appraiser/Appraisal از نظر UI و Reference Status نهایی تطبیق شود. |
| مزایده و Rule Registry | موجود / نیازمند بازبینی نهایی | موتور نسخه‌دار و snapshot موجود است؛ باید بعد از تکمیل فرم‌های کارشناسی و قرارداد روی Zero-Data دوباره Gate نهایی شود. |
| کمیسیون معاملات | موجود / نیازمند بازبینی نهایی | ایجاد/Transition/Audit موجود؛ بازبینی فرم‌ها و Reference Data باقی است. |
| انشعابات و مصرف | در حال تکمیل | منطق پایه ثبت قبض/سهم و Audit موجود است، اما مدل کامل FROZEN شامل Bill/Allocation/Measurement/Snapshot هنوز باید روی Zero-Data بازطراحی شود. |
| گردش پرونده / «الان دست کیه» | موجود / نیازمند بازبینی | FileMovement و current holder موجود است؛ باید فرم‌ها و قواعد handover/return نهایی شوند. |
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
4. بازطراحی انشعابات/مصرف و Rule/Reference Data بدون داده Seed عملیاتی.
5. تکمیل اسناد، گردش پرونده، هشدارها، کمیسیون و مزایده.
6. بازآزمایی Search/Filter/Report/Print روی schema نهایی.
7. Backup/Restore و Security regression.
8. ساخت Portable Windows Zero-Data، UAT واقعی و سپس تصمیم Owner.
