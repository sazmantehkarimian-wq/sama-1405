import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q

class Migration(migrations.Migration):
    dependencies=[
        ('operations','0008_zero_data_manual_entry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations=[
        migrations.CreateModel(
            name='Appraiser',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('first_name',models.CharField(max_length=120)),('last_name',models.CharField(max_length=160)),
                ('national_id',models.CharField(blank=True,db_index=True,max_length=10)),('license_number',models.CharField(blank=True,db_index=True,max_length=80)),
                ('specialty',models.CharField(blank=True,max_length=255)),('professional_authority',models.CharField(blank=True,max_length=255)),
                ('mobile',models.CharField(blank=True,max_length=20)),('phone',models.CharField(blank=True,max_length=30)),('address',models.TextField(blank=True)),('email',models.EmailField(blank=True,max_length=254)),
                ('collaboration_status',models.CharField(choices=[('ACTIVE','فعال'),('INACTIVE','غیرفعال')],default='ACTIVE',max_length=20)),
                ('notes',models.TextField(blank=True)),('archived_at',models.DateTimeField(blank=True,null=True)),
                ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
                ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='created_appraisers',to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering':['last_name','first_name','pk']},
        ),
        migrations.AddConstraint(model_name='appraiser',constraint=models.UniqueConstraint(condition=~Q(national_id=''),fields=('national_id',),name='uniq_nonblank_appraiser_national_id')),
        migrations.AddConstraint(model_name='appraiser',constraint=models.UniqueConstraint(condition=~Q(license_number=''),fields=('license_number',),name='uniq_nonblank_appraiser_license')),
        migrations.AddField(model_name='appraisal',name='appraiser_ref',field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='appraisals',to='operations.appraiser')),
        migrations.AddField(model_name='appraisal',name='response_number',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='appraisal',name='response_date',field=models.CharField(blank=True,max_length=10)),
        migrations.AddField(model_name='appraisal',name='is_current',field=models.BooleanField(default=False)),
        migrations.AddField(model_name='appraisal',name='notes',field=models.TextField(blank=True)),
        migrations.AddField(model_name='appraisal',name='updated_at',field=models.DateTimeField(auto_now=True)),
        migrations.AlterField(model_name='appraisal',name='amount_rial',field=models.DecimalField(blank=True,decimal_places=0,max_digits=24,null=True)),
        migrations.AddConstraint(model_name='appraisal',constraint=models.UniqueConstraint(condition=Q(is_current=True),fields=('space',),name='one_current_appraisal_per_space')),
        migrations.AddConstraint(model_name='appraisal',constraint=models.CheckConstraint(condition=Q(amount_rial__isnull=True)|Q(amount_rial__gte=0),name='appraisal_amount_nonnegative')),
        migrations.CreateModel(
            name='AppraisalNotification',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('number',models.CharField(blank=True,max_length=120)),('notification_date',models.CharField(max_length=10)),
                ('recipient',models.CharField(choices=[('EXPERT','کارشناس'),('REGION','منطقه'),('BOTH','کارشناس و منطقه'),('OTHER','سایر')],max_length=20)),
                ('recipient_detail',models.CharField(blank=True,max_length=255)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
                ('appraisal',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='notifications',to='operations.appraisal')),
                ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ('document',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='appraisal_notifications',to='documents.document')),
            ],
            options={'ordering':['-notification_date','-id']},
        ),
    ]
