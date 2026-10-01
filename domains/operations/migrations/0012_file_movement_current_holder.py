from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies=[("operations","0011_water_gas_utility_foundation")]
    operations=[
        migrations.AlterField(
            model_name="filemovement",
            name="direction",
            field=models.CharField(choices=[("OUT","خروج"),("IN","ورود")],max_length=20),
        ),
        migrations.AddConstraint(
            model_name="filemovement",
            constraint=models.UniqueConstraint(
                fields=("space",),
                condition=Q(returned_at__isnull=True),
                name="one_open_file_movement_per_space",
            ),
        ),
    ]
