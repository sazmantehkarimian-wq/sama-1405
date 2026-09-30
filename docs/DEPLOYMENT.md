# استقرار Windows/LAN

Python 3.11 و dependencies را نصب، migration/import/provision را یک بار اجرا و سپس `START_SAMA.bat` را اجرا کنید. پیش‌فرض `http://127.0.0.1:8765/` و LAN برابر `http://SERVER-IP:8765/` است. Firewall: inbound TCP 8765 فقط برای subnet سازمان. `SAMA_PORT` قابل تنظیم است.

## بازیابی کنترل‌شده

`python scripts/restore.py BACKUP_DIRECTORY` ابتدا manifest، SHA-256 همه فایل‌های رسانه، سلامت SQLite و کلیدهای خارجی را اعتبارسنجی می‌کند؛ سپس write lock سراسری می‌گیرد، پشتیبان pre-restore می‌سازد، DB و media را در staging آماده و به‌صورت atomic جایگزین می‌کند و سلامت نهایی را دوباره می‌سنجد. در هر خطا نسخه قبلی rollback می‌شود. اجرای بازیابی فقط برای مدیر سامانه و در پنجره نگهداری مجاز است.
