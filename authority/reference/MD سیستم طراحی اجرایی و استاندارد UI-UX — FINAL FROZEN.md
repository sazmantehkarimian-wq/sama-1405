# MD سیستم طراحی اجرایی و استاندارد UI/UX — SAMA

**پروژه:** سامانه املاک سازمان فرهنگی هنری شهرداری تهران (SAMA)  
**حوزه:** Executive Design System / UI Patterns / Components / Layout / Typography / Interaction  
**وضعیت:** `FINAL FROZEN`  
**وابستگی:** `MD نظام رنگ، پالت ماژول‌ها و هویت بصری — FINAL FROZEN`  
**هدف:** تبدیل معماری، رنگ‌ها و قواعد تأییدشده SAMA به یک سیستم طراحی واقعی، قابل پیاده‌سازی، مینیمال، حرفه‌ای و غیرکلیشه‌ای.

---

# 1. مأموریت طراحی

SAMA باید شبیه یک **محصول Enterprise واقعی** باشد؛ نه شبیه:

- داشبوردهای قالب‌آماده؛
- خروجی‌های رایج هوش مصنوعی؛
- پنل‌های پر از Card و Gradient؛
- سامانه‌های اداری قدیمی و سنگین؛
- رابط‌های نمایشی که در استفاده روزمره کند و خسته‌کننده‌اند.

هدف نهایی:

```text
Professional
Minimal
Data-first
RTL-native
High-legibility
Fast
Consistent
Distinctive
Enterprise-grade
```

---

# 2. منابع مرجع طراحی

قواعد این سند با مطالعه و تطبیق اصول سیستم‌های طراحی معتبر و به‌روز تدوین شده است:

- Microsoft Fluent 2
- IBM Carbon Design System
- Atlassian Design System
- Radix Themes / Radix UI
- اصول Accessibility مبتنی بر WCAG
- Vazirmatn برای تایپوگرافی فارسی وب

SAMA هیچ‌یک از این سیستم‌ها را Copy نمی‌کند؛ از قواعد اثبات‌شده آن‌ها برای ساخت هویت مستقل خود استفاده می‌کند.

---

# 3. قاعده اصلی ضد «AI-look»

## 3.1 موارد ممنوع

این موارد در UI نهایی SAMA ممنوع هستند:

- Card Soup؛ تبدیل هر داده به یک کارت جداگانه
- Gradient چندرنگ و تزئینی
- Glow و Neon
- سایه‌های سنگین و بزرگ
- Glassmorphism در کل صفحه
- Radius بسیار بزرگ روی همه اجزا
- Pill Button برای همه عملیات
- آیکون‌های بزرگ صرفاً تزئینی
- Hero Illustration بدون ارزش عملیاتی
- تصویرسازی/عکس مصنوعی در صفحات کاری
- Dashboard پر از Donut و Pie Chart
- نمودار سه‌بعدی
- رنگ‌های تصادفی برای KPI
- متن کم‌رنگ و کم‌کنتراست
- فضای خالی اغراق‌شده در صفحات داده‌محور
- دکمه‌های رنگی متعدد در یک ردیف جدول
- فرم‌های بزرگ داخل Modal
- استفاده از Patternهای تزئینی در فضای داده
- یک Radius واحد روی همه Components
- ترکیب هم‌زمان چند Accent در یک صفحه
- UI بیش از حد «نمایشی» به قیمت کاهش سرعت کار

---

# 4. امضای بصری SAMA

هویت SAMA از چهار عنصر ساخته می‌شود:

```text
Clean Neutral Surface
+ Domain Accent
+ Strong Typography
+ Precise Grid
```

امضای اختصاصی پیشنهادی:

1. نوار Accent باریک 3px یا 4px در Header ماژول
2. عنوان صفحه ساده و پرقدرت، بدون Hero Card
3. Command Row واضح و خطی
4. جدول‌ها و فهرست‌ها به‌عنوان عنصر اصلی
5. رنگ ماژول فقط در نقاط کنترلی
6. Borderهای دقیق و کم‌رنگ
7. Shadow بسیار محدود
8. Header پرونده‌ها با ساختار فشرده و اطلاعاتی

