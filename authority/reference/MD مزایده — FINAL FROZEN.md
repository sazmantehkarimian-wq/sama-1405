# MD مزایده — SAMA

**پروژه:** سامانه املاک سازمان فرهنگی هنری شهرداری تهران (SAMA)  
**حوزه:** مزایده، تشخیص کاندیدا، تولید اسناد، جلسه بازگشایی و ثبت نتیجه  
**وضعیت:** `FROZEN SPECIFICATION — IMPLEMENTATION GATED`  
**قاعده:** قواعد کسب‌وکار و تشخیص کاندیدا در این سند تثبیت شده‌اند. با این حال، هیچ کدنویسی Production برای Document Engine و خروجی‌های رسمی تا عبور موفق بسته‌های نمونه از آزمون چاپ و تأیید Golden Master مجاز نیست.

---

# 1. اهمیت و جایگاه ماژول مزایده

ماژول مزایده قلب عملیاتی SAMA است.

این ماژول مسئول است:

1. شناسایی خودکار فضاهای کاندیدای مزایده؛
2. توضیح دقیق دلیل ورود یا عدم ورود هر کد فضا؛
3. تشکیل دوره مزایده؛
4. انتخاب رسمی کدهای فضا برای دوره؛
5. کنترل آمادگی اطلاعات و مدارک؛
6. تولید خودکار تمام اسناد سازمانی؛
7. ثبت دریافت پیشنهادها و پاکت‌ها؛
8. پشتیبانی اطلاعاتی جلسه بازگشایی؛
9. ثبت نتیجه اعلام‌شده توسط اعضای جلسه؛
10. تولید صورتجلسه و PowerPoint؛
11. اتصال نتیجه مزایده به قرارداد جدید؛
12. حفظ Snapshot، تاریخچه و Audit کامل.

کوچک‌ترین خطای خاموش در شناسایی کاندیدا یا تکمیل اسناد غیرقابل قبول است.

---

# 2. اصل بنیادین موتور تشخیص مزایده

موتور تشخیص کاندیدای مزایده باید:

- قطعی و Deterministic باشد؛
- Rule-based باشد؛
- بدون حدس باشد؛
- از هوش مصنوعی مولد برای تصمیم Eligibility استفاده نکند؛
- نسخه Rule مؤثر را ثبت کند؛
- برای هر تصمیم Reason Code تولید کند؛
- تمام ورودی‌های مؤثر را Snapshot کند؛
- قابل بازآزمایی باشد؛
- در داده ناقص، فضای محتمل را بی‌صدا حذف نکند.

---

# 3. سه مفهوم مستقل

این سه مفهوم نباید با یکدیگر ادغام شوند:

## 3.1 کاندیدای خودکار

فضایی که بر اساس Ruleهای سامانه در فهرست بررسی مزایده قرار گرفته است.

```text
AUTO_CANDIDATE
```

## 3.2 انتخاب‌شده برای دوره

فضایی که کاربر مجاز آن را رسماً وارد یک AuctionPeriod کرده است.

```text
SELECTED_FOR_PERIOD
```

## 3.3 آماده برگزاری

فضایی که تمام کنترل‌های ضروری پیش از برگزاری مزایده را پاس کرده است.

```text
READY_FOR_AUCTION
```

کاندیدا بودن به معنی آماده بودن نیست.

---

# 4. خروجی ایمن موتور تشخیص

موتور تشخیص نباید فقط `TRUE / FALSE` داشته باشد.

خروجی پایه:

```text
CANDIDATE
NOT_CANDIDATE
REVIEW_REQUIRED
```

و جدا از آن:

```text
READY
ACTION_REQUIRED
REVIEW_REQUIRED
```

برای آمادگی مزایده نگهداری می‌شود.

## 4.1 اصل Fail-Safe

اگر داده لازم برای تصمیم قطعی ناقص یا متناقض باشد:

> فضا نباید از فهرست بررسی ناپدید شود.

خروجی:

```text
REVIEW_REQUIRED
```

همراه با علت دقیق.

---

# 5. دامنه اولیه بررسی خودکار

منبع اصلی بررسی کاندیدا:

```text
CommercialSpace
```

فقط کدهای فضای تجاری که وضعیت جاری آنها «فعال» است در موتور خودکار بررسی می‌شوند.

فضای «از دور خارج‌شده» به‌طور خودکار وارد فهرست کاندیدا نمی‌شود.

رابطه با ملک مادر در Eligibility عملیاتی مزایده نقشی ندارد.

---

# 6. مسیرهای اصلی ورود به مزایده

دو مسیر پایه وجود دارد:

```text
A) دارای قرارداد جاری
B) فاقد قرارداد جاری
```

هیچ‌کدام از این دو گروه به‌تنهایی مانع مزایده نیستند.

---

# 7. مسیر A — فضای دارای قرارداد جاری

برای فضای دارای قرارداد جاری، موتور این موارد را بررسی می‌کند:

1. وضعیت فضای تجاری = فعال؛
2. قرارداد جاری معتبر وجود دارد؛
3. بازه زمانی پایان قرارداد مطابق Rule جاری است؛
4. سطح معامله از مبلغ قرارداد جاری محاسبه می‌شود؛
5. سایر Ruleهای بازدارنده یا Override بررسی می‌شوند؛
6. وضعیت کارشناسی برای آمادگی برگزاری کنترل می‌شود.

---

# 8. بازه زمانی قرارداد

قاعده جاری:

```text
حداقل روز مانده = 1
حداکثر روز مانده = 90
شامل 1 = بله
شامل 90 = بله
```

یعنی:

```text
1 <= RemainingDays <= 90
```

این Rule Hard-code نیست.

در Rule Registry قابل ویرایش است.

برای هر تغییر:

- مقدار قبلی؛
- مقدار جدید؛
- تاریخ اثر؛
- کاربر؛
- تاریخ و ساعت؛
- علت تغییر؛
- Audit

