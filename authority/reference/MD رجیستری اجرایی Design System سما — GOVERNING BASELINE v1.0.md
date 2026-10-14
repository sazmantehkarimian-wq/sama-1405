# MD رجیستری اجرایی Design System سما — GOVERNING BASELINE v1.0

**پروژه:** سما  
**حوزه:** Design System Governance / Component Registry / UI Contract / Report Contract  
**وضعیت:** `APPROVED GOVERNING BASELINE`  
**نوع سند:** Delta تکمیلی و الزام‌آور  
**مرجع بالادست:** `MD سیستم طراحی اجرایی و استاندارد UI-UX — FINAL FROZEN`  
**مرجع رنگ:** `MD نظام رنگ، پالت ماژول‌ها و هویت بصری — FINAL FROZEN`  

> این سند هیچ تصمیم FROZEN قبلی را لغو نمی‌کند. هدف آن تبدیل قواعد موجود به یک «قرارداد اجرایی کددار» است تا هر جزء UI، هر Pattern، هر صفحه و هر خروجی دقیقاً معلوم باشد از کدام منبع رسمی تأمین می‌شود.

---

# 1. اصل حاکم: Single Source of Truth

در سما هیچ Component، Pattern، Style، Table، Button، Form، Card، Title، Search، Filter، Modal، PDF، Excel یا Print نباید به‌صورت محلی و سلیقه‌ای در یک صفحه ساخته شود.

هر چیزی که کاربر می‌بیند باید یکی از این حالت‌ها را داشته باشد:

1. کد رسمی Design System داشته باشد؛
2. از Pattern رسمی استفاده کند؛
3. از Page Template رسمی استفاده کند؛
4. از Report Template رسمی استفاده کند؛
5. اگر هیچ‌کدام مناسب نبودند، ابتدا Variant جدید در Design System تعریف و تأیید شود و سپس در صفحه مصرف شود.

قاعده رسمی:

```text
NO LOCAL REINVENTION
```

ممنوع:

- CSS اختصاصی برای یک صفحه بدون Variant رسمی؛
- ساخت Button یا Table جدید فقط برای رفع سریع ظاهر؛
- کپی‌کردن CSS بین ماژول‌ها؛
- Override زنجیره‌ای برای اصلاح Component مرکزی؛
- Variant بدون نام و بدون کد؛
- تغییر Component FROZEN فقط برای یک صفحه؛
- Patch تاریخی با نام نسخه در انتهای CSS به‌عنوان راهکار دائمی.

---

# 2. سلسله‌مراتب رسمی Design System

تمام UI و خروجی‌ها باید از این زنجیره پیروی کنند:

```text
FOUNDATION TOKENS
      ↓
COMPONENTS
      ↓
PATTERNS
      ↓
PAGE TEMPLATES
      ↓
MODULE USAGE
      ↓
REPORT / PRINT OUTPUT
```

هر لایه فقط از لایه پایین‌تر خود تغذیه می‌شود.

---

# 3. قرارداد نام‌گذاری کدها

ساختار کد:

```text
<FAMILY>-<ROLE>-<VARIANT>
```

نمونه:

```text
BTN-PRI-01
TBL-MGT-01
FRM-STD-01
TTL-PAGE-01
PAT-LIST-01
PAGE-LIST-01
RPT-PDF-LIST-01
```

کد پس از تأیید نباید برای مفهوم دیگری Reuse شود.

---

# 4. Foundation Tokens

## 4.1 خانواده‌های رسمی

| کد خانواده | نام | منبع |
|---|---|---|
| `CLR` | Color | `tokens.css` + پالت FROZEN |
| `TYP` | Typography | `tokens.css` |
| `SPC` | Spacing | `tokens.css` |
| `SIZ` | Size / Control Height | `tokens.css` |
| `RAD` | Radius | `tokens.css` |
| `BRD` | Border | `tokens.css` |
| `SHD` | Shadow | `tokens.css` |
| `ZIX` | Z-index | Design System Tokens |
| `ICO` | Icon rules | Design System Assets |
| `DEN` | Density | Comfortable / Compact |

