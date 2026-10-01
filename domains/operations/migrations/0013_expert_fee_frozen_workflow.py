import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies=[
        ("operations","0012_file_movement_current_holder"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations=[
        migrations.RemoveField(model_name="appraisalfee",name="payment_status"),
        migrations.AddField(model_name="appraisalfee",name="status",field=models.CharField(choices=[("FEE_ENTERED","مبلغ ثبت شده"),("READY_TO_SEND","آماده ارسال"),("SENT_TO_FINANCE","ارسال شده به مالی"),("IN_PROGRESS","در دست اقدام"),("PAID","پرداخت شده"),("CLOSED","مختومه"),("NEEDS_CORRECTION","نیازمند اصلاح"),("STOPPED","متوقف"),("CANCELLED","لغو شده")],default="FEE_ENTERED",max_length=30)),
        migrations.AddField(model_name="appraisalfee",name="sent_to_finance_date",field=models.CharField(blank=True,max_length=10)),
        migrations.AddField(model_name="appraisalfee",name="letter_number",field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="appraisalfee",name="letter_date",field=models.CharField(blank=True,max_length=10)),
        migrations.AddField(model_name="appraisalfee",name="paid_amount_rial",field=models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True)),
        migrations.AddField(model_name="appraisalfee",name="created_at",field=models.DateTimeField(auto_now_add=True,null=True)),
        migrations.AddField(model_name="appraisalfee",name="updated_at",field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="appraisalfee",name="created_by",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="created_appraisal_fees",to=settings.AUTH_USER_MODEL)),
        migrations.AddConstraint(model_name="appraisalfee",constraint=models.CheckConstraint(condition=Q(amount_rial__gt=0),name="appraisal_fee_amount_positive")),
        migrations.AddConstraint(model_name="appraisalfee",constraint=models.CheckConstraint(condition=Q(paid_amount_rial__isnull=True)|Q(paid_amount_rial__gte=0),name="appraisal_fee_paid_nonnegative")),
        migrations.CreateModel(
            name="ExpertFeePaymentBatch",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("code",models.CharField(blank=True,max_length=40,null=True,unique=True)),
                ("sent_date",models.CharField(max_length=10)),("letter_number",models.CharField(max_length=120)),("letter_date",models.CharField(max_length=10)),
                ("status",models.CharField(choices=[("DRAFT","پیش‌نویس"),("SENT","ارسال شده"),("CLOSED","مختومه"),("CANCELLED","لغو شده")],default="SENT",max_length=20)),
                ("notes",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),("updated_at",models.DateTimeField(auto_now=True)),
                ("created_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="created_fee_batches",to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering":["-created_at","-id"]},
        ),
        migrations.CreateModel(
            name="ExpertFeeBatchItem",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("active",models.BooleanField(default=True)),("created_at",models.DateTimeField(auto_now_add=True)),("removed_at",models.DateTimeField(blank=True,null=True)),("removal_reason",models.TextField(blank=True)),
                ("added_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="added_fee_batch_items",to=settings.AUTH_USER_MODEL)),
                ("batch",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="items",to="operations.expertfeepaymentbatch")),
                ("fee",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="batch_items",to="operations.appraisalfee")),
            ],
            options={"ordering":["batch_id","fee_id"]},
        ),
        migrations.AddConstraint(model_name="expertfeebatchitem",constraint=models.UniqueConstraint(fields=("batch","fee"),name="uniq_fee_in_batch")),
        migrations.AddConstraint(model_name="expertfeebatchitem",constraint=models.UniqueConstraint(condition=Q(active=True),fields=("fee",),name="one_active_batch_per_fee")),
    ]
