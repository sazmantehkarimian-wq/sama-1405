# MD داشبورد مدیریتی نهایی — SAMA

**پروژه:** سامانه املاک سازمان فرهنگی هنری شهرداری تهران (SAMA)  
**حوزه:** Dashboard / Management Overview / Action Center / Drill-down  
**وضعیت:** `FINAL FROZEN`  
**نوع سند:** مشخصات معماری اطلاعات، KPI، فیلتر، تعامل، امنیت و تجربه کاربری داشبورد

---

# 1. هدف

Dashboard مدیریتی SAMA یک صفحه تزئینی یا مجموعه‌ای از نمودارهای مستقل نیست.

Dashboard باید:

- خلاصه وضعیت واقعی سامانه را نشان دهد؛
- موارد نیازمند اقدام را در اولویت قرار دهد؛
- هر عدد را به Dataset واقعی متصل کند؛
- از همان Report Engine مرکزی استفاده کند؛
- هیچ منطق محاسباتی جداگانه‌ای نداشته باشد؛
- مدیر را از Summary به رکورد واقعی با یک کلیک برساند.

قاعده اصلی:

```text
Dashboard
=
Presentation Layer
on top of
Central Report Engine
```

---

# 2. اصل یک Dataset

هر KPI، Chart، Warning و Drill-down باید از همان Query Definition رسمی Report Engine تغذیه شود.

مثال:

```text
قراردادهای 1 تا 90 روز مانده = 27
```

کلیک روی 27:

```text
Exactly 27 records
```

و خروجی Excel/PDF همان Dataset را منعکس می‌کند.

---

# 3. ممنوعیت KPI بدون Drill-down

هیچ کارت یا عددی در Dashboard مجاز نیست مگر اینکه:

- Query مشخص داشته باشد؛
- Dataset قابل نمایش داشته باشد؛
- صفحه Drill-down داشته باشد؛
- Permission آن مشخص باشد.

```text
DEAD_END_KPI = PROHIBITED
```

---

# 4. جایگاه Dashboard

پس از ورود به SAMA، Dashboard صفحه اصلی عملیاتی/مدیریتی است.

Dashboard جایگزین صفحات تخصصی نمی‌شود.

مسیر:

```text
Dashboard
→ Drill-down
→ List / Report
→ Record Profile
→ Allowed Action
```

---

# 5. ساختار صفحه

Dashboard در حالت Desktop از این بخش‌ها تشکیل می‌شود:

```text
1. Header / Global Scope
2. Action Center
3. Core KPI Summary
4. Auction Intelligence
5. Contracts & Appraisals
6. Space Portfolio
7. Expert Fee Status
8. Utilities & Consumption
9. Management Charts
10. Data Quality
11. Recent / Priority Activity
```


## 5.1 KPI Catalog در برابر نمای اول Dashboard

تمام KPIهای تعریف‌شده در این سند، **KPI Catalog رسمی Dashboard** هستند؛ اما همه آن‌ها نباید هم‌زمان در نمای اول نمایش داده شوند.

قاعده Presentation:

```text
Above the Fold / First View:
6–8 KPI Maximum
2–3 Meaningful Charts Maximum
```

اولویت نمای اول:

1. Action Required / Critical؛
2. Core Portfolio؛
3. Contract Risk؛
4. Appraisal Risk؛
5. Auction Intelligence.

KPIهای دیگر حذف نمی‌شوند و باید از یکی از این الگوها استفاده کنند:

- Domain Section پایین‌تر صفحه؛
- «نمایش بیشتر»؛
- Drill-down؛
- Saved Dashboard View؛
- Section قابل گسترش در صورت اثبات نیاز.

بنابراین:

```text
Approved KPI Catalog != Simultaneous KPI Cards Above the Fold
```

ممنوع:

- نمایش 20+ کارت هم‌سطح در First View؛
- چند ردیف KPI بدون hierarchy؛
- تکرار یک KPI فقط برای پرکردن Layout.


---

# 6. Header داشبورد

Header حداقل شامل:

- عنوان «سامانه جامع املاک»
- نام کاربر
- نقش
- Scope فعال
- وضعیت Current / Snapshot
- دکمه مرکز گزارش‌ها
- دکمه جست‌وجوی سراسری
- دکمه تازه‌سازی
- آخرین زمان Refresh داده

است.

