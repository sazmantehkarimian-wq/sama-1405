from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("registry", "0001_initial"),
        ("properties", "0002_zero_data_foundation"),
        ("contracts", "0004_zero_data_manual_entry"),
        ("operations", "0008_zero_data_manual_entry"),
    ]

    operations = [
        migrations.DeleteModel(name="RawCell"),
        migrations.RemoveField(model_name="discrepancy", name="source_file"),
        migrations.DeleteModel(name="SourceFile"),
        migrations.DeleteModel(name="ImportBatch"),
    ]
