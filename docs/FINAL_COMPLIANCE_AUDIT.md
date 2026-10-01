# Compliance Audit — Zero-Data Foundation

## وضعیت جاری: DEVELOPMENT / UAT NOT YET APPROVED

این سند فقط شاخه `work/zero-data-foundation` را ارزیابی می‌کند. شواهد مربوط به Importهای قدیمی، شمارش workbookها و prereleaseهای UAT قبلی در این خط مبنای Compliance نیستند.

### اصول تثبیت‌شده

| الزام | وضعیت | شاهد / محدودیت |
|---|---|---|
| معماری بدون داده عملیاتی اولیه | PASS | Fresh migration + automated zero-row gate. |
| عدم Import Excel/CSV | PASS | Import runtime/CLI/schema حذف شده و authority workbooks داخل بسته اجرایی قرار نمی‌گیرند. |
| CommercialSpace.code یکتا و immutable | PASS | Form validation + DB trigger + automated tests. |
| MotherProperty مستقل | PASS | وابستگی اجباری به CommercialSpace وجود ندارد. |
| ورود دستی کنترل‌شده | PASS برای ماژول‌های بازطراحی‌شده | Space، MotherProperty، Beneficiary، Contract، Appraiser و Appraisal از فرم/سرویس کنترل‌شده عبور می‌کنند. |
| Audit Trail | PASS برای جریان‌های بازطراحی‌شده | ایجاد/ویرایش و رخدادهای اصلی Audit می‌شوند؛ Contract/Appraisal/Beneficiary relation دارای Timeline نیز هستند. |
| عدم overwrite تاریخچه | PASS برای قرارداد/کارشناسی/بهره‌بردار | قرارداد جدید رکورد جدید است؛ کارشناسی مرجع قبلی حفظ می‌شود؛ تغییر بهره‌بردار ارتباط قبلی را خاتمه می‌دهد. |
| قرارداد هم‌پوشان | PASS | overlap برای یک کد فضا رد می‌شود. |
| استقلال بهره‌بردار و قرارداد | PASS | BeneficiaryAssignment مستقل پیاده شده و آخرین CI پس از این تغییر باید سبز باشد. |
| کارشناسی ساختاری | PASS | Appraiser مستقل، ابلاغ 1:N، جواب و تاریخ کارشناسی مستقل، current appraisal واحد. |
| active / out-of-cycle | PASS | Viewهای جدا و نمایش current/latest context پیاده شده؛ آخرین CI باید تأیید کند. |
| Search / Filter | PARTIAL | جست‌وجوی کلیدهای اصلی توسعه یافته؛ فیلتر تخصصی همه ماژول‌ها کامل نیست. |
| Documents / FileMovement / Alerts / Workflow | EXISTING — REVIEW REQUIRED | پیاده‌سازی پایه موجود است؛ تطبیق نهایی Zero-Data/FROZEN هنوز باز است. |
| Auction / Commission | EXISTING — REVIEW REQUIRED | موتور و گردش پایه وجود دارد؛ Gate نهایی بعد از تکمیل دامنه‌های وابسته لازم است. |
| Electricity core | PASS | Bill/Allocation/Measurement، اولویت داده واقعی، محاسبه سهم‌ها، Override مجاز، کنترل درصد/ریال، Final/Reopen، Rule Registry و Snapshot نسخه‌دار روی Zero-Data تست شده‌اند. |
| Water / Gas foundation | PASS | Connection/Bill/Measurement و Audit مستقل از برق پیاده شده‌اند؛ هیچ فرمول برق به آب یا گاز اعمال نمی‌شود. |
| Water / Gas reporting and advanced filters | PENDING | گزارش‌ها، مقایسه دوره‌ای و فیلترهای تخصصی هنوز Gate نهایی نشده‌اند. |
| Official reports | REVIEW REQUIRED | موتور گزارش موجود است، ولی schema و ستون‌های جدید باید end-to-end بازآزمایی شوند. |
| Backup / Restore | REVIEW REQUIRED | سازوکار موجود است؛ بعد از تثبیت migration chain باید Regression نهایی شود. |
| Security / Auth | PASS در Quality tests | Password hashing، CSRF، throttle و user-management تست دارند. |
| Portable LAN method | FROZEN | START_SAMA/Waitress/8765 حفظ می‌شود. |
| Windows Zero-Data build | PENDING | بسته Windows جدید هنوز ساخته و UAT نشده است. |
| Owner acceptance | PENDING | فقط Owner می‌تواند UAT را تأیید کند. |
| Production/LAN-ready | NOT APPROVED | تا Windows gate + Owner UAT ممنوع است. |


## مواردی که عمداً دیگر Evidence محسوب نمی‌شوند

- شمار ۲۲۵ / ۳۵۰ / ۱۵۱ / ۵۰۱ از workbookها؛ این اعداد متعلق به مسیر Import قبلی بودند.
- RawCell / SourceFile / ImportBatch؛ از Runtime Zero-Data حذف شده‌اند.
- prerelease `v5.0.0-uat.6`؛ این بسته بر schema قبلی ساخته شده و مجوز استفاده به‌عنوان Zero-Data build ندارد.
- PR #2؛ نباید برای این مسیر Merge یا مبنای انتشار تلقی شود.

## شرط اعلام آمادگی

اعلام «LAN-ready» یا «Production-ready» فقط بعد از همه موارد زیر مجاز است:

1. تکمیل دامنه‌های FROZEN باقی‌مانده.
2. Quality Gate سبز روی head نهایی.
3. Fresh DB + migrate + zero-data assertion.
4. Backup/Restore regression.
5. Browser RTL/UAT regression.
6. Windows Portable build و تست واقعی روی Windows 10/LAN.
7. پذیرش انسانی Owner.
