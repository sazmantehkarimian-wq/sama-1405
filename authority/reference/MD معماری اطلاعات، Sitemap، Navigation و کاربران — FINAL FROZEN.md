# MD معماری اطلاعات، Sitemap، Navigation و کاربران — SAMA

**پروژه:** سامانه املاک سازمان فرهنگی هنری شهرداری تهران (SAMA)  
**حوزه:** Information Architecture / Sitemap / Navigation / Authentication / User Management  
**وضعیت:** `FINAL FROZEN`  
**نوع سند:** مشخصات ساختار صفحات، مسیرهای کاربر، منوها، حساب‌های کاربری و مدیریت رمز عبور

---

# 1. اصل طراحی

SAMA برای یک تیم کوچک داخلی در شبکه LAN سازمان طراحی می‌شود.

قاعده اصلی:

```text
سادگی عملیات
+
ردیابی دقیق کاربر
+
دسترسی کامل و برابر
+
عدم پیچیدگی امنیتی غیرضروری
```

سامانه دارای 5 کاربر عملیاتی نام‌دار و یک حساب فنی `admin` است.

---

# 2. مدل کاربران

## 2.1 کاربران عملیاتی

پنج کاربر اصلی دارای دسترسی عملیاتی کامل و برابر هستند.

هیچ Role عملیاتی جداگانه مانند:

- مدیر
- مشاهده‌گر
- اپراتور
- کارشناس محدود
- تأییدکننده

در این نسخه وجود ندارد.

مدل دسترسی:

```text
Authenticated Named User = Full Operational Access
Unauthenticated User = No Access
```

---

# 3. کاربران مصوب

## 3.1 اکبر قربانی

- نام: اکبر قربانی
- سمت: مدیر اقتصادی و املاک
- Username:

```text
a.ghorbani
```

- Password اولیه:

```text
Sama@G74#26
```

- وضعیت اولین ورود:

```text
MUST_CHANGE_PASSWORD = TRUE
```

---

## 3.2 اکبر مجیدی

- نام: اکبر مجیدی
- سمت: رئیس اداره املاک و مستغلات
- Username:

```text
a.majidi
```

- Password اولیه:

```text
Sama@M58#41
```

- وضعیت اولین ورود:

```text
MUST_CHANGE_PASSWORD = TRUE
```

---

## 3.3 مجید عبداللهی

- نام: مجید عبداللهی
- سمت: کارشناس اداره املاک و مستغلات
- Username:

```text
m.abdollahi
```

- Password اولیه:

```text
Sama@A63#29
```

- وضعیت اولین ورود:

```text
MUST_CHANGE_PASSWORD = TRUE
```

---

## 3.4 زهره محمدی

- نام: زهره محمدی
- سمت: کارشناس اداره املاک و مستغلات
- Username:

```text
z.mohammadi
```

- Password اولیه:

```text
Sama@Z47#82
```

- وضعیت اولین ورود:

```text
MUST_CHANGE_PASSWORD = TRUE
```

---

## 3.5 سید محمد کریمیان

- نام: سید محمد کریمیان
- سمت: مسئول دفتر مدیریت اقتصادی و املاک
- Username:

```text
sm.karimian
```

- Password اولیه:

```text
Sama@K91#35
```

- وضعیت اولین ورود:

```text
MUST_CHANGE_PASSWORD = TRUE
```

---

# 4. حساب فنی Admin

یک حساب فنی مستقل وجود دارد:

```text
Username: admin
Password: Mina123!
```

قواعد:

```text
MUST_CHANGE_PASSWORD = FALSE
PASSWORD_FIXED = TRUE
```

حساب `admin`:

- دسترسی کامل سامانه دارد؛
- مدیریت کاربران را دارد؛
- می‌تواند Password کاربران عملیاتی را Reset کند؛
- Password خودش از رابط عادی قابل تغییر نیست؛
- در استفاده روزمره عملیاتی توصیه نمی‌شود؛
- برای پشتیبانی و مدیریت حساب‌ها نگهداری می‌شود.

---

# 5. ذخیره رمز

هیچ Password در Database یا Audit به‌صورت Plain Text ذخیره نمی‌شود.

قاعده پیاده‌سازی:

```text
PASSWORD_STORAGE = HASHED
```

مقدار Passwordهای این سند فقط مقدار Bootstrap/Initial Credential هستند.

---

# 6. اولین ورود کاربران