## 4.2 قانون مصرف Token

- مقدار خام رنگ، فاصله، Radius و Shadow در صفحات ماژول‌ها ممنوع است مگر در خود فایل Token.
- Componentها باید Token مصرف کنند.
- رنگ ماژول فقط از Semantic Token همان Domain گرفته شود.
- UI اصلی: Vazirmatn محلی.
- چاپ رسمی: B Titr برای Title و B Nazanin برای Body طبق مصوبه قبلی.
- RTL باید Native باشد، نه Patch شده با Override پراکنده.

---

# 5. Registry دکمه‌ها

تعداد Variantها عمداً محدود است.

| کد | نام رسمی | کاربرد | نمونه |
|---|---|---|---|
| `BTN-PRI-01` | اقدام اصلی | تنها Primary Action هر Context | ذخیره، ثبت، افزودن اصلی |
| `BTN-SEC-01` | اقدام ثانویه | عملیات معتبر ولی غیر اصلی | ویرایش، بازگشت |
| `BTN-TER-01` | اقدام کم‌اهمیت | Action سبک و بدون وزن بصری زیاد | لغو فیلتر فرعی |
| `BTN-DNG-01` | اقدام خطرناک | غیرفعال‌سازی/عملیات برگشت‌ناپذیر مجاز | غیرفعال کردن |
| `BTN-ICO-01` | دکمه آیکونی | Action فشرده با Tooltip و Accessible Label | سه‌نقطه، بستن |
| `BTN-OUT-01` | خروجی | PDF / Excel / چاپ | PDF، Excel، چاپ |
| `BTN-TBL-01` | عملیات جدول | Action داخل Toolbar یا ردیف با نقش کنترل‌شده | مشاهده |

## قواعد دکمه

- در یک Context فقط یک `BTN-PRI-01`.
- PDF / Excel / چاپ همیشه از `BTN-OUT-01` استفاده می‌کنند.
- دکمه‌های خروجی از Primary Action صفحه مهم‌تر دیده نمی‌شوند.
- Icon-only بدون Tooltip ممنوع.
- برای عملیات Row، انباشتن چند Button ممنوع؛ الگوی رسمی «مشاهده + More Menu» است.
- Disabled، Hover، Focus و Loading جزو Contract اجباری هر Button هستند.
- رنگ Button از نقش Semantic می‌آید، نه رنگ دلخواه صفحه.

---

# 6. Registry عنوان‌ها و متن سلسله‌مراتبی

| کد | نام | کاربرد |
|---|---|---|
| `TTL-PAGE-01` | عنوان اصلی صفحه | عنوان یکتای صفحه + توضیح کوتاه |
| `TTL-SECT-01` | عنوان بخش | Sectionهای اصلی فرم/جزئیات |
| `TTL-CARD-01` | عنوان کارت | کارت‌های استاندارد |
| `TTL-TBL-01` | عنوان جدول | Table Surface |
| `TTL-MOD-01` | عنوان Modal/Drawer | لایه‌های شناور |

قواعد:

- عنوان صفحه نباید در Card تزئینی قرار گیرد.
- Page Title همیشه نقش Heading واقعی دارد.
- Subtitle کوتاه و عملیاتی است.
- اندازه، وزن و فاصله از Registry می‌آید، نه Style محلی.

---

# 7. Registry فرم‌ها و کنترل‌ها

## 7.1 Field Components

| کد | Component |
|---|---|
| `FLD-TXT-01` | Text Input |
| `FLD-NUM-01` | Numeric Input |
| `FLD-MNY-01` | Money Input |
| `FLD-DAT-01` | Jalali Date Input |
| `FLD-SEL-01` | Single Select |
| `FLD-MUL-01` | Multi Select |
| `FLD-TXA-01` | Textarea |
| `FLD-CHK-01` | Checkbox |
| `FLD-RAD-01` | Radio Group |
| `FLD-UPL-01` | File Upload |
| `FLD-SEA-01` | Search Input |

Contract همه Fieldها:

```text
Label
Control
Helper / Error
```

