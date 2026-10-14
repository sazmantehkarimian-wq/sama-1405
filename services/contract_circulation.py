"""Transactional contract-circulation rules; circulation is not a Contract."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from domains.contracts.models import Contract, ContractCirculation, ContractCustodyTransfer, ContractFinalApproval, ContractSignatureStep
from domains.identity.models import AuditEvent

OPERATIONAL_START_DATE = "1405/07/01"

def _audit(actor, action, obj, after=None, before=None):
    AuditEvent.objects.create(actor=actor, action=action, entity_type=type(obj).__name__, entity_id=str(obj.pk), before=before, after=after)

def current_custody(circulation):
    return circulation.transfers.filter(returned_at__isnull=True).order_by('-delivered_at', '-pk').first()

@transaction.atomic
def create_circulation(*, space, beneficiary, subject, operational_start_date, next_action, actor, due_date="", signature_steps=()):
    if operational_start_date < OPERATIONAL_START_DATE:
        raise ValidationError("گردش عملیاتی قرارداد پیش از ۱۴۰۵/۰۷/۰۱ مجاز نیست.")
    case=ContractCirculation.objects.create(space=space,beneficiary=beneficiary,subject=subject,operational_start_date=operational_start_date,next_action=next_action,due_date=due_date,created_by=actor)
    for position, step in enumerate(signature_steps, 1):
        ContractSignatureStep.objects.create(circulation=case,order=position,role=step['role'],unit=step['unit'],person=step.get('person',''),required=step.get('required',True),updated_by=actor)
    _audit(actor,'CONTRACT_CIRCULATION_CREATE',case,{'space':space.code,'state':case.state})
    return case

@transaction.atomic
def transfer(*, circulation, sender, receiver, unit, purpose, next_action, delivered_at, actor, due_date="", direction="OUT", signature_status=""):
    if current_custody(circulation): raise ValidationError("این پرونده هم‌اکنون یک تحویل باز دارد.")
    try:
        event=ContractCustodyTransfer.objects.create(circulation=circulation,sender=sender,receiver=receiver,unit=unit,delivered_at=delivered_at,purpose=purpose,next_action=next_action,due_date=due_date,direction=direction,signature_status=signature_status,created_by=actor)
    except IntegrityError as exc: raise ValidationError("این پرونده هم‌اکنون یک تحویل باز دارد.") from exc
    circulation.state=ContractCirculation.State.SIGNING;circulation.next_action=next_action;circulation.due_date=due_date;circulation.save(update_fields=['state','next_action','due_date'])
    _audit(actor,'CONTRACT_CUSTODY_TRANSFER',event,{'receiver':receiver,'unit':unit})
    return event

@transaction.atomic
def return_custody(*, circulation, actor, note="", returned_at=None):
    event=current_custody(circulation)
    if not event: raise ValidationError("برای این پرونده تحویل بازی وجود ندارد.")
    event.returned_at=returned_at or timezone.now();event.return_note=note;event.save(update_fields=['returned_at','return_note'])
    circulation.state=ContractCirculation.State.RETURNED;circulation.save(update_fields=['state'])
    _audit(actor,'CONTRACT_CUSTODY_RETURN',event,{'returned_at':event.returned_at.isoformat(),'note':note})
    return event

@transaction.atomic
def final_approve(*, circulation, actor, note="", approved_at=None):
    if circulation.signature_steps.filter(required=True).exclude(status=ContractSignatureStep.Status.SIGNED).exists():
        raise ValidationError("همه مراحل امضای الزامی باید تکمیل شوند.")
    approval=ContractFinalApproval.objects.create(circulation=circulation,approver=actor,approved_at=approved_at or timezone.now(),note=note)
    circulation.state=ContractCirculation.State.APPROVED;circulation.save(update_fields=['state']);_audit(actor,'CONTRACT_FINAL_APPROVAL',approval,{'circulation':circulation.identity})
    return approval

@transaction.atomic
def convert_to_contract(*, circulation, number, start_date, end_date, amount_rial, actor):
    if circulation.official_contract_id: raise ValidationError("قرارداد رسمی این گردش قبلاً ایجاد شده است.")
    if circulation.signature_steps.filter(required=True).exclude(status=ContractSignatureStep.Status.SIGNED).exists(): raise ValidationError("امضاهای الزامی تکمیل نشده‌اند.")
    if not hasattr(circulation,'final_approval'): raise ValidationError("تأیید نهایی ثبت نشده است.")
    contract=Contract.objects.create(space=circulation.space,beneficiary=circulation.beneficiary,number=number,start_date=start_date,end_date=end_date,amount_rial=amount_rial,status='OFFICIAL',signed_state='APPROVED',is_historical=False,created_by=actor)
    circulation.official_contract=contract;circulation.state=ContractCirculation.State.CONVERTED;circulation.save(update_fields=['official_contract','state']);_audit(actor,'CONTRACT_OFFICIAL_CREATE',contract,{'source_circulation':circulation.identity})
    return contract
