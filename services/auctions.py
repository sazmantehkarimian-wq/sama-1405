"""Deterministic, explainable auction candidate rules from the FROZEN authority."""
from decimal import Decimal

import jdatetime
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from domains.identity.models import AuditEvent
from domains.operations.models import Appraisal, AuctionEvaluation, AuctionInstruction, AuctionLot, AuctionPeriod, AuctionRule, TimelineEvent
from services.database import retry_locked


def _date(value: str) -> jdatetime.date:
    year, month, day = (int(part) for part in value.split("/"))
    return jdatetime.date(year, month, day)


def _add_months(value: jdatetime.date, months: int) -> jdatetime.date:
    index = value.year * 12 + value.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    day = min(value.day, jdatetime.j_days_in_month[month - 1] if month < 12 else (30 if jdatetime.date(year, 1, 1).isleap() else 29))
    return jdatetime.date(year, month, day)


def _level(amount: Decimal, rule: AuctionRule) -> str:
    if amount <= rule.minor_ceiling_rial:
        return "MINOR"
    if amount <= rule.medium_ceiling_rial:
        return "MEDIUM"
    return "MAJOR"


@retry_locked
@transaction.atomic
def evaluate_space(*, space, on_date: str, actor, rule: AuctionRule | None = None,
                   auction_date: str = "", ip_address=None) -> AuctionEvaluation:
    today = _date(on_date)
    rule = rule or AuctionRule.objects.filter(active=True,effective_year=today.year).order_by("-id").first()
    if not rule:
        raise ValidationError("قاعده فعال و مصوب مزایده برای سال ارزیابی ثبت نشده است.")
    contracts = []
    for contract in space.contracts.exclude(status__in=["باطل", "فسخ‌شده"]):
        try:
            if _date(contract.start_date) <= today <= _date(contract.end_date):
                contracts.append(contract)
        except (ValueError, TypeError):
            continue
    contract = sorted(contracts, key=lambda item: item.start_date, reverse=True)[0] if contracts else None
    appraisal = space.appraisals.filter(is_current=True).exclude(appraisal_date="").order_by("-appraisal_date","-pk").first()
    appraisal_date = None
    if appraisal:
        try:
            appraisal_date = _date(appraisal.appraisal_date)
        except (ValueError, TypeError):
            appraisal = None
    appraisal_expiry = _add_months(appraisal_date, rule.appraisal_valid_months) if appraisal_date else None
    appraisal_reference_date = _date(auction_date) if auction_date else today
    appraisal_valid_today = bool(appraisal_expiry and appraisal_expiry >= today)
    appraisal_valid_at_auction = bool(appraisal_expiry and appraisal_expiry >= appraisal_reference_date)
    appraisal_valid = appraisal_valid_at_auction
    reasons, decision, readiness, amount, basis, remaining = [], "REVIEW_REQUIRED", "REVIEW_REQUIRED", None, "", None

    if space.status != "ACTIVE":
        decision, readiness, reasons = "NOT_CANDIDATE", "ACTION_REQUIRED", ["NOT_CANDIDATE_SPACE_OUT_OF_CYCLE"]
    elif contract:
        remaining = (contract and (_date(contract.end_date).togregorian() - today.togregorian()).days)
        amount, basis = contract.amount_rial, "CONTRACT"
        if amount is None:
            reasons = ["REVIEW_MISSING_CONTRACT_AMOUNT"]
        elif rule.contract_window_min_days <= remaining <= rule.contract_window_max_days:
            if _level(amount, rule) == "MINOR":
                decision, readiness, reasons = "NOT_CANDIDATE", "ACTION_REQUIRED", ["NOT_CANDIDATE_LEVEL_JOZ"]
            else:
                decision, reasons = "CANDIDATE", ["CANDIDATE_CONTRACT_WINDOW"]
                readiness = "READY" if appraisal_valid else "ACTION_REQUIRED"
                if not appraisal:
                    reasons.append("REVIEW_MISSING_APPRAISAL")
                elif appraisal_valid_today and auction_date and not appraisal_valid_at_auction:
                    reasons.append("ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION")
                elif not appraisal_valid:
                    reasons.append("REVIEW_MISSING_APPRAISAL")
        else:
            decision, readiness, reasons = "NOT_CANDIDATE", "ACTION_REQUIRED", ["NOT_CANDIDATE_CONTRACT_OUTSIDE_WINDOW"]
    else:
        amount, basis = (appraisal.amount_rial if appraisal else None), "APPRAISAL"
        if not appraisal or amount is None or not appraisal_valid:
            if appraisal and appraisal_valid_today and auction_date and not appraisal_valid_at_auction:
                reasons = ["ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION"]
            else:
                reasons = ["REVIEW_MISSING_APPRAISAL"]
            readiness = "ACTION_REQUIRED"
        elif _level(amount, rule) == "MINOR":
            decision, readiness, reasons = "NOT_CANDIDATE", "ACTION_REQUIRED", ["NOT_CANDIDATE_LEVEL_JOZ"]
        else:
            decision, readiness, reasons = "CANDIDATE", "READY", ["CANDIDATE_NO_CONTRACT_VALID_APPRAISAL"]

    instructions = list(
        space.auction_instructions.filter(active=True,effective_from__lte=on_date)
        .filter(Q(effective_to="")|Q(effective_to__gte=on_date))
        .order_by("-effective_from","-pk")
    )
    directions={item.direction for item in instructions}
    if len(directions)>1:
        decision,readiness,reasons="REVIEW_REQUIRED","REVIEW_REQUIRED",["CONFLICTING_AUTHORIZED_INSTRUCTIONS"]
    elif directions=={AuctionInstruction.Direction.EXCLUDE}:
        decision,readiness,reasons="NOT_CANDIDATE","ACTION_REQUIRED",["BLOCKED_BY_MANUAL_EXCLUSION"]
    elif directions=={AuctionInstruction.Direction.INCLUDE}:
        decision="CANDIDATE"
        readiness="READY" if appraisal_valid else "ACTION_REQUIRED"
        reasons=["INCLUDED_BY_MANUAL_OVERRIDE"]
        if not appraisal:
            reasons.append("REVIEW_MISSING_APPRAISAL")
        elif appraisal_valid_today and auction_date and not appraisal_valid_at_auction:
            reasons.append("ACTION_APPRAISAL_EXPIRES_BEFORE_AUCTION")
    snapshot = {"space_code": space.code, "space_status": space.status, "contract_id": contract.pk if contract else None,
        "remaining_days": remaining, "amount_rial": str(amount) if amount is not None else None, "amount_basis": basis,
        "transaction_level": _level(amount, rule) if amount is not None else None,
        "appraisal_id": appraisal.pk if appraisal else None, "appraisal_date": appraisal.appraisal_date if appraisal else None,
        "appraisal_amount_rial": str(appraisal.amount_rial) if appraisal and appraisal.amount_rial is not None else None,
        "appraisal_expiry": str(appraisal_expiry) if appraisal_expiry else None,
        "rule_version": rule.version, "threshold_rule_version": rule.version,
        "override_state":[{"id":x.pk,"source":x.source,"direction":x.direction,"reference":x.reference} for x in instructions],
        "evaluation_date": on_date, "auction_date": auction_date or None, "engine_version":"zero-data-1"}
    evaluation = AuctionEvaluation.objects.create(space=space, rule=rule, decision=decision,
        readiness=readiness, reason_codes=reasons, snapshot=snapshot, evaluated_by=actor)
    AuditEvent.objects.create(actor=actor, action="AUCTION_EVALUATE", entity_type="AuctionEvaluation",
        entity_id=str(evaluation.pk), after={"decision": decision, "reasons": reasons, "space": space.code},
        ip_address=ip_address)
    TimelineEvent.objects.create(space=space,event_type="AUCTION_EVALUATE",jalali_date=on_date,source_entity="AuctionEvaluation",source_entity_id=str(evaluation.pk),title="ارزیابی شرایط ورود به مزایده",new_state=evaluation.get_decision_display(),responsible_person=actor.get_full_name() or actor.username,provenance="ارزیابی نسخه‌دار بر اساس قاعده مصوب",target_url=f"/spaces/{space.code}/")
    return evaluation


