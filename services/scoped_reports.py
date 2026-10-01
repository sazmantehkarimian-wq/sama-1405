"""SpaceCode-scoped reporting over canonical Zero-Data domain models."""
from django.db.models import Q

from domains.contracts.models import BeneficiaryAssignment, Contract
from domains.documents.models import Document
from domains.identity.models import AuditEvent
from domains.operations.models import (
    Appraisal, AppraisalFee, AuctionEvaluation, AuctionLot, CommissionCase,
    CommissionDecision, ElectricityAllocation, UtilityBill, UtilityMeasurement,
)
from services.contracts import current_beneficiary_assignment, effective_contract
from services.dates import today_jalali
from services.money import format_rial

SCOPED_DOMAINS = (
    ("summary", "خلاصه"),
    ("space", "مشخصات فضا"),
    ("contracts", "قراردادها"),
    ("beneficiaries", "بهره‌برداران"),
    ("appraisals", "کارشناسی"),
    ("appraisers", "کارشناسان مرتبط"),
    ("auctions", "مزایده"),
    ("commissions", "کمیسیون معاملات"),
    ("fees", "حق‌الزحمه کارشناسان"),
    ("utilities", "انشعابات و مصرف"),
    ("documents", "اسناد"),
    ("audit", "تاریخچه تغییرات / Audit"),
)
DOMAIN_KEYS = {key for key, _ in SCOPED_DOMAINS}


def normalize_domains(values, *, full=False):
    selected = [value for value in values if value in DOMAIN_KEYS]
    if full or "all" in values:
        return [key for key, _ in SCOPED_DOMAINS]
    return selected or ["summary"]


def _display(instance, field, fallback="—"):
    value = getattr(instance, field, None)
    display = getattr(instance, f"get_{field}_display", None)
    if callable(display):
        value = display()
    return fallback if value in (None, "") else value


def _section(key, title, labels, rows):
    materialized = [list(row) for row in rows]
    return {"key": key, "title": title, "labels": list(labels), "rows": materialized, "count": len(materialized)}


