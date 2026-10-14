# تصمیمات مالک

- بنیان پاک و بدون reuse لایه‌های legacy؛ modular monolith.
- یک جهان ۵۰۱ کدی؛ طبقه‌بندی اولیه Excel authoritative است.
- ۲۲۵ ملک مادر و لینک صرفاً با evidence صریح.
- UI فارسی RTL، Vazirmatn محلی و navigation افقی؛ پورت 8765.
- raw evidence بدون حذف، domain typed، discrepancy به‌جای حدس.
- تاریخ کار عملیاتی جدید: ۱۴۰۵/۰۷/۰۱؛ سابقه واردشده workflow ساختگی ندارد.
- `SAMA-DS 1.0` مرجع اجرایی الزام‌آور UI/UX و خروجی است؛ Token → Component → Pattern → Page Template → Module Usage → Report/Print.
- قانون `NO LOCAL REINVENTION` مصوب است: ساخت Component، CSS، Table، Button، Form، Card، Filter یا Report محلی و سلیقه‌ای ممنوع است؛ نیاز جدید ابتدا باید در Design System تعریف و سپس مصرف شود.
- تغییرات Design System و صفحات به‌صورت Delta انجام می‌شوند؛ Component تأییدشده FROZEN است و تغییر آن فقط با درخواست Owner یا Defect معتبر مجاز است.
- ماژول «اطلاعات پایه» از نظر دامنه، داده، رفتار و منطق کاری `FINAL FROZEN` است؛ ظاهر فعلی هنوز نهایی نیست و `VISUAL NORMALIZATION PENDING` طبق `SAMA-DS 1.0` باقی می‌ماند.
- اصلاح ظاهری اطلاعات پایه در آینده مجاز است، مشروط بر اینکه داده، Workflow و منطق FROZEN تغییر نکند.
- منوی اصلی ۱۴‌گانه سامانه باید خوانایی اداری مناسب داشته باشد؛ اندازه/فاصله فعلی آیتم‌های Navigation به‌عنوان Visual Debt ثبت شده و بعداً بدون تغییر معماری منو اصلاح می‌شود.
- ماژول بعدی برای طراحی و تصویب: «قوانین».
