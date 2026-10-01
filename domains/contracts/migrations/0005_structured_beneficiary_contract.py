from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0004_zero_data_manual_entry"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(model_name="beneficiary", name="identity_number", field=models.CharField(blank=True, db_index=True, max_length=11)),
        migrations.AlterField(model_name="beneficiary", name="kind", field=models.CharField(choices=[("NATURAL","شخص حقیقی"),("LEGAL","شخص حقوقی")], max_length=20)),
        migrations.AddField(model_name="beneficiary", name="first_name", field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="beneficiary", name="last_name", field=models.CharField(blank=True,max_length=160)),
        migrations.AddField(model_name="beneficiary", name="father_name", field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="beneficiary", name="birth_certificate_number", field=models.CharField(blank=True,max_length=30)),
        migrations.AddField(model_name="beneficiary", name="birth_date", field=models.CharField(blank=True,max_length=10)),
        migrations.AddField(model_name="beneficiary", name="legal_name", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="beneficiary", name="registration_number", field=models.CharField(blank=True,max_length=60)),
        migrations.AddField(model_name="beneficiary", name="legal_entity_type", field=models.CharField(blank=True,max_length=80)),
        migrations.AddField(model_name="beneficiary", name="economic_code", field=models.CharField(blank=True,max_length=30)),
        migrations.AddField(model_name="beneficiary", name="representative_name", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="beneficiary", name="mobile", field=models.CharField(blank=True,max_length=20)),
        migrations.AddField(model_name="beneficiary", name="phone", field=models.CharField(blank=True,max_length=30)),
        migrations.AddField(model_name="beneficiary", name="address", field=models.TextField(blank=True)),
        migrations.AddField(model_name="beneficiary", name="postal_code", field=models.CharField(blank=True,max_length=20)),
        migrations.AddField(model_name="beneficiary", name="created_at", field=models.DateTimeField(auto_now_add=True, null=True)),
        migrations.AddField(model_name="beneficiary", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="beneficiary", name="created_by", field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="created_beneficiaries",to=settings.AUTH_USER_MODEL)),
        migrations.AddConstraint(model_name="beneficiary", constraint=models.UniqueConstraint(condition=~Q(identity_number=""), fields=("identity_number",), name="uniq_nonblank_beneficiary_identity")),
        migrations.AlterField(model_name="beneficiaryassignment", name="status", field=models.CharField(choices=[("ACTIVE","جاری"),("ENDED","خاتمه‌یافته")],default="ACTIVE",max_length=20)),
        migrations.AddField(model_name="beneficiaryassignment", name="basis", field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="beneficiaryassignment", name="termination_reason", field=models.TextField(blank=True)),
        migrations.AlterField(model_name="contract", name="beneficiary", field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="contracts",to="contracts.beneficiary")),
        migrations.AlterField(model_name="contract", name="number", field=models.CharField(db_index=True,max_length=120)),
        migrations.AlterField(model_name="contract", name="start_date", field=models.CharField(max_length=10)),
        migrations.AlterField(model_name="contract", name="end_date", field=models.CharField(max_length=10)),
        migrations.AlterField(model_name="contract", name="amount_rial", field=models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True,validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
        migrations.AlterField(model_name="contract", name="investment_commitment_rial", field=models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True,validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
        migrations.AddField(model_name="contract", name="subject", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="contract", name="notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="contract", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddConstraint(model_name="contract", constraint=models.UniqueConstraint(fields=("space","number"),name="uniq_contract_number_per_space")),
        migrations.AddConstraint(model_name="contract", constraint=models.CheckConstraint(condition=Q(amount_rial__isnull=True)|Q(amount_rial__gte=0),name="contract_amount_nonnegative")),
        migrations.AddConstraint(model_name="contract", constraint=models.CheckConstraint(condition=Q(investment_commitment_rial__isnull=True)|Q(investment_commitment_rial__gte=0),name="contract_investment_nonnegative")),
        migrations.AlterField(model_name="contractamendment", name="amount_change_rial", field=models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True)),
        migrations.AddConstraint(model_name="contractamendment", constraint=models.UniqueConstraint(fields=("contract","number"),name="uniq_amendment_number_per_contract")),
    ]