---

# 5. معماری صفحه

الگوی عمومی:

```text
Global Shell
→ Page Header
→ Context / Breadcrumb
→ Command Bar
→ Filters / Scope
→ Main Data Surface
→ Contextual Detail
```

صفحات نباید با چند ردیف Card شروع شوند مگر Dashboard.

---

# 6. Global Shell

## 6.1 Sidebar

RTL و در سمت راست.

Desktop Expanded:

```text
Width: 236px
```

Collapsed:

```text
Width: 64px
```

قواعد:

- Icon + Label
- Active item با Accent ماژول
- هیچ Gradient در Sidebar
- حداکثر یک سطح Sub-navigation باز
- زیرمنوی عمیق‌تر از دو Level ممنوع
- Divider محدود
- Settings و Logout در پایین

---

## 6.2 Top Bar

```text
Height: 56px
```

شامل:

- Global Search
- Scope indicator
- Notification
- User profile
- Context utility actions

Top Bar نباید محل انباشتن Actionهای ماژول باشد.

---

# 7. Grid

Desktop:

```text
12-column responsive grid
```

Margins:

```text
≥ 1440px : 24px
1280–1439: 20px
1024–1279: 16px
```

Gutter:

```text
16px / 20px / 24px
```

Page content نباید بدون Grid به لبه مرورگر بچسبد.

---

# 8. Spacing System

SAMA از Scale محدود استفاده می‌کند:

```text
4
8
12
16
20
24
32
40
48
64
```

Base Rhythm:

```text
4px
```

قواعد رایج:

```text
Icon ↔ Label            8px
Field label ↔ Input     8px
Related Controls        12–16px
Form Fields             24px
Section separation      32px
Major Page Sections     40–48px
```

---

# 9. Typography

## 9.1 UI

فونت اصلی رابط فارسی:

```text
Vazirmatn
```

Fallback:

```text
Tahoma
Segoe UI
system-ui
sans-serif
```

Vazirmatn در نسخه LAN باید به‌صورت Local Asset بسته‌بندی شود و به اینترنت وابسته نباشد.

قاعده مجوز و استقرار:

- Production UI نباید به فونت تجاری یا دارای محدودیت مجوز وابسته باشد.
- فونت اصلی UI فقط از Asset محلی بسته سامانه بارگذاری می‌شود.
- فونت Yekan جزو Production Baseline نیست.
- نبود اینترنت نباید روی Typography اثر بگذارد.

## 9.2 چاپ رسمی

قواعد قبلی حفظ می‌شوند:

```text
Title: B Titr
Body: B Nazanin
```

UI و Print دو سیستم تایپوگرافی جدا هستند.

---


# 9.3 نظام ارقام، جهت و Alignment

## 9.3.1 ارقام نمایشی UI

تمام اعداد کاربرمحور در UI با **ارقام فارسی** نمایش داده می‌شوند:

```text
۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹
```

شامل:

- KPI و شمارنده‌ها؛
- مبلغ؛
- درصد؛
- تاریخ شمسی؛
- شماره صفحه؛
- تعداد نتایج؛
- اعداد نمایشی جدول‌ها و فرم‌ها.

این Rule فقط Presentation است؛ مقدار عددی در Data Model همچنان Numeric واقعی باقی می‌ماند.

## 9.3.2 استثناهای ارقام لاتین

مقادیر Machine-readable و Reference ID به صورت لاتین حفظ می‌شوند:

```text
EXP-000001
CON-000145
PAY-1405-001
SHA-256
FileName
Hash
Technical Identifier
```

این مقادیر نباید به ارقام فارسی تبدیل شوند.

## 9.3.3 Alignment رسمی

