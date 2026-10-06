from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("utilities", "0001_initial")]
    operations = [
        migrations.AlterModelOptions(
            name="utilityspaceprofile",
            options={"ordering": ["space_id"]},
        ),
    ]
