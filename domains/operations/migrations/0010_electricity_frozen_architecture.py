import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies=[
        ('operations','0009_structured_appraisals'),
        ('properties','0003_immutable_business_keys'),
        ('documents','0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations=[
        migrations.CreateModel(name='UtilityUnit',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=255)),('kind',models.CharField(choices=[('REGION','منطقه'),('CENTER','مرکز خاص'),('OTHER','سایر')],max_length=20)),
            ('active',models.BooleanField(default=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('center',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='utility_units',to='properties.center')),
            ('region',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='utility_units',to='properties.region')),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='created_utility_units',to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['name','pk']}),
        migrations.AddConstraint(model_name='utilityunit',constraint=models.UniqueConstraint(fields=('name','kind'),name='uniq_utility_unit_name_kind')),
        migrations.AddConstraint(model_name='utilityunit',constraint=models.CheckConstraint(condition=Q(kind='REGION',region__isnull=False,center__isnull=True)|Q(kind='CENTER',center__isnull=False)|Q(kind='OTHER'),name='utility_unit_kind_link_valid')),
        migrations.CreateModel(name='UtilityMeasurement',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('utility_type',models.CharField(choices=[('ELECTRICITY','برق'),('WATER','آب'),('GAS','گاز'),('OTHER','سایر')],max_length=20)),
            ('period_start',models.CharField(max_length=10)),('period_end',models.CharField(max_length=10)),('consumption',models.DecimalField(decimal_places=3,max_digits=20)),
            ('reading_date',models.CharField(max_length=10)),('meter_number',models.CharField(blank=True,max_length=120)),('measurement_unit',models.CharField(default='kWh',max_length=40)),
            ('source',models.CharField(blank=True,max_length=120)),('is_submeter',models.BooleanField(default=False)),('is_valid',models.BooleanField(default=True)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('space',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='utility_measurements',to='properties.commercialspace')),
        ],options={'ordering':['-reading_date','-id']}),
        migrations.AddConstraint(model_name='utilitymeasurement',constraint=models.CheckConstraint(condition=Q(consumption__gte=0),name='utility_measurement_nonnegative')),
        migrations.CreateModel(name='UtilityParameterRule',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('key',models.CharField(db_index=True,max_length=120)),('label',models.CharField(max_length=255)),
            ('value_decimal',models.DecimalField(blank=True,decimal_places=6,max_digits=20,null=True)),('value_text',models.CharField(blank=True,max_length=255)),('unit',models.CharField(blank=True,max_length=40)),
            ('effective_from',models.CharField(max_length=10)),('effective_to',models.CharField(blank=True,max_length=10)),('active',models.BooleanField(default=True)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['key','-effective_from','-id']}),
        migrations.AddConstraint(model_name='utilityparameterrule',constraint=models.UniqueConstraint(fields=('key','effective_from'),name='uniq_utility_rule_key_effective')),
        migrations.CreateModel(name='ElectricityConsumptionCategory',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=255,unique=True)),
            ('eui',models.DecimalField(blank=True,decimal_places=6,max_digits=16,null=True)),('effective_from',models.CharField(blank=True,max_length=10)),('active',models.BooleanField(default=True)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['name']}),
        migrations.CreateModel(name='ElectricityBill',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('period_start',models.CharField(max_length=10)),('period_end',models.CharField(max_length=10)),('bill_date',models.CharField(blank=True,max_length=10)),
            ('amount_rial',models.DecimalField(decimal_places=0,max_digits=24)),('beneficiary_share_percent',models.DecimalField(decimal_places=4,max_digits=7)),('organization_share_percent',models.DecimalField(decimal_places=4,max_digits=7)),
            ('status',models.CharField(choices=[('DRAFT','پیش‌نویس'),('CALCULATED','محاسبه‌شده'),('REVIEW_REQUIRED','نیازمند بررسی'),('FINAL','نهایی'),('REOPENED','بازگشایی‌شده')],default='DRAFT',max_length=30)),
            ('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('finalized_at',models.DateTimeField(blank=True,null=True)),('reopen_reason',models.TextField(blank=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('finalized_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='finalized_electricity_bills',to=settings.AUTH_USER_MODEL)),
            ('supporting_document',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='electricity_bills',to='documents.document')),
            ('unit',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='electricity_bills',to='operations.utilityunit')),
        ],options={'ordering':['-period_end','-id']}),
        migrations.AddConstraint(model_name='electricitybill',constraint=models.UniqueConstraint(fields=('unit','period_start','period_end'),name='uniq_electricity_bill_unit_period')),
        migrations.AddConstraint(model_name='electricitybill',constraint=models.CheckConstraint(condition=Q(amount_rial__gte=0),name='electricity_bill_amount_nonnegative')),
        migrations.AddConstraint(model_name='electricitybill',constraint=models.CheckConstraint(condition=Q(beneficiary_share_percent__gte=0)&Q(beneficiary_share_percent__lte=100),name='electricity_beneficiary_share_range')),
        migrations.AddConstraint(model_name='electricitybill',constraint=models.CheckConstraint(condition=Q(organization_share_percent__gte=0)&Q(organization_share_percent__lte=100),name='electricity_org_share_range')),
        migrations.CreateModel(name='ElectricityAllocation',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('eligible',models.BooleanField(default=True)),
            ('effective_area',models.DecimalField(blank=True,decimal_places=2,max_digits=16,null=True)),('eui',models.DecimalField(blank=True,decimal_places=6,max_digits=16,null=True)),('operational_factor',models.DecimalField(blank=True,decimal_places=6,max_digits=12,null=True)),('special_consumption',models.DecimalField(blank=True,decimal_places=3,max_digits=20,null=True)),
            ('calculated_share_percent',models.DecimalField(blank=True,decimal_places=4,max_digits=7,null=True)),('manual_override_percent',models.DecimalField(blank=True,decimal_places=4,max_digits=7,null=True)),('final_share_percent',models.DecimalField(decimal_places=4,max_digits=7)),
            ('calculation_source',models.CharField(choices=[('SUBMETER','زیرکنتور'),('MEASUREMENT','اندازه‌گیری واقعی'),('EQUIPMENT','داده تجهیزات'),('APPROVED_MODEL','مدل مصوب'),('MANUAL_OVERRIDE','Override دستی')],max_length=30)),
            ('confidence_level',models.CharField(choices=[('REAL_MEASUREMENT','اندازه‌گیری واقعی'),('VALID_EQUIPMENT','داده تجهیزات معتبر'),('APPROVED_MODEL','محاسبه مدل مصوب'),('INCOMPLETE','نیازمند تکمیل'),('REVIEW','نیازمند بررسی')],max_length=30)),
            ('override_reason',models.TextField(blank=True)),('notes',models.TextField(blank=True)),('payable_amount_rial',models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('bill',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='allocations',to='operations.electricitybill')),
            ('category',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='allocations',to='operations.electricityconsumptioncategory')),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('measurement',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='electricity_allocations',to='operations.utilitymeasurement')),
            ('space',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='electricity_allocations',to='properties.commercialspace')),
        ],options={'ordering':['space__code','pk']}),
        migrations.AddConstraint(model_name='electricityallocation',constraint=models.UniqueConstraint(fields=('bill','space'),name='uniq_electricity_allocation_bill_space')),
        migrations.AddConstraint(model_name='electricityallocation',constraint=models.CheckConstraint(condition=Q(final_share_percent__gte=0)&Q(final_share_percent__lte=100),name='electricity_final_share_range')),
        migrations.AddConstraint(model_name='electricityallocation',constraint=models.CheckConstraint(condition=Q(calculated_share_percent__isnull=True)|(Q(calculated_share_percent__gte=0)&Q(calculated_share_percent__lte=100)),name='electricity_calc_share_range')),
        migrations.AddConstraint(model_name='electricityallocation',constraint=models.CheckConstraint(condition=Q(manual_override_percent__isnull=True)|(Q(manual_override_percent__gte=0)&Q(manual_override_percent__lte=100)),name='electricity_override_share_range')),
        migrations.CreateModel(name='ElectricityCalculationSnapshot',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('version',models.PositiveIntegerField()),('payload',models.JSONField()),('reason',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('bill',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='snapshots',to='operations.electricitybill')),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-version','-id']}),
        migrations.AddConstraint(model_name='electricitycalculationsnapshot',constraint=models.UniqueConstraint(fields=('bill','version'),name='uniq_electricity_snapshot_version')),
    ]