ثبت می‌شود.

---

# 9. تست مرزی Rule زمانی

این حالات باید به‌صورت Automated Test وجود داشته باشند:

```text
90 روز مانده → داخل Rule
91 روز مانده → خارج Rule
1 روز مانده → داخل Rule
0 روز مانده → خارج Rule مسیر قراردادِ 1..90
```

قاعده قطعی:

> در روز پایان قرارداد، قرارداد هنوز در همان روز «جاری» محسوب می‌شود؛ اما چون `RemainingDays = 0` است، از Rule بازه 1 تا 90 روز عبور نمی‌کند.

> از روز تقویمی بعد از تاریخ پایان قرارداد، قرارداد دیگر جاری نیست و فضای مربوط از مسیر «فاقد قرارداد جاری» بررسی می‌شود.

اگر فضای مربوط قبلاً به یک AuctionPeriod رسمی وارد شده باشد، تغییر روز شمار نباید آن Lot را به‌صورت خودکار از دوره حذف کند.

---


# 9.1 قاعده ماندگاری کاندیدا (Sticky Candidate)

این قاعده قطعی است:

> هر کد فضایی که یک‌بار بر اساس Ruleهای معتبر به‌درستی وارد فهرست `CANDIDATE` شده باشد، صرف گذشت زمان و رسیدن قرارداد به روز پایان یا عبور از آن، از فهرست کاندیدا حذف نمی‌شود.

Trigger ورود:

```text
1 تا 90 روز مانده به پایان قرارداد
→ Candidate
```

ماندگاری:

```text
Candidate ایجادشده
→ روز پایان قرارداد
→ همچنان Candidate

از روز بعد پایان قرارداد
→ وضعیت قرارداد = فاقد قرارداد جاری
→ Candidate همچنان باقی می‌ماند
→ کنترل‌های بعدی بر اساس کارشناسی معتبر و سایر Ruleها ادامه پیدا می‌کند
```

حذف یا تعیین تکلیف Candidate فقط از مسیرهای رسمی مجاز است؛ از جمله:

- انتخاب و ورود به دوره رسمی مزایده؛
- Manual Exclude / دستور معتبر؛
- تغییر Lifecycle فضا به «از دور خارج‌شده»؛
- کشف و اصلاح خطای داده‌ای که نشان دهد Candidate اولیه به اشتباه ایجاد شده؛
- تعیین تکلیف رسمی دیگری که در Rule Registry تعریف شده باشد.

رسیدن `RemainingDays` به صفر یا منفی **به‌تنهایی مجوز حذف Candidate نیست**.

# 10. مسیر B — فضای فاقد قرارداد جاری

فاقد قرارداد بودن مانع مزایده نیست.

مسیر:

```text
Active CommercialSpace
→ No Current Contract
→ Latest Valid Appraisal
→ Transaction Level
→ Other Rules
→ Candidate Decision
```

فضایی که قرارداد قبلی آن پایان یافته و دیگر قرارداد جاری ندارد، از همین مسیر بررسی می‌شود.

---

# 11. فضای فاقد بهره‌بردار

فاقد بهره‌بردار بودن مانع ورود به مزایده نیست.

اگر قرارداد جاری وجود ندارد:

```text
Valid Appraisal
→ Transaction Level
→ Other Rules
```

مبنای تصمیم است.

---

# 12. سطح معامله

سطوح:

- جزء
- متوسط
- عمده

Thresholdها سالانه و در Rule Registry نگهداری می‌شوند.

## 12.1 فضای دارای قرارداد جاری

مبنا:

```text
Current Contract Amount
```

## 12.2 فضای فاقد قرارداد جاری

مبنا:

```text
Latest Valid Appraisal Amount
```

سامانه باید همیشه همراه سطح معامله، منبع و مبلغ مبنا را نمایش دهد.

---

# 13. سطوح واجد ورود خودکار

سطوح واجد ورود خودکار:

```text
متوسط
عمده
```

سطح «جزء» به‌طور خودکار وارد فهرست کاندیدا نمی‌شود؛ مگر Rule یا Override رسمی جداگانه‌ای تصویب شود.

## 13.1 مرزهای نمونه سال 1405

مبنای نگهداری مبلغ در سامانه: **ریال**.

با آستانه مصوب نمونه:

```text
حد جزء = 350,000,000 ریال
         = 35,000,000 تومان
```

قاعده مرزی:

```text
جزء:
Amount <= 350,000,000 IRR

متوسط:
350,000,000 IRR < Amount <= 3,500,000,000 IRR

عمده:
Amount > 3,500,000,000 IRR
```

بنابراین خود مبلغ `350,000,000 ریال` (35 میلیون تومان) در سطح «جزء» قرار می‌گیرد و خود مبلغ `3,500,000,000 ریال` در سطح «متوسط» قرار می‌گیرد.

Thresholdها سالانه و Versioned هستند و اعداد سال 1405 نباید در کد Hard-code شوند.

---

# 14. کارشناسی و مزایده

قاعده قطعی:

> اعتبار کارشناسی برای مزایده = 6 ماه تقویمی از تاریخ خود کارشناسی

با توجه به تقویم عملیاتی سامانه، محاسبه بر اساس ماه‌های تقویمی شمسی انجام می‌شود.

مبنای تاریخ اعتبار:

```text
AppraisalDate
```

قاعده:

```text
ExpiryDate = AppraisalDate + 6 calendar months
```

خود `ExpiryDate` آخرین روز معتبر است و از روز بعد کارشناسی برای مزایده منقضی محسوب می‌شود.

فایل کارشناسی الزامی نیست.

تاریخ نامه پاسخ یا تاریخ ورود اطلاعات در SAMA مبنای اعتبار نیست.

---

# 15. نقش کارشناسی در دو مسیر

## 15.1 فاقد قرارداد

بدون کارشناسی معتبر، مبلغ مبنا و سطح معامله قابل اتکا نیست.

