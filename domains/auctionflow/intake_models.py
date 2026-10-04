from django.conf import settings
from django.db import models


class AuctionParticipantProfile(models.Model):
    """Structured participant identity used for receipts, minutes and contract hand-off."""

    class Kind(models.TextChoices):
        NATURAL = "NATURAL", "شخص حقیقی"
        LEGAL = "LEGAL", "شخص حقوقی"

    participant = models.OneToOneField(
        "operations.AuctionParticipant", on_delete=models.PROTECT,
        related_name="identity_profile",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NATURAL)
    father_name = models.CharField(max_length=120, blank=True)
    birth_certificate_number = models.CharField(max_length=40, blank=True)
    birth_date = models.CharField(max_length=10, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    legal_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=60, blank=True)
    economic_code = models.CharField(max_length=40, blank=True)
    representative_name = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name="updated_auction_participant_profiles",
    )
    updated_at = models.DateTimeField(auto_now=True)


class AuctionProposalIntake(models.Model):
    """Reception metadata and envelope-B decision kept separate from the bid amount."""

    class EnvelopeBDecision(models.TextChoices):
        PENDING = "PENDING", "در انتظار بررسی"
        ACCEPTED = "ACCEPTED", "مورد تأیید جلسه"
        REJECTED = "REJECTED", "ردشده توسط جلسه"

    proposal = models.OneToOneField(
        "operations.AuctionProposal", on_delete=models.PROTECT,
        related_name="intake",
    )
    receipt_number = models.CharField(max_length=80, blank=True)
    registrar = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="registered_auction_proposals",
    )
    notes = models.TextField(blank=True)
    envelope_b_decision = models.CharField(
        max_length=20, choices=EnvelopeBDecision.choices, default=EnvelopeBDecision.PENDING,
    )
    c_opening_allowed = models.BooleanField(null=True, blank=True)
    decision_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuctionOpeningSession(models.Model):
    """Versioned opening-session record; SAMA records declared decisions, never computes them."""

    class State(models.TextChoices):
        DRAFT = "DRAFT", "پیش‌نویس"
        HELD = "HELD", "برگزارشده"
        CLOSED = "CLOSED", "مختومه"
        CANCELLED = "CANCELLED", "لغوشده"

    period = models.ForeignKey(
        "operations.AuctionPeriod", on_delete=models.PROTECT,
        related_name="opening_sessions",
    )
    session_date = models.CharField(max_length=10)
    session_time = models.CharField(max_length=5, blank=True)
    location = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.DRAFT)
    member_snapshot = models.JSONField(default=list, blank=True)
    declared_summary = models.TextField(blank=True)
    signature_note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="created_auction_opening_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-session_date", "-pk"]