- Placeholder جای Label را نمی‌گیرد.
- Required state یکسان.
- Error نزدیک Field.
- Focus واضح.
- حالت Read-only با Disabled اشتباه گرفته نمی‌شود.
- Validation Message فارسی، کوتاه و مشخص است.

## 7.2 Form Patterns

| کد | نام | کاربرد |
|---|---|---|
| `FRM-STD-01` | فرم استاندارد تک‌جریان | فرم‌های عمومی |
| `FRM-PAIR-01` | فرم جفت‌فیلدی | دو فیلد دارای رابطه روشن |
| `FRM-SECT-01` | فرم بخش‌بندی‌شده | اطلاعات پایه و فرم‌های چندبخشی |
| `FRM-WIZ-01` | فرم مرحله‌ای | Workflowهای چندمرحله‌ای |
| `FRM-MOD-01` | فرم کوتاه Modal | حداکثر عملیات کوتاه و محدود |

قانون: فرم تخصصی بلند در Modal ممنوع است.

---

# 8. Registry کارت‌ها و Surfaceها

| کد | نام | کاربرد |
|---|---|---|
| `CRD-INF-01` | کارت اطلاعات | گروه منطقی اطلاعات |
| `CRD-REC-01` | کارت رکورد | رکوردی که Table مناسب آن نیست |
| `CRD-KPI-01` | KPI Card | فقط داشبورد/خلاصه مدیریتی |
| `CRD-STA-01` | کارت وضعیت | وضعیت فشرده و عملیاتی |
| `PNL-SEC-01` | Section Panel | گروه فرم/جزئیات بدون Card Soup |

قواعد:

- استفاده از Card فقط وقتی ساختار اطلاعاتی آن را توجیه کند.
- Card Soup ممنوع.
- Shadow برای Cardهای عادی ممنوع یا بسیار محدود طبق سند FROZEN.
- Padding و Radius باید از Token بیاید.

---

# 9. Registry جدول‌ها

Table عنصر اصلی صفحات داده‌محور سما است.

| کد | نام | کاربرد |
|---|---|---|
| `TBL-SMP-01` | جدول ساده | نمایش داده کم‌تعامل |
| `TBL-DAT-01` | Data Table | Sort/Search/Filter/Pagination |
| `TBL-MGT-01` | جدول مدیریتی | Data Table + عملیات رکورد |
| `TBL-HIS-01` | جدول تاریخچه | سوابق زمانی و Audit-friendly |
| `TBL-SEL-01` | جدول انتخاب | انتخاب یک/چند رکورد |

## Contract مشترک Table

- RTL واقعی؛
- Sticky Header در Use-case لازم؛
- ستون‌ها دارای Alignment ثابت بر اساس نوع داده؛
- متن فارسی Right؛
- مبلغ و اعداد نمایشی Right؛
- Reference/System ID به‌صورت LTR در Cell مخصوص؛
- Empty State رسمی؛
- Loading State رسمی؛
- Pagination رسمی؛
- Horizontal Scroll کنترل‌شده؛
- Header و Row Height از Density Token؛
- Row Hover استاندارد؛
- Selected Row استاندارد؛
- Keyboard navigation در جدول‌های تعاملی؛
- Column Visibility برای جدول‌های مدیریتی؛
- Export از Dataset فیلترشده و نه صرفاً صفحه جاری.

## عملیات Row

الگوی رسمی:

```text
مشاهده   ⋮
```

More Menu می‌تواند شامل ویرایش، تاریخچه، اسناد و Actionهای Contextual باشد.

---

# 10. Search و Filter

| کد | نام | کاربرد |
|---|---|---|
| `SRC-FRE-01` | جست‌وجوی آزاد | نام/شماره/سمت/مرکز/متن |
| `FLT-PRI-01` | فیلترهای اصلی | فیلترهای پرتکرار |
| `FLT-ADV-01` | فیلتر پیشرفته | پنل/Drawer جمع‌وجور |
| `FLT-MUL-01` | فیلتر چندانتخابی | منطقه، مرکز، وضعیت و... |
| `FLT-RNG-01` | فیلتر بازه | تاریخ/عدد/منطقه با تعریف روشن |
| `FLT-CHP-01` | Active Filter Chip | فقط نمایش فیلتر فعال |
| `FLT-RST-01` | پاک‌کردن فیلترها | Reset روشن و یکسان |