اگر کارشناسی وجود نداشته یا منقضی باشد:

```text
REVIEW_REQUIRED / ACTION_REQUIRED
```

و فضا نباید بی‌صدا حذف شود.

## 15.2 دارای قرارداد جاری

قرارداد می‌تواند Trigger زمانی و مبنای سطح را تعیین کند.

اما برای برگزاری واقعی مزایده، کارشناسی معتبر موردنیاز است.

بنابراین فضای دارای قرارداد می‌تواند:

```text
CANDIDATE
+
ACTION_REQUIRED: NEW_APPRAISAL
```

باشد.

---

# 16. اعتبار کارشناسی در تاریخ برگزاری

کنترل فقط بر اساس «امروز» کافی نیست.

سامانه باید بررسی کند کارشناسی در تاریخ برنامه‌ریزی‌شده برگزاری مزایده نیز معتبر باشد.

نمونه:

```text
Today: Valid
Auction Date: Expired
→ ACTION_REQUIRED
```

---

# 17. تاریخچه کارشناسی

برای Eligibility فقط کارشناسی مرجع معتبر استفاده می‌شود.

کارشناسی‌های تاریخی:

- حذف نمی‌شوند؛
- برای Audit باقی می‌مانند؛
- نباید به اشتباه جای کارشناسی جاری استفاده شوند.

---

# 18. Ruleهای دستی و دستورات سازمانی

سامانه باید ظرفیت این موارد را داشته باشد:

- دستور کمیسیون؛
- دستور مدیر؛
- ورود دستی مجاز؛
- سایر Overrideهای رسمی.

## 18.1 اعتبار دستور کمیسیون و مدیر

دستور کمیسیون و دستور مدیر هر دو **معتبر و هم‌تراز از نظر اعتبار ثبتی در سامانه** هستند.

هیچ‌کدام به‌صورت خودکار دیگری را رد، لغو یا Override نمی‌کند.

سامانه نباید Priority مخفی میان این دو منبع تعریف کند.

اگر دو دستور درباره یک کد فضا، یک بازه اثر و یک موضوع، نتیجه متعارض ایجاد کنند:

```text
CONFLICTING_AUTHORIZED_INSTRUCTIONS
→ REVIEW_REQUIRED
```

سامانه حق انتخاب یکی از آنها را ندارد.

تا رفع تعارض با مرجع رسمی، تصمیم خودکار Final نمی‌شود.

هر Override باید:

- نوع؛
- جهت اثر؛
- علت؛
- مرجع؛
- شماره/شناسه مستند در صورت وجود؛
- تاریخ اثر؛
- کاربر؛
- Audit

داشته باشد.

هیچ Override ناشناس یا بدون دلیل پذیرفته نمی‌شود.

---

# 19. Manual Inclusion / Manual Exclusion

در معماری دو مفهوم مستقل وجود دارد:

```text
MANUAL_INCLUDE
MANUAL_EXCLUDE
```

دستور معتبر کمیسیون و دستور معتبر مدیر می‌توانند حسب محتوای خود موجب Inclusion یا Exclusion شوند.

هیچ‌یک بر دیگری اولویت خودکار ندارد.

در صورت تعارض مستقیم:

```text
REVIEW_REQUIRED
```

و سامانه از تصمیم خودکار خودداری می‌کند.

ورود دستی مجاز نیز فقط با Permission، علت، مرجع و Audit قابل انجام است.

---

# 20. قرارداد بلندمدت

قاعده تعریف:

```text
LongTerm = ContractDuration > 365 days
```

قاعده قطعی Eligibility:

> مدت اولیه قرارداد هیچ اثر بازدارنده‌ای بر ورود به مزایده ندارد.

اگر هر قرارداد جاری، خواه یک‌ساله، سه‌ساله، پنج‌ساله یا بیشتر، وارد بازه:

```text
1..90 days remaining
```

شود، مانند سایر قراردادها بررسی می‌شود.

بنابراین `is_long_term` صرفاً یک ویژگی اطلاعاتی/گزارشی است و **Exclusion Rule مزایده نیست**.

---

# 21. فضای فعال و وضعیت ملک مادر

وضعیت ملک مادر:

- در Eligibility فضای تجاری اثر عملیاتی ندارد؛
- نباید باعث حذف خودکار کد فضا شود؛
- رابطه ParentProperty صرفاً تطبیقی / گزارشی است.

---

# 22. وضعیت «0 روز مانده»

قاعده قطعی:

```text
RemainingDays = 0
→ خارج از Rule 1..90
```

در خود تاریخ پایان، قرارداد همان روز جاری محسوب می‌شود.

از **روز بعد**:

```text
CurrentContract = None
```

و فضا از مسیر «فاقد قرارداد جاری» بررسی می‌شود.

این Rule باید Test مرزی مستقل داشته باشد.

---

# 23. قرارداد پایان‌یافته

پس از پایان قرارداد، اگر Contract دیگر جاری محسوب نشود:

```text
No Current Contract
```

و فضا از مسیر فاقد قرارداد بررسی می‌شود.

در این حالت:

```text
Latest Valid Appraisal
+
Transaction Level
```

مبنای اصلی است.

---

# 24. قرارداد با بیش از 90 روز باقی‌مانده

به‌طور خودکار کاندیدا نیست.

Reason Code:

```text
NOT_CANDIDATE_CONTRACT_OUTSIDE_WINDOW
```

مگر Override رسمی وجود داشته باشد.

---

# 25. فضای از دور خارج‌شده

به‌صورت خودکار کاندیدا نیست.

Reason Code:

```text
NOT_CANDIDATE_SPACE_OUT_OF_CYCLE
```

بازگشت آن به Active باید ابتدا از Lifecycle خود فضای تجاری انجام شود.

---

# 26. جلوگیری از حذف خاموش به دلیل داده ناقص

نمونه‌های داده ناقص:

