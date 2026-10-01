from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0007_alert_actionability"),
    ]

    operations = [
        migrations.RemoveField(model_name="appraisal", name="source_file"),
        migrations.RemoveField(model_name="appraisal", name="source_row"),
        migrations.RemoveField(model_name="auction", name="source_file"),
        migrations.RemoveField(model_name="auction", name="source_row"),
        migrations.RemoveField(model_name="decisionorder", name="source_file"),
        migrations.RemoveField(model_name="decisionorder", name="source_row"),
        migrations.RemoveField(model_name="utilityobligation", name="source_file"),
        migrations.RemoveField(model_name="utilityobligation", name="source_row"),
        migrations.RemoveField(model_name="sourcedocumentreference", name="source_file"),
        migrations.RemoveField(model_name="sourcedocumentreference", name="source_row"),
    ]
