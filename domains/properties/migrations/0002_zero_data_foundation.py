# Zero-data foundation: remove import provenance from operational property models.
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="MotherPropertySpaceLink"),
        migrations.RemoveField(model_name="commercialspacestatushistory", name="source_file"),
        migrations.RemoveField(model_name="commercialspace", name="source_row"),
        migrations.RemoveField(model_name="commercialspace", name="source_classification"),
        migrations.RemoveField(model_name="motherproperty", name="source_row"),
        migrations.AddField(
            model_name="commercialspace",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="commercialspace",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="motherproperty",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="motherproperty",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="commercialspace",
            name="area",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=16, null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0"))],
            ),
        ),
        migrations.AlterField(
            model_name="commercialspace",
            name="code",
            field=models.CharField(
                db_index=True, max_length=30, unique=True,
                validators=[django.core.validators.RegexValidator(
                    regex="^[1-9][0-9]*$",
                    message="کد فضا باید فقط عدد صحیح مثبت و بدون صفر ابتدایی باشد.",
                )],
            ),
        ),
        migrations.AlterField(
            model_name="motherproperty",
            name="area",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=16, null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0"))],
            ),
        ),
        migrations.AddConstraint(
            model_name="commercialspace",
            constraint=models.CheckConstraint(
                condition=models.Q(area__isnull=True) | models.Q(area__gte=0),
                name="commercial_space_area_nonnegative",
            ),
        ),
        migrations.AddConstraint(
            model_name="motherproperty",
            constraint=models.CheckConstraint(
                condition=models.Q(area__isnull=True) | models.Q(area__gte=0),
                name="mother_property_area_nonnegative",
            ),
        ),
        migrations.AddConstraint(
            model_name="center",
            constraint=models.UniqueConstraint(fields=("name", "region"), name="uniq_center_region"),
        ),
    ]