---

# 7. Global Scope

Dashboard باید Global Filter داشته باشد.

فیلترهای اصلی:

- کل سازمان
- منطقه
- مرکز
- نوع/کاربری فضا
- وضعیت فضای تجاری
- بازه زمانی تحلیلی
- Current / Snapshot

این Scope بر تمام Widgetهایی که قابلیت Scope دارند اعمال می‌شود.

---

# 8. فیلتر منطقه و مرکز

قواعد Report Engine عیناً حفظ می‌شوند:

```text
ALL_CENTERS_IN_SELECTED_REGIONS
ONLY_SELECTED_CENTERS
SELECTED_REGIONS_PLUS_EXTRA_CENTERS
```

Region و Center هر دو Multi-select هستند.

---

# 9. فیلتر نوع/کاربری

Dashboard باید بتواند نمای مدیریتی را برای یک یا چند کاربری محدود کند.

مثال:

```text
کل فضاهای ورزشی سازمان
```

یا:

```text
فضاهای آموزشی در مناطق 1، 3، 5، 15
+
چند مرکز منتخب
```

---

# 10. نمایش Scope فعال

Scope باید همیشه واضح باشد.

مثال:

```text
دامنه فعال:
کاربری آموزشی
مناطق 1، 3، 5، 15
+ مراکز خاوران و معرفت
```

کاربر نباید فراموش کند که Dashboard فیلتر شده است.

---

# 11. Reset Scope

یک دکمه واضح:

```text
بازگشت به کل سازمان
```

وجود دارد.

---

# 12. Action Center

Action Center مهم‌ترین بخش بالای Dashboard است.

این بخش فقط مواردی را نشان می‌دهد که نیازمند اقدام یا بررسی هستند.

گروه‌های اصلی:

- قراردادهای نزدیک پایان
- کارشناسی‌های منقضی/نیازمند اقدام
- Candidateهای نیازمند اقدام
- Review Required مزایده
- پرونده‌های ناقص
- حق‌الزحمه‌های در دست اقدام
- Data Quality Issues
- موارد دستور مدیر/کمیسیون نیازمند پیگیری

---

# 13. ترتیب Action Center

ترتیب پیش‌فرض:

```text
Critical
High
Medium
Informational
```

Severity توسط Rule Registry / Business Rule تعریف می‌شود و از ظاهر کارت حدس زده نمی‌شود.

---

# 14. کارت‌های Action Center

هر کارت شامل:

- عنوان
- تعداد
- شرح کوتاه
- Severity
- آخرین Refresh
- Drill-down
- در صورت مجاز بودن Action Shortcut

است.

---

# 15. اقدام از روی کارت

اگر کاربر Permission داشته باشد، پس از Drill-down می‌تواند اقدام مرتبط را انجام دهد.

اما:

> Dashboard نباید مستقیماً داده را بدون مشاهده رکورد و Context تغییر دهد.

---

# 16. KPIهای اصلی Portfolio

کارت‌های پایه:

- کل فضاهای فعال
- فضاهای از دور خارج‌شده
- دارای بهره‌بردار
- فاقد بهره‌بردار
- دارای قرارداد جاری
- فاقد قرارداد جاری
- سطح جزء
- سطح متوسط
- سطح عمده

---

# 17. KPI قرارداد

کارت‌های قراردادی:

- قراردادهای جاری
- پایان امروز
- 1 تا 30 روز مانده
- 31 تا 60 روز مانده
- 61 تا 90 روز مانده
- منقضی‌شده
- قراردادهای بیش از 365 روز

این Bucketها صرفاً نمایشی هستند و Rule مزایده را بازتعریف نمی‌کنند.

---

# 18. KPI کارشناسی

کارت‌های کارشناسی:

- دارای کارشناسی
- فاقد کارشناسی
- معتبر برای مزایده
- منقضی برای مزایده
- در آستانه انقضا
- نیازمند اصلاح
- کارشناسی ثبت‌شده در بازه انتخابی

---

# 19. نمایش سوابق کارشناسی در Drill-down

از KPIهای کارشناسی، Drill-down به List می‌رود.

در لیست فضاها امکان نمایش:

```text
آخرین کارشناسی
کارشناسی قبلی 1
کارشناسی قبلی 2
```

حفظ می‌شود.

---

# 20. Auction Intelligence

