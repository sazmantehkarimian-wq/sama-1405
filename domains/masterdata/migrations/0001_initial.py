import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("properties", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="OrganizationPerson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(db_index=True, max_length=180)),
                ("mobile", models.CharField(blank=True, max_length=40)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("extension", models.CharField(blank=True, max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["full_name", "id"]},
        ),
        migrations.CreateModel(
            name="ReferenceCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("USAGE", "گروه کاربری"), ("ACTIVITY", "نوع فعالیت"), ("CENTER_TYPE", "نوع مرکز"), ("ORGANIZATIONAL_SCOPE", "حوزه سازمانی")], db_index=True, max_length=30)),
                ("code", models.SlugField(max_length=80)),
                ("name", models.CharField(max_length=180)),
                ("aliases", models.JSONField(blank=True, default=list)),
                ("sort_order", models.PositiveIntegerField(default=100)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={"ordering": ["kind", "sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="OrganizationUnit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("unit_type", models.CharField(choices=[("ORGANIZATION", "سازمان"), ("DEPUTY", "معاونت"), ("MANAGEMENT", "مدیریت"), ("DEPARTMENT", "اداره"), ("REGION", "منطقه"), ("CENTER", "مرکز"), ("SPECIAL_CENTER", "مرکز خاص"), ("OTHER", "سایر")], db_index=True, max_length=30)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("extension", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("center", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="masterdata_units", to="properties.center")),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="masterdata.organizationunit")),
                ("region", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="masterdata_units", to="properties.region")),
            ],
            options={"ordering": ["unit_type", "name"]},
        ),
        migrations.CreateModel(
            name="PositionAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(db_index=True, max_length=180)),
                ("start_date", models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message="تاریخ باید به صورت ۱۴۰۵/۰۷/۱۵ یا 1405/07/15 وارد شود.", regex="^[0-9۰-۹]{4}/[0-9۰-۹]{2}/[0-9۰-۹]{2}$")])),
                ("end_date", models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message="تاریخ باید به صورت ۱۴۰۵/۰۷/۱۵ یا 1405/07/15 وارد شود.", regex="^[0-9۰-۹]{4}/[0-9۰-۹]{2}/[0-9۰-۹]{2}$")])),
                ("is_current", models.BooleanField(db_index=True, default=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assignments", to="masterdata.organizationperson")),
                ("unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assignments", to="masterdata.organizationunit")),
            ],
            options={"ordering": ["-is_current", "unit__name", "title", "person__full_name"]},
        ),
        migrations.AddConstraint(model_name="referencecategory", constraint=models.UniqueConstraint(fields=("kind", "code"), name="uniq_masterdata_category_kind_code")),
        migrations.AddConstraint(model_name="referencecategory", constraint=models.UniqueConstraint(fields=("kind", "name"), name="uniq_masterdata_category_kind_name")),
        migrations.AddIndex(model_name="positionassignment", index=models.Index(fields=["unit", "is_current"], name="masterdata_p_unit_id_9042af_idx")),
        migrations.AddIndex(model_name="positionassignment", index=models.Index(fields=["title", "is_current"], name="masterdata_p_title_9f1c8e_idx")),
    ]
