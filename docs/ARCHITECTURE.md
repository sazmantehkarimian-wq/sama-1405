# معماری

سما یک **modular monolith** مبتنی بر Django و SQLite برای اجرای Portable روی LAN است.

## جریان داده

ورودی عملیاتی فقط از UI کنترل‌شده عبور می‌کند:

`UI/Form → validation → domain service → transaction → typed domain models → audit/timeline → query/reporting`

Excel/CSV در معماری Runtime هیچ نقشی ندارد و Import Pipeline جزو محصول نیست.

## مرز دامنه‌ها

- `CommercialSpace`: پرونده مستقل فضای تجاری با Business Key یکتای `code`.
- `MotherProperty`: دامنه مستقل با شناسه مخصوص خود؛ هیچ Foreign Key یا استنتاج اجباری از/به CommercialSpace ندارد.
- `contracts`, `operations`, `documents`: سوابق فضای تجاری را از طریق CommercialSpace دنبال می‌کنند.
- `services/`: مالک قواعد کسب‌وکار، Validation و Transaction.
- `queries/`: مالک Query schema، Search و Filtering.
- `reporting/`: مالک خروجی رسمی.
- `ui/`: Controller و Form؛ منطق کسب‌وکار نباید در Template یا JavaScript پخش شود.

## اصول سلامت

- هیچ write عملیاتی خارج از سرویس/فرم کنترل‌شده مجاز نیست.
- اعتبار تاریخ شمسی و عددها Server-side کنترل می‌شود.
- Hard delete عادی برای سوابق عملیاتی مجاز نیست.
- Audit/Timeline نتیجه عملیات واقعی است، نه داده ساختگی یا واردشده.
- Schema migration و backup/restore باید مستقل از داده نمونه باشند.
