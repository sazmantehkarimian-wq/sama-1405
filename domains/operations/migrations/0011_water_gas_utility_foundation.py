import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies=[
        ('operations','0010_electricity_frozen_architecture'),
        ('properties','0003_immutable_business_keys'),
        ('documents','0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations=[
        migrations.CreateModel(name='UtilityConnection',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('utility_type',models.CharField(choices=[('WATER','آب'),('GAS','گاز'),('OTHER','سایر')],max_length=20)),
            ('account_number',models.CharField(max_length=120)),('meter_number',models.CharField(blank=True,max_length=120)),
            ('provider',models.CharField(blank=True,max_length=255)),('status',models.CharField(choices=[('ACTIVE','فعال'),('INACTIVE','غیرفعال')],default='ACTIVE',max_length=20)),
            ('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('space',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='utility_connections',to='properties.commercialspace')),
        ],options={'ordering':['utility_type','account_number','pk']}),
        migrations.AddConstraint(model_name='utilityconnection',constraint=models.UniqueConstraint(fields=('utility_type','account_number'),name='uniq_utility_connection_type_account')),
        migrations.CreateModel(name='UtilityBill',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('period_start',models.CharField(max_length=10)),('period_end',models.CharField(max_length=10)),('bill_date',models.CharField(blank=True,max_length=10)),
            ('amount_rial',models.DecimalField(decimal_places=0,max_digits=24)),('consumption',models.DecimalField(blank=True,decimal_places=3,max_digits=20,null=True)),
            ('payment_status',models.CharField(choices=[('UNPAID','پرداخت‌نشده'),('PAID','پرداخت‌شده'),('UNKNOWN','نامشخص')],default='UNKNOWN',max_length=20)),
            ('payment_date',models.CharField(blank=True,max_length=10)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('connection',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='bills',to='operations.utilityconnection')),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('measurement',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='utility_bills',to='operations.utilitymeasurement')),
            ('supporting_document',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='generic_utility_bills',to='documents.document')),
        ],options={'ordering':['-period_end','-id']}),
        migrations.AddConstraint(model_name='utilitybill',constraint=models.UniqueConstraint(fields=('connection','period_start','period_end'),name='uniq_utility_bill_connection_period')),
        migrations.AddConstraint(model_name='utilitybill',constraint=models.CheckConstraint(condition=Q(amount_rial__gte=0),name='utility_bill_amount_nonnegative')),
        migrations.AddConstraint(model_name='utilitybill',constraint=models.CheckConstraint(condition=Q(consumption__isnull=True)|Q(consumption__gte=0),name='utility_bill_consumption_nonnegative')),
    ]
