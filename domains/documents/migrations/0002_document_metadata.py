from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="document",
            name="document_date",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="document",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="document",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
