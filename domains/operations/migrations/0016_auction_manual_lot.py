from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0015_auction_instructions"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="auctionlot",
            name="evaluation",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="operations.auctionevaluation"),
        ),
        migrations.AddField(
            model_name="auctionlot",
            name="entry_method",
            field=models.CharField(choices=[("EVALUATED","انتخاب از ارزیابی کاندیدا"),("MANUAL","افزودن دستی مجاز")], default="EVALUATED", max_length=20),
        ),
        migrations.AddField(
            model_name="auctionlot",
            name="manual_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="auctionlot",
            name="manual_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="auctionlot",
            name="added_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="added_auction_lots", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name="auctionlot",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(("entry_method","EVALUATED"),("evaluation__isnull",False))
                    | models.Q(("entry_method","MANUAL"),("manual_reason__gt",""),("manual_reference__gt",""))
                ),
                name="auction_lot_entry_evidence_required",
            ),
        ),
    ]