@retry_locked
@transaction.atomic
def create_period(*, identity: str, title: str, planned_date: str, actor, ip_address=None) -> AuctionPeriod:
    identity, title = identity.strip(), title.strip()
    if not identity or not title:
        raise ValidationError("شناسه و عنوان دوره مزایده الزامی است.")
    try:
        _date(planned_date)
    except (ValueError, TypeError) as exc:
        raise ValidationError("تاریخ شمسی دوره معتبر نیست.") from exc
    if AuctionPeriod.objects.filter(identity=identity).exists():
        raise ValidationError("شناسه دوره مزایده تکراری است.")
    period = AuctionPeriod.objects.create(
        identity=identity, title=title, planned_date=planned_date, created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor, action="AUCTION_PERIOD_CREATE", entity_type="AuctionPeriod",
        entity_id=str(period.pk), after={"identity": identity, "planned_date": planned_date},
        ip_address=ip_address,
    )
    return period


@retry_locked
@transaction.atomic
def add_evaluated_lot(*, period: AuctionPeriod, evaluation: AuctionEvaluation, actor,
                      ip_address=None) -> AuctionLot:
    if period.state != AuctionPeriod.State.DRAFT:
        raise ValidationError("افزودن فضا فقط به دوره پیش‌نویس مجاز است.")
    if evaluation.decision != AuctionEvaluation.Decision.CANDIDATE:
        raise ValidationError("فقط ارزیابی کاندیدا می‌تواند وارد دوره شود.")
    lot, created = AuctionLot.objects.get_or_create(
        period=period, space=evaluation.space,
        defaults={"evaluation": evaluation, "readiness": evaluation.readiness},
    )
    if not created:
        raise ValidationError("این فضا قبلاً در دوره ثبت شده است.")
    AuditEvent.objects.create(
        actor=actor, action="AUCTION_LOT_ADD", entity_type="AuctionLot", entity_id=str(lot.pk),
        after={"period": period.identity, "space": evaluation.space.code,
               "evaluation": evaluation.pk}, ip_address=ip_address,
    )
    TimelineEvent.objects.create(space=evaluation.space,event_type="AUCTION_LOT_ADD",jalali_date=period.planned_date,source_entity="AuctionLot",source_entity_id=str(lot.pk),title=f"افزودن به دوره مزایده {period.title}",new_state=lot.readiness,responsible_person=actor.get_full_name() or actor.username,provenance="ثبت عملیاتی دوره مزایده",target_url=f"/spaces/{evaluation.space.code}/")
    return lot