- مبلغ قرارداد خالی؛
- تاریخ پایان قرارداد خالی؛
- کارشناسی مرجع نامشخص؛
- Threshold سال موجود نیست؛
- دو رکورد متناقض؛
- Rule مؤثر یافت نشد.

خروجی:

```text
REVIEW_REQUIRED
```

نه `NOT_CANDIDATE`.

---

# 27. Reason Code

هر تصمیم باید کد دلیل داشته باشد.

نمونه:

```text
CANDIDATE_CONTRACT_WINDOW
CANDIDATE_NO_CONTRACT_VALID_APPRAISAL
NOT_CANDIDATE_LEVEL_JOZ
NOT_CANDIDATE_OUTSIDE_TIME_WINDOW
NOT_CANDIDATE_SPACE_OUT_OF_CYCLE
REVIEW_MISSING_CONTRACT_AMOUNT
REVIEW_MISSING_APPRAISAL
REVIEW_MISSING_YEAR_RULE
ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION
BLOCKED_BY_MANUAL_EXCLUSION
INCLUDED_BY_MANUAL_OVERRIDE
```

Reason Codeها Reference Data / Rule Registry کنترل‌شده هستند.

---

# 28. Explainability

برای هر کد فضا کاربر باید بتواند صفحه «چرا؟» را باز کند.

مثال:

```text
کد فضا: 378
وضعیت: CANDIDATE

علت:
- وضعیت فضا: فعال
- قرارداد جاری: دارد
- روز مانده: 47
- Rule زمانی: 1..90
- مبلغ مبنا: قرارداد
- سطح معامله: متوسط
- کارشناسی: معتبر تا ...
- Override: ندارد
```

هیچ تصمیم غیرقابل توضیح پذیرفته نیست.

---

# 29. Snapshot تصمیم

هنگام اجرای Candidate Engine ذخیره می‌شود:

- SpaceCode
- SpaceStatus
- ContractID
- ContractStart
- ContractEnd
- RemainingDays
- ContractAmount
- AppraisalID
- AppraisalDate
- AppraisalAmount
- TransactionLevel
- ThresholdRuleVersion
- AuctionRuleVersion
- Override State
- Decision
- Reason Codes
- EvaluationTimestamp
- EngineVersion

---

# 30. عدم استفاده از AI برای Eligibility

مدل زبانی یا AI مولد:

- حق تعیین کاندیدا ندارد؛
- حق تغییر Rule ندارد؛
- حق حدس مبلغ یا تاریخ ندارد؛
- حق پر کردن داده مفقود ندارد.

AI فقط می‌تواند در آینده برای:

- توضیح قابل فهم Rule؛
- جست‌وجوی اسناد؛
- کمک نگارشی غیرحقوقی

استفاده شود.

Decision Engine مستقل و Deterministic است.

---

# 31. Decision Table نسخه‌بندی‌شده

منطق تشخیص باید به‌صورت جدول تصمیم نسخه‌بندی‌شده نگهداری شود.

نمونه مفهومی:

| Active | Current Contract | Days | Level | Appraisal | Override | نتیجه |
|---|---|---|---|---|---|---|
| خیر | * | * | * | * | * | NOT_CANDIDATE |
| بله | بله | 1..90 | متوسط/عمده | معتبر | ندارد | CANDIDATE/READY |
| بله | بله | 1..90 | متوسط/عمده | منقضی | ندارد | CANDIDATE/ACTION_REQUIRED |
| بله | خیر | N/A | متوسط/عمده | معتبر | ندارد | CANDIDATE |
| بله | خیر | N/A | نامشخص | مفقود | ندارد | REVIEW_REQUIRED |

جدول کامل Production باید همه ترکیبات معتبر را پوشش دهد.

---

# 32. تغییر Rule

هیچ Rule Production مستقیماً overwrite نمی‌شود.

چرخه:

```text
DRAFT
→ REVIEW
→ APPROVED
→ EFFECTIVE
→ RETIRED
```

Ruleهای قبلی برای Audit باقی می‌مانند.

---

# 33. کنترل دو نفره Ruleهای حساس

برای Ruleهای حیاتی پیشنهاد می‌شود تغییر به‌صورت Four-Eyes انجام شود:

```text
Editor
+
Approver
```

حداقل برای:

- بازه روزهای قرارداد؛
- Threshold سطح معامله؛
- اعتبار کارشناسی؛
- Override permissions؛
- Ruleهای Inclusion/Exclusion.

---

# 34. یک فضای واحد در چند دوره باز

سامانه باید از ورود ناخواسته هم‌زمان یک کد فضا به چند AuctionPeriod باز جلوگیری کند.

اگر دوره قبلی هنوز مختومه یا لغو نشده باشد:

```text
REVIEW_REQUIRED / BLOCK
```

نمایش داده می‌شود.

استثنا فقط با Override رسمی.

---

# 35. مزایده قبلی بدون نتیجه

فضایی که مزایده قبلی آن بدون نتیجه خاتمه یافته می‌تواند در دوره جدید دوباره بررسی شود.

اما دوره قبلی باید وضعیت نهایی مشخص داشته باشد.

هیچ سابقه‌ای overwrite نمی‌شود.

---

# 36. تشکیل دوره مزایده

موجودیت:

```text
AuctionPeriod
```

حداقل:

- کد دوره؛
- عنوان؛
- سال؛
- مجوز؛
- تاریخ‌های مهم؛
- وضعیت؛
- فهرست Lotها؛
- Template Versionها؛
- اعضای جلسه؛
- اسناد؛
- نتایج؛
- Snapshot؛
- Audit.

---

# 37. AuctionLot

هر کد فضای انتخاب‌شده در هر دوره یک رکورد مستقل دارد:

```text
AuctionLot
```

شامل:

- کد فضا؛
- Snapshot اطلاعات؛
- قیمت پایه؛
- سپرده؛
- مدت واگذاری؛
- سرمایه‌گذاری؛
- نوع بسته اسناد؛
- وضعیت آمادگی؛
- پیشنهادها؛
- نتیجه؛
- Contract Link.