def build_space_sections(space, domains):
    today = today_jalali()
    sections = []

    if "summary" in domains:
        contract = effective_contract(space.contracts.all(), today)
        assignment = current_beneficiary_assignment(space, today)
        appraisals = list(space.appraisals.select_related("appraiser_ref").order_by("-appraisal_date", "-pk")[:3])
        latest_evaluation = space.auction_evaluations.select_related("rule").order_by("-evaluated_at", "-pk").first()
        latest_fee = AppraisalFee.objects.filter(appraisal__space=space).order_by("-created_at", "-pk").first()
        open_alerts = space.alerts.exclude(status="RESOLVED").count()
        latest = appraisals[0] if appraisals else None
        previous = appraisals[1:]
        sections.append(_section(
            "summary", "خلاصه پرونده",
            ("عنوان", "مقدار"),
            [
                ("کد فضا", space.code),
                ("نام فضا", space.name or "—"),
                ("منطقه", space.region.name if space.region_id else "—"),
                ("مرکز", space.center.name if space.center_id else "—"),
                ("کاربری", space.current_usage or "—"),
                ("وضعیت Lifecycle", space.get_status_display()),
                ("بهره‌بردار فعلی", assignment.beneficiary.name if assignment else "فاقد بهره‌بردار"),
                ("قرارداد فعلی", contract.number if contract else "فاقد قرارداد"),
                ("پایان قرارداد", contract.end_date if contract else "—"),
                ("آخرین کارشناسی", f"{latest.sama_code} / {latest.appraisal_date} / {format_rial(latest.amount_rial)}" if latest else "فاقد کارشناسی"),
                ("کارشناسی قبلی ۱", f"{previous[0].sama_code} / {previous[0].appraisal_date}" if len(previous) > 0 else "—"),
                ("کارشناسی قبلی ۲", f"{previous[1].sama_code} / {previous[1].appraisal_date}" if len(previous) > 1 else "—"),
                ("وضعیت Candidate", latest_evaluation.get_decision_display() if latest_evaluation else "ارزیابی نشده"),
                ("RuleVersion مزایده", latest_evaluation.rule.version if latest_evaluation else "—"),
                ("حق‌الزحمه آخرین کارشناسی", latest_fee.get_status_display() if latest_fee else "فاقد پرونده حق‌الزحمه"),
                ("هشدارهای باز", open_alerts),
            ],
        ))

    if "space" in domains:
        sections.append(_section(
            "space", "مشخصات فضا",
            ("کد فضا", "نام", "وضعیت", "منطقه", "مرکز", "حوزه سازمانی", "نوع دارایی", "مساحت", "کاربری", "کاربری پیشین", "نشانی"),
            [(
                space.code, space.name, space.get_status_display(),
                space.region.name if space.region_id else "—",
                space.center.name if space.center_id else "—",
                space.organizational_scope or "—", space.asset_type or "—",
                space.area if space.area is not None else "—",
                space.current_usage or "—", space.previous_usage or "—", space.address or "—",
            )],
        ))

    if "contracts" in domains:
        qs = space.contracts.select_related("beneficiary").order_by("-start_date", "-pk")
        sections.append(_section(
            "contracts", "قراردادها",
            ("شماره", "بهره‌بردار", "شروع", "پایان", "وضعیت زمانی", "مبلغ", "وضعیت حقوقی", "وضعیت امضا"),
            ((x.number, x.beneficiary.name, x.start_date, x.end_date, x.time_status_label,
              format_rial(x.amount_rial), x.status or "—", x.signed_state or "—") for x in qs),
        ))

    if "beneficiaries" in domains:
        qs = space.beneficiary_assignments.select_related("beneficiary").order_by("-start_date", "-pk")
        sections.append(_section(
            "beneficiaries", "بهره‌برداران",
            ("کد بهره‌بردار", "نام", "نقش", "شروع", "پایان", "وضعیت", "مبنا", "علت خاتمه"),
            ((x.beneficiary.sama_code, x.beneficiary.name, x.role, x.start_date or "—",
              x.end_date or "جاری", x.get_status_display(), x.basis or "—", x.termination_reason or "—") for x in qs),
        ))

    if "appraisals" in domains:
        qs = space.appraisals.select_related("appraiser_ref").order_by("-appraisal_date", "-pk")
        sections.append(_section(
            "appraisals", "کارشناسی",
            ("کد", "کارشناس", "تاریخ کارشناسی", "مبلغ", "شماره جواب", "تاریخ جواب", "وضعیت", "مرجع جاری"),
            ((x.sama_code, x.appraiser_display or "—", x.appraisal_date or "—", format_rial(x.amount_rial),
              x.response_number or "—", x.response_date or "—", x.status or "—", "بله" if x.is_current else "خیر") for x in qs),
        ))

    if "appraisers" in domains:
        qs = (
            Appraisal.objects.filter(space=space, appraiser_ref__isnull=False)
            .select_related("appraiser_ref").order_by("appraiser_ref__last_name", "appraiser_ref__first_name")
        )
        seen = set()
        rows = []
        for appraisal in qs:
            expert = appraisal.appraiser_ref
            if expert.pk in seen:
                continue
            seen.add(expert.pk)
            rows.append((expert.sama_code, expert.full_name, expert.license_number or "—",
                         expert.specialty or "—", expert.get_collaboration_status_display()))
        sections.append(_section("appraisers", "کارشناسان مرتبط", ("کد", "نام", "شماره پروانه", "رشته / صلاحیت", "وضعیت همکاری"), rows))

    if "auctions" in domains:
        evaluations = space.auction_evaluations.select_related("rule").order_by("-evaluated_at", "-pk")
        lots = space.auction_lots.select_related("period").order_by("-period__planned_date", "-pk")
        rows = [
            ("ارزیابی", x.evaluated_at, x.get_decision_display(), x.readiness,
             x.rule.version, "، ".join(x.reason_codes), "—") for x in evaluations
        ]
        rows += [
            ("دوره", x.period.planned_date, x.period.identity, x.readiness,
             x.get_entry_method_display(), x.result or "—", x.winner_name or "—") for x in lots
        ]
        sections.append(_section("auctions", "مزایده", ("نوع", "تاریخ", "تصمیم / دوره", "آمادگی", "Rule / روش ورود", "علت / نتیجه", "برنده"), rows))

    if "commissions" in domains:
        cases = CommissionCase.objects.filter(spaces=space).select_related("session").order_by("-session__session_date", "-pk")
        decisions = CommissionDecision.objects.filter(Q(spaces=space) | Q(case__spaces=space)).select_related("case", "responsible").distinct().order_by("-decision_date", "-pk")
        rows = [
            ("موضوع", x.session.session_date, x.sama_code, x.title, x.get_status_display(), x.responsible.get_username() if x.responsible_id else "—")
            for x in cases
        ]
        rows += [
            ("تصمیم", x.decision_date, x.sama_code, x.decision, x.get_execution_status_display(),
             x.responsible.get_username() if x.responsible_id else "—") for x in decisions
        ]
        sections.append(_section("commissions", "کمیسیون معاملات", ("نوع", "تاریخ", "کد", "موضوع / تصمیم", "وضعیت", "مسئول"), rows))

    if "fees" in domains:
        qs = AppraisalFee.objects.filter(appraisal__space=space).select_related("appraisal", "appraisal__appraiser_ref").order_by("-created_at", "-pk")
        sections.append(_section(
            "fees", "حق‌الزحمه کارشناسان",
            ("کد", "کارشناسی", "کارشناس", "مبلغ", "وضعیت", "نامه", "تاریخ پرداخت", "مرجع پرداخت"),
            ((x.sama_code, x.appraisal.sama_code, x.appraisal.appraiser_display or "—", format_rial(x.amount_rial),
              x.get_status_display(), x.letter_number or "—", x.payment_date or "—", x.payment_reference or "—") for x in qs),
        ))

    if "utilities" in domains:
        measurements = UtilityMeasurement.objects.filter(space=space).order_by("-period_end", "-pk")
        generic_bills = UtilityBill.objects.filter(connection__space=space).select_related("connection").order_by("-period_end", "-pk")
        allocations = ElectricityAllocation.objects.filter(space=space).select_related("bill", "bill__unit").order_by("-bill__period_end", "-pk")
        rows = [
            ("Measurement", x.get_utility_type_display(), f"{x.period_start} تا {x.period_end}",
             x.consumption, x.measurement_unit, "—", "زیرکنتور" if x.is_submeter else x.source or "—", "معتبر" if x.is_valid else "نامعتبر")
            for x in measurements
        ]
        rows += [
            (x.sama_code, x.connection.get_utility_type_display(), f"{x.period_start} تا {x.period_end}",
             x.consumption if x.consumption is not None else "—", "—", format_rial(x.amount_rial),
             x.connection.account_number, x.get_payment_status_display()) for x in generic_bills
        ]
        rows += [
            (x.bill.sama_code, "برق", f"{x.bill.period_start} تا {x.bill.period_end}",
             x.final_share_percent, "%", format_rial(x.payable_amount_rial),
             x.get_calculation_source_display(), x.get_confidence_level_display()) for x in allocations
        ]
        sections.append(_section("utilities", "انشعابات و مصرف", ("رکورد", "نوع", "دوره", "مصرف / سهم", "واحد", "مبلغ", "منبع / اشتراک", "وضعیت"), rows))

    if "documents" in domains:
        qs = Document.objects.filter(entity_type="CommercialSpace", entity_id=space.code).order_by("-uploaded_at", "-pk")
        sections.append(_section(
            "documents", "اسناد",
            ("عنوان", "نوع", "مرجع", "تاریخ سند", "وضعیت", "نام فایل", "SHA-256"),
            ((x.title, x.document_type, x.reference or "—", x.document_date or "—", x.status_label,
              x.original_filename, x.sha256) for x in qs),
        ))

    if "audit" in domains:
        contract_ids = [str(pk) for pk in Contract.objects.filter(space=space).values_list("pk", flat=True)]
        assignment_ids = [str(pk) for pk in BeneficiaryAssignment.objects.filter(space=space).values_list("pk", flat=True)]
        appraisal_ids = [str(pk) for pk in Appraisal.objects.filter(space=space).values_list("pk", flat=True)]
        fee_ids = [str(pk) for pk in AppraisalFee.objects.filter(appraisal__space=space).values_list("pk", flat=True)]
        condition = Q(entity_type="CommercialSpace", entity_id=space.code)
        if contract_ids:
            condition |= Q(entity_type="Contract", entity_id__in=contract_ids)
        if assignment_ids:
            condition |= Q(entity_type="BeneficiaryAssignment", entity_id__in=assignment_ids)
        if appraisal_ids:
            condition |= Q(entity_type="Appraisal", entity_id__in=appraisal_ids)
        if fee_ids:
            condition |= Q(entity_type="AppraisalFee", entity_id__in=fee_ids)
        qs = AuditEvent.objects.filter(condition).select_related("actor").order_by("-created_at", "-pk")
        sections.append(_section(
            "audit", "تاریخچه تغییرات / Audit",
            ("زمان", "Entity", "Action", "کاربر", "علت", "مقدار قبلی", "مقدار جدید"),
            ((x.created_at, x.entity_type, x.action, x.actor.get_username() if x.actor_id else "سیستم",
              x.reason or "—", str(x.before) if x.before is not None else "—", str(x.after) if x.after is not None else "—") for x in qs),
        ))

    return sections
