# SAMA — FINAL MD AUTHORITY INDEX — PRE-UI REFERENCE REVIEW

**وضعیت:** `FINAL FROZEN`  
**دامنه:** تمام تصمیم‌ها و MDهای نهایی تا قبل از مرحله اخیر High-Fidelity / UI Reference Review  
**قاعده:** فقط اسناد این بسته برای ادامه طراحی و ساخت مرجع هستند.

---

## اسناد مرجع نهایی

1. MD املاک مادر — FINAL FROZEN
2. MD فضاهای تجاری — FINAL FROZEN
3. MD بهره‌برداران — FINAL FROZEN
4. MD قراردادها — FINAL FROZEN
5. MD کارشناسی — FINAL FROZEN
6. MD کمیسیون معاملات — FINAL FROZEN
7. MD انشعابات و مصرف — FINAL FROZEN
8. MD مزایده — FINAL FROZEN
9. MD اسناد رسمی و Golden Master مزایده — FINAL FROZEN
10. Golden Master Field Registry فضای تجاری
11. MD حق‌الزحمه کارشناسان — FINAL FROZEN
12. MD موتور گزارش‌گیری و تحلیل مدیریتی — FINAL FROZEN v2
13. MD داشبورد مدیریتی نهایی — FINAL FROZEN
14. MD معماری اطلاعات، Sitemap، Navigation و کاربران — FINAL FROZEN
15. MD نظام رنگ، پالت ماژول‌ها و هویت بصری — FINAL FROZEN
16. MD سیستم طراحی اجرایی و استاندارد UI/UX — FINAL FROZEN

---

## اصلاحات مستقل Review که اکنون در اسناد مرجع ادغام شده‌اند

- فونت Production UI = Vazirmatn Local؛ وابستگی به فونت تجاری وجود ندارد.
- تمام اعداد کاربرمحور UI فارسی هستند؛ Technical/System IDs لاتین می‌مانند.
- Alignment مبلغ، عدد، تاریخ و شناسه سیستم به‌صورت صریح تعریف شده است.
- CommercialSpace هیچ Photo/Gallery Field ندارد.
- `SPACE-010` بازنشسته و غیرقابل استفاده است.
- عکس در PowerPoint فقط Manual Optional Image Placeholder است و Data Field نیست.
- KPI Catalog داشبورد از First View تفکیک شده است.
- First View داشبورد حداکثر 6–8 KPI و 2–3 Chart معنادار دارد؛ KPIهای مصوب حذف نمی‌شوند.

---

## اسناد خارج از Authority این بسته

این موارد نباید برای Implementation به‌عنوان مرجع نهایی استفاده شوند:

- `SAMA_MASTER_REFERENCE.md` قدیمی/درحال‌تکمیل؛
- نسخه قدیمی Report Engine بدون v2؛
- `MD مزایده — REVIEW سختگیرانه.md`؛
- `MD مزایده — FROZEN سختگیرانه.md` در صورت تعارض با FINAL FROZEN؛
- هر Prototype یا Build قبلی به‌عنوان منبع Rule؛
- `SAMA_UI_REVIEW_GATE_ROUND_1.md` و بررسی High-Fidelity اخیر، چون کاربر صریحاً آن مرحله را فعلاً از Freeze نهایی خارج کرده است.

---

## قاعده تقدم

در هر تعارض:

```text
Owner-approved current FINAL FROZEN MD
> older FROZEN draft
> REVIEW document
> prototype/build
> historical conversation inference
```

هیچ AI یا پیاده‌ساز مجاز نیست ابهام را با حدس پر کند.

---

## قاعده تغییر

```text
FINAL FROZEN
→ CHANGE REQUEST
→ REVIEW
→ OWNER APPROVAL
→ UPDATED FINAL FROZEN
```

---

**این بسته مرجع فعلی پروژه تا قبل از ادامه مرحله UI Reference / High-Fidelity است.**