---

# 38. انتخاب رسمی کدهای دوره

دو روش:

1. انتخاب از Candidate List؛
2. افزودن دستی توسط کاربر مجاز.

ورود دستی باید Audit شود.

سامانه نباید فهرست رسمی دوره را فقط از خروجی خودکار بسازد بدون تأیید کاربر مجاز.

---

# 39. کنترل آمادگی

Readiness Checklist حداقل شامل:

- Space identity complete؛
- Active status؛
- Auction basis known؛
- Appraisal valid for auction date؛
- Base amount known؛
- Transaction level known؛
- Security deposit known؛
- Duration known؛
- Investment amount known if applicable؛
- Required organizational data complete؛
- Correct document package selected؛
- No unresolved critical placeholder؛
- No conflicting open AuctionPeriod.

---

# 40. اسناد رسمی مرجع

Corpus فعلی مرجع شامل:

- شرایط عمومی و اختصاصی فضای تجاری؛
- شرایط عمومی و اختصاصی فضای کافه؛
- شرایط عمومی و اختصاصی فضای ورزشی؛
- روکش پاکت الف؛
- روکش پاکت ب؛
- روکش پاکت ج؛
- فرمت خام صورتجلسه بازگشایی؛
- PowerPoint جلسه مزایده 1405.

این فایل‌ها منبع بازسازی Master Template هستند.

---

# 41. اصل عدم تغییر متن رسمی

پس از تأیید Master:

> سامانه حق بازنویسی، خلاصه‌سازی، حذف، افزودن یا تغییر معنایی متن رسمی را ندارد.

مجاز:

- رفع غلط تایپی روشن در مرحله آماده‌سازی Master؛
- نیم‌فاصله؛
- فاصله؛
- علائم نگارشی؛
- یکدست‌سازی فونت؛
- اندازه عنوان؛
- Border؛
- فاصله سطر؛
- حاشیه؛
- اصلاحات ظاهری بدون تغییر مفهوم.

هر تغییر معنایی نیازمند Template Version جدید و تأیید رسمی است.

---

# 42. Master Template

برای هر سند یک Master مستقل وجود دارد.

هر Master دارای:

```text
TemplateID
TemplateType
TemplateVersion
SourceDocument
ApprovedAt
ApprovedBy
Hash
PageCount
FieldMap
Status
```

است.

---

# 43. Field Registry

تمام اطلاعات قابل تکمیل Field ID یکتا دارند.

نمونه:

```text
ORG-001    نام سازمان
ORG-002    نشانی سازمان
ORG-003    حساب بانکی

SPACE-001  کد فضا
SPACE-002  نام فضا
SPACE-003  منطقه
SPACE-004  مرکز
SPACE-005  نشانی
SPACE-006  کاربری
SPACE-007  متراژ

APP-001    تاریخ کارشناسی
APP-002    مبلغ کارشناسی

AUC-001    کد دوره
AUC-002    تاریخ آگهی
AUC-003    مهلت دریافت پیشنهاد
AUC-004    تاریخ بازگشایی
AUC-005    ساعت جلسه
AUC-006    محل جلسه

LOT-001    قیمت پایه
LOT-002    سپرده
LOT-003    مدت واگذاری
LOT-004    مبلغ سرمایه گذاری

SESSION-001 مجوز برگزاری
SESSION-002 شماره دعوتنامه
```

---

# 44. Field ID در سند چاپی

Field IDها در خروجی رسمی چاپ نمی‌شوند.

آنها فقط:

- در Template؛
- Field Map؛
- QA Mode

وجود دارند.

---

# 45. Single Source of Truth

هر Field فقط یک منبع رسمی دارد.

نمونه:

```text
SPACE-001
← CommercialSpace.space_code
```

```text
LOT-001
← AuctionLot.base_amount_snapshot
```

```text
AUC-004
← AuctionPeriod.opening_date
```

Template حق انتخاب منبع جایگزین ندارد.

---

# 46. اطلاعات ثابت سازمان

یک صفحه مرکزی «مشخصات سازمان و مزایده» وجود دارد.

شامل:

- نام سازمان؛
- واحد سازمانی؛
- نشانی؛
- تلفن؛
- بانک؛
- شماره حساب؛
- لوگو؛
- اطلاعات دبیرخانه؛
- اطلاعات مصوب دیگر.

کاربر یک بار داده را ثبت می‌کند و تمام اسناد از همان منبع تکمیل می‌شوند.

---

# 47. اطلاعات دوره

در همان صفحه یا بخش مستقل:

- مجوز برگزاری؛
- شماره نامه / گردش؛
- تاریخ آگهی؛
- رسانه انتشار؛
- تاریخ شروع فروش اسناد؛
- مهلت تحویل؛
- تاریخ جلسه؛
- ساعت؛
- محل؛
- شماره دعوتنامه؛
- اعضای جلسه.

---

# 48. اطلاعات فضا

از CommercialSpace / AuctionLot Snapshot:

- کد؛
- نام؛
- منطقه؛
- مرکز؛
- نشانی؛
- کاربری؛
- متراژ؛
- قیمت پایه؛
- سپرده؛
- مدت؛
- سرمایه‌گذاری؛
- توضیح مصوب.

---

# 49. اطلاعات شرکت‌کننده

در اسناد اولیه‌ای که برای متقاضی صادر می‌شوند، اطلاعات Participant عمداً خالی می‌ماند.

Policy:

```text
BLANK_FOR_PARTICIPANT
```

سامانه نباید این Blankها را به‌عنوان خطا در Finalization اسناد اولیه تلقی کند.

---

# 50. پاکت الف

اطلاعات سازمانی و Lot خودکار پر می‌شوند.

اطلاعات متقاضی خالی می‌ماند.

بخش دبیرخانه در مرحله دریافت پیشنهاد توسط کاربر ثبت می‌شود.