برای پنج کاربر عملیاتی:

```text
Initial Login
→ Force Password Change
→ New Personal Password
→ Main Application
```

تا قبل از تغییر Password اولیه، کاربر وارد Dashboard اصلی نمی‌شود.

---

# 7. تغییر رمز توسط کاربر

هر کاربر عملیاتی در منوی حساب خود گزینه:

```text
تغییر رمز عبور
```

دارد.

ورودی:

- رمز فعلی
- رمز جدید
- تکرار رمز جدید

پس از تغییر موفق:

- Session معتبر باقی می‌ماند یا طبق Policy جدید صادر می‌شود؛
- Password قبلی دیگر معتبر نیست؛
- رخداد در Audit ثبت می‌شود؛
- خود Password در Audit ذخیره نمی‌شود.

---

# 8. فراموشی رمز

SAMA دارای:

- بازیابی با ایمیل
- بازیابی با SMS
- سؤال امنیتی
- لینک Forgot Password

نیست.

فرآیند:

```text
کاربر رمز را فراموش می‌کند
↓
مراجعه به مدیر سامانه
↓
ورود با admin
↓
مدیریت کاربران
↓
انتخاب کاربر
↓
Reset Password
↓
تعیین Password موقت جدید
↓
MUST_CHANGE_PASSWORD = TRUE
↓
کاربر در ورود بعدی Password شخصی جدید تعیین می‌کند
```

---

# 9. محدودیت Reset Password

فقط:

```text
admin
```

حق Reset Password کاربران را دارد.

هیچ یک از پنج کاربر عملیاتی، حتی با دسترسی کامل عملیاتی، حق Reset Password حساب دیگر را ندارد.

---

# 10. Audit کاربران

Audit حداقل این رخدادها را ثبت می‌کند:

- Login موفق
- Logout
- Login ناموفق
- تغییر Password توسط خود کاربر
- Reset Password توسط admin
- ایجاد حساب
- غیرفعال/فعال کردن حساب

Audit شامل Password نمی‌شود.

---

# 11. هویت کاربر در Audit

برای هر عملیات مهم سامانه:

```text
UserID
Username
DisplayName
Timestamp
Action
Entity
RecordID
OldValue
NewValue
Reason / Context
```

حسب نوع عملیات ذخیره می‌شود.

نمایش پیشنهادی:

```text
sm.karimian — سید محمد کریمیان
```

---

# 12. ساختار اصلی Sitemap

```text
SAMA
├── Dashboard
├── فضاهای تجاری
│   ├── فعال
│   ├── از دور خارج‌شده
│   ├── پرونده فضا
│   └── جست‌وجوی کد فضا
├── املاک مادر
│   ├── فهرست
│   └── پرونده ملک مادر
├── بهره‌برداران
│   ├── فهرست
│   └── پرونده بهره‌بردار
├── قراردادها
│   ├── فهرست
│   └── پرونده قرارداد
├── کارشناسی
│   ├── کارشناسی‌ها
│   ├── کارشناسان
│   ├── ثبت کارشناسی جدید
│   ├── حق‌الزحمه کارشناسان
│   └── Batchهای ارسال به مالی
├── کمیسیون معاملات
│   ├── جلسات
│   ├── تصمیمات
│   └── اقدامات
├── مزایده
│   ├── Candidate Engine
│   ├── دوره‌های مزایده
│   ├── AuctionLotها
│   ├── اسناد مزایده
│   ├── دریافت پاکات
│   ├── جلسه بازگشایی
│   ├── ثبت نتیجه
│   └── آرشیو
├── انشعابات و مصرف
│   ├── دوره‌ها
│   ├── ثبت مصرف
│   └── گزارش‌ها
├── گزارش‌ها و تحلیل مدیریتی
│   ├── مرکز گزارش‌ها
│   ├── گزارش‌ساز
│   ├── Saved Reports
│   ├── Snapshots
│   ├── Data Quality
│   └── Audit Reports
├── جست‌وجوی سراسری
├── تنظیمات
│   ├── اطلاعات سازمان
│   ├── قواعد سالانه
│   ├── Templateها
│   └── تنظیمات عمومی
└── حساب کاربری
    ├── مشخصات
    ├── تغییر رمز
    └── خروج
```

---

# 13. Sitemap حساب Admin

برای `admin` یک گزینه اضافه وجود دارد:

```text
مدیریت کاربران
```

ساختار:

```text
Admin
├── مدیریت کاربران
│   ├── فهرست کاربران
│   ├── Reset Password
│   ├── فعال/غیرفعال کردن حساب
│   └── مشاهده وضعیت اولین ورود
└── سایر بخش‌های SAMA
```

---

# 14. ساختار Navigation

Navigation اصلی Desktop:

```text
Sidebar / Main Navigation
+
Top Command Area
+
Breadcrumb
+
Context Actions
```

منوی اصلی باید ساده و کوتاه باشد.

زیرمنوهای عمیق غیرضروری ممنوع است.

---

# 15. ترتیب پیشنهادی منوی اصلی

ترتیب اصلی:

1. داشبورد
2. فضاهای تجاری
3. املاک مادر
4. قراردادها
5. بهره‌برداران
6. کارشناسی
7. کمیسیون معاملات
8. مزایده
9. انشعابات و مصرف
10. گزارش‌ها
11. تنظیمات

جست‌وجوی سراسری باید مستقل و همیشه در دسترس باشد.

---

# 16. الگوی List → Profile

قاعده عمومی:

```text
List
→ Profile
→ Domain Tabs
```

مثال:

```text
فضاهای تجاری
→ کد فضا 378
→ پرونده جامع فضا
```

---

# 17. پرونده جامع فضا

تب‌های پیشنهادی:

```text
خلاصه
مشخصات
بهره‌بردار
قرارداد
کارشناسی
مزایده
کمیسیون
حق‌الزحمه
انشعابات
اسناد
تاریخچه
```

تب‌ها داده را Duplicate نمی‌کنند؛ فقط Read Model همان Entityهای اصلی هستند.

---

# 18. پرونده قرارداد

تب/بخش‌ها:

- مشخصات قرارداد
- کد فضا
- بهره‌بردار
- تاریخ‌ها
- اطلاعات مالی
- اسناد
- تاریخچه
- مزایده مبدأ در صورت وجود

---

# 19. پرونده بهره‌بردار

بخش‌ها:

- مشخصات
- قراردادهای جاری/تاریخی
- فضاهای مرتبط
- اسناد
- تاریخچه

---

# 20. پرونده کارشناسی

بخش‌ها:

- اطلاعات کارشناسی
- کارشناس
- کد فضا
- مبلغ کارشناسی
- سطح معامله
- وضعیت اعتبار مزایده
- حق‌الزحمه
- اسناد
- تاریخچه

---

# 21. پرونده کارشناس

بخش‌ها:

- مشخصات
- کارشناسی‌ها
- حق‌الزحمه‌ها
- پرداخت‌ها
- مناطق/مراکز مرتبط
- تاریخچه

---

# 22. پرونده مزایده

ساختار:

```text
AuctionPeriod
→ AuctionLot
→ SpaceCode
```

هر Lot یک SpaceCode مستقل دارد.

بخش‌ها:

- اطلاعات دوره
- وضعیت Candidate
- Readiness
- اسناد
- شرکت‌کنندگان
- پاکت‌ها
- جلسه بازگشایی
- نتیجه
- قرارداد حاصل
- Audit

---

# 23. جست‌وجوی کد فضا

Entry Point رسمی:

```text
جست‌وجوی کد فضا
```

شامل:

- SpaceCode
- Domain Selector
- Multi-select Domain
- «همه موارد»
- «نمایش پرونده کامل»

است.

Domainهای قابل انتخاب:

- مشخصات
- قرارداد
- بهره‌بردار
- کارشناسی
- مزایده
- کمیسیون
- حق‌الزحمه
- انشعابات
- اسناد
- Audit

---

# 24. جست‌وجوی سراسری

Global Search برای پیدا کردن Entity:

- SpaceCode
- نام فضا
- قرارداد
- بهره‌بردار
- کارشناس

است.

Global Search با SpaceCode Scoped Search یکی نیست.

---

# 25. Breadcrumb

تمام صفحات Detail باید Breadcrumb داشته باشند.

مثال:

```text
فضاهای تجاری
/
فعال
/
کد فضا 378
/
کارشناسی
```

---

# 26. حفظ Context

وقتی کاربر از:

```text
List
→ Profile
→ Back
```

برمی‌گردد:

- Filter
- Sort
- Page
- Search
- Scope

باید حفظ شوند.

---

# 27. Deep Link

