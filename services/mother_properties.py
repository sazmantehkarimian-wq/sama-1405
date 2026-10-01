from datetime import timedelta

import jdatetime
from django.core.exceptions import ValidationError
from django.db import transaction

from domains.identity.models import AuditEvent
from domains.properties.models import MotherPropertyCorrespondence, MotherPropertyUsageHistory
from services.database import retry_locked
from services.dates import normalize_jalali
from services.text import normalize_persian_text


def _previous_jalali_day(value):
    year, month, day = (int(part) for part in value.split("/"))
    current = jdatetime.date(year, month, day).togregorian()
    return jdatetime.date.fromgregorian(date=current - timedelta(days=1)).strftime("%Y/%m/%d")


@retry_locked
@transaction.atomic
def change_mother_property_usage(*, property, actor, values, ip_address=None):
    try:
        start = normalize_jalali(values.get("start_date", ""))
    except ValueError as exc:
        raise ValidationError("تاریخ شروع بهره‌برداری معتبر نیست.") from exc
    if not start:
        raise ValidationError("تاریخ شروع بهره‌برداری الزامی است.")

    usage_status = normalize_persian_text(values.get("usage_status", ""))
    if not usage_status:
        raise ValidationError("وضعیت بهره‌برداری الزامی است.")

    current = (
        MotherPropertyUsageHistory.objects.select_for_update()
        .filter(property=property, end_date="")
        .order_by("-start_date", "-pk")
        .first()
    )
    termination_reason = normalize_persian_text(values.get("termination_reason", ""))
    if current and not termination_reason:
        raise ValidationError("برای تغییر بهره‌برداری، علت خاتمه سابقه جاری الزامی است.")
    if current:
        previous_end = _previous_jalali_day(start)
        if current.start_date and previous_end < current.start_date:
            raise ValidationError("تاریخ شروع سابقه جدید باید بعد از شروع سابقه جاری باشد.")
        current.end_date = previous_end
        current.termination_reason = termination_reason
        current.save(update_fields=["end_date", "termination_reason"])

    record = MotherPropertyUsageHistory.objects.create(
        property=property,
        usage_status=usage_status,
        holder_type=normalize_persian_text(values.get("holder_type", "")),
        holder_unit=normalize_persian_text(values.get("holder_unit", "")),
        beneficiary_name=normalize_persian_text(values.get("beneficiary_name", "")),
        beneficiary_type=normalize_persian_text(values.get("beneficiary_type", "")),
        start_date=start,
        end_date="",
        basis=normalize_persian_text(values.get("basis", "")),
        contract_reference=normalize_persian_text(values.get("contract_reference", "")),
        document=values.get("document"),
        notes=normalize_persian_text(values.get("notes", "")),
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="MOTHER_PROPERTY_USAGE_CHANGE",
        entity_type="MotherProperty",
        entity_id=property.identifier,
        reason=termination_reason,
        before={
            "usage_id": current.pk,
            "usage_status": current.usage_status,
            "holder_unit": current.holder_unit,
            "beneficiary_name": current.beneficiary_name,
        } if current else None,
        after={
            "usage_id": record.pk,
            "usage_status": record.usage_status,
            "holder_unit": record.holder_unit,
            "beneficiary_name": record.beneficiary_name,
            "start_date": record.start_date,
        },
        ip_address=ip_address,
    )
    return record



@retry_locked
@transaction.atomic
def transition_mother_property_correspondence(*, record, actor, new_status, reason, ip_address=None):
    if new_status not in MotherPropertyCorrespondence.FollowUpStatus.values:
        raise ValidationError("وضعیت پیگیری معتبر نیست.")
    reason = normalize_persian_text(reason)
    if not reason:
        raise ValidationError("علت / نتیجه تغییر وضعیت پیگیری الزامی است.")
    if not record.needs_follow_up:
        raise ValidationError("این مکاتبه به‌عنوان نیازمند پیگیری ثبت نشده است.")
    if record.follow_up_status == new_status:
        raise ValidationError("وضعیت جدید با وضعیت فعلی یکسان است.")
    before = record.follow_up_status
    record.follow_up_status = new_status
    record.save(update_fields=["follow_up_status"])
    AuditEvent.objects.create(
        actor=actor,
        action="MOTHER_PROPERTY_CORRESPONDENCE_TRANSITION",
        entity_type="MotherProperty",
        entity_id=record.property.identifier,
        reason=reason,
        before={"correspondence_id": record.pk, "follow_up_status": before},
        after={"correspondence_id": record.pk, "follow_up_status": new_status},
        ip_address=ip_address,
    )
    return record
