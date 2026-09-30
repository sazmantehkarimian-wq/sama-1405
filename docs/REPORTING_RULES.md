# گزارش رسمی

`reporting.engine` تنها موتور خروجی رسمی است و query فیلترشده جاری، ترتیب آن، ستون‌های انتخابی و ستون‌های خالی سفارشی را به XLSX سازگار با Excel 2019، DOCX واقعی و PDF server-side تبدیل می‌کند. PDF از TTF محلی Vazirmatn، shaping فارسی، جدول با header تکرارشونده و شماره صفحه استفاده می‌کند. XLSX راست‌به‌چپ، freeze، autofilter، border، wrap و width کنترل‌شده دارد.

هدر فقط لوگوی مصوب و سه سطح هویت سازمانی است. Browser print گزارش رسمی محسوب نمی‌شود و در UI دکمه رسمی `window.print()` وجود ندارد.