قواعد اختصاصی سما:

- Region Exact Match است.
- منطقه ۲۱ فقط منطقه ۲۱ است و نباید با ۱/۱۰/۱۱/... Match شود.
- بازه منطقه باید مستقل و صریح تعریف شود.
- فیلترها قابل ترکیب هستند.
- Free Search جای Exact Filter را نمی‌گیرد.
- فیلترهای حجیم نباید تمام صفحه را اشغال کنند.

---

# 11. Toolbar / Command Bar

| کد | نام | کاربرد |
|---|---|---|
| `TBR-PAGE-01` | Page Command Bar | Actionهای سطح صفحه |
| `TBR-TBL-01` | Table Toolbar | Search/Filter/Columns/Export |
| `TBR-FRM-01` | Form Action Bar | ذخیره/انصراف |

ترتیب و جایگاه Actionها ثابت است و هر صفحه چیدمان اختصاصی اختراع نمی‌کند.

---

# 12. Navigation و Tabs

| کد | نام | کاربرد |
|---|---|---|
| `NAV-GLB-01` | Navigation اصلی | Global Shell |
| `NAV-MOD-01` | Navigation ماژول | سطح ماژول |
| `TAB-MOD-01` | تب ماژول | تب‌های اصلی یک Hub |
| `TAB-DET-01` | تب جزئیات | پرونده/پروفایل |
| `BRC-CTX-01` | Breadcrumb Context | فقط جایی که Context لازم است |

قانون پرونده:

- صفحه تخصصی → «مشاهده پرونده» = پرونده تخصصی همان حوزه.
- لینک ثانویه → «مشاهده پرونده جامع فضا».
- املاک مادر و فضاهای تجاری → مشاهده پرونده = پرونده جامع فضا.

---

# 13. Badge / Alert / Feedback

| کد | نام |
|---|---|
| `BDG-STA-01` | Status Badge |
| `ALT-INF-01` | Info Alert |
| `ALT-SUC-01` | Success Alert |
| `ALT-WRN-01` | Warning Alert |
| `ALT-ERR-01` | Error Alert |
| `EMP-STD-01` | Empty State |
| `LOD-STD-01` | Loading State |
| `TST-STD-01` | Toast |

رنگ تنها حامل معنا نیست؛ متن/آیکون/Label نیز باید وضعیت را منتقل کنند.

---

# 14. Modal / Drawer / Menu

| کد | نام | کاربرد |
|---|---|---|
| `MOD-CFM-01` | Confirm Modal | تأیید عملیات |
| `MOD-SFM-01` | Small Form Modal | فرم کوتاه |
| `DRW-QVW-01` | Quick View Drawer | مشاهده سریع |
| `DRW-FLT-01` | Filter Drawer | فیلتر پیشرفته |
| `MNU-ACT-01` | Action Menu | عملیات سه‌نقطه |

فرم‌های اصلی کارشناسی، قرارداد، مزایده و پرونده کامل باید Full Page باشند.

---

# 15. Patterns رسمی

| کد | نام | ساختار |
|---|---|---|
| `PAT-LIST-01` | فهرست استاندارد | Header → Toolbar → Filter → Table → Pagination |
| `PAT-MGT-01` | مدیریت رکورد | Header → Add Action → Search/Filter → Management Table |
| `PAT-FORM-01` | فرم استاندارد | Header → Section Panels → Form Action Bar |
| `PAT-DETAIL-01` | جزئیات | Profile/Header → Tabs/Sections → Context Actions |
| `PAT-HIST-01` | تاریخچه | Scope → Timeline/Table → Detail |
| `PAT-DASH-01` | داشبورد | Action Center → KPI → Domain Sections → Charts |
| `PAT-REPORT-01` | گزارش‌ساز | Scope → Fields/Columns → Filter → Preview → Export |

