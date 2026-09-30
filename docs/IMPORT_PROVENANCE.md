# ورود و منشأ

پیش از ایجاد هر رکورد canonical، `import_pipeline.authority_inventory.inspect_package`
سه workbook را مستقیماً از ZIP می‌خواند، شناسه‌ها را با عنوان واقعی ستون پیدا می‌کند و
تعداد، یکتایی و نبود هم‌پوشانی دو طبقه فضای تجاری را کنترل می‌کند. نتیجه همین inventory
ورودی کنترل پس از import است؛ شمارنده رابط یا مقدار از پیش نوشته‌شده جای بازخوانی Excel
را نمی‌گیرد. `verify_manifest` نیز SHA-256 همه ورودی‌های فهرست‌شده را با رد مسیر ناامن
بررسی می‌کند.

هر cell غیرتهی در هر sheet ــ شامل عنوان‌ها و metadata پیش از header ــ با filename، sheet، row، column، original heading در صورت وجود، raw value، mapping status، import batch و row fingerprint ذخیره می‌شود. آزمون کامل تعداد cellهای workbook را مستقل محاسبه و با `RawCell` مقایسه می‌کند.

مقدار خام هرگز تغییر نمی‌کند. normalization canonical جداست؛ تاریخ نامعتبر یا ناموجود در provenance می‌ماند و تاریخ نامعتبر discrepancy می‌سازد. طبقه‌بندی اولیه ۳۵۰ `ACTIVE` و ۱۵۱ `OUT_OF_CYCLE` مستقیماً از دو workbook مرجع می‌آید و از قرارداد یا سابقه بازاستنتاج نمی‌شود. شیت «موارد نیازمند بررسی» به رکوردهای `Discrepancy` تبدیل می‌شود، بدون اصلاح خودکار داده.