Dashboard مزایده یک بخش شاخص دارد.

کارت‌های اصلی:

- Candidate
- Candidate + Action Required
- Review Required
- Ready for Auction
- Selected for Period
- AuctionLot فعال
- بدون پیشنهاد
- نتیجه ثبت‌شده
- بدون نتیجه

---

# 21. Candidate Reason Breakdown

نمایش تحلیلی:

- مسیر قرارداد
- مسیر فاقد قرارداد
- Override
- دستور مدیر
- دستور کمیسیون
- Conflict
- Data Issue

با Drill-down.

---

# 22. Shadow Mode

تا زمانی که Candidate Engine در دوره Shadow فعال است، Dashboard یک Widget مستقل دارد:

```text
Manual ∩ SAMA
Manual Only
SAMA Only
Review Required
```

False Negative احتمالی باید برجسته‌ترین وضعیت باشد.

---

# 23. Auction Period Selector

بخش مزایده باید امکان انتخاب:

- دوره جاری
- دوره قبلی
- دوره مشخص
- همه دوره‌ها

را داشته باشد.

انتخاب دوره روی Widgetهای مربوط به مزایده اعمال می‌شود، نه کل Dashboard مگر کاربر صراحتاً Global کند.

---

# 24. Expert Fee KPI

در بخش حق‌الزحمه:

- مبلغ ثبت نشده
- آماده ارسال
- ارسال‌شده به مالی
- در دست اقدام
- پرداخت‌شده
- نیازمند اصلاح
- جمع حق‌الزحمه
- جمع پرداخت‌شده
- مبلغ در انتظار پرداخت

همه با Drill-down.

---

# 25. Utility / Consumption KPI

در صورت وجود داده:

- دوره‌های ثبت‌شده
- مبلغ کل
- سهم سازمان
- سهم بهره‌برداران
- موارد دارای Override
- مغایرت
- بیشترین هزینه/مصرف بر اساس Scope

نمایش داده می‌شوند.

---

# 26. Data Quality Panel

Widget مستقل:

```text
کنترل کیفیت داده
```

شامل:

- SpaceCode تکراری
- قرارداد متناقض
- تاریخ نامعتبر
- مبلغ نامعتبر
- کارشناسی متناقض
- Missing Required Field
- Missing Rule
- Snapshot ناقص
- Conflictهای نیازمند بررسی

---

# 27. Data Quality Drill-down

هر Quality Issue باید:

- Entity
- SpaceCode
- Severity
- Rule
- Reason
- DetectedAt
- Status
- Owner/Assignee در صورت وجود

داشته باشد.

---

# 28. نمودارهای مدیریتی مجاز

حداکثر تعداد نمودارهای پیش‌فرض در صفحه اصلی باید محدود باشد.

نمودارهای مناسب:

- توزیع فضاها بر اساس منطقه
- توزیع بر اساس نوع/کاربری
- وضعیت قراردادها
- وضعیت کارشناسی
- توزیع سطح معامله
- روند Candidate / مزایده در زمان
- حق‌الزحمه به تفکیک وضعیت
- مصرف/هزینه در زمان

---

# 29. ممنوعیت Chart Decoration

Chart صرفاً برای زیبایی ممنوع است.

هر نمودار باید:

- سؤال مدیریتی مشخص را پاسخ دهد؛
- Dataset مشخص داشته باشد؛
- Drill-down داشته باشد.

---

# 30. Chart Drill-down

کلیک روی Segment نمودار:

```text
Chart Segment
→ Exact underlying records
```

مثلاً:

```text
منطقه 15 = 23 فضا
```

کلیک:

```text
23 رکورد
```

---

# 31. Trend

Trend فقط با داده تاریخی معتبر نمایش داده می‌شود.

اگر Snapshot یا تاریخچه کافی نیست:

```text
داده تاریخی کافی نیست
```

نمایش داده می‌شود.

سامانه حق ندارد روند گذشته را از Current State حدس بزند.

---

# 32. مقایسه دوره‌ای

در صورت وجود داده:

- ماه جاری vs ماه قبل
- فصل جاری vs فصل قبل
- سال جاری vs سال قبل

نمایش داده می‌شود.

---

# 33. Delta Indicator

Delta فقط وقتی نمایش داده می‌شود که مبنای مقایسه واقعی باشد.

مثال:

