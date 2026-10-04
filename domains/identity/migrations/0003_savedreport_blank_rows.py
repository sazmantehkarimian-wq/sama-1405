from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("identity", "0002_savedreport_layout_orientation")]
    operations = [
        migrations.AddField(
            model_name="savedreport",
            name="blank_rows",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
