# UAT.10 real export QA

The same live Authority-backed configurations were generated as real XLSX, PDF and DOCX files under `docs/qa/uat10/`.

## Commercial spaces

Order from the visual right: کد فضا، نام فضا / مرکز، منطقه، وضعیت، کاربری، مساحت، توضیحات کارشناس، امضاء. Rows are sorted by region then space code.

## Mother properties

Order from the visual right: شناسه ملک، نام ملک / مرکز، منطقه، نشانی، کاربری اصلی، مساحت، تعداد فضاهای مرتبط، توضیحات کارشناس، امضاء. Rows are sorted by region then identifier.

Programmatic inspection confirmed XLSX `rightToLeft`, freeze pane, autofilter, print titles/area, Persian font, borders and wrapping. DOCX packages are genuine OOXML with bidi paragraphs/table and repeated header markup. PDF text and rendered first-page PNGs were inspected: shaping, RTL order, wrapping, borders, official identity and pagination are present; application identity and SMK credit are absent.