---

# 51. پاکت ب

همان قاعده:

- مشخصات مزایده و فضا → خودکار؛
- مشخصات متقاضی → خالی در نسخه اولیه؛
- تحویل دبیرخانه → در زمان دریافت.

Checklist مدارک بر اساس Template مصوب همان نوع فضا تولید می‌شود.

---

# 52. پاکت ج

مشخصات فضای مزایده خودکار.

مشخصات شرکت‌کننده و مبلغ پیشنهادی در نسخه توزیع‌شونده خالی.

---

# 53. صورتجلسه بازگشایی

اطلاعات قبل از جلسه باید خودکار تکمیل شوند:

- عنوان مزایده؛
- کد فضا؛
- مجوز؛
- مدت؛
- قیمت پایه؛
- سرمایه‌گذاری؛
- سپرده؛
- تاریخ آگهی؛
- دعوتنامه؛
- تاریخ؛
- ساعت؛
- محل؛
- اعضای جلسه.

اطلاعات پاکت‌ها از ثبت‌های همان جلسه وارد می‌شوند.

---

# 54. نقش SAMA در پاکت‌ها

SAMA اطلاعات را ثبت و Workflow را کنترل می‌کند.

SAMA حق ندارد مستقلاً:

- صلاحیت حقوقی Participant را تعیین کند؛
- پیشنهاد را رد حقوقی کند؛
- برنده را محاسبه کند.

نتیجه بررسی توسط اعضای جلسه ثبت می‌شود.

---

# 55. پاکت ج و نتیجه پاکت ب

در اسناد فعلی Rule وجود دارد که در برخی شرایط پاکت ج بازگشایی نمی‌شود.

سامانه این تصمیم را از خودش صادر نمی‌کند.

Workflow:

```text
Commission Decision on Envelope B
→ Recorded
→ C Opening Allowed / Not Allowed
```

---

# 56. Participant

Participant موجودیت مستقل عملیاتی است.

ثبت Participant به معنی Beneficiary شدن نیست.

فقط در صورت ایجاد Contract، ارتباط بعدی برقرار می‌شود.

---

# 57. دریافت پیشنهاد

برای هر پیشنهاد:

- Participant؛
- Lot؛
- تاریخ و ساعت دریافت؛
- شماره رسید؛
- پاکت‌ها؛
- ثبت‌کننده؛
- توضیحات؛
- Audit.

---

# 58. جلسه بازگشایی

Entity:

```text
AuctionOpeningSession
```

شامل:

- Session metadata؛
- Members Snapshot؛
- Lot list؛
- Envelope records؛
- Declared results؛
- Minutes؛
- Signatures metadata؛
- Audit.

---

# 59. نتیجه مزایده

فیلد:

```text
DeclaredResult
```

مفهوم:

> نتیجه اعلام‌شده توسط اعضای جلسه.

نه نتیجه محاسبه‌شده توسط SAMA.

---

# 60. برنده اعلام‌شده

در صورت اعلام:

- Participant؛
- Lot؛
- مبلغ؛
- مرجع؛
- تاریخ؛
- توضیح؛
- وضعیت اقدام بعدی

ثبت می‌شود.

---

# 61. ارتباط با Contract

در صورت منجر شدن نتیجه به قرارداد:

```text
AuctionLot
→ New Contract
```

Contract جدید منشأ مزایده را حفظ می‌کند.

---

# 62. PowerPoint جلسه

PowerPoint باید از AuctionPeriod / AuctionLot تولید شود.

بخش‌های داده‌ای به‌صورت خودکار از Snapshot رسمی دوره/Lot تکمیل می‌شوند.

حداقل:

- جلد؛
- خلاصه دوره؛
- آمار؛
- مستندات تبلیغات در صورت ثبت؛
- یک Slide برای هر Lot؛
- کد؛
- نام؛
- منطقه؛
- متراژ؛
- قیمت پایه؛
- مدت؛
- سرمایه‌گذاری؛
- موقعیت؛
- QR پرونده؛
- **Image Placeholder اختیاری برای ورود دستی عکس توسط کاربر**.

قاعده عکس:

```text
CommercialSpace Photo Field = NONE
PowerPoint Image Placeholder = MANUAL / OPTIONAL / NON-DATA
```

- SAMA عکس فضای تجاری را ذخیره، واکشی یا حدس نمی‌زند.
- Placeholder به Data Model متصل نیست.
- کاربر می‌تواند بعد از تولید فایل، برای هر Slide عکس دلخواه را دستی درج کند.
- خالی ماندن Placeholder نباید تولید PowerPoint را Block کند.

---

# 63. کنترل تعداد Slide

قبل از Final Export:

```text
AuctionLot Count
=
Property Slide Count
```

در صورت اختلاف خروجی Final تولید نمی‌شود.

---

# 64. QR

QR باید به پرونده رسمی Lot یا Space در SAMA LAN اشاره کند.

QR نباید لینک دستی پراکنده یا غیرقابل ممیزی باشد.

---

# 65. Template Versioning

تغییر متن رسمی:

```text
New Template Version
```

نه overwrite نسخه قبلی.

دوره‌های قدیمی به نسخه خود متصل باقی می‌مانند.

---

# 66. Hash

برای Master و Document Instance Hash نگهداری می‌شود.

تغییر خارج از فرآیند تأیید قابل تشخیص است.

---

# 67. Document Instance Audit

برای هر سند خروجی:

```text
DocumentInstanceID
TemplateID
TemplateVersion
AuctionPeriodID
AuctionLotID
SnapshotID
GeneratedBy
GeneratedAt
OutputHash
```

ثبت می‌شود.

---

# 68. کنترل Placeholder

قبل از Final:

تمام Field Tokenها Scan می‌شوند.

Unresolved سازمانی:

```text
0
```

باید باشد.

استثنا:

```text
BLANK_FOR_PARTICIPANT
```

---

# 69. Required Field Validation

