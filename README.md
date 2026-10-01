# سامانه مدیریت قراردادها

پیاده‌سازی پاک «سامانه مدیریت قراردادها» برای اداره املاک و مستغلات. این شاخه هیچ ancestry کاربردی از runtime قدیمی ندارد. دستورهای توسعه:

```bash
python -m pip install -e '.[test]'
python manage.py migrate
python -m import_pipeline.cli verify authority/inputs/1405-07-06
python -m import_pipeline.cli inspect authority/inputs/1405-07-06/بسته_به_روزرسانی_سه_اکسل_سما_6مهر.zip
python -m import_pipeline.cli import authority/inputs/1405-07-06/بسته_به_روزرسانی_سه_اکسل_سما_6مهر.zip
python scripts/run_server.py
```

نسخه در حال آماده‌سازی برای بازآزمایی UAT: `5.0.0-uat.5`. این نسخه تا عبور از workflow ویندوز و پذیرش مالک، آماده Production/LAN نیست. دستورهای بالا فقط برای توسعه و بازآزمایی منبع هستند.
