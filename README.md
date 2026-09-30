# SAMA Next

پیاده‌سازی پاک «سامانه مدیریت قراردادها» برای اداره املاک و مستغلات. این شاخه هیچ ancestry کاربردی از runtime قدیمی ندارد. دستورهای توسعه:

```bash
python -m pip install -e '.[test]'
python manage.py migrate
python import_pipeline/cli.py authority/inputs/1405-07-06/بسته_به_روزرسانی_سه_اکسل_سما_6مهر.zip
python scripts/run_server.py
```
