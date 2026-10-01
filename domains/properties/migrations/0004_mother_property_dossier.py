import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0003_immutable_business_keys"),
        ("documents", "0002_document_metadata"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PropertyReferenceValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(choices=[
                    ("STATUS","وضعیت جاری ملک"),("CENTER_TYPE","نوع مرکز / مکان"),("USAGE","نوع کاربری"),
                    ("USAGE_GROUP","گروه کاربری"),("ORG_UNIT","واحد / مرکز سازمانی"),
                    ("USAGE_STATUS","وضعیت بهره‌برداری"),("OWNERSHIP_STATUS","وضعیت مستند مالکیت"),
                ], max_length=40)),
                ("value", models.CharField(max_length=120)),
                ("active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering":["category","sort_order","value"]},
        ),
        migrations.AddConstraint(model_name="propertyreferencevalue", constraint=models.UniqueConstraint(fields=("category","value"), name="uniq_property_reference_category_value")),
        migrations.AddField(model_name="motherproperty", name="current_status", field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="motherproperty", name="holder_unit", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="motherproperty", name="land_area", field=models.DecimalField(blank=True,decimal_places=2,max_digits=16,null=True)),
        migrations.AddField(model_name="motherproperty", name="ownership_document_status", field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name="motherproperty", name="owner_name", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="motherproperty", name="owner_type", field=models.CharField(blank=True,choices=[("NATURAL","حقیقی"),("LEGAL","حقوقی"),("ORGANIZATIONAL","سازمانی"),("UNKNOWN","نامشخص")],max_length=20)),
        migrations.AddField(model_name="motherproperty", name="ownership_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="motherproperty", name="has_utilities", field=models.CharField(choices=[("YES","دارد"),("NO","ندارد"),("UNKNOWN","نامشخص")],default="UNKNOWN",max_length=10)),
        migrations.AddField(model_name="motherproperty", name="electricity_presence", field=models.CharField(choices=[("YES","دارد"),("NO","ندارد"),("UNKNOWN","نامشخص")],default="UNKNOWN",max_length=10)),
        migrations.AddField(model_name="motherproperty", name="water_presence", field=models.CharField(choices=[("YES","دارد"),("NO","ندارد"),("UNKNOWN","نامشخص")],default="UNKNOWN",max_length=10)),
        migrations.AddField(model_name="motherproperty", name="gas_presence", field=models.CharField(choices=[("YES","دارد"),("NO","ندارد"),("UNKNOWN","نامشخص")],default="UNKNOWN",max_length=10)),
        migrations.AddField(model_name="motherproperty", name="other_utilities", field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name="motherproperty", name="utility_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="motherproperty", name="created_by", field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="created_mother_properties",to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="motherproperty", name="updated_by", field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="updated_mother_properties",to=settings.AUTH_USER_MODEL)),
        migrations.AddConstraint(model_name="motherproperty", constraint=models.CheckConstraint(condition=Q(land_area__isnull=True)|Q(land_area__gte=0), name="mother_property_land_area_nonnegative")),
        migrations.CreateModel(
            name="MotherPropertyOwnership",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("owner_name",models.CharField(max_length=255)),
                ("owner_type",models.CharField(choices=[("NATURAL","حقیقی"),("LEGAL","حقوقی"),("ORGANIZATIONAL","سازمانی"),("UNKNOWN","نامشخص")],max_length=20)),
                ("share_percent",models.DecimalField(blank=True,decimal_places=4,max_digits=7,null=True)),
                ("start_date",models.CharField(blank=True,max_length=10)),("end_date",models.CharField(blank=True,max_length=10)),
                ("basis",models.CharField(blank=True,max_length=255)),("notes",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),
                ("created_by",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("property",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="ownership_history",to="properties.motherproperty")),
            ], options={"ordering":["-start_date","-pk"]},
        ),
        migrations.AddConstraint(model_name="motherpropertyownership",constraint=models.CheckConstraint(condition=Q(share_percent__isnull=True)|(Q(share_percent__gte=0)&Q(share_percent__lte=100)),name="mother_owner_share_range")),
        migrations.CreateModel(
            name="MotherPropertyOwnershipDocument",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("document_type",models.CharField(max_length=120)),("document_number",models.CharField(blank=True,max_length=120)),("document_date",models.CharField(blank=True,max_length=10)),
                ("notary_number",models.CharField(blank=True,max_length=80)),("notary_name",models.CharField(blank=True,max_length=255)),
                ("main_plate",models.CharField(blank=True,max_length=80)),("sub_plate",models.CharField(blank=True,max_length=80)),("registration_section",models.CharField(blank=True,max_length=120)),
                ("documented_area",models.DecimalField(blank=True,decimal_places=2,max_digits=16,null=True)),("documented_owner_name",models.CharField(blank=True,max_length=255)),
                ("owner_type",models.CharField(blank=True,choices=[("NATURAL","حقیقی"),("LEGAL","حقوقی"),("ORGANIZATIONAL","سازمانی"),("UNKNOWN","نامشخص")],max_length=20)),
                ("description",models.TextField(blank=True)),("status",models.CharField(choices=[("ACTIVE","فعال"),("VOID","باطل"),("ERROR","ثبت اشتباه")],default="ACTIVE",max_length=20)),
                ("created_at",models.DateTimeField(auto_now_add=True)),
                ("created_by",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("document",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="mother_property_ownership_records",to="documents.document")),
                ("property",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="ownership_documents",to="properties.motherproperty")),
            ], options={"ordering":["-document_date","-pk"]},
        ),
        migrations.AddConstraint(model_name="motherpropertyownershipdocument",constraint=models.CheckConstraint(condition=Q(documented_area__isnull=True)|Q(documented_area__gte=0),name="mother_ownership_doc_area_nonnegative")),
        migrations.CreateModel(
            name="MotherPropertyUsageHistory",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("usage_status",models.CharField(max_length=120)),("holder_type",models.CharField(blank=True,max_length=120)),("holder_unit",models.CharField(blank=True,max_length=255)),
                ("beneficiary_name",models.CharField(blank=True,max_length=255)),("beneficiary_type",models.CharField(blank=True,max_length=120)),
                ("start_date",models.CharField(max_length=10)),("end_date",models.CharField(blank=True,max_length=10)),("basis",models.CharField(blank=True,max_length=255)),
                ("contract_reference",models.CharField(blank=True,max_length=255)),("termination_reason",models.TextField(blank=True)),("notes",models.TextField(blank=True)),
                ("created_at",models.DateTimeField(auto_now_add=True)),
                ("created_by",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("document",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="mother_property_usage_records",to="documents.document")),
                ("property",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="usage_history",to="properties.motherproperty")),
            ], options={"ordering":["-start_date","-pk"]},
        ),
        migrations.AddConstraint(model_name="motherpropertyusagehistory",constraint=models.UniqueConstraint(condition=Q(end_date=""),fields=("property",),name="one_open_mother_property_usage")),
        migrations.CreateModel(
            name="MotherPropertyCorrespondence",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("document_type",models.CharField(max_length=120)),("number",models.CharField(blank=True,max_length=120)),("document_date",models.CharField(blank=True,max_length=10)),
                ("subject",models.CharField(max_length=255)),("sender",models.CharField(blank=True,max_length=255)),("recipient",models.CharField(blank=True,max_length=255)),
                ("organizational_unit",models.CharField(blank=True,max_length=255)),("summary",models.TextField(blank=True)),("needs_follow_up",models.BooleanField(default=False)),
                ("due_date",models.CharField(blank=True,max_length=10)),("follow_up_status",models.CharField(choices=[("OPEN","باز"),("DONE","انجام‌شده"),("CLOSED","مختومه"),("REVIEW_REQUIRED","نیازمند بررسی")],default="OPEN",max_length=30)),
                ("notes",models.TextField(blank=True)),("created_at",models.DateTimeField(auto_now_add=True)),
                ("created_by",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="created_mother_property_correspondence",to=settings.AUTH_USER_MODEL)),
                ("document",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="mother_property_correspondence",to="documents.document")),
                ("property",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="correspondence",to="properties.motherproperty")),
                ("responsible",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="mother_property_correspondence",to=settings.AUTH_USER_MODEL)),
            ], options={"ordering":["-document_date","-pk"]},
        ),
        migrations.CreateModel(
            name="MotherPropertyNote",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("subject",models.CharField(blank=True,max_length=255)),("text",models.TextField()),("active",models.BooleanField(default=True)),("created_at",models.DateTimeField(auto_now_add=True)),
                ("created_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL)),
                ("property",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="internal_notes",to="properties.motherproperty")),
            ], options={"ordering":["-created_at","-pk"]},
        ),
    ]