---

# 16. Page Templates رسمی

| کد | نام |
|---|---|
| `PAGE-LIST-01` | صفحه فهرست |
| `PAGE-MGT-01` | صفحه مدیریت |
| `PAGE-FORM-01` | صفحه فرم |
| `PAGE-DETAIL-01` | صفحه جزئیات/پرونده |
| `PAGE-WIZ-01` | صفحه مرحله‌ای |
| `PAGE-DASH-01` | داشبورد |
| `PAGE-RPT-01` | گزارش‌ساز |

قانون: هر View باید در مستندات/کد مشخص کند از کدام `PAGE-*` استفاده می‌کند.

---

# 17. Report / PDF / Excel / Print Registry

Browser Print خروجی رسمی سما نیست.

## 17.1 PDF

| کد | نام |
|---|---|
| `RPT-PDF-LIST-01` | PDF فهرستی رسمی |
| `RPT-PDF-DETAIL-01` | PDF تفصیلی |
| `RPT-PDF-FILE-01` | PDF پرونده کامل |
| `RPT-PDF-MIN-01` | PDF صورتجلسه/سند رسمی |

## 17.2 Excel

| کد | نام |
|---|---|
| `RPT-XLS-LIST-01` | Excel فهرستی |
| `RPT-XLS-DETAIL-01` | Excel تفصیلی |
| `RPT-XLS-ANL-01` | Excel تحلیلی |

## 17.3 Print

| کد | نام |
|---|---|
| `RPT-PRT-OFFICIAL-01` | چاپ رسمی سازمانی |
| `RPT-PRT-TABLE-01` | چاپ جدول فیلترشده |
| `RPT-PRT-FILE-01` | چاپ پرونده |

## Contract خروجی رسمی

Header رسمی:

```text
سازمان فرهنگی هنری شهرداری تهران
مدیریت اقتصادی و املاک
اداره املاک و مستغلات
لوگوی رسمی
```

- نام نرم‌افزار در گزارش رسمی ممنوع.
- PDF/Excel/Print باید همان Filterهای فعال را اعمال کنند.
- همان Column Visibility و همان ترتیب ستون‌ها باید رعایت شود.
- داده از صفحه اول شروع شود.
- Header جدول در صفحات بعد تکرار شود.
- شماره صفحه صحیح.
- RTL صحیح.
- Page Break کنترل‌شده.
- B Titr برای عنوان و B Nazanin برای متن چاپ رسمی مطابق مصوبه.
- Export مستقل از Pagination UI است و باید کل Dataset فیلترشده مجاز را پوشش دهد.

---

# 18. Mapping الزامی برای ماژول «اطلاعات پایه»

اطلاعات پایه نخستین ماژول برای Normalize کامل بر اساس این Registry است.

## 18.1 نمای کلی

```text
PAGE-MGT-01
PAT-MGT-01
TTL-PAGE-01
TAB-MOD-01
TBR-PAGE-01
```

## 18.2 اطلاعات سازمان

```text
PAGE-FORM-01
PAT-FORM-01
FRM-SECT-01
PNL-SEC-01
TBR-FRM-01
BTN-PRI-01 = ذخیره
BTN-SEC-01 = انصراف/بازگشت در صورت وجود
BTN-OUT-01 = PDF / Excel / چاپ در صورت مجاز بودن خروجی همین View
```

## 18.3 مناطق و مراکز

```text
PAGE-MGT-01
PAT-MGT-01
SRC-FRE-01
FLT-PRI-01 / FLT-ADV-01 در صورت نیاز
TBL-MGT-01
BTN-PRI-01 = افزودن رکورد مجاز
BTN-TBL-01 + MNU-ACT-01 = عملیات رکورد
BTN-OUT-01 = خروجی
```

## 18.4 شماره تماس‌ها

```text
PAGE-MGT-01
PAT-MGT-01
SRC-FRE-01
FLT-MUL-01
TBL-MGT-01
BTN-PRI-01 = افزودن شماره تماس
BTN-OUT-01 = PDF / Excel / چاپ
```

