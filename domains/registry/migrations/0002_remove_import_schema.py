from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("registry", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="RawCell"),
        migrations.RemoveField(model_name="discrepancy", name="source_file"),
        migrations.DeleteModel(name="SourceFile"),
        migrations.DeleteModel(name="ImportBatch"),
    ]