```text
+12%
```

بدون Baseline معتبر ممنوع است.

---

# 34. Management Summary

یک Summary مختصر مدیریتی می‌تواند شامل:

- تعداد کل موارد نیازمند اقدام
- مهم‌ترین 3 هشدار
- وضعیت مزایده
- وضعیت قراردادهای نزدیک پایان
- وضعیت کارشناسی منقضی
- وضعیت Data Quality

باشد.

این Summary باید Deterministic باشد و از Queryها تولید شود.

---

# 35. عدم تولید تفسیر حقوقی/مدیریتی خودکار

Dashboard حق ندارد:

- برنده مزایده پیشنهاد دهد؛
- تفسیر حقوقی ارائه دهد؛
- تصمیم مدیر را جایگزین کند؛
- علت ناموجود را حدس بزند.

---

# 36. Recent Activity

بخش فعالیت‌های اخیر:

- ثبت کارشناسی
- تغییر قرارداد
- تغییر Lifecycle
- ایجاد/تغییر AuctionPeriod
- ثبت نتیجه مزایده
- تغییر حق‌الزحمه
- ثبت پرداخت
- Resolve شدن Data Quality Issue

را نمایش می‌دهد.

---

# 37. Recent Activity Security

کاربر فقط فعالیت‌هایی را می‌بیند که Permission مشاهده Entity مربوط را دارد.

---

# 38. جست‌وجوی سراسری

از Dashboard جست‌وجوی:

```text
SpaceCode
نام فضا
شماره قرارداد
نام بهره‌بردار
نام کارشناس
```

در دسترس است.

---

# 39. Search Result

نتیجه Search باید دسته‌بندی‌شده باشد و کاربر را مستقیم به Record Profile ببرد.

---

# 40. Saved Dashboard View

کاربر می‌تواند Scope و Layout شخصی خود را ذخیره کند.

ذخیره می‌شود:

- Scope
- Widget visibility
- Widget order
- Chart preference
- Default report links

Business Definition کارت‌ها تغییر نمی‌کند.

---

# 41. Dashboard Default

یک Default Dashboard سازمانی وجود دارد که توسط مدیر سامانه کنترل می‌شود.

کاربر می‌تواند Layout شخصی داشته باشد اما نمی‌تواند KPI Definition رسمی را تغییر دهد.

---

# 42. Widget Visibility

Widgetها بر اساس:

- Role
- Permission
- Available Data
- Scope

نمایش داده می‌شوند.

---

# 43. Dashboard برای نقش‌های مختلف

همان Dashboard Engine استفاده می‌شود، اما ترکیب Widgetها متفاوت است.

نمونه:

## مدیر
- KPI مدیریتی
- روند
- مزایده
- قرارداد
- Data Quality

## کارشناس املاک
- Action Center
- قرارداد
- کارشناسی
- فضا
- مزایده

## کاربر کارشناسی
- کارشناسی
- کارشناسان
- حق‌الزحمه
- Action Required

Role Matrix نهایی در MD دسترسی‌ها Freeze می‌شود.

---

# 44. عدم افشای داده

Widget مخفی یا غیرمجاز فقط از UI حذف نمی‌شود.

Query آن نیز Server-side باید Block شود.

---

# 45. Zero-data State

در نسخه صفر-داده:

Dashboard باید بدون داده نیز کاملاً سالم باشد.

نمایش:

```text
0
```

و Empty State مناسب.

هیچ Sample Data در Production نمایش داده نمی‌شود.

---

# 46. Empty State

به‌جای نمودار یا کارت خراب:

```text
داده‌ای برای دامنه انتخاب‌شده ثبت نشده است.
```

نمایش داده می‌شود.

---

# 47. Error State

خطای Query نباید به‌صورت عدد صفر نمایش داده شود.

سه حالت جدا:

```text
0 Records
No Data Yet
Query/Error
```

---

# 48. Data Freshness

در Dashboard باید زمان Refresh قابل مشاهده باشد.

در صورت Cache:

```text
Data As Of
```

نمایش داده می‌شود.

---

# 49. Refresh

دو حالت:

- Refresh Widget
- Refresh Dashboard

وجود دارد.

Refresh نباید Scope را Reset کند.

---

# 50. Performance

Dashboard نباید برای Load اولیه همه Datasetها را کامل دریافت کند.

