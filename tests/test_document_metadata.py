import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from domains.documents.models import Document
from domains.identity.models import AuditEvent
from domains.properties.models import CommercialSpace


@pytest.mark.django_db
def test_space_document_upload_keeps_structured_metadata_and_audit(client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    user = get_user_model().objects.create_user("document-user", password="A-very-safe-password")
    client.force_login(user)
    space = CommercialSpace.objects.create(code="8901", name="فضای سند", status="ACTIVE")

    response = client.post(
        "/spaces/8901/documents/",
        {
            "title": "نامه مصوب",
            "document_type": "نامه",
            "reference": "1405/123",
            "document_date": "1405/07/15",
            "notes": "نسخه اسکن‌شده اصل نامه",
            "file": SimpleUploadedFile("letter.pdf", b"%PDF-1.4\nSAMA", content_type="application/pdf"),
        },
    )
    assert response.status_code == 302
    document = Document.objects.get()
    assert document.reference == "1405/123"
    assert document.document_date == "1405/07/15"
    assert document.notes == "نسخه اسکن‌شده اصل نامه"
    assert document.status_label == "فعال"
    event = AuditEvent.objects.get(action="DOCUMENT_UPLOAD", entity_type="CommercialSpace", entity_id="8901")
    assert event.after["reference"] == "1405/123"
    assert event.after["document_date"] == "1405/07/15"

    dossier = client.get("/spaces/8901/").content.decode()
    assert "1405/123" in dossier
    assert "1405/07/15" in dossier

    registry = client.get("/records/documents/", {"q": "1405/123"})
    assert registry.status_code == 200
    assert registry.context["page"].paginator.count == 1
    assert "نامه مصوب" in registry.content.decode()


@pytest.mark.django_db
def test_document_upload_rejects_invalid_jalali_date(client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    user = get_user_model().objects.create_user("document-date", password="A-very-safe-password")
    client.force_login(user)
    CommercialSpace.objects.create(code="8902", name="فضا", status="ACTIVE")

    response = client.post(
        "/spaces/8902/documents/",
        {
            "title": "سند",
            "document_type": "نامه",
            "document_date": "1405/13/40",
            "file": SimpleUploadedFile("bad.pdf", b"%PDF-1.4\nSAMA", content_type="application/pdf"),
        },
    )
    assert response.status_code == 302
    assert Document.objects.count() == 0