```text
متن فارسی                  → Right
مبلغ و عدد نمایشی           → Right
تاریخ شمسی                  → Right
Reference/System ID         → LTR + Left در سلول/فیلد خودش
Hash / Technical Value      → LTR
```

قواعد تکمیلی:

- مبلغ‌ها با جداکننده هزارگان نمایش داده می‌شوند.
- ستون مبلغ و عدد بی‌دلیل Center نمی‌شود.
- Alignment یک ستون در تمام Table ثابت می‌ماند.
- Mixed RTL/LTR باید بدون به‌هم‌ریختگی Visual Order رندر شود.


# 10. Type Scale

```text
Display / rare          32px / 44
Page Title              24px / 34 / 700
Section Title           18px / 28 / 600
Card/KPI number         28–32px / 38 / 700
Body                    14px / 22 / 400
Table                   13–14px / 20
Button                  14px / 20 / 500
Label                   12–13px / 18 / 500
Helper                  12px / 18
```

تیترهای 40–60px در محیط کاری SAMA استفاده نمی‌شوند.

---

# 11. متن و Microcopy

- کوتاه
- مستقیم
- بدون جملات نمایشی
- بدون علامت تعجب غیرضروری
- Labelها ترجیحاً 1 تا 3 کلمه
- Button با فعل روشن
- «ثبت»
- «ذخیره»
- «مشاهده»
- «ویرایش»
- «بازگشت»
- «خروجی Excel»

ممنوع:

```text
اینجا کلیک کنید
عملیات موفق بود
در صورت تمایل...
```

نمونه صحیح:

```text
کارشناسی ثبت شد
قرارداد ذخیره شد
۱۲ رکورد به مالی ارسال شد
```

---

# 12. Density

SAMA دو Density دارد:

## Comfortable

پیش‌فرض.

```text
Input height      44px
Button height     40–44px
Table row         44px
Toolbar           44px
```

## Compact

برای کاربر حرفه‌ای و جدول‌های پرتراکم.

```text
Input height      36–40px
Button height     36px
Table row         36px
Toolbar           40px
```

Preference برای User ذخیره می‌شود.

---

# 13. Radius

پالت Radius محدود:

```text
4px  → Table cells / badges
6px  → Inputs
8px  → Buttons / compact surfaces
10px → Cards / panels
12px → Dialog / Drawer / major surfaces
16px → فقط Login یا Hero-level surfaces محدود
```

Radiusهای 20–32px در صفحات کاری ممنوع.

Pill فقط برای:

- Status
- Tag
- Toggle-like control

نه Buttonهای اصلی.

---

# 14. Borders

Default:

```text
1px solid neutral-border
```

Focus:

```text
2px accent
```

Selected:

```text
1px accent
+ subtle background tint
```

استفاده از Border به Shadow ترجیح دارد.

---

# 15. Shadows

Shadow فقط برای لایه‌های شناور:

```text
Dropdown
Popover
Dialog
Drawer
Toast
```

سطوح معمول صفحه Shadow سنگین ندارند.

Suggested:

```text
Level 1: 0 1px 2px rgba(...)
Level 2: 0 4px 12px rgba(...)
Level 3: 0 10px 30px rgba(...)  فقط Dialog
```

---

# 16. Glass

Glass فقط در:

- Login
- Overlay محدود
- Popover خاص
- Command overlay

استفاده می‌شود.

در Table، Form، Dashboard Card و Main Surface ممنوع است.

---

# 17. Buttons

انواع:

```text
Primary
Secondary
Tertiary
Danger
Icon Button
```

در یک Context فقط یک Primary Action.

مثال:

```text
[ثبت کارشناسی] Primary
[انصراف] Secondary
```

ممنوع:

- سه Primary Button کنار هم
- دکمه‌های رنگارنگ
- Button با Icon بدون Tooltip
- CTA بزرگ برای Action کم‌اهمیت

---

# 18. Inputs

هر Input باید Label داشته باشد.

ساختار:

```text
Label
Input
Helper / Error
```

قواعد:

