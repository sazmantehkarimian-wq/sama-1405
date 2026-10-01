# استقرار Windows/LAN

بسته انتشار Portable است و روش اجرای LAN ثابت می‌ماند.

- Local: `http://127.0.0.1:8765/`
- LAN: `http://SERVER-IP:8765/`
- پورت پیش‌فرض: `8765`
- کلاینت‌ها نیاز به نصب Python ندارند.

## دیتابیس تحویلی

Database پس از migration ساخته می‌شود و **هیچ داده عملیاتی** در آن Seed یا Import نمی‌شود. تنها حساب‌ها و تعاریف سیستمی مصوب می‌توانند در First Start ایجاد شوند.

هیچ فایل Excel/CSV و هیچ ابزار Import در Release Runtime قرار نمی‌گیرد.

## شروع

ZIP را در مسیر محلی باز کنید و `START_SAMA.bat` را اجرا کنید. Startup باید migration، تنظیم حساب‌های مصوب و سپس Waitress را اجرا کند. داده، اسناد، secret و backup در `data` نگهداری می‌شوند و نباید روی Share عمومی قرار گیرند.

## شبکه

برای Firewall ویندوز، Rule ورودی TCP پورت 8765 فقط برای subnet سازمان تعریف شود. `SAMA_PORT` در صورت نیاز پورت Start/Stop را هم‌زمان تغییر می‌دهد.

## بازیابی

Restore باید manifest/hash، SQLite integrity و foreign-key check را پیش و پس از جایگزینی بررسی کند و در خطا rollback انجام دهد.