صفحات اصلی و پرونده‌ها باید URL قابل Bookmark داشته باشند.

اما اطلاعات حساس یا Password در URL قرار نمی‌گیرند.

---

# 28. Action Placement

Actionهای اصلی باید Contextual باشند.

مثال در پرونده کارشناسی:

- ویرایش
- ثبت حق‌الزحمه
- مشاهده تاریخچه

نه اینکه همه Actionهای سامانه در یک Ribbon عمومی قرار گیرند.

---

# 29. ثبت اطلاعات مالی

اطلاعات مالی در هر Domain از اطلاعات عمومی متمایز است.

در UI:

```text
اطلاعات عمومی
≠
اطلاعات مالی
```

این جداسازی باید بصری و ساختاری باشد.

---

# 30. Zero-data

نسخه Production SAMA باید با Zero Data سالم اجرا شود.

هیچ Sample Data در:

- Dashboard
- Lists
- Profiles
- Reports

نمایش داده نمی‌شود.

---

# 31. Empty State

Empty State باید توضیح روشن داشته باشد.

مثال:

```text
هنوز هیچ کارشناسی برای این کد فضا ثبت نشده است.
```

---

# 32. Unauthorized State

برای کاربران عملیاتی عملاً اغلب بخش‌ها مجاز هستند.

اما Endpointهای Admin User Management باید برای آنها:

```text
403 / Unauthorized
```

باشد.

صرف مخفی کردن منو کافی نیست.

---

# 33. Error State

خطا باید با Empty State متفاوت باشد.

```text
No Data
≠
Error
```

---

# 34. Read-only State

اگر رکورد به‌علت Finalization یا Business Rule قابل ویرایش نیست:

- داده نمایش داده می‌شود؛
- علت Read-only واضح است؛
- Edit Action غیرفعال/حذف می‌شود.

---

# 35. Confirmations

برای عملیات حساس:

- تغییر Lifecycle
- Finalize AuctionPeriod
- ثبت نتیجه مزایده
- اصلاح بعد از پرداخت
- Reset Password

Confirmation روشن لازم است.

---

# 36. حذف فیزیکی

رکوردهای اصلی Business به‌صورت Physical Delete حذف نمی‌شوند.

در صورت نیاز از:

- Status
- Cancel
- Inactive
- Correction

استفاده می‌شود.

---

# 37. Session

پس از Login یک Session معتبر ایجاد می‌شود.

به‌دلیل LAN داخلی:

- MFA ندارد؛
- OTP ندارد؛
- Email Verification ندارد.

اما Login الزامی است.

---

# 38. Logout

کاربر باید بتواند دستی Logout کند.

بستن مرورگر جایگزین Logout رسمی نیست، ولی Session Policy می‌تواند با زمان انقضا مدیریت شود.

---

# 39. Session Timeout

برای جلوگیری از پیچیدگی غیرضروری، Session Timeout سخت‌گیرانه کوتاه توصیه نمی‌شود.

مقدار دقیق در Deployment Config تنظیم می‌شود.

هدف:

```text
Usability First
+
Reasonable Session Safety
```

---

# 40. Login UI

صفحه Login ساده است.

فیلدها:

```text
نام کاربری
رمز عبور
ورود
```

هیچ گزینه:

- ثبت‌نام
- فراموشی رمز
- ورود با موبایل
- ورود با ایمیل
- OTP

وجود ندارد.

---

# 41. نمایش هویت کاربر

پس از ورود، در Header نمایش داده می‌شود:

```text
نام کامل
|
سمت
```

مثال:

```text
سید محمد کریمیان | مسئول دفتر مدیریت اقتصادی و املاک
```

---

# 42. مدیریت کاربران توسط Admin

Admin صفحه‌ای ساده دارد با ستون‌های:

- نام کامل
- Username
- سمت
- وضعیت حساب
- وضعیت Change Password
- آخرین ورود
- Reset Password

---

# 43. ایجاد کاربر جدید

اگر در آینده کاربر جدید اضافه شود:

- فقط Admin ایجاد می‌کند؛
- Username یکتا است؛
- Password اولیه تعیین می‌شود؛
- `MUST_CHANGE_PASSWORD = TRUE`.

این کار نیاز به تغییر Role Model ندارد.

---

# 44. غیرفعال کردن کاربر

در صورت خروج کاربر از مجموعه:

```text
Active = FALSE
```

می‌شود.

