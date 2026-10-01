from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domains.identity.models import AuditEvent
from domains.operations.models import FileMovement, TimelineEvent
from services.database import retry_locked
from services.dates import normalize_jalali


def current_holder(space):
    return space.file_movements.filter(returned_at__isnull=True).order_by("-handover_at", "-id").first()


def _date(value):
    raw=(value or "").strip()
    if not raw:return ""
    try:return normalize_jalali(raw)
    except ValueError as exc:raise ValidationError("تاریخ مهلت معتبر نیست.") from exc


@retry_locked
@transaction.atomic
def register_handover(*,space,actor,values,ip_address=None):
    required=("location","holder","delivered_by","received_by","signature_state","direction")
    missing=[field for field in required if not str(values.get(field,"") or "").strip()]
    if missing:raise ValidationError("تکمیل همه فیلدهای الزامی گردش پرونده لازم است.")
    direction=str(values.get("direction","")).strip()
    if direction not in FileMovement.Direction.values:
        raise ValidationError("جهت گردش پرونده معتبر نیست.")
    now=timezone.now()
    existing=list(
        FileMovement.objects.select_for_update()
        .filter(space=space,returned_at__isnull=True)
        .order_by("-handover_at","-id")
    )
    for item in existing:
        item.returned_at=now
        item.save(update_fields=["returned_at"])
    movement=FileMovement.objects.create(
        space=space,
        location=str(values.get("location","")).strip(),
        holder=str(values.get("holder","")).strip(),
        delivered_by=str(values.get("delivered_by","")).strip(),
        received_by=str(values.get("received_by","")).strip(),
        handover_at=now,
        signature_state=str(values.get("signature_state","")).strip(),
        direction=direction,
        next_action=str(values.get("next_action","") or "").strip(),
        due_date=_date(values.get("due_date","")),
        notes=str(values.get("notes","") or "").strip(),
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action="FILE_MOVEMENT_CREATE",entity_type="CommercialSpace",entity_id=space.code,
        before={"closed_movement_ids":[item.pk for item in existing]} if existing else None,
        after={
            "movement_id":movement.pk,"holder":movement.holder,"location":movement.location,
            "direction":movement.direction,"due_date":movement.due_date,
        },
        ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=space,event_type="FILE_MOVEMENT_CREATE",occurred_at=movement.handover_at,
        source_entity="FileMovement",source_entity_id=str(movement.pk),title="ثبت تحویل فیزیکی پرونده",
        description=f"{movement.holder} — {movement.location}",previous_state=existing[0].holder if existing else "",
        new_state=movement.holder,responsible_person=actor.get_full_name() or actor.username,
        provenance="گردش فیزیکی ثبت‌شده در سما",target_url=f"/spaces/{space.code}/",
    )
    return movement


@retry_locked
@transaction.atomic
def close_current_movement(*,space,actor,reason,ip_address=None):
    reason=(reason or "").strip()
    if not reason:raise ValidationError("علت بازگشت / بستن تحویل پرونده الزامی است.")
    movement=(
        FileMovement.objects.select_for_update()
        .filter(space=space,returned_at__isnull=True)
        .order_by("-handover_at","-id")
        .first()
    )
    if not movement:raise ValidationError("برای این فضا پرونده‌ای در دست شخص یا محل جاری ثبت نشده است.")
    movement.returned_at=timezone.now()
    movement.save(update_fields=["returned_at"])
    AuditEvent.objects.create(
        actor=actor,action="FILE_MOVEMENT_RETURN",entity_type="CommercialSpace",entity_id=space.code,
        reason=reason,before={"movement_id":movement.pk,"holder":movement.holder,"location":movement.location},
        after={"returned_at":movement.returned_at.isoformat()},ip_address=ip_address,
    )
    TimelineEvent.objects.create(
        space=space,event_type="FILE_MOVEMENT_RETURN",occurred_at=movement.returned_at,
        source_entity="FileMovement",source_entity_id=str(movement.pk),title="بازگشت / خاتمه تحویل پرونده",
        description=reason,previous_state=movement.holder,new_state="فاقد دارنده جاری",
        responsible_person=actor.get_full_name() or actor.username,
        provenance="گردش فیزیکی ثبت‌شده در سما",target_url=f"/spaces/{space.code}/",
    )
    return movement
