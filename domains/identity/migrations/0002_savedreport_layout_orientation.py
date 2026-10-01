from django.db import migrations, models
class Migration(migrations.Migration):
 dependencies=[('identity','0001_initial')]
 operations=[migrations.AddField(model_name='savedreport',name='layout',field=models.JSONField(default=list)),migrations.AddField(model_name='savedreport',name='orientation',field=models.CharField(default='landscape',max_length=20))]