Audit تاریخی او حفظ می‌شود.

Username قبلی برای Audit تغییر داده نمی‌شود.

---

# 45. تغییر نام/سمت

نام و سمت قابل اصلاح هستند.

Username ترجیحاً ثابت می‌ماند تا Audit پیوسته باقی بماند.

در صورت اجبار به تغییر Username، تاریخچه باید حفظ شود.

---

# 46. امنیت LAN

مدل امنیت این پروژه عمداً سبک است.

موارد لازم:

- Login
- Password Hash
- Named Users
- Server-side Admin Restriction
- Audit
- Session
- Input Validation

موارد خارج از Scope فعلی:

- MFA
- SSO سازمانی
- Complex RBAC
- IP-based ACL
- Device Certificate
- Security Questions
- SMS Recovery

---

# 47. اصل Audit over Complexity

با توجه به تیم 5 نفره:

> هدف اصلی Authentication، تفکیک هویت کاربران و ثبت دقیق عملیات است؛ نه ساخت سیستم امنیتی پیچیده.

---

# 48. Admin Audit

عملیات Admin نیز Audit می‌شود.

مثال:

```text
admin reset password for a.majidi
```

بدون ثبت Password جدید.

---

# 49. Navigation در LAN

تمام صفحات از Chrome/Edge قابل استفاده هستند.

هیچ مسیر Navigation نباید وابسته به نصب Client باشد.

---

# 50. ساختار URL پیشنهادی

نمونه:

```text
/dashboard
/spaces/active
/spaces/out-of-cycle
/spaces/{space_code}
/contracts
/contracts/{id}
/beneficiaries
/beneficiaries/{id}
/appraisals
/experts
/expert-fees
/commissions
/auctions
/auctions/{period_id}
/reports
/search/space
/settings
/account
/admin/users
```

نام نهایی Route در Implementation می‌تواند متفاوت باشد، اما IA باید همین معنا را حفظ کند.

---

# 51. معیار پذیرش Navigation

```text
Dead-end Page = 0
Broken Back Context = 0
Hidden Required Action = 0
Duplicate Business Data Entry = 0
Unclear Current Scope = 0
Unauthorized Admin Access = 0
Anonymous Operational Access = 0
```

---

# 52. تصمیم‌های نهایی FROZEN

1. پنج کاربر عملیاتی نام‌دار داریم.
2. همه پنج کاربر دسترسی عملیاتی کامل و یکسان دارند.
3. Role عملیاتی پیچیده وجود ندارد.
4. هر کاربر Username/Password مستقل دارد.
5. کاربران در اولین ورود باید Password اولیه را تغییر دهند.
6. کاربر می‌تواند Password خودش را تغییر دهد.
7. Forgot Password عمومی وجود ندارد.
8. فقط `admin` می‌تواند Password کاربران را Reset کند.
9. Reset Password باعث اجبار تغییر رمز در ورود بعدی می‌شود.
10. Username حساب فنی `admin` است.
11. Password ثابت حساب admin مقدار مصوب این سند است.
12. Password حساب admin از UI عادی تغییر نمی‌کند.
13. Passwordها Hash می‌شوند.
14. Password در Audit ذخیره نمی‌شود.
15. تمام عملیات Business با هویت User ثبت می‌شوند.
16. Admin User Management تنها بخش دسترسی متفاوت با کاربران عملیاتی است.
17. Sitemap بر الگوی List → Profile → Domain Tabs ساخته می‌شود.
18. پرونده جامع SpaceCode مرکز Navigation داده‌های مرتبط است.
19. SpaceCode Scoped Search Entry Point رسمی است.
20. Report Center و Dashboard با Navigation یکپارچه هستند.
21. Filter/Scope در رفت‌وبرگشت حفظ می‌شود.
22. Deep Link پشتیبانی می‌شود.
23. Zero-data State رسمی است.
24. مکاتبات عمومی خارج از Scope سامانه است.
25. امنیت LAN ساده و متناسب با محیط داخلی باقی می‌ماند.
26. MFA، OTP، Email/SMS Recovery و Complex RBAC خارج از Scope هستند.
27. حذف فیزیکی سوابق اصلی Business انجام نمی‌شود.
28. Admin نیز Audit می‌شود.

---

# 53. وضعیت سند

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

**پایان سند — MD معماری اطلاعات، Sitemap، Navigation و کاربران — SAMA**
