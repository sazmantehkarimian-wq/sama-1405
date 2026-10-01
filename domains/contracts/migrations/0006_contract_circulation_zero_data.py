import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies=[
        ("contracts","0005_structured_beneficiary_contract"),
        ("properties","0005_restore_mother_property_immutable_trigger"),
        ("documents","0002_document_metadata"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations=[
        migrations.CreateModel(
            name="ContractCirculation",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("identity",models.CharField(blank=True,editable=False,max_length=30,unique=True)),
                ("subject",models.CharField(max_length=255)),
                ("operational_start_date",models.CharField(default="1405/07/01",max_length=10)),
                ("state",models.CharField(choices=[("RECEIVED","دریافت‌شده"),("READY","آماده ارسال"),("SIGNING","در گردش امضا"),("RETURNED","برگشت برای اصلاح"),("RESEND","ارسال مجدد"),("READY_APPROVAL","آماده تأیید نهایی"),("APPROVED","تأیید نهایی‌شده"),("CONVERTED","تبدیل‌شده به قرارداد رسمی"),("CLOSED_NO_CONTRACT","مختومه بدون قرارداد")],default="RECEIVED",max_length=30)),
                ("next_action",models.CharField(max_length=255)),("due_date",models.CharField(blank=True,max_length=10)),
                ("close_reason",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),("updated_at",models.DateTimeField(auto_now=True)),
                ("beneficiary",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="contract_circulations",to="contracts.beneficiary")),
                ("created_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="created_contract_circulations",to=settings.AUTH_USER_MODEL)),
                ("official_contract",models.OneToOneField(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="source_circulation",to="contracts.contract")),
                ("space",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="contract_circulations",to="properties.commercialspace")),
            ],
            options={"ordering":["-created_at","-pk"],"indexes":[models.Index(fields=["state","due_date"],name="contracts_c_state_3eeafe_idx")]},
        ),
        migrations.CreateModel(
            name="ContractCustodyTransfer",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("sender",models.CharField(max_length=255)),("receiver",models.CharField(max_length=255)),("unit",models.CharField(max_length=255)),
                ("delivered_at",models.DateTimeField()),("purpose",models.CharField(max_length=255)),("next_action",models.CharField(max_length=255)),
                ("due_date",models.CharField(blank=True,max_length=10)),("direction",models.CharField(choices=[("OUT","خروج"),("IN","ورود")],default="OUT",max_length=20)),
                ("signature_status",models.CharField(blank=True,max_length=80)),("returned_at",models.DateTimeField(blank=True,null=True)),("return_note",models.TextField(blank=True)),
                ("created_at",models.DateTimeField(auto_now_add=True)),
                ("circulation",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="transfers",to="contracts.contractcirculation")),
                ("created_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("document",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="contract_custody_transfers",to="documents.document")),
            ],
            options={"ordering":["-delivered_at","-pk"],"constraints":[models.UniqueConstraint(condition=models.Q(returned_at__isnull=True),fields=("circulation",),name="one_open_contract_custody")]},
        ),
        migrations.CreateModel(
            name="ContractSignatureStep",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("order",models.PositiveSmallIntegerField()),("role",models.CharField(max_length=120)),("person",models.CharField(blank=True,max_length=255)),
                ("unit",models.CharField(max_length=255)),("required",models.BooleanField(default=True)),
                ("sent_at",models.DateTimeField(blank=True,null=True)),("signed_at",models.DateTimeField(blank=True,null=True)),("returned_at",models.DateTimeField(blank=True,null=True)),
                ("status",models.CharField(choices=[("PENDING","در انتظار ارسال"),("SENT","ارسال‌شده برای امضا"),("SIGNED","امضاشده"),("RETURNED","برگشت برای اصلاح"),("WAIVED","صرف‌نظر از مرحله اختیاری")],default="PENDING",max_length=20)),
                ("note",models.TextField(blank=True)),("updated_at",models.DateTimeField(auto_now=True)),
                ("circulation",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="signature_steps",to="contracts.contractcirculation")),
                ("document",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="contract_signature_steps",to="documents.document")),
                ("updated_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering":["order","pk"],"constraints":[models.UniqueConstraint(fields=("circulation","order"),name="unique_signature_order")]},
        ),
        migrations.CreateModel(
            name="ContractFinalApproval",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("approved_at",models.DateTimeField()),("note",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),
                ("approver",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("circulation",models.OneToOneField(on_delete=django.db.models.deletion.PROTECT,related_name="final_approval",to="contracts.contractcirculation")),
            ],
            options={"ordering":["-approved_at","-pk"]},
        ),
    ]
