# سیستم طراحی

تنها منبع tokenها `design_system/static/design_system/css/tokens.css` است و component styling در `app.css` فقط از tokenها استفاده می‌کند. Vazirmatn Regular/SemiBold محلی است. پوسته دارای top navigation افقی RTL است؛ sidebar دائمی ممنوع است. کنترل‌ها، table، card، badge، filter، pagination، dossier و timeline shared هستند.

## قرارداد اجرایی محصول

- پالت خنثی سطوح، متن و border با tokenهای `neutral-*` تعریف می‌شود؛ پس‌زمینه صفحات روشن و کم‌کنتراست تزئینی است.
- هویت هر بخش فقط با `section-*` و جفت semantic accent/soft آن اعمال می‌شود. تعریف رنگ در template یا component ممنوع است.
- سلسله‌مراتب `page-title`، `section-title`، `card-title`، body، label، helper، table و badge از Type Scale مرکزی پیروی می‌کند.
- ارتفاع کنترل‌ها سه سطح `compact`، `standard` و `emphasized` دارد. اقدام ردیف جدول همیشه compact است و تنها اقدام اصلی فرم emphasized می‌شود.
- Shell شامل عنوان رسمی «سامانه مدیریت قراردادها»، ناوبری دارای `aria-current` و account menu مستقل است؛ خروج بخشی از navigation محصول نیست.
- الگوهای مشترک `filter-panel`، `multi-select`، `saved-filters`، `tabs`، `empty`، `kpis` و `dashboard-grid` تنها پیاده‌سازی مجاز این اجزا هستند.
- جدول پیش‌فرض پرتراکم ولی خوانا، header چسبان و action فشرده دارد. Card برای مرزبندی اطلاعات مرتبط است و نباید به Card Wall تبدیل شود.
- صفحه پرونده از anchor tabهای چسبان، field/value جدا و disclosure مستقل منبع و ممیزی استفاده می‌کند.
- هیچ صفحه‌ای مجاز به stylesheet، inline style، رنگ یا اندازه قلم اختصاصی نیست؛ تغییرات بصری عمومی باید در token یا component مرکزی انجام شوند.
