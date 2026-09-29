# SAMA Project Inputs — Canonical Intake

این پوشه محل ورودی‌های مرجع پروژه SAMA است.

## Authority
ترتیب تقدم:
1. Owner-approved current FINAL FROZEN
2. older FROZEN draft
3. REVIEW document
4. prototype/build
5. historical conversation inference

## Rules
- هیچ فایل قدیمی یا Prototype به‌تنهایی منبع Business Rule نیست.
- `SAMA_ENTERPRISE_LAN...` فقط مرجع LAN / Startup / Login است و هیچ Business Rule، Data Model یا UI از آن وارد سامانه جدید نمی‌شود.
- Excelهای واقعی منبع Operational/Master Data هستند؛ هیچ ستون یا سطر نباید Silent Drop شود.
- گزارش‌ها و PPTها فقط Benchmark/Presentation Reference هستند مگر سند FINAL FROZEN خلاف آن را مشخص کند.

## Folder map
- `00_authority/`: Authority Index و اسناد مرجع نهایی
- `01_final_md/`: FINAL MD Pack و MDهای تکمیلی
- `02_master_data/`: Excelهای واقعی سازمان
- `03_contract_samples/`: نمونه قراردادها
- `04_auction_documents/`: اسناد مزایده
- `05_reporting_references/`: PDF/PPT/نمونه گزارش
- `06_branding/`: لوگو و هویت بصری
- `07_workflow_references/`: سامانه کارشناسان و سامانه قراردادها به‌عنوان Reference
- `08_lan_deployment_reference/`: SAMA Enterprise فقط برای الگوی اجرا روی LAN

## Expected files
### 00_authority
- SAMA_FINAL_MD_AUTHORITY_INDEX_PRE_UI.md

### 01_final_md
- SAMA_FINAL_MD_PACK_PRE_UI.zip
- MD sama.zip

### 02_master_data
- اکسل نهایی اداره املاک و مستغلات.zip
- نام مراکز (1).xlsx
- اصلی اسامی مدیران مناطق سازمان.xlsx

### 03_contract_samples
- نمونه قراراداد 1.zip
- نمونه قرار داد2.zip
- نمونه قرارداد 3.zip

### 04_auction_documents
- اسناد مزایده فضای تجاری.zip

### 05_reporting_references
- daramad final2.pdf
- قالب_سه_صفحه_ای_برج_آزادی_همه_محتوا_قابل_ویرایش.pptx
- قالب_سه_صفحه_ای_برج_میلاد_همه_محتوا_قابل_ویرایش.pptx

### 06_branding
- لوگو جدید سازمان.zip

### 07_workflow_references
- سامانه_کارشناسان_نسخه_1.4.14_اصلاح_سوابق_کارشناسی(5)(1).zip
- Samane_Modiriat_Gharardadha_v1.0.4(1)(1).zip

### 08_lan_deployment_reference
- SAMA_ENTERPRISE_LAN_v3.8.5_LONG_TERM_OVER_365_1405-05-15(1).zip

## Codex start rule
Codex must read this manifest first, inventory the uploaded files, verify hashes where available, then resolve authority before implementation.