- Placeholder جای Label را نمی‌گیرد
- Input بی‌دلیل Full-width نمی‌شود
- نوع Field متناسب با داده
- Select برای داده‌های محدود
- Text input فقط برای Free-form
- Error دقیق و نزدیک Field
- Focus واضح

---

# 19. Money Input

برای مبالغ:

```text
350,000,000
```

Formatting هنگام تایپ.

Data Storage:

```text
Raw Numeric Value
```

UI:

```text
Formatted Display
```

Helper اختیاری:

```text
سیصد و پنجاه میلیون ریال
```

در نقاط حساس فعال می‌شود.

---

# 20. Date Input

- تاریخ شمسی
- Calendar رسمی
- تایپ دستی کنترل‌شده
- Mask مشخص
- Validation واقعی
- عدم استفاده از Date Placeholder مبهم

---

# 21. Forms

اولویت:

```text
Single-column logical flow
```

دو ستون فقط وقتی Fieldها رابطه روشن دارند.

مثال صحیح:

```text
شماره قرارداد | تاریخ قرارداد
```

فرم‌ها Section-based:

```text
اطلاعات عمومی
اطلاعات قراردادی
اطلاعات مالی
اسناد
```

اطلاعات مالی از عمومی کاملاً جداست.

---

# 22. Modal vs Page vs Drawer

## Modal

فقط:

- Confirm
- فرم کوتاه
- Action محدود

## Drawer

برای:

- Quick View
- Context Detail
- Preview
- Filter advanced

## Full Page

برای:

- ثبت کارشناسی
- قرارداد
- مزایده
- پرونده کامل
- فرم‌های چندبخشی

---

# 23. Tables

Table عنصر اصلی SAMA است.

Standard:

- RTL
- Sticky Header
- Sort
- Filter
- Search
- Pagination
- Column visibility
- Controlled resize
- Horizontal scroll
- Pinned identity columns
- Hover
- Selected row
- Keyboard navigation

---

# 24. Table Dimensions

Comfortable:

```text
Header: 40px
Row:    44px
```

Compact:

```text
Header: 36px
Row:    36px
```

Cell horizontal padding:

```text
12–16px
```

---

# 25. Table Actions

در هر Row:

```text
مشاهده
⋮
```

سه‌نقطه:

- ویرایش
- تاریخچه
- اسناد
- Actionهای Contextual

ممنوع:

```text
[مشاهده] [ویرایش] [حذف] [اسناد] [چاپ] [تاریخچه]
```

در هر ردیف.

---

# 26. Sticky Identity Columns

در جدول‌های عریض:

```text
کد فضا
نام فضا
```

می‌توانند Sticky باشند.

سمت مقابل:

```text
Actions
```

در صورت نیاز Sticky.

---

# 27. Long Tables

برای داده زیاد:

- Pagination سروری
- Filter سروری
- Sort سروری
- Virtualization فقط در Use-caseهای مناسب
- Loading incremental
- Export مستقل از Pagination

---

# 28. Filter Bar

ساختار:

```text
Search
Primary filters
More filters
Reset
Saved view
```

Filter Bar در یک خط در Desktop.

Advanced Filter در Drawer.

Filter Chip فقط برای نشان‌دادن Filter فعال.

---

# 29. KPI Cards

KPI Card باید Information-first باشد.

ساختار:

```text
Title
Number
Small context
Drilldown cue
```

قواعد:

- Icon کوچک
- Accent line یا small indicator
- بدون Gradient
- بدون تصویر تزئینی
- بدون Shadow بزرگ
- clickable فقط اگر Drilldown واقعی دارد

---

# 30. Dashboard

ترتیب:

```text
Action Center
Core KPI
Auction Intelligence
Contracts / Appraisal
Portfolio
DQ
Charts
Recent Activity
```

در First View / Above the Fold حداکثر:

```text
6–8 KPI
2–3 meaningful charts
```