@retry_locked
@transaction.atomic
def create_instruction(*, space, actor, values, commission_decision=None, ip_address=None):
    if not actor.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("ثبت دستور مؤثر بر مزایده فقط برای کاربر مجاز امکان‌پذیر است.")
    source=values.get("source","")
    direction=values.get("direction","")
    reason=(values.get("reason") or "").strip()
    reference=(values.get("reference") or "").strip()
    if source not in AuctionInstruction.Source.values or direction not in AuctionInstruction.Direction.values:
        raise ValidationError("نوع منبع یا جهت اثر معتبر نیست.")
    if not reason or not reference:
        raise ValidationError("علت و مرجع دستور الزامی است.")
    try:
        effective_from=_date(values.get("effective_from",""))
        effective_to=_date(values.get("effective_to","")) if values.get("effective_to") else ""
    except (ValueError,TypeError) as exc:
        raise ValidationError("تاریخ اثر دستور معتبر نیست.") from exc
    if effective_to and effective_to<effective_from:
        raise ValidationError("پایان اثر نمی‌تواند قبل از شروع اثر باشد.")
    if source==AuctionInstruction.Source.COMMISSION and commission_decision is None:
        raise ValidationError("برای دستور کمیسیون، انتخاب تصمیم کمیسیون الزامی است.")
    item=AuctionInstruction.objects.create(
        space=space,source=source,direction=direction,reason=reason,reference=reference,
        effective_from=effective_from,effective_to=effective_to,
        commission_decision=commission_decision,created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action="AUCTION_INSTRUCTION_CREATE",entity_type="AuctionInstruction",
        entity_id=str(item.pk),after={"space":space.code,"source":source,"direction":direction,"reference":reference,
        "effective_from":effective_from,"effective_to":effective_to},reason=reason,ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=space,event_type="AUCTION_INSTRUCTION_CREATE",jalali_date=effective_from,
        source_entity="AuctionInstruction",source_entity_id=str(item.pk),
        title="ثبت دستور مؤثر بر مزایده",description=f"{item.get_source_display()} — {item.get_direction_display()} — {reference}",
        new_state=direction,responsible_person=actor.get_full_name() or actor.username,
        provenance="دستور رسمی ثبت‌شده با مرجع و Audit",target_url=f"/spaces/{space.code}/",
    )
    return item