## 18.5 کمیسیون‌ها

فهرست کمیسیون‌ها باید از Pattern مدیریتی رسمی پیروی کند و Card اختصاصی فقط در صورت توجیه ساختاری استفاده شود.

```text
PAGE-MGT-01
PAT-MGT-01
TBL-MGT-01 یا CRD-REC-01 فقط با یک Contract ثابت
BTN-PRI-01 = افزودن کمیسیون
BTN-SEC-01 = ویرایش
BTN-TBL-01 = اعضا و ترتیب / مشاهده
BTN-OUT-01 = خروجی
```

اعضا و ترتیب:

```text
PAGE-MGT-01 یا MOD-SFM-01 فقط اگر عملیات واقعاً کوتاه باشد
TBL-MGT-01 / TBL-SEL-01
Drag & Drop یا بالا/پایین به‌عنوان رفتار رسمی واحد
```

## 18.6 اطلاعات بانکی

```text
PAGE-MGT-01
PAT-MGT-01
TBL-MGT-01
BTN-PRI-01 = افزودن حساب
BTN-OUT-01 = خروجی
```

نتیجه: مناطق، شماره تماس‌ها، کمیسیون‌ها و اطلاعات بانکی نباید چهار زبان بصری مستقل داشته باشند؛ همه زیر یک Pattern مدیریتی مشترک قرار می‌گیرند.

---

# 19. Component Contract اجباری

هر Component رسمی باید حداقل این Metadata را داشته باشد:

```text
Code
Persian Name
Family
Purpose
Allowed Contexts
Forbidden Contexts
Visual Tokens
States
Density
RTL Behavior
Keyboard Behavior
Accessibility Labeling
Print Behavior
Version
Status
```

Status فقط یکی از این‌هاست:

```text
DRAFT
APPROVED
FROZEN
DEPRECATED
```

---

# 20. Source Ownership — هر چیز از کجا تأمین می‌شود؟

| نیاز | منبع رسمی |
|---|---|
| رنگ/Spacing/Radius/Size | Foundation Tokens |
| Button/Input/Table/Card | Components |
| ترکیب Search/Filter/Table | Patterns |
| اسکلت View | Page Templates |
| PDF/Excel/Print | Report Engine + Report Registry |
| رنگ ماژول | Domain Semantic Token |
| لوگوی سازمان | Asset رسمی مورد تأیید کاربر |
| فونت UI | Local Vazirmatn Asset |
| فونت چاپ | Print Typography Policy |
| رفتار پرونده‌ها | Navigation Contract |
| Statusها | Badge/Alert Registry |

صفحه حق تعریف منبع جایگزین ندارد.

---

# 21. معماری فایل هدف

وضع موجود ممکن است تا زمان مهاجرت هنوز `app.css` مرکزی داشته باشد؛ اما معماری هدف Design System این است:

```text
design_system/
  static/design_system/css/
    tokens.css
    foundations.css
    components/
      buttons.css
      fields.css
      tables.css
      cards.css
      navigation.css
      feedback.css
      overlays.css
    patterns/
      list.css
      management.css
      forms.css
      detail.css
      reports.css
    utilities.css
    print.css
```

نکته: این ساختار باید با مهاجرت کنترل‌شده ایجاد شود؛ شکستن ناگهانی `app.css` یا بازطراحی کل سامانه ممنوع است.

---

# 22. Migration Rule

مهاجرت از UI فعلی به Registry باید Delta باشد:

1. Inventory صفحه؛
2. مشخص‌کردن Component/Pattern فعلی؛
3. Mapping به کد رسمی؛
4. حذف فقط Duplicate/Local Style مربوط به همان Component؛
5. استفاده از Component مرکزی؛
6. Regression Test؛
7. تأیید کاربر؛
8. Freeze ماژول.

هیچ Refactor گسترده هم‌زمان با تغییر Business Logic انجام نمی‌شود.

---

# 23. Definition of Done برای هر صفحه

یک View فقط زمانی Design-System Compliant است که:

- `PAGE-*` مشخص باشد؛
- Patternهای مصرفی مشخص باشند؛
- تمام Buttonها کد رسمی داشته باشند؛
- تمام Tableها کد رسمی داشته باشند؛
- تمام Fieldها کد رسمی داشته باشند؛
- Search/Filter از Registry باشد؛
- Titleها از Registry باشند؛
- Local visual override نداشته باشد؛
- حالت Empty/Loading/Error تعریف شده باشد؛
- Keyboard/Focus قابل استفاده باشد؛
- RTL صحیح باشد؛
- Export/Print از Report Contract پیروی کند؛
- Regression Visual Test پاس شود.

---

# 24. کنترل تغییرات

## قانون FROZEN

بعد از تأیید یک Component:

```text
APPROVED → FROZEN
```

تغییر Component FROZEN فقط در یکی از این حالات مجاز است:

1. درخواست مستقیم Owner؛
2. Bug واقعی؛
3. Accessibility defect؛
4. Security/Browser compatibility defect؛
5. نیاز سراسری جدید که ابتدا تأیید شده باشد.

تغییر Component مرکزی باید اثر آن در تمام Consumerها بررسی شود.

---

# 25. ممنوعیت Patch صفحه‌ای

از این Baseline به بعد:

```text
.page-x .button { ... }
#specific-view table { ... }
.module-y .card { ... }
```

برای تغییر ظاهر Component رسمی، راهکار پذیرفته‌شده نیست مگر Scope واقعاً Structural باشد و در Registry مستند شود.

اگر یک Component در یک صفحه متفاوت دیده می‌شود، اول علت بررسی می‌شود:

```text
Wrong component?
Wrong variant?
Local override?
Token mismatch?
Old cached asset?
```

نه اینکه فوراً CSS جدید اضافه شود.

---

# 26. Quality Gates

قبل از Freeze هر ماژول:

- Visual consistency review؛
- Component registry compliance؛
- RTL review؛
- Keyboard/Focus review؛
- Responsive desktop/LAN review؛
- Print/PDF/Excel review؛
- Browser cache/static asset review؛
- Data integrity regression؛
- عدم Hard Delete؛
- Portable runtime regression.

---

# 27. تست‌های حداقلی Design System

باید به‌تدریج تست‌های زیر وارد پروژه شوند:

```text
Component render tests
Template integration tests
Critical CSS selector regression
RTL layout tests
Print template smoke tests
PDF/Excel schema tests
Accessibility smoke tests
Static asset/version tests
```

هدف این است که تفاوت ناخواسته صفحات فقط با مشاهده دستی کشف نشود.

---

# 28. قاعده Versioning

Design System نسخه مستقل دارد:

```text
SAMA-DS 1.0
```

تغییرات:

- Patch: اصلاح Bug بدون تغییر Contract؛
- Minor: Variant/Component جدید سازگار؛
- Major: تغییر Contract موجود.

هر Package سما باید نسخه Design System مصرفی خود را قابل ردیابی نگه دارد.

---

# 29. وضعیت این Baseline

از زمان تصویب این سند:

```text
SAMA Design System Governance = ACTIVE
No Local Reinvention = MANDATORY
Component Registry = MANDATORY
Pattern Mapping = MANDATORY
Report Contract = MANDATORY
```

ماژول «اطلاعات پایه» اولین Candidate برای Compliance کامل و سپس Freeze است.

---

# 30. تصمیم اجرایی نهایی

از این نقطه به بعد توسعه سما با سؤال «این صفحه را چطور طراحی کنیم؟» شروع نمی‌شود.

سؤال رسمی این است:

```text
این نیاز از کدام Token / Component / Pattern / Page Template / Report Template رسمی سما تأمین می‌شود؟
```

اگر پاسخ موجود است، همان مصرف می‌شود.
اگر پاسخ موجود نیست، ابتدا Design System تکمیل می‌شود و بعد Feature ساخته می‌شود.

این قاعده برای تمام ماژول‌های فعلی و آینده سما الزام‌آور است.
