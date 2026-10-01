from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("contracts", "0003_beneficiary_kind_choices"),
    ]

    operations = [
        migrations.RemoveField(model_name="beneficiaryassignment", name="source_file"),
        migrations.RemoveField(model_name="beneficiaryassignment", name="source_row"),
        migrations.RemoveField(model_name="contract", name="source_file"),
        migrations.RemoveField(model_name="contract", name="source_row"),
        migrations.AlterField(
            model_name="contract",
            name="is_historical",
            field=models.BooleanField(default=False),
        ),
    ]