الگوی:

```text
Summary Query
→ Lazy Detail
→ Drill-down on demand
```

است.

---

# 51. Query Budget

Widgetهای Dashboard Queryهای کنترل‌شده و Index-friendly دارند.

Query آزاد و سنگین در Dashboard ممنوع است.

---

# 52. Pagination

Drill-down Listها Page-based هستند.

Dashboard هیچ‌وقت هزاران رکورد را مستقیم داخل Widget Render نمی‌کند.

---

# 53. Export از Dashboard

برای Widgetهای مجاز:

```text
Excel
PDF / Print
```

از همان Dataset/Scope موجود قابل تولید است.

---

# 54. Dashboard Snapshot

مدیر می‌تواند وضعیت Dashboard را به‌عنوان Snapshot مدیریتی Freeze کند.

Snapshot شامل:

- Scope
- KPI values
- Query definitions
- Dataset hashes
- GeneratedAt
- GeneratedBy

است.

---

# 55. چاپ Dashboard

نسخه Print Dashboard باید:

- ساده
- رسمی
- کم‌مصرف
- بدون پس‌زمینه سنگین
- با لوگوی رسمی
- با Scope فعال
- با تاریخ Snapshot/گزارش
- با نمودارهای قابل چاپ سیاه‌وسفید

باشد.

---

# 56. عدم چاپ UI

در Print:

- Sidebar
- Button
- Search box
- Interactive controls

چاپ نمی‌شوند.

---

# 57. طراحی بصری

جهت کلی:

```text
Modern
Minimal
Data-first
Professional
Non-generic administrative UI
```

Dashboard نباید شبیه قالب‌های تکراری داشبورد اداری یا خروجی خام AI باشد.

---

# 58. اولویت بصری

ترتیب اهمیت:

```text
Action Required
→ Core KPI
→ Auction
→ Contracts / Appraisal
→ Portfolio
→ Analytical Charts
→ Secondary Information
```

---

# 59. رنگ

رنگ برای معنا استفاده می‌شود، نه تزئین.

- Error / Critical
- Warning
- Success
- Neutral
- Informational

Contrast باید بالا باشد.

رنگ تنها عامل انتقال معنا نیست؛ Icon/Label نیز لازم است.

---

# 60. کارت‌ها

کارت‌ها:

- ساده
- بدون Glow سنگین
- بدون Gradient آزاردهنده
- بدون Shadow زیاد
- دارای عدد خوانا
- Label کوتاه
- Click affordance واضح

هستند.

---

# 61. فونت و خوانایی

- فارسی‌خوان
- RTL
- عددهای KPI بزرگ و خوانا
- Label با Contrast مناسب
- متن روی زمینه تیره باید کاملاً خوانا باشد

---

# 62. جدول Drill-down

جدول‌ها:

- داخل Viewport
- بدون خروج از سمت چپ
- دارای Horizontal Scroll کنترل‌شده در صورت نیاز
- Sticky Header
- ستون‌های قابل انتخاب
- Responsive

هستند.

---

# 63. Navigation

بازگشت از Drill-down به Dashboard باید Scope قبلی را حفظ کند.

---

# 64. Deep Link

هر Widget/Drill-down می‌تواند URL قابل Bookmark داشته باشد که Scope و Query Definition را بازسازی کند، بدون قرار دادن داده حساس در URL.

---

# 65. Mobile / Tablet

اولویت اصلی Desktop/LAN است.

اما Layout باید Responsive باشد و در Tablet قابل استفاده باشد.

در Mobile:

- Widgetها Stack می‌شوند؛
- جدول به List/Scroll مناسب تبدیل می‌شود؛
- قابلیت اصلی از بین نمی‌رود.

---

# 66. Accessibility

حداقل:

- Keyboard Navigation
- Focus State
- Contrast
- Label غیررنگی
- Tooltip برای Icon
- متن جایگزین برای Chart

رعایت می‌شود.

---

# 67. Audit

رخدادهای مهم Dashboard که ثبت می‌شوند:

- Snapshot creation
- Sensitive export
- Saved View creation/change
- Admin default-layout change

صرف مشاهده Dashboard به‌طور معمول Audit سنگین ایجاد نمی‌کند مگر Policy امنیتی آینده الزام کند.

---

# 68. Dashboard Admin

مدیر سامانه می‌تواند:

