from domains.documents.models import Document
from domains.identity.models import AuditEvent
from services.money import format_rial


def _section(key,title,labels,rows):
    rows=[list(row) for row in rows]
    return {"key":key,"title":title,"labels":list(labels),"rows":rows,"count":len(rows)}


def build_mother_property_sections(item):
    current=item.current_usage_record
    sections=[
        _section("summary","خلاصه پرونده",("عنوان","مقدار"),[
            ("شناسه ملک",item.identifier),
            ("نام ملک",item.name),
            ("منطقه",item.region.name if item.region_id else "—"),
            ("وضعیت جاری",item.current_status or "ثبت نشده"),
            ("نوع مرکز / مکان",item.center_type or "ثبت نشده"),
            ("نوع کاربری",item.primary_usage or "ثبت نشده"),
            ("گروه کاربری",item.usage_group or "ثبت نشده"),
            ("نشانی",item.address or "—"),
            ("مساحت عرصه",item.land_area if item.land_area is not None else "—"),
            ("مساحت اعیان",item.area if item.area is not None else "—"),
            ("وضعیت مالکیت",item.ownership_document_status or "ثبت نشده"),
            ("مالک / دارنده سند",item.owner_name or "ثبت نشده"),
            ("وضعیت بهره‌برداری",current.usage_status if current else "ثبت نشده"),
            ("واحد در اختیارگیرنده",current.holder_unit if current and current.holder_unit else item.holder_unit or "ثبت نشده"),
            ("بهره‌بردار فعلی",current.beneficiary_name if current and current.beneficiary_name else "فاقد بهره‌بردار / ثبت نشده"),
            ("انشعاب برق",item.get_electricity_presence_display()),
            ("انشعاب آب",item.get_water_presence_display()),
            ("انشعاب گاز",item.get_gas_presence_display()),
            ("تعداد مکاتبات",item.correspondence.count()),
            ("تعداد فایل‌ها",Document.objects.filter(entity_type="MotherProperty",entity_id=item.identifier).count()),
            ("وضعیت تکمیل پرونده",item.completeness_status),
        ]),
        _section("ownership","تاریخچه مالکیت",("مالک","نوع","سهم","از","تا","مبنا","توضیحات"),(
            (x.owner_name,x.get_owner_type_display(),f"{x.share_percent}%" if x.share_percent is not None else "—",
             x.start_date or "—",x.end_date or "جاری / ثبت نشده",x.basis or "—",x.notes or "—")
            for x in item.ownership_history.all()
        )),
        _section("ownership_documents","مدارک مالکیت",("نوع","شماره","تاریخ","دفترخانه","پلاک اصلی","پلاک فرعی","بخش ثبتی","مساحت سند","مالک مندرج","وضعیت"),(
            (x.document_type,x.document_number or "—",x.document_date or "—",x.notary_name or x.notary_number or "—",
             x.main_plate or "—",x.sub_plate or "—",x.registration_section or "—",
             x.documented_area if x.documented_area is not None else "—",x.documented_owner_name or "—",x.get_status_display())
            for x in item.ownership_documents.all()
        )),
        _section("usage","تاریخچه بهره‌برداری",("وضعیت","نوع در اختیارگیرنده","واحد در اختیارگیرنده","بهره‌بردار","نوع بهره‌بردار","از","تا","مبنا","مرجع قرارداد","علت خاتمه"),(
            (x.usage_status,x.holder_type or "—",x.holder_unit or "—",x.beneficiary_name or "فاقد بهره‌بردار",
             x.beneficiary_type or "—",x.start_date,x.end_date or "جاری",x.basis or "—",
             x.contract_reference or "فاقد قرارداد / ثبت نشده",x.termination_reason or "—")
            for x in item.usage_history.all()
        )),
        _section("utilities","وجود انشعابات",("انشعابات","برق","آب","گاز","سایر","توضیح"),[(
            item.get_has_utilities_display(),item.get_electricity_presence_display(),item.get_water_presence_display(),
            item.get_gas_presence_display(),item.other_utilities or "—",item.utility_notes or "—"
        )]),
        _section("correspondence","مکاتبات اداری",("نوع","شماره","تاریخ","موضوع","فرستنده","گیرنده","واحد مرتبط","نیاز پیگیری","مسئول","مهلت","وضعیت"),(
            (x.document_type,x.number or "—",x.document_date or "—",x.subject,x.sender or "—",x.recipient or "—",
             x.organizational_unit or "—","بله" if x.needs_follow_up else "خیر",
             x.responsible.get_username() if x.responsible_id else "—",x.due_date or "—",x.get_follow_up_status_display())
            for x in item.correspondence.select_related("responsible").all()
        )),
        _section("documents","فایل‌ها و مدارک",("عنوان","نوع","مرجع","تاریخ","وضعیت","نام فایل","SHA-256"),(
            (x.title,x.document_type,x.reference or "—",x.document_date or "—",x.status_label,x.original_filename,x.sha256)
            for x in Document.objects.filter(entity_type="MotherProperty",entity_id=item.identifier).order_by("-uploaded_at","-pk")
        )),
        _section("notes","یادداشت‌های داخلی",("زمان","موضوع","متن","کاربر","وضعیت"),(
            (x.created_at,x.subject or "یادداشت",x.text,x.created_by.get_username(),"فعال" if x.active else "غیرفعال")
            for x in item.internal_notes.select_related("created_by").all()
        )),
        _section("audit","Audit Trail",("زمان","کاربر","عملیات","علت","قبل","بعد"),(
            (x.created_at,x.actor.get_username() if x.actor_id else "سیستم",x.action,x.reason or "—",
             str(x.before) if x.before is not None else "—",str(x.after) if x.after is not None else "—")
            for x in AuditEvent.objects.filter(entity_type="MotherProperty",entity_id=item.identifier).select_related("actor").order_by("-created_at","-pk")
        )),
    ]
    return sections
