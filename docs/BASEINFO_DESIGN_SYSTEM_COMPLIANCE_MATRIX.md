# ماتریس تطبیق Design System — ماژول اطلاعات پایه

**پروژه:** سما  
**Design System:** `SAMA-DS 1.0.0`  
**وضعیت:** `ACTIVE COMPLIANCE PLAN`  
**قاعده حاکم:** `NO LOCAL REINVENTION`

این سند نقشه اجرایی یکسان‌سازی «اطلاعات پایه» است. هدف، شبیه‌کردن کورکورانه همه صفحات نیست؛ صفحات هم‌نوع باید دقیقاً از Pattern و Component یکسان استفاده کنند و صفحات با ماهیت متفاوت باید از Pattern رسمی مناسب خود مصرف کنند.

## 1. قرارداد مشترک تمام صفحات اطلاعات پایه

تمام صفحات این ماژول باید از این قراردادها پیروی کنند:

- Accent ماژول: `#6F7783` و زمینه نرم `#F7F7F7` فقط از Token مرکزی.
- عنوان صفحه: `TTL-PAGE-01`.
- تب‌های داخلی اطلاعات پایه: `TAB-MOD-01`.
- نوار عملیات صفحه: `TBR-PAGE-01` یا `TBR-FRM-01` طبق نوع صفحه.
- PDF / Excel / چاپ: فقط `BTN-OUT-01` و موتور گزارش مرکزی.
- Action اصلی: فقط یک `BTN-PRI-01` در Context.
- Action ثانویه: `BTN-SEC-01`.
- عملیات ردیف جدول: `BTN-TBL-01` + `MNU-ACT-01` در صورت تعدد عملیات.
- Badge وضعیت: `BDG-STA-01`.
- Empty state: `EMP-STD-01`.
- هیچ CSS، رنگ، Radius، Font-size یا Button Variant محلی مجاز نیست.

## 2. Mapping صفحات

| صفحه | نوع رسمی | Pattern | اجزای اصلی اجباری | خروجی رسمی |
|---|---|---|---|---|
| اطلاعات سازمان | `PAGE-FORM-01` | `PAT-FORM-01` | `TTL-PAGE-01` + `FRM-SECT-01` + `PNL-SEC-01` + `TBR-FRM-01` + `BTN-PRI-01` | `RPT-PDF-DETAIL-01` / `RPT-PRT-OFFICIAL-01` در صورت نیاز |
| مناطق و مراکز | `PAGE-MGT-01` | `PAT-MGT-01` | `SRC-FRE-01` + `FLT-PRI-01` + `TBL-MGT-01` + `TBR-TBL-01` + `BTN-PRI-01` + `BTN-TBL-01` | `RPT-PDF-LIST-01` / `RPT-XLS-LIST-01` / `RPT-PRT-TABLE-01` |
| شماره تماس‌ها | `PAGE-MGT-01` | `PAT-MGT-01` | `SRC-FRE-01` + `FLT-MUL-01` + `FLT-RNG-01` در صورت نیاز + `TBL-MGT-01` + `TBR-TBL-01` | همان قرارداد فهرستی |
| کمیسیون‌ها | `PAGE-MGT-01` | `PAT-MGT-01` | `TBL-MGT-01` + `BTN-PRI-01` افزودن + `BTN-SEC-01` ویرایش + `BTN-TBL-01` مدیریت اعضا + `BDG-STA-01` | همان قرارداد فهرستی |
| اطلاعات بانکی | `PAGE-MGT-01` | `PAT-MGT-01` | `TBL-MGT-01` + `BTN-PRI-01` افزودن + `BTN-TBL-01` ویرایش + `BDG-STA-01` | همان قرارداد فهرستی |

## 3. قرارداد `PAGE-MGT-01`

ترتیب ثابت در Desktop:

```text
TTL-PAGE-01
→ TAB-MOD-01
→ TBR-PAGE-01 (Primary + Export)
→ SRC-FRE-01 + FLT-*
→ TBL-MGT-01
→ Pagination / Result Count
→ EMP-STD-01 (در حالت بدون نتیجه)
```

قواعد:

- جای Search، Filter، Export و Add بین صفحات مدیریتی جابه‌جا نمی‌شود.
- PDF/Excel/چاپ یک Toolbar مشترک دارند و از نظر وزن بصری ثانویه‌اند.
- Table Header، Row height، Padding، Hover، Selected state، Status و Actions یکسان‌اند.
- ستون عملیات شکل یکسان دارد.
- Search آزاد و Filter دقیق از هم تفکیک می‌شوند.
- Filter فعال باید روی Export و Print اعمال شود.
- Column visibility در صورت فعال بودن، روی Table و خروجی یک قرارداد واحد دارد.

## 4. قرارداد `PAGE-FORM-01`

ترتیب ثابت:

```text
TTL-PAGE-01
→ TAB-MOD-01
→ FRM-SECT-01
   → PNL-SEC-01 × n
→ TBR-FRM-01
   → BTN-PRI-01 ذخیره
   → BTN-SEC-01 انصراف/بازگشت در صورت نیاز
```

قواعد:

- هر Section فقط یک عنوان `TTL-SECT-01` دارد.
- فیلدها از خانواده `FLD-*` مصرف می‌شوند.
- Label، Required، Helper، Error و Focus Contract مشترک است.
- فرم اطلاعات سازمان نباید برای هم‌شکل شدن با صفحات فهرستی به Table تبدیل شود.

## 5. تطبیق اولیه با اسکرین‌های UAT 9.2

بر اساس اسکرین‌های مالک، موارد زیر باید در Normalize بررسی شوند:

1. Toolbar خروجی در «اطلاعات سازمان» و «کمیسیون‌ها» از یک `BTN-OUT-01` مشترک استفاده کند.
2. وزن بصری «افزودن کمیسیون» با Primary Action سراسری یکی باشد.
3. «اعضا و ترتیب» نقش Secondary/Contextual داشته باشد و Primary دوم نباشد.
4. ساختار کارت کمیسیون باید با `CRD-REC-01`/`TBL-MGT-01` بر اساس حجم داده نهایی تعیین شود؛ کارت اختصاصی صفحه مجاز نیست.
5. صفحات «مناطق و مراکز»، «شماره تماس‌ها»، «کمیسیون‌ها» و «اطلاعات بانکی» باید یک اسکلت مدیریتی مشترک داشته باشند.
6. فاصله عنوان، Tabs، Toolbar و Main Surface باید از Token/Pattern مشترک بیاید.

## 6. Definition of Done برای Freeze اطلاعات پایه

ماژول فقط وقتی قابل Freeze است که:

- پنج Mapping فوق بدون Variant محلی اجرا شده باشند؛
- هیچ Inline Style یا Page-specific visual patch وجود نداشته باشد؛
- Button/Table/Form/Title/Filter/Output از Registry رسمی مصرف شوند؛
- RTL، Focus و Keyboard smoke test عبور کند؛
- PDF/Excel/Print همان Filter/Column/Order فعال را رعایت کنند؛
- Cache/static versioning کنترل شده باشد؛
- داده و Workflow تغییر ناخواسته نکرده باشد؛
- تست Regression و Portable runtime عبور کند؛
- Owner ظاهر و رفتار را تأیید کند.

پس از آن وضعیت ماژول:

```text
BASEINFO → FROZEN
```

و هر تغییر بعدی فقط با درخواست مستقیم Owner یا Defect معتبر انجام می‌شود.