این سقف فقط برای **نمای اول** است و به معنی حذف KPIهای مصوب Dashboard نیست.
KPIهای دیگر باید پایین‌تر صفحه، در Domain Section، «نمایش بیشتر» یا Drill-down سازمان‌دهی شوند.

نه 20 کارت هم‌سطح در نمای اول.

---

# 31. Charts

Allowed:

- Bar
- Line
- Area محدود
- Stacked Bar
- Donut فقط برای composition ساده
- Trend Sparkline

Avoid:

- 3D
- Gauge نمایشی
- Radar
- چند Donut کنار هم
- نمودار با بیش از 5 سری اصلی

Chart همیشه باید Tooltip، Label یا Legend واضح داشته باشد.

---

# 32. Status Badges

Badge فقط برای Status.

ساختار:

```text
● فعال
● در دست اقدام
● منقضی
● نیازمند بررسی
```

Color تنها حامل معنا نیست.

---

# 33. Tabs

برای Profileها:

```text
Summary
Domain Tabs
History
```

Active Tab:

- Accent color
- 2px underline یا edge
- بدون Filled Pill بزرگ

---

# 34. Profile Header

پرونده‌ها با Header فشرده شروع می‌شوند:

```text
کد / عنوان
Status
Key Facts
Primary Action
Context Actions
```

نه Banner بزرگ.

---

# 35. Breadcrumb

کوچک، کم‌رنگ ولی خوانا:

```text
فضاهای تجاری / فعال / کد 378
```

در یک خط.

---

# 36. Search

Global Search:

```text
کد فضا
نام فضا
قرارداد
بهره‌بردار
کارشناس
```

Search field در Header.

Scoped Search صفحه کد فضا مستقل باقی می‌ماند.

---

# 37. Empty State

بدون Illustration بزرگ.

مثال:

```text
هنوز کارشناسی ثبت نشده است
[ثبت کارشناسی]
```

Icon ساده در صورت نیاز.

---

# 38. Loading

Table:

```text
Skeleton Rows
```

Page:

```text
Skeleton Blocks
```

Spinner فقط برای Action کوتاه و Local.

---

# 39. Error

Error باید:

- واضح
- قابل اقدام
- Contextual

باشد.

مثال:

```text
داده‌های قرارداد دریافت نشد
[تلاش مجدد]
```

---

# 40. Toast

حداکثر 1–2 خط.

Timeout منطقی.

Action اختیاری:

```text
بازگردانی
مشاهده
```

---

# 41. Confirmation

Confirmation فقط برای عملیات:

- غیرقابل بازگشت
- حساس
- Finalization
- Lifecycle change
- Result registration
- Password reset

برای Save عادی Confirm ممنوع.

---

# 42. Accessibility

حداقل:

```text
Text contrast       4.5:1
Large text          3:1
Interactive UI      3:1
```

- Focus visible
- Keyboard accessible
- Label برای Input
- Tooltip برای Icon
- Heading hierarchy
- Color + Text/Icon
- Zoom-safe
- Tab order منطقی

Interactive target ترجیحاً حداقل:

```text
44×44px
```

در Comfortable Mode.

---

# 43. RTL

SAMA از ابتدا RTL-native است.

نه LTR UI که Mirror شده باشد.

قواعد:

- Sidebar راست
- Labelها راست
- Numeric data بسته به نوع داده
- Icon direction بررسی شود
- Arrow meaning مطابق Navigation
- Table hierarchy RTL
- Date/Money alignment تعریف‌شده

---

# 44. Responsive

Priority:

```text
1920×1080
1366×768
1280×720
```

Tablet:

Secondary.

Mobile:

Read / light action priority.

Breakpoints:

```text
≥1440 Large Desktop
1280–1439 Desktop
1024–1279 Compact Desktop
768–1023 Tablet
<768 Mobile
```

---

# 45. 1366×768 Acceptance

تمام صفحات اصلی باید در 1366×768:

