# فرهنگ شاخص‌های داشبورد مدیریتی

تمام شاخص‌ها در هر درخواست از QuerySetهای canonical محاسبه می‌شوند؛ هیچ عددی در template یا view ثابت نشده است. جمعیت و drill-down هر شاخص باید دقیقاً یک predicate داشته باشند.

| شاخص | تعریف | جمعیت / فیلتر | مجموعه داده | Drill-down |
|---|---|---|---|---|
| فضاهای فعال | فضای canonical موجود در چرخه | `CommercialSpace.status=ACTIVE` | فضاهای تجاری | `/spaces/?status=ACTIVE` |
| خارج از چرخه | فضای canonical خارج‌شده از چرخه | `CommercialSpace.status=OUT_OF_CYCLE` | فضاهای تجاری | `/spaces/?status=OUT_OF_CYCLE` |
| سوابق قرارداد | تعداد ردیف‌های canonical از `Contract`؛ هر ردیف یک سابقه تاریخی/عملیاتی دارای شاهد قرارداد است، نه تعداد فضای یکتا و نه فقط قرارداد جاری | همه ردیف‌های `Contract` پس از حذف ردیف‌های صرفاً status-like در import | قراردادها | `/records/contracts/` |
| فاقد سابقه قرارداد | فضای فعال که هیچ ردیف canonical قرارداد تاریخی یا عملیاتی ندارد | `status=ACTIVE AND contracts IS NULL` | فضاهای تجاری | `/spaces/?status=ACTIVE&contract_presence=empty` |
| فاقد کارشناسی | فضای فعال بدون هیچ سابقه canonical کارشناسی | `status=ACTIVE AND appraisals IS NULL` | فضاهای تجاری | `/spaces/?status=ACTIVE&appraisal_presence=empty` |
| موارد نیازمند پیگیری | هشدار عملیاتی مختومه‌نشده؛ مغایرت واردات جزو این شاخص نیست | `Alert.status != RESOLVED` | موارد نیازمند پیگیری | `/records/alerts/?state=OPEN` |
| فرایندهای باز | نمونه فرایند عملیاتی در وضعیت باز | `WorkflowInstance.state=OPEN` | پیگیری پرونده | `/records/workflows/?state=OPEN` |

## تطبیق قرارداد با مرجع ۶ مهر

Import کامل مرجع ۶ مهر ۳۳۲ ردیف canonical قرارداد ایجاد می‌کند. این عدد از ردیف‌هایی به دست می‌آید که پس از جداسازی عبارت‌های وضعیت از «شماره قرارداد»، هنوز یکی از شواهد واقعی قرارداد (شماره معتبر، تاریخ، مبلغ یا وضعیت قراردادی) را دارند. عبارت صرفی مانند «خارج از مزایده» بدون شاهد دیگر Contract نمی‌سازد. در همین import، ۷۰ فضای فعال هیچ سابقه Contract ندارند. آزمون import تعداد مدل، فهرست UI، context داشبورد و نتیجه drill-down را با هم تطبیق می‌دهد؛ این اعداد در کد محصول hard-code نشده‌اند.
