from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auctionflow', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuctionOrganizationProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(default='سازمان فرهنگی هنری شهرداری تهران', max_length=255)),
                ('unit_title', models.CharField(default='مدیریت اقتصادی و املاک — اداره املاک و مستغلات', max_length=255)),
                ('official_address', models.TextField(blank=True)),
                ('secretariat_address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=80)),
                ('bank_name', models.CharField(blank=True, max_length=120)),
                ('bank_branch', models.CharField(blank=True, max_length=120)),
                ('account_number', models.CharField(blank=True, max_length=80)),
                ('iban', models.CharField(blank=True, max_length=80)),
                ('office_hours', models.CharField(blank=True, max_length=255)),
                ('submission_location', models.TextField(blank=True)),
                ('representative_name', models.CharField(blank=True, max_length=255)),
                ('representative_title', models.CharField(blank=True, max_length=255)),
                ('economic_code', models.CharField(blank=True, max_length=80)),
                ('national_id', models.CharField(blank=True, max_length=80)),
                ('postal_code', models.CharField(blank=True, max_length=30)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'مشخصات سازمان برای اسناد مزایده', 'verbose_name_plural': 'مشخصات سازمان برای اسناد مزایده'},
        ),
        migrations.CreateModel(
            name='AuctionTemplateSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.CharField(choices=[('GENERAL','عمومی'),('COMMERCIAL','تجاری'),('CAFE','کافه'),('SPORT','ورزشی')], max_length=20)),
                ('kind', models.CharField(choices=[('CONDITIONS','شرایط عمومی و اختصاصی'),('ENVELOPE_COVER','روکش پاکات'),('OPENING_MINUTES','صورتجلسه بازگشایی پاکات'),('EXPERT_NOTICE','ابلاغ کارشناس رسمی'),('SAMPLE_CONTRACT','نمونه قرارداد')], max_length=30)),
                ('version', models.CharField(max_length=80)),
                ('source_filename', models.CharField(max_length=255)),
                ('source_sha256', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('print_qa_approved', models.BooleanField(default=False)),
                ('owner_approved', models.BooleanField(default=False)),
                ('imported_at', models.DateTimeField(auto_now_add=True)),
                ('imported_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('source_document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='auction_template_sources', to='documents.document')),
            ],
            options={'ordering': ['family','kind','-imported_at']},
        ),
        migrations.AddConstraint(
            model_name='auctiontemplatesource',
            constraint=models.UniqueConstraint(fields=('family','kind','version'), name='auction_template_family_kind_version_unique'),
        ),
        migrations.AddField(model_name='auctionperiodprofile', name='permit_date', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='auctionperiodprofile', name='newspaper_page', field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name='auctionperiodprofile', name='publication_media', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='auctionperiodprofile', name='document_sales_start', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='auctionperiodprofile', name='document_sales_end', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='auctionperiodprofile', name='proposal_deadline', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='auctionperiodprofile', name='submission_day_name', field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name='auctionperiodprofile', name='invitation_date', field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name='auctionperiodprofile', name='opening_day_name', field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name='auctionlotprofile', name='base_monthly_rent_words', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='auctionlotprofile', name='guarantee_type', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='auctionlotprofile', name='grace_period', field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name='auctionlotprofile', name='investment_description', field=models.TextField(blank=True)),
        migrations.AddField(model_name='auctionlotprofile', name='transaction_level', field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name='auctionlotprofile', name='location_description', field=models.TextField(blank=True)),
        migrations.AddField(model_name='auctionlotprofile', name='coordination_phone', field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name='auctionlotprofile', name='coordination_person', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='auctiondocumentinstance', name='template_source', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='document_instances', to='auctionflow.auctiontemplatesource')),
        migrations.AddField(model_name='auctiondocumentinstance', name='output_sha256', field=models.CharField(blank=True, max_length=64)),
    ]