اگر Field ضروری سازمانی خالی باشد:

Final Output ممنوع.

سامانه باید نام دقیق فیلد ناقص را نشان دهد.

---

# 70. Layout Validation

برای هر Template:

- Page Count؛
- Page Break؛
- Table position؛
- Font؛
- Font size؛
- Margin؛
- Header/Footer؛
- Border؛
- RTL؛
- Numeric format

کنترل می‌شود.

---

# 71. اصل Preservation

متن ثابت سند نباید توسط Runtime تولید شود.

Runtime فقط Field Value را وارد می‌کند.

این اصل احتمال تغییر ناخواسته متن حقوقی را به حداقل می‌رساند.

---

# 72. DOCX و PDF Master

برای اسناد حساس:

```text
DOCX Master
+
PDF Print Master
```

نگهداری می‌شود.

DOCX برای آرشیو/ویرایش مجاز Template.

PDF برای کنترل Fidelity چاپ.

---

# 73. Gate قبل از کدنویسی

هیچ Document Engine Production ساخته نمی‌شود تا Template Qualification کامل شود.

فرآیند:

```text
Source Document
→ Exact Transcription
→ Typography Cleanup
→ Field Identification
→ Field Registry
→ Master Template
→ Sample Data Fill
→ DOCX Render
→ PDF Render
→ Print
→ Page-by-page Review
→ User Approval
→ GOLDEN MASTER
→ Coding Allowed
```

---

# 74. Pilot اسناد قبل از کدنویسی

حداقل سه Pilot پیشنهاد می‌شود:

1. فضای تجاری؛
2. کافه؛
3. فضای ورزشی.

برای هر Pilot:

- شرایط عمومی و اختصاصی؛
- روکش الف؛
- روکش ب؛
- روکش ج؛
- نمونه قرارداد؛
- صورتجلسه؛
- PowerPoint Slide؛
- PDF نهایی چاپی.

---

# 75. Golden Master

بعد از تأیید چاپ هر نمونه:

```text
GOLDEN_MASTER
```

می‌شود.

Production Engine باید با Golden Master Regression Test شود.

---

# 76. Regression Test

هر تغییر کد در Document Engine باید دوباره کنترل کند:

- Page Count؛
- Static text unchanged؛
- Fields correct؛
- No unresolved token؛
- Layout within tolerance؛
- PDF generated؛
- Print sample acceptable.

---

# 77. Static Text Fingerprint

برای متن ثابت هر Template Fingerprint نگهداری می‌شود.

اگر Static Layer تغییر کند:

```text
BUILD FAIL / TEMPLATE RE-APPROVAL
```

---

# 78. تست‌های اجباری Candidate Engine

حداقل Test Suite:

1. Active + Contract + 90 days
2. Active + Contract + 91 days
3. Active + Contract + 1 day
4. Active + Contract + 0 days
5. Active + No Contract + Valid Appraisal + Medium
6. Active + No Contract + Valid Appraisal + Major
7. Active + No Contract + Valid Appraisal + Joz
8. Active + No Contract + Expired Appraisal
9. Active + No Contract + Missing Appraisal
10. Out-of-cycle Space
11. Missing Contract Amount
12. Missing Contract End Date
13. Missing Annual Threshold Rule
14. Appraisal valid today but expired by Auction Date
15. Manual Include
16. Manual Exclude
17. Long-term Contract
18. Space already in another open AuctionPeriod
19. Previous Auction failed but closed
20. Duplicate Current Appraisal data corruption

---

# 79. Shadow Mode قبل از اعتماد کامل

پیشنهاد الزامی:

Candidate Engine حداقل برای چند اجرای واقعی در حالت Shadow اجرا شود.

یعنی:

```text
Manual Official List
vs
SAMA Candidate List
```

مقایسه شود.

هر اختلاف:

- ثبت؛
- تحلیل؛
- Rule اصلاح؛
- Regression Test

شود.

تا زمانی که اختلاف توضیح‌نشده وجود دارد، Candidate Engine نباید تنها مرجع تصمیم عملیاتی باشد.

---

# 80. Reconciliation Report

در Shadow Mode گزارش:

```text
Manual ∩ SAMA
Manual Only
SAMA Only
Review Required
```

تولید می‌شود.

هدف:

```text
Unexplained Difference = 0
```

---

# 81. Rule Coverage Report

سامانه توسعه باید نشان دهد هر Rule:

- Test دارد؛
- Boundary Test دارد؛
- Reason Code دارد؛
- Rule Version دارد.

Rule بدون Test وارد Production نمی‌شود.

---

# 82. Data Quality Gate

قبل از اجرای Candidate Engine کنترل می‌شود:

- duplicate space code؛
- duplicate current contract؛
- overlapping contract؛
- duplicate current appraisal؛
- invalid dates؛
- missing annual rules؛
- invalid amount format.

Data corruption باید جدا از Business Decision گزارش شود.

---

# 83. تغییر نتیجه Candidate Engine

اگر Rule تغییر کند، تصمیمات گذشته overwrite نمی‌شوند.

Evaluation جدید رکورد جدید ایجاد می‌کند.

---

# 84. امنیت تغییر Rule

Permission مستقل برای:

- مشاهده Rule؛
- ویرایش Draft؛
- تصویب Rule؛
- فعال‌سازی Rule؛
- Manual Override.

لازم است.

---

# 85. Audit حساس مزایده

Audit حداقل برای:

- Candidate decision؛
- Rule changes؛
- Manual Include/Exclude؛
- Period list changes؛
- Base amount؛
- Appraisal snapshot؛
- Template selection؛
- Proposal receipt؛
- Envelope decision؛
- Declared result؛
- Result correction؛
- Document generation

الزامی است.

---

# 86. اصلاح نتیجه جلسه

تغییر DeclaredResult بعد از ثبت نهایی:

- علت اجباری؛
- مرجع اجباری؛
- کاربر مجاز؛
- Audit؛
- نسخه قبلی محفوظ.