- Page Title دیده شود
- Filter قابل استفاده باشد
- Table Header دیده شود
- Primary Action خارج Viewport نباشد
- Sidebar قابل Collapse باشد
- Horizontal clipping کنترل شود

---

# 46. Print vs Screen

Screen Design هرگز مستقیم Print نمی‌شود.

Print دارای Template مستقل است.

Screen:

```text
interactive
responsive
accent-based
```

Print:

```text
official
bordered
low-toner
high-legibility
black/white safe
```

---

# 47. Icons

یک خانواده Icon واحد.

ویژگی:

- Outline
- Stroke consistent
- 16 / 20 / 24px
- بدون Emoji
- بدون ترکیب چند Style

آیکون تزئینی بزرگ ممنوع.

---

# 48. Images

در Workspace عادی:

```text
No decorative stock imagery
No AI-generated business imagery
```

قاعده قطعی CommercialSpace:

```text
NO PHOTO FIELD
NO GALLERY
```

- CommercialSpace هیچ فیلد عکس، تصویر اصلی یا Gallery ندارد.
- عکس فضای تجاری در Database ذخیره نمی‌شود.
- صفحه پرونده فضا نباید Photo/Gallery Component داشته باشد.
- Scan یا تصویرِ خودِ یک سند، فقط در Document Viewer همان سند مجاز است و «عکس فضا» محسوب نمی‌شود.

استثنای PowerPoint مزایده:

- Template پاورپوینت می‌تواند برای هر Slide یک **Image Placeholder اختیاری** داشته باشد.
- Placeholder به هیچ Field در Data Model متصل نیست.
- کاربر بعد از تولید PowerPoint می‌تواند تصویر را به‌صورت دستی وارد کند.
- نبود تصویر نباید تولید یا اعتبار Slide را Block کند.

Login می‌تواند Background کنترل‌شده داشته باشد؛ طراحی نهایی Login در مرحله UI Reference جداگانه تأیید می‌شود.

---

# 49. Logo

فقط Asset رسمی سازمان.

ممنوع:

- بازطراحی لوگو
- تولید لوگوی جایگزین
- تایپ مجدد نوشته زیر لوگو
- تغییر نسبت
- تغییر رنگ بدون Rule

---

# 50. Module Accent Transition

Global Shell:

```text
آجری دودی
```

وقتی Domain فعال است:

```text
Active nav
Page accent
Primary action
Focus
```

از رنگ Domain استفاده می‌کند.

کل Sidebar رنگ Domain نمی‌شود.

---

# 51. Data-first Rule

در صفحات عملیاتی اولویت:

```text
Data > Decoration
Action > Illustration
Structure > Effect
Legibility > Novelty
```

---

# 52. Signature Screens برای تست Design System

قبل از شروع تولید انبوه UI، این صفحات باید High-Fidelity ساخته و تأیید شوند:

1. Login
2. Dashboard
3. Active Spaces List
4. Space 360 Profile
5. Contract List + Contract Form
6. Appraisal List + Appraisal Form
7. Auction Candidate Engine
8. Auction Period / Lot
9. Report Builder
10. Settings / Users

این 10 صفحه Reference Implementation کل Design System هستند.

---

# 53. Anti-AI Acceptance Checklist

هر صفحه قبل از تأیید باید این Check را پاس کند:

```text
[ ] آیا بیش از حد Card دارد؟
[ ] آیا Gradient غیرضروری دارد؟
[ ] آیا Radiusها بیش از حد بزرگ‌اند؟
[ ] آیا Icon تزئینی بدون کاربرد دارد؟
[ ] آیا Shadow سنگین دارد؟
[ ] آیا بخش مهمی فقط با رنگ معنی می‌شود؟
[ ] آیا Table یا Form قربانی زیبایی شده؟
[ ] آیا Layout شبیه قالب‌های SaaS عمومی است؟
[ ] آیا تصویر غیرواقعی/تزئینی دارد؟
[ ] آیا Primary Action بیش از یکی است؟
[ ] آیا فضای خالی غیرمنطقی دارد؟
[ ] آیا در 1366×768 قابل استفاده است؟
```

