from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from domains.documents.models import Document
from domains.operations.models import AuctionLot, AuctionParticipant, AuctionPeriod, AuctionProposal
from domains.properties.models import CommercialSpace


@pytest.mark.django_db
def test_auction_period_participant_envelope_and_document_workflow(client):
    user = get_user_model().objects.create_user("auction-entry", password="Safe-pass-123")
    client.force_login(user)
    space = CommercialSpace.objects.create(code="9901", name="فضای آزمون", status="ACTIVE")
    period = AuctionPeriod.objects.create(
        identity="AUC-TEST-01", title="دوره آزمون", planned_date="1405/08/01", created_by=user
    )
    lot = AuctionLot.objects.create(
        period=period, space=space, entry_method="MANUAL",
        manual_reason="آزمون گردش ثبت", manual_reference="REF-01",
        readiness="READY", added_by=user,
    )

    response = client.get(reverse("auction-period-detail", args=[period.pk]))
    assert response.status_code == 200
    assert "اسناد، شرکت‌کنندگان" not in response.content.decode("utf-8")

    response = client.post(reverse("auction-participant-create", args=[period.pk]), {
        "name": "شرکت نمونه", "identity_number": "10101010101", "contact": "02100000000",
    })
    assert response.status_code == 302
    participant = AuctionParticipant.objects.get(period=period)

    response = client.post(reverse("auction-proposal-create", args=[lot.pk]), {
        "participant": participant.pk,
        "received_at": "2026-10-03T10:30",
        "envelope_a_received": "on",
        "envelope_b_received": "on",
        "offered_amount_rial": "1500000000",
        "status": "دریافت اولیه",
    })
    assert response.status_code == 302
    proposal = AuctionProposal.objects.get(lot=lot, participant=participant)
    assert proposal.envelope_a_received is True
    assert proposal.envelope_b_received is True
    assert proposal.envelope_c_received is False
    assert proposal.offered_amount_rial == Decimal("1500000000")

    response = client.post(reverse("auction-proposal-edit", args=[proposal.pk]), {
        "participant": participant.pk,
        "received_at": "2026-10-03T10:30",
        "envelope_a_received": "on",
        "envelope_b_received": "on",
        "envelope_c_received": "on",
        "offered_amount_rial": "1500000000",
        "status": "تکمیل پاکات",
        "change_reason": "ثبت دریافت پاکت C",
    })
    assert response.status_code == 302
    proposal.refresh_from_db()
    assert proposal.envelope_c_received is True
    assert proposal.status == "تکمیل پاکات"

    uploaded = SimpleUploadedFile("auction.pdf", b"%PDF-1.4\n%test\n", content_type="application/pdf")
    response = client.post(reverse("auction-period-document-upload", args=[period.pk]), {
        "title": "آگهی مزایده",
        "document_type": "آگهی",
        "reference": "A-1405-01",
        "document_date": "1405/07/11",
        "notes": "نسخه آزمون",
        "file": uploaded,
    })
    assert response.status_code == 302
    document = Document.objects.get(entity_type="AuctionPeriod", entity_id=str(period.pk))
    assert document.title == "آگهی مزایده"
    assert len(document.sha256) == 64


@pytest.mark.django_db
def test_duplicate_proposal_for_same_participant_and_lot_is_blocked(client):
    user = get_user_model().objects.create_user("auction-entry-2", password="Safe-pass-123")
    client.force_login(user)
    space = CommercialSpace.objects.create(code="9902", name="فضای آزمون دو", status="ACTIVE")
    period = AuctionPeriod.objects.create(
        identity="AUC-TEST-02", title="دوره آزمون دو", planned_date="1405/08/02", created_by=user
    )
    lot = AuctionLot.objects.create(
        period=period, space=space, entry_method="MANUAL", manual_reason="آزمون",
        manual_reference="REF-02", readiness="READY", added_by=user,
    )
    participant = AuctionParticipant.objects.create(period=period, name="متقاضی نمونه")
    AuctionProposal.objects.create(
        lot=lot, participant=participant, received_at="2026-10-03T10:00:00Z", status="ثبت اولیه"
    )
    response = client.post(reverse("auction-proposal-create", args=[lot.pk]), {
        "participant": participant.pk,
        "received_at": "2026-10-03T11:00",
        "status": "تکراری",
    })
    assert response.status_code == 200
    assert AuctionProposal.objects.filter(lot=lot, participant=participant).count() == 1
    assert "قبلاً پیشنهاد ثبت شده" in response.content.decode("utf-8")
