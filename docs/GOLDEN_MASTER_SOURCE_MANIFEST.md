# Golden Master Source Manifest

این فایل فقط **ردیابی منبع** است و به‌تنهایی هیچ Asset قدیمی را به Authority اجرایی ارتقا نمی‌دهد. مبنای قواعد همچنان `authority/reference/MD اسناد رسمی و Golden Master مزایده — FINAL FROZEN.md` است.

## Source repository snapshot

- Repository: `sazmantehkarimian-wq/sama-1405`
- Reference branch: `main`
- Reference commit: `ae8a789b6f0eb4ade6f5a11c80d2e198a617e75b`
- Intake manifest: `project_inputs/PROJECT_INPUT_MANIFEST.md`
- Intake manifest blob: `da08675bac11555e3e33a22e4a11fe38cce8beae`

## Candidate source assets

| نقش | مسیر در snapshot اصلی | Git blob SHA | اندازه | وضعیت |
|---|---|---:|---:|---|
| اسناد مزایده فضای تجاری | `اسناد مزایده فضای تجاری.zip` | `2b5478df0917f179d5726b4fb56684a72b57c03f` | 3,905,137 B | REFERENCE — CONTENT VERIFICATION REQUIRED |
| نمونه قرارداد ۱ | `project_inputs/نمونه قراراداد 1.zip` | `2b5478df0917f179d5726b4fb56684a72b57c03f` | 3,905,137 B | REFERENCE — DUPLICATE BLOB ALERT |
| نمونه قرارداد ۲ | `project_inputs/نمونه قرار داد2.zip` | `1d65046c6e2886ee635867bfe8a2e583e1c56dcc` | 3,629,986 B | REFERENCE — CONTENT VERIFICATION REQUIRED |
| نمونه قرارداد ۳ | `project_inputs/نمونه قرارداد 3.zip` | `b236fb6dfbeeda102fa116499a9c05a3526d9902` | 4,105,549 B | REFERENCE — CONTENT VERIFICATION REQUIRED |
| بسته هویت بصری/لوگو | `project_inputs/لوگو جدید سازمان.zip` | `aad426df6c2aeb3d811e13fac1eff3bf32d00380` | 3,265,721 B | REFERENCE — EXACT ASSET REVIEW REQUIRED |

## Duplicate blob alert

`اسناد مزایده فضای تجاری.zip` و `project_inputs/نمونه قراراداد 1.zip` در snapshot اصلی **Git blob SHA و اندازه کاملاً یکسان** دارند. بنابراین این دو نام در مخزن به یک بایت‌استریم اشاره می‌کنند.

تا زمانی که محتوا به‌صورت انسانی/ابزاری بازبینی و نقش واقعی آن تأیید نشده است:

- این دو فایل نباید دو منبع مستقل تلقی شوند؛
- نباید بر اساس نام فایل Template Family یا متن حقوقی استنتاج شود؛
- نباید Golden Master از روی یکی از آنها Production-final شود.

## Promotion rule

هر Asset فقط پس از این زنجیره می‌تواند وارد Golden Master شود:

`REFERENCE BLOB → CONTENT INVENTORY → FAMILY CLASSIFICATION → HIGHLIGHT/FIELD MAP VERIFICATION → STATIC TEXT DIFF → TEST RENDER → PHYSICAL PRINT QA → OWNER APPROVAL → APPROVED GOLDEN MASTER VERSION`

## Required Golden Master families

طبق FINAL FROZEN، سه خانواده مستقل باید وجود داشته باشند:

- `COMMERCIAL`
- `CAFE`
- `SPORT`

و برای هر خانواده حداقل این اقلام مستقل لازم است:

- اسناد مزایده
- نمونه قرارداد
- پاکت الف
- پاکت ب
- پاکت ج
- منع مداخله
- صورتجلسه

نبود Source تأییدشده برای هر خانواده به معنی `BLOCKED` بودن همان Golden Master است، نه مجوز استفاده از Template خانواده دیگر.

## Production boundary

تا پایان Print QA واقعی، `domains.documents.Document` فقط برای مدیریت سند بارگذاری‌شده و شواهد عملیاتی معتبر است. این مدل نباید به‌عنوان Document Engine رسمی Golden Master معرفی شود و هیچ PASS مربوط به گزارش‌های جدولی PDF/DOCX/XLSX جایگزین این Gate نیست.