اگر پاسخ هر یک از موارد مسئله‌دار باشد، UI باید اصلاح شود.

---

# 54. Design Tokens

حداقل Tokenها:

```text
color.*
space.*
radius.*
shadow.*
font.*
line-height.*
border.*
size.*
z-index.*
motion.*
```

هیچ Developer مجاز نیست:

```text
random hex
random spacing
random radius
random shadow
```

مستقیماً در Page تعریف کند.

---

# 55. Motion

Animation محدود:

```text
120–180ms
```

برای:

- Hover
- Drawer
- Dropdown
- Tab
- Toast

Animation نمایشی یا طولانی ممنوع.

---

# 56. Performance Rule

- Blur بزرگ در کل Viewport ممنوع
- Shadow زیاد ممنوع
- Chart سنگین بدون Lazy Load ممنوع
- Table Client-side عظیم ممنوع
- Assetهای بصری باید Local و بهینه باشند

---

# 57. Browser / LAN

Target:

```text
Chrome
Edge
LAN
No installation
```

Design نباید به API یا CDN خارجی وابسته باشد.

---

# 58. Zero-data

تمام Componentها باید Zero-data را پشتیبانی کنند.

Production:

```text
Sample Data = 0
```

---

# 59. Error ≠ Empty

سیستم باید تفاوت بصری واضح داشته باشد:

```text
Zero Records
No Matching Result
Loading
Error
Permission Denied
Read-only
```

---

# 60. قواعد نهایی FROZEN

1. SAMA یک Design System واحد دارد.
2. هر Domain فقط Accent هویتی خود را دارد.
3. UI Data-first است.
4. Table مهم‌ترین Component عملیاتی است.
5. Card فقط برای Summary و KPI استفاده می‌شود.
6. فرم بزرگ Modal نیست.
7. Global Shell ساده و خنثی است.
8. تم عمومی آجری دودی حفظ می‌شود.
9. رنگ‌های Domain مطابق MD رنگ نهایی هستند.
10. Vazirmatn فونت اصلی UI است.
11. Print از UI جدا است.
12. Spacing محدود و Tokenized است.
13. Radius متوسط و کنترل‌شده است.
14. Shadow حداقلی است.
15. Glass فقط محدود و هدفمند است.
16. Gradient تزئینی ممنوع است.
17. Decorative AI imagery ممنوع است.
18. Componentها باید RTL-native باشند.
19. Comfortable و Compact هر دو پشتیبانی می‌شوند.
20. Accessibility بخشی از Definition of Done است.
21. Desktop/LAN اولویت اصلی است.
22. 1366×768 باید First-class باشد.
23. 10 Reference Screen قبل از تولید انبوه تأیید می‌شوند.
24. هر صفحه Anti-AI Checklist را پاس می‌کند.
25. تغییر بنیادین این سند فقط با Change Request مجاز است.
26. اعداد کاربرمحور UI با ارقام فارسی نمایش داده می‌شوند؛ شناسه‌های سیستمی و Machine-readable لاتین می‌مانند.
27. Alignment عدد، مبلغ، تاریخ و Reference ID مطابق §9.3 الزامی است.
28. CommercialSpace هیچ Photo/Gallery Field ندارد.
29. عکس در PowerPoint مزایده فقط Manual Image Placeholder اختیاری است و جزو Data Model نیست.
30. سقف 6–8 KPI و 2–3 Chart مربوط به First View Dashboard است، نه کل KPI Catalog.

---

# 61. وضعیت سند

```text
FINAL FROZEN
```

Calibration محدود در پیاده‌سازی واقعی برای:

- Contrast
- exact spacing
- text fit
- browser rendering
- performance

مجاز است، اما تغییر زبان طراحی، پالت، ساختار یا Component philosophy بدون Change Request ممنوع است.

---

**پایان سند — MD سیستم طراحی اجرایی و استاندارد UI/UX — SAMA**
