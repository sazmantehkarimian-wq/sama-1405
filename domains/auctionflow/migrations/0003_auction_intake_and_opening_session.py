from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auctionflow", "0002_controlled_templates_and_registry_fields"),
        ("operations", "0017_alert_workflow_constraints"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuctionOpeningSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_date", models.CharField(max_length=10)),
                ("session_time", models.CharField(blank=True, max_length=5)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("reference", models.CharField(blank=True, max_length=255)),
                ("state", models.CharField(choices=[("DRAFT", "پیش‌نویس"), ("HELD", "برگزارشده"), ("CLOSED", "مختومه"), ("CANCELLED", "لغوشده")], default="DRAFT", max_length=20)),
                ("member_snapshot", models.JSONField(blank=True, default=list)),
                ("declared_summary", models.TextField(blank=True)),
                ("signature_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_auction_opening_sessions", to=settings.AUTH_USER_MODEL)),
                ("period", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="opening_sessions", to="operations.auctionperiod")),
            ],
            options={"ordering": ["-session_date", "-pk"]},
        ),
        migrations.CreateModel(
            name="AuctionParticipantProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("NATURAL", "شخص حقیقی"), ("LEGAL", "شخص حقوقی")], default="NATURAL", max_length=20)),
                ("father_name", models.CharField(blank=True, max_length=120)),
                ("birth_certificate_number", models.CharField(blank=True, max_length=40)),
                ("birth_date", models.CharField(blank=True, max_length=10)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("address", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("mobile", models.CharField(blank=True, max_length=20)),
                ("legal_name", models.CharField(blank=True, max_length=255)),
                ("registration_number", models.CharField(blank=True, max_length=60)),
                ("economic_code", models.CharField(blank=True, max_length=40)),
                ("representative_name", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("participant", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="identity_profile", to="operations.auctionparticipant")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="updated_auction_participant_profiles", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="AuctionProposalIntake",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receipt_number", models.CharField(blank=True, max_length=80)),
                ("notes", models.TextField(blank=True)),
                ("envelope_b_decision", models.CharField(choices=[("PENDING", "در انتظار بررسی"), ("ACCEPTED", "مورد تأیید جلسه"), ("REJECTED", "ردشده توسط جلسه")], default="PENDING", max_length=20)),
                ("c_opening_allowed", models.BooleanField(blank=True, null=True)),
                ("decision_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("proposal", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="intake", to="operations.auctionproposal")),
                ("registrar", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="registered_auction_proposals", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
