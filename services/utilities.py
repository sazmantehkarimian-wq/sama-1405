from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from domains.identity.models import AuditEvent
from domains.operations.models import UtilityBill, UtilityConnection, UtilityMeasurement
from services.database import retry_locked
from services.dates import normalize_jalali


def _date(value, *, required=True):
    raw=(value or "").strip()
    if not raw and not required:
        return ""
    try:
        result=normalize_jalali(raw)
    except ValueError as exc:
        raise ValidationError("تاریخ شمسی معتبر نیست.") from exc
    if required and not result:
        raise ValidationError("تاریخ الزامی است.")
    return result


def _decimal(value,label,*,allow_null=False):
    if value in (None,""):
        if allow_null:return None
        raise ValidationError(f"{label} الزامی است.")
    try:result=Decimal(str(value).replace(",","").strip())
    except Exception as exc:raise ValidationError(f"{label} باید عدد معتبر باشد.") from exc
    if result<0:raise ValidationError(f"{label} نمی‌تواند منفی باشد.")
    return result


@retry_locked
@transaction.atomic
def create_utility_connection(*,space,actor,values,ip_address=None):
    utility_type=values.get("utility_type","")
    if utility_type not in UtilityConnection.Type.values:
        raise ValidationError("نوع انشعاب معتبر نیست.")
    account=(values.get("account_number") or "").strip()
    if not account:raise ValidationError("شماره اشتراک الزامی است.")
    if UtilityConnection.objects.filter(utility_type=utility_type,account_number=account).exists():
        raise ValidationError("این شماره اشتراک برای این نوع انشعاب قبلاً ثبت شده است.")
    record=UtilityConnection.objects.create(
        space=space,utility_type=utility_type,account_number=account,
        meter_number=(values.get("meter_number") or "").strip(),
        provider=(values.get("provider") or "").strip(),
        status=values.get("status") if values.get("status") in UtilityConnection.Status.values else UtilityConnection.Status.ACTIVE,
        notes=(values.get("notes") or "").strip(),created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action="UTILITY_CONNECTION_CREATE",entity_type="UtilityConnection",entity_id=str(record.pk),
        after={"space":space.code,"utility_type":record.utility_type,"account_number":record.account_number,"meter_number":record.meter_number},
        ip_address=ip_address,
    )
    return record


@retry_locked
@transaction.atomic
def create_utility_bill(*,connection,actor,values,document=None,ip_address=None):
    start=_date(values.get("period_start"));end=_date(values.get("period_end"))
    if start>end:raise ValidationError("پایان دوره نمی‌تواند قبل از شروع دوره باشد.")
    if UtilityBill.objects.filter(connection=connection,period_start=start,period_end=end).exists():
        raise ValidationError("برای این اشتراک و دوره قبلاً قبض ثبت شده است.")
    measurement=values.get("measurement")
    if measurement:
        if measurement.space_id!=connection.space_id or measurement.utility_type!=connection.utility_type:
            raise ValidationError("Measurement انتخاب‌شده با اشتراک و نوع انشعاب سازگار نیست.")
        if not measurement.is_valid:
            raise ValidationError("Measurement نامعتبر نمی‌تواند به قبض متصل شود.")
        if measurement.period_start>end or measurement.period_end<start:
            raise ValidationError("دوره Measurement با دوره قبض هم‌پوشانی ندارد.")
    payment_status=values.get("payment_status",UtilityBill.PaymentStatus.UNKNOWN)
    if payment_status not in UtilityBill.PaymentStatus.values:
        raise ValidationError("وضعیت پرداخت معتبر نیست.")
    payment_date=_date(values.get("payment_date"),required=False)
    if payment_status==UtilityBill.PaymentStatus.PAID and not payment_date:
        raise ValidationError("برای قبض پرداخت‌شده، تاریخ پرداخت الزامی است.")
    record=UtilityBill.objects.create(
        connection=connection,period_start=start,period_end=end,
        bill_date=_date(values.get("bill_date"),required=False),
        amount_rial=_decimal(values.get("amount_rial"),"مبلغ قبض"),
        consumption=_decimal(values.get("consumption"),"مصرف",allow_null=True),
        measurement=measurement,payment_status=payment_status,payment_date=payment_date,
        supporting_document=document,notes=(values.get("notes") or "").strip(),created_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor,action="UTILITY_BILL_CREATE",entity_type="UtilityBill",entity_id=str(record.pk),
        after={"code":record.sama_code,"space":connection.space.code,"utility_type":connection.utility_type,
               "period_start":start,"period_end":end,"amount_rial":str(record.amount_rial),
               "consumption":str(record.consumption) if record.consumption is not None else None,
               "measurement_id":record.measurement_id},
        ip_address=ip_address,
    )
    return record