---

# 87. ممنوعیت حذف فیزیکی

AuctionPeriod، AuctionLot، Proposal، Result، Document Instance و Audit فیزیکی حذف نمی‌شوند.

ابطال یا ثبت اشتباه با Status انجام می‌شود.

---

# 88. تصمیم‌های مرزی نهایی‌شده

## 88.1 روز صفر قرارداد

`RemainingDays = 0` داخل Rule «1 تا 90 روز مانده» نیست.

در خود روز پایان، قرارداد همان روز جاری است.

از روز بعد فضای مربوط «فاقد قرارداد جاری» محسوب و از مسیر کارشناسی معتبر و سطح معامله بررسی می‌شود.

## 88.2 قرارداد بلندمدت

مدت کل قرارداد در Eligibility مزایده اثر بازدارنده ندارد.

یک‌ساله، سه‌ساله، پنج‌ساله و سایر مدت‌ها در صورت رسیدن به بازه 1 تا 90 روز مانده به پایان، مشمول بررسی یکسان هستند.

## 88.3 دستور کمیسیون و مدیر

هر دو معتبر و هم‌تراز هستند.

هیچ‌کدام به‌صورت خودکار دیگری را رد یا Override نمی‌کند.

تعارض مستقیم → `REVIEW_REQUIRED` و نیازمند حل رسمی است.

## 88.4 اعتبار کارشناسی

`6 ماه تقویمی شمسی` از تاریخ خود کارشناسی.

آخرین روز اعتبار همان تاریخ متناظر شش ماه بعد است و از روز بعد منقضی محسوب می‌شود.

## 88.5 مرز سطح معامله

در نمونه سال 1405:

```text
350,000,000 ریال
= 35,000,000 تومان
= جزء
```

قاعده نمونه:

```text
جزء      <= 350,000,000 IRR
متوسط     > 350,000,000 IRR و <= 3,500,000,000 IRR
عمده      > 3,500,000,000 IRR
```

Thresholdها سالانه و Versioned هستند.

---

# 89. تصمیم‌های قطعی نهایی

1. فقط CommercialSpace فعال وارد موتور خودکار می‌شود.
2. ParentProperty در Eligibility عملیاتی نقشی ندارد.
3. فضای دارای قرارداد و فاقد قرارداد هر دو می‌توانند وارد مزایده شوند.
4. فاقد بهره‌بردار بودن مانع نیست.
5. بازه فعلی قرارداد 1 تا 90 روز مانده است.
6. خود روز 1 و روز 90 داخل بازه هستند.
7. روز 0 خارج از این بازه است.
8. از روز بعد پایان قرارداد، فضا از مسیر فاقد قرارداد بررسی می‌شود.
9. مدت کل قرارداد مانع نیست.
10. بازه زمانی از Rule Registry قابل ویرایش است.
11. سطح معامله در قرارداد از مبلغ قرارداد جاری محاسبه می‌شود.
12. در نبود قرارداد جاری، سطح از آخرین کارشناسی معتبر محاسبه می‌شود.
13. سطوح متوسط و عمده وارد مسیر کاندیدای خودکار می‌شوند.
14. سطح جزء وارد مسیر خودکار نمی‌شود مگر Rule/Override معتبر.
15. کارشناسی برای مزایده 6 ماه تقویمی اعتبار دارد.
16. مبنا تاریخ خود کارشناسی است.
17. فایل کارشناسی اجباری نیست.
18. داده ناقص نباید موجب حذف خاموش فضا شود.
19. Candidate و Readiness دو مفهوم جدا هستند.
20. فهرست رسمی دوره با تأیید کاربر مجاز تشکیل می‌شود.
21. دستور مدیر و کمیسیون هر دو معتبر و بدون Priority خودکار هستند.
22. تعارض دستورهای معتبر به REVIEW_REQUIRED می‌رود.
23. SAMA تصمیم حقوقی کمیسیون را جایگزین نمی‌کند.
24. SAMA برنده را مستقل تعیین نمی‌کند.
25. متن رسمی اسناد در Runtime تغییر نمی‌کند.
26. تمام Fieldهای سازمانی خودکار تکمیل می‌شوند.
27. Fieldهای Participant در اسناد اولیه خالی می‌مانند.
28. تمام Templates نسخه‌بندی و Hash می‌شوند.
29. تمام اسناد قبل از Coding باید Pilot و Print Test شوند.
30. هیچ Rule حیاتی بدون Test وارد Production نمی‌شود.
31. Candidate Engine قبل از اتکا در Shadow Mode با فهرست واقعی سازمان تطبیق داده می‌شود.
32. اختلاف توضیح‌نشده میان فهرست دستی و SAMA برای پذیرش موتور مجاز نیست.
33. Candidate ایجادشده با عبور از تاریخ پایان قرارداد حذف نمی‌شود و تا تعیین تکلیف رسمی باقی می‌ماند.

---

# 90. وضعیت نهایی سند

قواعد Business این سند `FROZEN` هستند.

اما Implementation دارای Gate اجباری است:

```text
BUSINESS SPEC FROZEN
↓
GOLDEN DOCUMENT PILOTS
↓
PRINT VALIDATION
↓
SHADOW CANDIDATE VALIDATION
↓
ZERO UNEXPLAINED DIFFERENCE
↓
IMPLEMENTATION APPROVED
↓
PRODUCTION CODING
```

---

# 91. معیار پذیرش قلب مزایده

ماژول مزایده فقط زمانی قابل قبول است که همزمان:

```text
Candidate False Negative = 0
Unexplained Candidate Difference = 0
Unresolved Organizational Placeholder = 0
Static Legal Text Unauthorized Change = 0
Final Document Calculation Conflict = 0
Golden Master Regression Failure = 0
```

باشد.

هر خطای توضیح‌نشده در این موارد Release را Block می‌کند.

---

**پایان سند — MD مزایده — SAMA**
