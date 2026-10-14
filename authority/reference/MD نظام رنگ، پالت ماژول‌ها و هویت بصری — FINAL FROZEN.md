# MD نظام رنگ، پالت ماژول‌ها و هویت بصری — SAMA

**پروژه:** سامانه املاک سازمان فرهنگی هنری شهرداری تهران (SAMA)  
**حوزه:** UI/UX / Color System / Module Identity / Login / Global Shell  
**وضعیت:** `FINAL FROZEN`  
**هدف:** ثبت یک مرجع واحد برای رنگ‌های تأییدشده، جلوگیری از جابه‌جایی پالت‌ها و آماده‌سازی برای Design System و پیاده‌سازی واقعی.

---

## 1. اصل حاکم

SAMA یک Design System واحد دارد، اما هر ماژول اصلی دارای «هویت رنگی» مستقل است.

```text
Shared Design System
+ Module Color Identity
+ Fixed Semantic Colors
+ Shared Neutral System
```

تفاوت رنگی ماژول‌ها نباید باعث تفاوت در ساختار Componentها، Typography، Grid، Table، Form، Spacing یا Navigation شود.

---

## 2. قاعده استفاده از رنگ

رنگ ماژول برای این موارد استفاده می‌شود:

- Page/Module Accent
- Header Accent
- Active Navigation
- Active Tab
- Primary Action
- Focus State
- Selected State
- KPI Accent
- Chart Primary Series
- Subtle Surface Tint
- Module Icon Accent

رنگ ماژول به معنی رنگی‌کردن کامل صفحه نیست.

قاعده پیشنهادی مصرف:

```text
Neutral / White Surfaces   70–80%
Module Identity Color      15–25%
Semantic / Supporting       5–10%
```

---

# 3. پالت‌های نهایی ماژول‌ها

## 3.1 داشبورد مدیریتی

**پالت:** `عنابی مدرن`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#FDF6F7
#F4E6EA
#E0C1C9
#C08491
#9B3B4A
#6E2431
```

کاربرد: Dashboard shell accents، KPIهای مدیریتی، Headerهای مدیریتی و نمودارهای اصلی.

---

## 3.2 املاک مادر

**پالت:** `آبی ایرانی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F5FAFF
#DCEBFA
#B8D3F2
#7FAFE3
#3E7FC4
#1F5FA8
#153A73
```

کاربرد: پرونده ملک مادر، فهرست، Summary، CTA و عناصر هویتی این Domain.

---

## 3.3 فضاهای تجاری فعال

**پالت:** `سبز باغ ایرانی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F6F9F4
#DDEBD2
#A9CD89
#5B9852
#2E5D31
```

کاربرد: فهرست فضاهای فعال، پرونده فضای فعال، کارت‌های وضعیت عادی و Accentهای Domain.

---

## 3.4 فضاهای از دور خارج‌شده

**پالت:** `نوک‌مدادی گرم`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F6F5F4
#DCD6D3
#B5ABA6
#8A7E78
#5D534E
#3A3431
```

کاربرد: فضاهای غیرفعال/خارج از چرخه، Archive-like states و پرونده‌های تاریخی.

---

## 3.5 بهره‌برداران

**پالت:** `بژ کله‌غازی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F9F6EF
#EFE4D6
#E0D0B8
#C9B28C
#A88B67
#8B6F4F
#6B4F32
```

کاربرد: اشخاص/بهره‌برداران، کارت هویت، پرونده، فهرست و تعاملات انسانی Domain.

---

## 3.6 قراردادها

**پالت:** `اکر / خردلی لوکس`  
**وضعیت:** ✅ نهایی برای رفع شباهت با بهره‌برداران

> پالت قبلی «شتری درخشان» کنار گذاشته شد تا قراردادها با بهره‌برداران بیش از حد هم‌خانواده دیده نشوند.

Anchor Palette:

```text
#FFFAEC
#FFE5B7
#E6B325
#C89400
#7A5A00
```

کاربرد: قراردادها، تعهدات، پرونده قرارداد، CTAهای حقوقی/اسنادی و Headerهای Domain.

---

## 3.7 کارشناسی و کارشناسان

**پالت:** `ارغوانی خاکستری`  
**وضعیت:** ✅ تأیید نهایی

> انتخاب قبلی یاسی/آمتیست حذف شده و این پالت جایگزین آن است.

Anchor Palette:

```text
#F7F4F8
#E4DDE8
#C5B4C7
#8C6B8F
#67406A
#3C2440
```

کاربرد: کارشناسی، کارشناسان، ارجاع، تاریخچه کارشناسی و پرونده کارشناسی.

---

## 3.8 حق‌الزحمه کارشناسان

**پالت:** `شرابی خاکی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F9EDED
#D9B7B4
#A66B6B
#7F3F46
#4B1E28
```

کاربرد: مبلغ حق‌الزحمه، Batch ارسال به مالی، وضعیت پرداخت، پرونده پرداخت و گزارش‌های این فرآیند.

---

## 3.9 مزایده و اسناد مزایده

**پالت:** `لوکس و شیشه‌ای مزایده`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#FFF8F1   Cream Glass
#F7EBDD   Ivory
#C59262   Soft Camel
#D6AF70   Sandy Gold
#F0731F   Primary Orange
#FF8B3D   Bright Orange
#7F2526   Deep Red
#541823   Luxury Burgundy
```

کاربرد:

- Candidate Engine
- AuctionPeriod
- AuctionLot
- Readiness
- اسناد مزایده
- دریافت پیشنهاد
- بازگشایی پاکات
- ثبت نتیجه
- آرشیو مزایده

تمام زیرصفحه‌های مزایده همین هویت را به ارث می‌برند.

---

## 3.10 انشعابات و مصرف

**پالت:** `کله‌غازی یشمی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#E2F3EE
#A8D9CC
#4FB39F
#1F8A77
#0A5B4F
```

کاربرد: برق، آب، گاز، پایش مصرف، قرائت، نمودار مصرف و مدیریت انشعابات.

رنگ‌های Category می‌توانند به‌صورت محدود استفاده شوند:

```text
برق  → Amber/Yellow Accent
آب   → Blue Accent
گاز  → Orange Accent
```

هویت اصلی صفحه همچنان کله‌غازی یشمی است.

---

## 3.11 کمیسیون معاملات

**پالت:** `سرمه‌ای نفتی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F4F7F9
#DCE5EA
#8EA4B2
#3E5A68
#1E2D35
```

کاربرد: جلسات، تصمیمات، مصوبات و اقدامات کمیسیون معاملات.

---

## 3.12 گزارش‌گیری و تحلیل مدیریتی

**پالت:** `لاجوردی دودی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F5F6FA
#D9DFEC
#A4B2CC
#5A6F9B
#27324A
```

کاربرد:

- Report Center
- Report Builder
- Saved Reports
- Snapshot Reports
- جداول تحلیلی
- Drilldownهای گزارش
- نمودارها و خروجی‌های مدیریتی

---

## 3.13 کاربران، تنظیمات و مدیریت دسترسی

**پالت:** `دودی پلاتینی`  
**وضعیت:** ✅ تأیید نهایی

Anchor Palette:

```text
#F7F7F7
#E3E3E6
#B8BDC6
#6F7783
#2F343C
```

کاربرد:

- Settings
- User Management
- Admin
- Reset Password
- System Configuration
- Technical/Neutral Screens

---

# 4. صفحه ورود کاربران

**هویت:** `زرشکی اناری + نقره‌ای بسیار روشن مرواریدی`  
**وضعیت:** ✅ تأیید نهایی

Primary:

```text
#901E38
```

Burgundy Support:

```text
#FFE9EB
#F6B7C1
#CF4766
#901E38
#4A081D
```

Pearl / Bright Silver:

```text
#FFFFFF
#F8F9FA
#EEF1F4
#DCE1E6
#C9D0D7
```

Text / Contrast:

```text
#25292E
#545B63
```

قاعده:

- زمینه غالب روشن و نزدیک به سفید
- Silver باید «روشن، براق و مرواریدی» باشد، نه خاکستری تیره
- زرشکی اناری برای CTA، Focus و هویت Login
- بدون طلایی، نارنجی یا بنفش اضافی
- لوگوی رسمی سازمان باید از Asset رسمی استفاده شود و بازطراحی/بازنویسی نشود

---

# 5. پوسته عمومی SAMA

**پالت:** `آجری دودی`  
**وضعیت:** ✅ تأیید نهایی

این پالت برای اجزایی است که متعلق به یک Domain خاص نیستند:

- Sidebar
- Top Bar
- Global Search
- Breadcrumb
- Generic Navigation
- Generic Page Header
- Global Command Areas
- General Shell

Anchor Palette:

```text
#FAF6F4
#EADCD7
#D2B6AA
#A4715D
#8B4A3A
#5E2E22
```

قاعده:

> وقتی کاربر وارد یک Domain مشخص می‌شود، Accent همان Domain بر پوسته عمومی غالب می‌شود؛ اما ساختار و Neutral Base ثابت می‌ماند.

---

# 6. رنگ‌های معنایی ثابت

رنگ‌های Semantic مستقل از رنگ ماژول هستند و در کل SAMA معنی یکسان دارند.

```text
Success      → Green
Warning      → Amber / Orange
Error        → Red
Information  → Blue
Review       → Controlled Violet / Neutral as defined
```

رنگ ماژول نباید جای معنی Semantic را بگیرد.

مثال:

```text
مزایده = نارنجی/شرابی هویتی
اما Error مزایده همچنان Error Red است.
```

---

# 7. Shared Neutral System

برای تمام ماژول‌ها:

```text
Background       #FAFAFA / near-white
Surface          #FFFFFF
Border           light neutral
Primary Text     dark neutral
Secondary Text   medium neutral
Disabled         controlled light neutral
```

Neutralها می‌توانند هنگام Implementation برای Contrast دقیق Calibration شوند.

---

# 8. Gloss / Glass Treatment

ظاهر تأییدشده کاربر:

```text
Real-looking Gloss
Subtle Glass
High-quality Surface
Controlled Highlight
Soft Border
Minimal Shadow
No AI-looking multicolor blend
```

ممنوع:

- Rainbow Gradient
- Neon
- Glow سنگین
- چند Hue نامرتبط در یک Surface
- Glass بیش از حد
- Pastel کم‌کنتراست
- رنگ‌های «نامشخص و ترکیبی» بدون هویت

---

# 9. Production Color Calibration

پالت‌های این سند مرجع رسمی Color Direction هستند.

در Implementation:

- رنگ‌ها باید در sRGB بررسی شوند.
- Contrast متن و UI کنترل شود.
- مانیتورهای اداری مختلف بررسی شوند.
- اگر یک Hex نیازمند اصلاح جزئی برای Accessibility باشد، Hue identity نباید تغییر کند.
- تغییر Hue یا تعویض Palette نیازمند Change Request است.
- اصلاح Lightness/Contrast جزئی برای Production مجاز است، مشروط به حفظ هویت تصویری.

---

# 10. رابطه ماژول و زیرماژول

زیرماژول‌ها پالت Parent Domain را به ارث می‌برند مگر در این سند استثنا شده باشند.

استثنای تأییدشده:

```text
کارشناسی              → ارغوانی خاکستری
حق‌الزحمه کارشناسان   → شرابی خاکی
```

مزایده و اسناد آن یک خانواده واحد هستند.

---

# 11. تصمیم‌های نهایی FROZEN

1. Design System واحد است؛ رنگ Domainها متفاوت است.
2. تم عمومی SAMA آجری دودی است.
3. Dashboard عنابی مدرن است.
4. Parent Property آبی ایرانی است.
5. Active Commercial Spaces سبز باغ ایرانی است.
6. Out-of-Cycle Spaces نوک‌مدادی گرم است.
7. Beneficiary بژ کله‌غازی است.
8. Contract اکر/خردلی لوکس است.
9. Appraisal/Experts ارغوانی خاکستری است.
10. Expert Fees شرابی خاکی است.
11. Auction خانواده لوکس و شیشه‌ای مزایده است.
12. Utilities کله‌غازی یشمی است.
13. Commission سرمه‌ای نفتی است.
14. Reporting لاجوردی دودی است.
15. Settings/Admin دودی پلاتینی است.
16. Login زرشکی اناری + Silver Pearl بسیار روشن است.
17. Semantic Colors در کل سامانه ثابت‌اند.
18. رنگ‌های Module فقط نقش هویتی دارند، نه معنی Status.
19. Exact visual polish در پیاده‌سازی قابل Calibration محدود است.
20. تغییر خانواده رنگی پس از این سند فقط از مسیر Change Request انجام می‌شود.

---

# 12. وضعیت سند

```text
FINAL FROZEN
```

تغییر آینده:

```text
CHANGE REQUEST
→ REVIEW
→ APPROVED
→ FROZEN
```

---

**پایان سند — MD نظام رنگ، پالت ماژول‌ها و هویت بصری — SAMA**
