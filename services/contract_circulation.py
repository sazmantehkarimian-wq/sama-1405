"""Contract circulation is operational workflow, not a Contract record."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from domains.contracts.models import (
    ContractCirculation, ContractCustodyTransfer, ContractFinalApproval, ContractSignatureStep,
)
from domains.identity.models import AuditEvent
from domains.operations.models import TimelineEvent
from services.contracts import create_contract
from services.database import retry_locked
from services.dates import normalize_jalali
from services.text import normalize_persian_text

OPERATIONAL_START_DATE = "1405/07/01"


def _date(value, *, required=False):
    raw = (value or "").strip()
    if not raw and not required:
        return ""
    try:
        result = normalize_jalali(raw)
    except ValueError as exc:
        raise ValidationError("تاریخ شمسی معتبر نیست.") from exc
    if required and not result:
        raise ValidationError("تاریخ الزامی است.")
    return result


def _timeline(circulation, actor, event_type, title, *, description="", previous="", new=""):
    TimelineEvent.objects.create(
        space=circulation.space,
        event_type=event_type,
        source_entity="ContractCirculation",
        source_entity_id=str(circulation.pk),
        title=title,
        description=description,
        previous_state=previous,
        new_state=new,
        responsible_person=actor.get_full_name() or actor.username,
        provenance="گردش قرارداد ثبت‌شده در سما",
        target_url=f"/contract-circulations/{circulation.pk}/",
    )


def current_custody(circulation):
    return circulation.transfers.filter(returned_at__isnull=True).order_by("-delivered_at", "-pk").first()


def _ensure_open(circulation):
    if circulation.state in {
        ContractCirculation.State.CONVERTED,
        ContractCirculation.State.CLOSED_NO_CONTRACT,
    }:
        raise ValidationError("این گردش قرارداد مختومه است و قابل تغییر نیست.")


@retry_locked
@transaction.atomic
def create_circulation(*, space, beneficiary, subject, operational_start_date, next_action, actor, due_date="", ip_address=None):
    start = _date(operational_start_date, required=True)
    if start < OPERATIONAL_START_DATE:
        raise ValidationError("گردش عملیاتی قرارداد پیش از ۱۴۰۵/۰۷/۰۱ مجاز نیست.")
    subject = normalize_persian_text(subject)
    next_action = normalize_persian_text(next_action)
    if not subject or not next_action:
        raise ValidationError("موضوع و اقدام بعدی گردش قرارداد الزامی است.")
    case = ContractCirculation.objects.create(
        space=space,
        beneficiary=beneficiary,
        subject=subject,
        operational_start_date=start,
        next_action=next_action,
        due_date=_date(due_date),
        created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_CIRCULATION_CREATE",
        entity_type="ContractCirculation", entity_id=str(case.pk),
        after={
            "identity": case.identity, "space": space.code, "beneficiary_id": beneficiary.pk,
            "operational_start_date": start, "state": case.state,
        },
        ip_address=ip_address,
    )
    _timeline(case, actor, "CONTRACT_CIRCULATION_CREATE", f"ایجاد گردش قرارداد {case.identity}", new=case.state)
    return case


@retry_locked
@transaction.atomic
def add_signature_step(*, circulation, actor, role, unit, person="", required=True, ip_address=None):
    _ensure_open(circulation)
    role = normalize_persian_text(role)
    unit = normalize_persian_text(unit)
    person = normalize_persian_text(person)
    if not role or not unit:
        raise ValidationError("نقش امضا و واحد سازمانی الزامی است.")
    order = (circulation.signature_steps.order_by("-order").values_list("order", flat=True).first() or 0) + 1
    step = ContractSignatureStep.objects.create(
        circulation=circulation, order=order, role=role, unit=unit, person=person,
        required=bool(required), updated_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_SIGNATURE_STEP_CREATE",
        entity_type="ContractCirculation", entity_id=str(circulation.pk),
        after={"step_id": step.pk, "order": order, "role": role, "unit": unit, "required": step.required},
        ip_address=ip_address,
    )
    return step


@retry_locked
@transaction.atomic
def transition_signature_step(*, step, actor, new_status, note="", document=None, ip_address=None):
    circulation = step.circulation
    _ensure_open(circulation)
    if new_status not in ContractSignatureStep.Status.values:
        raise ValidationError("وضعیت امضا معتبر نیست.")
    allowed = {
        ContractSignatureStep.Status.PENDING: {ContractSignatureStep.Status.SENT},
        ContractSignatureStep.Status.SENT: {ContractSignatureStep.Status.SIGNED, ContractSignatureStep.Status.RETURNED},
        ContractSignatureStep.Status.RETURNED: {ContractSignatureStep.Status.SENT},
        ContractSignatureStep.Status.SIGNED: set(),
        ContractSignatureStep.Status.WAIVED: set(),
    }
    if not step.required:
        allowed[step.status] = set(allowed.get(step.status, set())) | {ContractSignatureStep.Status.WAIVED}
    if new_status not in allowed.get(step.status, set()):
        raise ValidationError("این انتقال وضعیت امضا مجاز نیست.")
    now = timezone.now()
    before = step.status
    step.status = new_status
    step.note = normalize_persian_text(note)
    if document is not None:
        step.document = document
    if new_status == ContractSignatureStep.Status.SENT:
        step.sent_at = now
    elif new_status == ContractSignatureStep.Status.SIGNED:
        step.signed_at = now
    elif new_status == ContractSignatureStep.Status.RETURNED:
        step.returned_at = now
    step.updated_by = actor
    step.save()
    if new_status == ContractSignatureStep.Status.RETURNED:
        circulation.state = ContractCirculation.State.RETURNED
    elif circulation.signature_steps.filter(required=True).exclude(status=ContractSignatureStep.Status.SIGNED).exists():
        circulation.state = ContractCirculation.State.SIGNING
    else:
        circulation.state = ContractCirculation.State.READY_APPROVAL
    circulation.save(update_fields=["state", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_SIGNATURE_TRANSITION",
        entity_type="ContractSignatureStep", entity_id=str(step.pk),
        reason=step.note, before={"status": before},
        after={"status": new_status, "circulation_state": circulation.state, "document_id": step.document_id},
        ip_address=ip_address,
    )
    _timeline(
        circulation, actor, "CONTRACT_SIGNATURE_TRANSITION",
        f"تغییر وضعیت امضا: {step.role}", description=step.note,
        previous=before, new=new_status,
    )
    return step


@retry_locked
@transaction.atomic
def transfer_custody(*, circulation, sender, receiver, unit, purpose, next_action, actor,
                     due_date="", direction="OUT", signature_status="", document=None, ip_address=None):
    _ensure_open(circulation)
    if current_custody(circulation):
        raise ValidationError("این گردش قرارداد هم‌اکنون یک تحویل باز دارد؛ ابتدا بازگشت را ثبت کنید.")
    values = {
        "sender": normalize_persian_text(sender),
        "receiver": normalize_persian_text(receiver),
        "unit": normalize_persian_text(unit),
        "purpose": normalize_persian_text(purpose),
        "next_action": normalize_persian_text(next_action),
    }
    if any(not value for value in values.values()):
        raise ValidationError("تحویل‌دهنده، تحویل‌گیرنده، واحد، هدف و اقدام بعدی الزامی هستند.")
    if direction not in ContractCustodyTransfer.Direction.values:
        raise ValidationError("جهت گردش معتبر نیست.")
    try:
        event = ContractCustodyTransfer.objects.create(
            circulation=circulation, sender=values["sender"], receiver=values["receiver"],
            unit=values["unit"], delivered_at=timezone.now(), purpose=values["purpose"],
            next_action=values["next_action"], due_date=_date(due_date), direction=direction,
            signature_status=normalize_persian_text(signature_status), document=document, created_by=actor,
        )
    except IntegrityError as exc:
        raise ValidationError("این گردش قرارداد هم‌اکنون یک تحویل باز دارد.") from exc
    previous = circulation.state
    circulation.state = ContractCirculation.State.SIGNING
    circulation.next_action = event.next_action
    circulation.due_date = event.due_date
    circulation.save(update_fields=["state", "next_action", "due_date", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_CUSTODY_TRANSFER",
        entity_type="ContractCustodyTransfer", entity_id=str(event.pk),
        after={"circulation": circulation.identity, "receiver": event.receiver, "unit": event.unit, "direction": event.direction},
        ip_address=ip_address,
    )
    _timeline(circulation, actor, "CONTRACT_CUSTODY_TRANSFER", "تحویل پرونده گردش قرارداد",
              description=f"{event.receiver} — {event.unit}", previous=previous, new=circulation.state)
    return event


@retry_locked
@transaction.atomic
def return_custody(*, circulation, actor, note, ip_address=None):
    _ensure_open(circulation)
    note = normalize_persian_text(note)
    if not note:
        raise ValidationError("شرح بازگشت پرونده الزامی است.")
    event = (
        ContractCustodyTransfer.objects.select_for_update()
        .filter(circulation=circulation, returned_at__isnull=True)
        .order_by("-delivered_at", "-pk").first()
    )
    if not event:
        raise ValidationError("برای این گردش قرارداد تحویل بازی وجود ندارد.")
    event.returned_at = timezone.now()
    event.return_note = note
    event.save(update_fields=["returned_at", "return_note"])
    before = circulation.state
    circulation.state = ContractCirculation.State.RETURNED
    circulation.save(update_fields=["state", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_CUSTODY_RETURN",
        entity_type="ContractCustodyTransfer", entity_id=str(event.pk),
        reason=note, before={"state": before}, after={"state": circulation.state, "returned_at": event.returned_at.isoformat()},
        ip_address=ip_address,
    )
    _timeline(circulation, actor, "CONTRACT_CUSTODY_RETURN", "بازگشت پرونده گردش قرارداد",
              description=note, previous=before, new=circulation.state)
    return event


@retry_locked
@transaction.atomic
def final_approve(*, circulation, actor, note="", ip_address=None):
    _ensure_open(circulation)
    if current_custody(circulation):
        raise ValidationError("تا زمان ثبت بازگشت تحویل جاری، تأیید نهایی مجاز نیست.")
    if not circulation.signature_steps.exists():
        raise ValidationError("حداقل یک مرحله امضا باید از دستور کار مصوب ثبت شود.")
    if circulation.signature_steps.filter(required=True).exclude(status=ContractSignatureStep.Status.SIGNED).exists():
        raise ValidationError("همه مراحل امضای الزامی باید تکمیل شوند.")
    if hasattr(circulation, "final_approval"):
        raise ValidationError("تأیید نهایی قبلاً ثبت شده است.")
    approval = ContractFinalApproval.objects.create(
        circulation=circulation, approver=actor, approved_at=timezone.now(),
        note=normalize_persian_text(note),
    )
    before = circulation.state
    circulation.state = ContractCirculation.State.APPROVED
    circulation.save(update_fields=["state", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_FINAL_APPROVAL",
        entity_type="ContractFinalApproval", entity_id=str(approval.pk),
        after={"circulation": circulation.identity, "state": circulation.state}, ip_address=ip_address,
    )
    _timeline(circulation, actor, "CONTRACT_FINAL_APPROVAL", "تأیید نهایی گردش قرارداد",
              description=approval.note, previous=before, new=circulation.state)
    return approval


@retry_locked
@transaction.atomic
def convert_to_contract(*, circulation, actor, values, ip_address=None):
    _ensure_open(circulation)
    if circulation.official_contract_id:
        raise ValidationError("قرارداد رسمی این گردش قبلاً ایجاد شده است.")
    if not hasattr(circulation, "final_approval"):
        raise ValidationError("تأیید نهایی گردش قرارداد ثبت نشده است.")
    contract = create_contract(
        space=circulation.space, beneficiary=circulation.beneficiary,
        actor=actor, values=values, ip_address=ip_address,
    )
    circulation.official_contract = contract
    before = circulation.state
    circulation.state = ContractCirculation.State.CONVERTED
    circulation.next_action = "قرارداد رسمی ثبت شد"
    circulation.save(update_fields=["official_contract", "state", "next_action", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_CIRCULATION_CONVERT",
        entity_type="ContractCirculation", entity_id=str(circulation.pk),
        after={"contract_id": contract.pk, "contract_number": contract.number, "state": circulation.state},
        ip_address=ip_address,
    )
    _timeline(circulation, actor, "CONTRACT_CIRCULATION_CONVERT", f"ثبت قرارداد رسمی {contract.number}",
              previous=before, new=circulation.state)
    return contract


@retry_locked
@transaction.atomic
def close_without_contract(*, circulation, actor, reason, ip_address=None):
    _ensure_open(circulation)
    if circulation.official_contract_id:
        raise ValidationError("گردش دارای قرارداد رسمی قابل مختومه‌سازی بدون قرارداد نیست.")
    if current_custody(circulation):
        raise ValidationError("ابتدا بازگشت تحویل جاری را ثبت کنید.")
    reason = normalize_persian_text(reason)
    if not reason:
        raise ValidationError("علت مختومه‌سازی بدون قرارداد الزامی است.")
    before = circulation.state
    circulation.state = ContractCirculation.State.CLOSED_NO_CONTRACT
    circulation.close_reason = reason
    circulation.next_action = "مختومه"
    circulation.save(update_fields=["state", "close_reason", "next_action", "updated_at"])
    AuditEvent.objects.create(
        actor=actor, action="CONTRACT_CIRCULATION_CLOSE_NO_CONTRACT",
        entity_type="ContractCirculation", entity_id=str(circulation.pk),
        reason=reason, before={"state": before}, after={"state": circulation.state},
        ip_address=ip_address,
    )
    _timeline(circulation, actor, "CONTRACT_CIRCULATION_CLOSE_NO_CONTRACT", "مختومه‌سازی گردش بدون قرارداد",
              description=reason, previous=before, new=circulation.state)
    return circulation
