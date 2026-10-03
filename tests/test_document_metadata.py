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


@pytest.mark.django_db
def test_document_archive_keeps_file_and_audits_without_hard_delete(client,tmp_path,settings):
    settings.MEDIA_ROOT=tmp_path
    user=get_user_model().objects.create_user("document-archive",password="A-very-safe-password")
    client.force_login(user)
    space=CommercialSpace.objects.create(code="8903",name="فضا",status="ACTIVE")
    client.post("/spaces/8903/documents/",{
        "title":"سند قابل بایگانی","document_type":"نامه","reference":"REF-1",
        "document_date":"1405/07/10",
        "file":SimpleUploadedFile("archive.pdf",b"%PDF-1.4\nSAMA",content_type="application/pdf"),
    })
    document=Document.objects.get()
    stored_name=document.file.name

    response=client.post(f"/documents/{document.pk}/archive/",{"reason":"جایگزینی با نسخه جدید"})
    assert response.status_code==302
    document.refresh_from_db()
    assert document.archived_at is not None
    assert Document.objects.filter(pk=document.pk).exists()
    assert document.file.name==stored_name
    event=AuditEvent.objects.get(action="DOCUMENT_ARCHIVE",entity_type="CommercialSpace",entity_id="8903")
    assert event.reason=="جایگزینی با نسخه جدید"

    dossier=client.get("/spaces/8903/").content.decode()
    assert "بایگانی‌شده" in dossier
    assert "REF-1" in dossier
    download=client.get(f"/documents/{document.pk}/download/")
    assert download.status_code==200


@pytest.mark.django_db
def test_document_download_fails_closed_when_file_hash_changes(client,tmp_path,settings):
    settings.MEDIA_ROOT=tmp_path
    user=get_user_model().objects.create_user("document-integrity",password="A-very-safe-password")
    client.force_login(user)
    CommercialSpace.objects.create(code="8904",name="فضا",status="ACTIVE")
    client.post("/spaces/8904/documents/",{
        "title":"سند کنترل صحت","document_type":"نامه",
        "file":SimpleUploadedFile("integrity.pdf",b"%PDF-1.4\nORIGINAL",content_type="application/pdf"),
    })
    document=Document.objects.get()
    path=document.file.path
    with open(path,"wb") as handle:
        handle.write(b"%PDF-1.4\nTAMPERED")

    response=client.get(f"/documents/{document.pk}/download/")
    assert response.status_code==409
    assert "کنترل صحت فایل ناموفق بود" in response.json()["detail"]
