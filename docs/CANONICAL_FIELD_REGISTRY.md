# ثبت فیلد canonical

`CanonicalField` metadata شامل کلید، برچسب فارسی، alias، نوع، domain/entity، معنی، authority/precedence، nullable/required و قابلیت‌های search/filter/sort/export/default visibility/sensitivity/deprecation/validation را ذخیره می‌کند. importer هر heading را دقیقاً به `MAPPED`، `DERIVED`، `REFERENCE_ONLY`، `DEPRECATED` یا `UNRESOLVED` طبقه‌بندی می‌کند.

فیلد بی‌عنوان با برچسب audit-only ثبت می‌شود؛ هیچ فیلد positional مانند «ستون N» به صفحه عملیاتی راه ندارد. Import مرجع ۶ مهر ۱۵۳ کلید ساخت: ۱۰۶ `MAPPED`، ۳۱ `REFERENCE_ONLY` و ۱۶ `UNRESOLVED`. همه ۱۶ مورد unresolved سلول‌های غیرتهی خارج از جدول و بدون heading هستند؛ به‌عنوان evidence خام حفظ می‌شوند و وارد UI عملیاتی نمی‌شوند.
