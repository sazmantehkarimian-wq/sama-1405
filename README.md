# سما

سامانه اداره املاک و مستغلات — معماری پاک، Zero-Data و Portable LAN.

## توسعه

```bash
python -m pip install -e '.[test]'
python manage.py migrate
pytest -q
python scripts/run_server.py
```

## قواعد پایه

- داده عملیاتی اولیه: صفر
- Import Excel/CSV: ندارد
- ورود اطلاعات: فقط فرم‌های کنترل‌شده
- محور پرونده فضای تجاری: کد فضا
- املاک مادر: دامنه مستقل
- LAN: پورت 8765

مبنای تصمیم: `docs/ZERO_DATA_FOUNDATION.md`.

این شاخه تا عبور از تست واقعی و پذیرش Owner، Production/LAN-ready نیست.
