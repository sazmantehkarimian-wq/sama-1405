from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies=[("operations","0016_auction_manual_lot")]

    operations=[
        migrations.AlterField(
            model_name="alert",name="status",
            field=models.CharField(choices=[("OPEN","باز"),("RESOLVED","مختومه")],default="OPEN",max_length=30),
        ),
        migrations.AddConstraint(
            model_name="alert",
            constraint=models.CheckConstraint(condition=models.Q(priority__in=["LOW","MEDIUM","HIGH","CRITICAL"]),name="alert_priority_valid"),
        ),
        migrations.AddConstraint(
            model_name="alert",
            constraint=models.CheckConstraint(condition=models.Q(status__in=["OPEN","RESOLVED"]),name="alert_status_valid"),
        ),
        migrations.AlterField(
            model_name="workflowinstance",name="process_type",
            field=models.CharField(choices=[("CONTRACT","قرارداد"),("APPRAISAL","کارشناسی"),("AUCTION","مزایده"),("COMMISSION","کمیسیون"),("FILE","پرونده"),("OTHER","سایر")],max_length=80),
        ),
        migrations.AddConstraint(
            model_name="workflowinstance",
            constraint=models.CheckConstraint(condition=models.Q(process_type__in=["CONTRACT","APPRAISAL","AUCTION","COMMISSION","FILE","OTHER"]),name="workflow_process_type_valid"),
        ),
        migrations.AddConstraint(
            model_name="workflowinstance",
            constraint=models.CheckConstraint(condition=models.Q(state__in=["OPEN","DONE","CANCELLED"]),name="workflow_state_valid"),
        ),
    ]