- Default Widget Order
- Default Visibility
- Widget Titles
- Scope Defaults
- Allowed Charts

را تنظیم کند.

اما Query Definitionهای Business فقط از طریق Change Request/Release تغییر می‌کنند.

---

# 69. عدم تغییر Business Rule از Dashboard

Dashboard محل ویرایش:

- Rule مزایده
- اعتبار کارشناسی
- سطح معاملات
- Thresholdها

نیست.

فقط Result آنها را نمایش می‌دهد.

---

# 70. Explainability

برای KPIهای Rule-based مانند Candidate:

دکمه/لینک:

```text
چرا؟
```

باید Explainability View را باز کند.

---

# 71. Dashboard و Report Engine

هر Widget دارای:

```text
WidgetID
ReportDefinitionID
QueryVersion
PermissionKey
DrilldownRoute
ScopeSupport
RefreshPolicy
```

است.

---

# 72. Versioning

تغییر معنی KPI:

```text
NEW QUERY VERSION
```

می‌خواهد.

عددهای تاریخی باید با QueryVersion خود قابل تفسیر باشند.

---

# 73. معیار پذیرش Dashboard

Dashboard فقط زمانی پذیرفته می‌شود که:

```text
KPI / Drill-down mismatch = 0
Chart / Drill-down mismatch = 0
Unauthorized query = 0
Dead-end KPI = 0
Silent error shown as zero = 0
Horizontal layout break = 0
Unreadable low-contrast text = 0
Sample production data = 0
```

---

# 74. تصمیم‌های نهایی FROZEN

1. Dashboard روی Report Engine مرکزی ساخته می‌شود.
2. Dashboard منطق داده مستقل ندارد.
3. همه KPIها Drill-down دارند.
4. Action Center در بالاترین اولویت است.
5. Global Scope شامل Region/Center/Usage است.
6. Multi-select منطقه و مرکز پشتیبانی می‌شود.
7. سه Mode ترکیب Region/Center حفظ می‌شود.
8. Scope فعال همیشه واضح نمایش داده می‌شود.
9. KPIهای فضا، قرارداد، کارشناسی، مزایده، حق‌الزحمه، مصرف و Data Quality وجود دارند.
10. Candidate Engine یک بخش مدیریتی ویژه دارد.
11. Shadow Mode تا زمان خاتمه رسمی قابل نمایش است.
12. نمودار فقط در صورت ارزش مدیریتی استفاده می‌شود.
13. هر Segment نمودار Drill-down دارد.
14. Trend فقط از تاریخچه معتبر ساخته می‌شود.
15. Delta بدون Baseline واقعی نمایش داده نمی‌شود.
16. Dashboard تصمیم حقوقی یا برنده مزایده تولید نمی‌کند.
17. Saved Dashboard View برای کاربر مجاز است.
18. KPI Definition رسمی توسط کاربر تغییر نمی‌کند.
19. امنیت Query Server-side است.
20. Zero-data State بخشی از طراحی رسمی است.
21. Error و Empty و Zero سه وضعیت جدا هستند.
22. Print Dashboard ساده، رسمی و کم‌مصرف است.
23. نسخه چاپی UI Controls ندارد.
24. طراحی مدرن، مینیمال و Data-first است.
25. Contrast و خوانایی الزامی است.
26. جدول‌های Drill-down نباید از قاب خارج شوند.
27. Scope هنگام رفت‌وبرگشت حفظ می‌شود.
28. Dashboard Snapshot برای گزارش مدیریتی ثابت پشتیبانی می‌شود.
29. هر Widget به ReportDefinition و QueryVersion رسمی متصل است.
30. تغییر معنای KPI نیازمند Version جدید است.
31. کل KPI Catalog می‌تواند گسترده باشد، اما First View حداکثر 6–8 KPI دارد.
32. First View حداکثر 2–3 نمودار معنادار دارد.
33. KPIهای خارج First View باید با Domain Section، نمایش بیشتر یا Drill-down سازمان‌دهی شوند.

---

# 75. وضعیت سند

```text
FINAL FROZEN
```

هر تغییر آینده فقط از مسیر:

```text
CHANGE REQUEST
→ REVIEW
→ APPROVED
→ FROZEN
```

مجاز است.

---

**پایان سند — MD داشبورد مدیریتی نهایی — SAMA**
