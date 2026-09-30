# Final Compliance Audit

این سند وضعیت واقعی clean branch را ثبت می‌کند و مجوز Release نیست.

| الزام بحرانی | وضعیت | شاهد/شکاف |
|---|---|---|
| جدایی معماری از Legacy | PASS | `LEGACY_BOUNDARY.md`; root commit مستقل |
| Authority/hash/data baseline | PASS | authority و full importer tests |
| Raw provenance | PASS | تمام cellهای غیرتهی، حتی metadata پیش از header، تطبیق شمارشی می‌شوند |
| Registry | NEEDS VERIFICATION | schema و classification فعال است؛ مرور نهایی معنایی ۱۵۳ کلید لازم است |
| Typed canonical domains | PASS | مدل‌های رابطه‌ای و migrations؛ JSON فقط config/evidence است |
| Design system/navigation/dossier | PASS | token enforcement، navigation افقی، dossier integration |
| Historical contracts/beneficiaries/appraisals/auctions | PASS | importer typed و provenance-linked |
| Source decisions/documents/utility obligations | PASS | importer typed و dossier-linked |
| Appraisal fees/utilities/commission workflow | FAIL | schema/read views موجود؛ lifecycle نوشتن کامل نشده |
| Workflow/file movement | FAIL | derive/list موجود؛ ثبت و transition عملیاتی کامل نشده |
| Document upload/alerts/audit | FAIL | storage schema موجود؛ end-to-end permission/audit UI کامل نشده |
| Advanced filters/saved views | FAIL | core query موجود؛ همه operatorها و save action کامل نیست |
| Official exports | PASS | XLSX/DOCX/PDF واقعی، فیلتر/ستون جاری، فونت فارسی محلی و page number |
| RBAC/user administration | PASS | native create/reset/activate actions، staff enforcement و audit test |
| Backup/restore | NEEDS VERIFICATION | scripts؛ write-lock/media round-trip کامل نشده |
| Browser/print/concurrency/security matrices | NEEDS VERIFICATION | automated unit/security موجود؛ full real-browser/concurrency pending |
| Clean release | FAIL | به‌علت FAILهای بحرانی، release عمداً تولید نشده است |

هر FAIL بحرانی انتشار را مسدود می‌کند؛ این وضعیت ادعای DONE یا LAN Ready نیست.
