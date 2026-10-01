import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[
        ('contracts','0005_structured_beneficiary_contract'),
        ('operations','0013_expert_fee_frozen_workflow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations=[
        migrations.CreateModel(name='CommissionMember',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=255)),('position',models.CharField(blank=True,max_length=255)),('role',models.CharField(blank=True,max_length=120)),
            ('sign_order',models.PositiveSmallIntegerField(default=1)),('start_date',models.CharField(blank=True,max_length=10)),('end_date',models.CharField(blank=True,max_length=10)),
            ('status',models.CharField(choices=[('ACTIVE','فعال'),('INACTIVE','غیرفعال')],default='ACTIVE',max_length=20)),('notes',models.TextField(blank=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('created_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='created_commission_members',to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['sign_order','name','pk']}),
        migrations.CreateModel(name='CommissionSession',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('number',models.CharField(blank=True,max_length=120)),('session_date',models.CharField(max_length=10)),('session_time',models.CharField(blank=True,max_length=5)),
            ('location',models.CharField(blank=True,max_length=255)),('title',models.CharField(max_length=255)),('description',models.TextField(blank=True)),
            ('status',models.CharField(choices=[('DRAFT','پیش‌نویس'),('HELD','برگزارشده'),('CLOSED','مختومه'),('CANCELLED','لغوشده')],default='DRAFT',max_length=20)),
            ('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='created_commission_sessions',to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-session_date','-id']}),
        migrations.CreateModel(name='CommissionCase',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=255)),('description',models.TextField(blank=True)),('reason',models.TextField(blank=True)),('case_type',models.CharField(blank=True,max_length=120)),
            ('referral_reference',models.CharField(blank=True,max_length=255)),('status',models.CharField(choices=[('OPEN','باز'),('UNDER_REVIEW','در حال بررسی'),('DECIDED','تصمیم‌گیری‌شده'),('CLOSED','مختومه'),('CANCELLED','باطل')],default='OPEN',max_length=30)),
            ('follow_up_due_date',models.CharField(blank=True,max_length=10)),('notes',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='created_commission_cases',to=settings.AUTH_USER_MODEL)),
            ('responsible',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='commission_cases',to=settings.AUTH_USER_MODEL)),
            ('session',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='cases',to='operations.commissionsession')),
            ('spaces',models.ManyToManyField(blank=True,related_name='commission_cases',to='properties.commercialspace')),
            ('contracts',models.ManyToManyField(blank=True,related_name='commission_cases',to='contracts.contract')),
            ('beneficiaries',models.ManyToManyField(blank=True,related_name='commission_cases',to='contracts.beneficiary')),
            ('auction_periods',models.ManyToManyField(blank=True,related_name='commission_cases',to='operations.auctionperiod')),
        ],options={'ordering':['session','id']}),
        migrations.CreateModel(name='CommissionSessionMember',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=255)),('position',models.CharField(blank=True,max_length=255)),('role',models.CharField(blank=True,max_length=120)),
            ('present',models.BooleanField(default=True)),('sign_order',models.PositiveSmallIntegerField(default=1)),('notes',models.TextField(blank=True)),
            ('member',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='session_snapshots',to='operations.commissionmember')),
            ('session',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='member_snapshots',to='operations.commissionsession')),
        ],options={'ordering':['sign_order','pk']}),
        migrations.AddConstraint(model_name='commissionsessionmember',constraint=models.UniqueConstraint(fields=('session','name','position'),name='uniq_commission_session_member_snapshot')),
        migrations.AddField(model_name='commissiondecision',name='case',field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='decisions',to='operations.commissioncase')),
        migrations.AddField(model_name='commissiondecision',name='decision_type',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='commissiondecision',name='result',field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name='commissiondecision',name='responsible',field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='commission_decisions',to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='commissiondecision',name='due_date',field=models.CharField(blank=True,max_length=10)),
        migrations.AddField(model_name='commissiondecision',name='execution_status',field=models.CharField(choices=[('ACTION_REQUIRED','نیازمند اقدام'),('IN_PROGRESS','در دست اقدام'),('DONE','انجام‌شده'),('CLOSED','مختومه'),('REVIEW_REQUIRED','نیازمند بررسی')],default='ACTION_REQUIRED',max_length=30)),
        migrations.AddField(model_name='commissiondecision',name='created_by',field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='created_commission_decisions',to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='commissiondecision',name='created_at',field=models.DateTimeField(auto_now_add=True,null=True)),
        migrations.AddField(model_name='commissiondecision',name='updated_at',field=models.DateTimeField(auto_now=True)),
        migrations.CreateModel(name='CommissionFollowUp',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('required_action',models.TextField()),('responsible_unit',models.CharField(blank=True,max_length=255)),('referred_date',models.CharField(blank=True,max_length=10)),('due_date',models.CharField(blank=True,max_length=10)),
            ('status',models.CharField(choices=[('ACTION_REQUIRED','نیازمند اقدام'),('IN_PROGRESS','در دست اقدام'),('DONE','انجام‌شده'),('CLOSED','مختومه'),('REVIEW_REQUIRED','نیازمند بررسی')],default='ACTION_REQUIRED',max_length=30)),
            ('completed_date',models.CharField(blank=True,max_length=10)),('result',models.TextField(blank=True)),('notes',models.TextField(blank=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='created_commission_followups',to=settings.AUTH_USER_MODEL)),
            ('decision',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='followups',to='operations.commissiondecision')),
            ('responsible',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='commission_followups',to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-created_at','-id']}),
        migrations.CreateModel(name='CommissionFollowUpHistory',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('previous_status',models.CharField(blank=True,max_length=30)),('new_status',models.CharField(choices=[('ACTION_REQUIRED','نیازمند اقدام'),('IN_PROGRESS','در دست اقدام'),('DONE','انجام‌شده'),('CLOSED','مختومه'),('REVIEW_REQUIRED','نیازمند بررسی')],max_length=30)),
            ('note',models.TextField(blank=True)),('changed_at',models.DateTimeField(auto_now_add=True)),
            ('changed_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
            ('followup',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='history',to='operations.commissionfollowup')),
        ],options={'ordering':['-changed_at','-id']}),
    ]
