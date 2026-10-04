from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0017_alert_workflow_constraints'),
        ('contracts', '0009_contract_circulation'),
        ('documents', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='AuctionPeriodProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permit_reference', models.CharField(blank=True, max_length=255)),
                ('ad_day_name', models.CharField(blank=True, max_length=40)),
                ('ad_date', models.CharField(blank=True, max_length=10)),
                ('newspaper', models.CharField(blank=True, default='همشهری', max_length=120)),
                ('invitation_number', models.CharField(blank=True, max_length=120)),
                ('opening_session_date', models.CharField(blank=True, max_length=10)),
                ('opening_session_time', models.CharField(blank=True, max_length=5)),
                ('opening_session_location', models.CharField(blank=True, max_length=255)),
                ('duration_years', models.PositiveSmallIntegerField(default=1)),
                ('template_version', models.CharField(default='reference-1405-07-12-v1', max_length=80)),
                ('notes', models.TextField(blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('period', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='flow_profile', to='operations.auctionperiod')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuctionLotProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_family', models.CharField(choices=[('COMMERCIAL', 'تجاری'), ('CAFE', 'کافه'), ('SPORT', 'ورزشی')], default='COMMERCIAL', max_length=20)),
                ('base_monthly_rent_rial', models.DecimalField(blank=True, decimal_places=0, max_digits=24, null=True)),
                ('guarantee_amount_rial', models.DecimalField(blank=True, decimal_places=0, max_digits=24, null=True)),
                ('investment_amount_rial', models.DecimalField(blank=True, decimal_places=0, max_digits=24, null=True)),
                ('proposed_job', models.CharField(blank=True, max_length=255)),
                ('decision_reference', models.CharField(blank=True, max_length=255)),
                ('decision_date', models.CharField(blank=True, max_length=10)),
                ('result_state', models.CharField(choices=[('OPEN', 'در جریان'), ('AWARDED', 'برنده تعیین شده'), ('CONTRACTING', 'در فرایند قرارداد'), ('CONTRACTED', 'قرارداد نهایی شده'), ('NO_WINNER', 'بدون برنده'), ('CANCELLED', 'لغو شده')], default='OPEN', max_length=30)),
                ('snapshot', models.JSONField(blank=True, default=dict)),
                ('awarded_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('awarded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auction_awards_made', to=settings.AUTH_USER_MODEL)),
                ('beneficiary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auction_awards', to='contracts.beneficiary')),
                ('contract_circulation', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auction_award', to='contracts.contractcirculation')),
                ('lot', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='flow_profile', to='operations.auctionlot')),
                ('official_contract', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auction_award', to='contracts.contract')),
                ('runner_up_proposal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='runner_up_lot_profiles', to='operations.auctionproposal')),
                ('winner_proposal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='won_lot_profiles', to='operations.auctionproposal')),
            ],
            options={
                'constraints': [
                    models.CheckConstraint(condition=models.Q(('base_monthly_rent_rial__isnull', True), ('base_monthly_rent_rial__gte', 0), _connector='OR'), name='auctionflow_base_rent_nonnegative'),
                    models.CheckConstraint(condition=models.Q(('guarantee_amount_rial__isnull', True), ('guarantee_amount_rial__gte', 0), _connector='OR'), name='auctionflow_guarantee_nonnegative'),
                    models.CheckConstraint(condition=models.Q(('investment_amount_rial__isnull', True), ('investment_amount_rial__gte', 0), _connector='OR'), name='auctionflow_investment_nonnegative'),
                ],
            },
        ),
        migrations.CreateModel(
            name='AuctionDocumentInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('CONDITIONS', 'شرایط عمومی و اختصاصی'), ('PRICE_FORM', 'فرم پیشنهاد قیمت / روکش پاکات'), ('OPENING_MINUTES', 'صورتجلسه بازگشایی پاکات'), ('EXPERT_NOTICE', 'ابلاغ کارشناس رسمی'), ('SAMPLE_CONTRACT', 'نمونه قرارداد'), ('ENVELOPE_A', 'پاکت الف'), ('ENVELOPE_B', 'پاکت ب'), ('ENVELOPE_C', 'پاکت ج')], max_length=30)),
                ('template_family', models.CharField(blank=True, choices=[('COMMERCIAL', 'تجاری'), ('CAFE', 'کافه'), ('SPORT', 'ورزشی')], max_length=20)),
                ('template_version', models.CharField(max_length=80)),
                ('source_sha256', models.CharField(max_length=64)),
                ('snapshot', models.JSONField()),
                ('snapshot_sha256', models.CharField(max_length=64)),
                ('status', models.CharField(choices=[('UAT_DRAFT', 'پیش‌نویس کنترل‌شده UAT'), ('APPROVED', 'تأییدشده'), ('INVALIDATED', 'باطل‌شده')], default='UAT_DRAFT', max_length=20)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('invalidated_at', models.DateTimeField(blank=True, null=True)),
                ('invalidation_reason', models.TextField(blank=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='auction_generated_instances', to='documents.document')),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('lot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='generated_documents', to='operations.auctionlot')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='generated_documents', to='operations.auctionperiod')),
            ],
            options={'ordering': ['-generated_at', '-pk']},
        ),
        migrations.AddIndex(
            model_name='auctiondocumentinstance',
            index=models.Index(fields=['period', 'lot', 'document_type', 'status'], name='auctionflow_period_doc_idx'),
        ),
    ]
