import hashlib

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from domains.auctionflow.intake_models import AuctionParticipantProfile
from domains.auctionflow.models import AuctionDocumentInstance, AuctionLotProfile
from domains.identity.models import AuditEvent
from services.auction_flow import build_field_registry, build_lot_snapshot, snapshot_hash
from services.auction_pdf_contracts import render_contract_pdf
from services.auction_templates import render_docx_from_source, source_bytes, source_for
from services.documents import store_document


def _participant_payload(participant):
    profile = getattr(participant, "identity_profile", None)
    data = {
        "name": participant.name,
        "identity_number": participant.identity_number,
        "contact": participant.contact,
    }
    if not profile:
        return data
    data.update({
        "kind": profile.kind,
        "father_name": profile.father_name,
        "birth_certificate_number": profile.birth_certificate_number,
        "birth_date": profile.birth_date,
        "postal_code": profile.postal_code,
        "address": profile.address,
        "phone": profile.phone,
        "mobile": profile.mobile,
        "legal_name": profile.legal_name,
        "registration_number": profile.registration_number,
        "economic_code": profile.economic_code,
        "representative_name": profile.representative_name,
    })
    return data


def _enrich_fields(lot, fields):
    profile = AuctionLotProfile.objects.select_related("winner_proposal__participant", "beneficiary", "official_contract").get(lot=lot)
    proposals = []
    for proposal in lot.proposals.select_related("participant").order_by("pk"):
        person = _participant_payload(proposal.participant)
        intake = getattr(proposal, "intake", None)
        proposals.append({
            "name": person.get("name", ""),
            "contact": person.get("mobile") or person.get("phone") or person.get("contact", ""),
            "postal_code": person.get("postal_code", ""),
            "birth_date": person.get("birth_date", ""),
            "identity_number": person.get("identity_number", ""),
            "receipt_number": intake.receipt_number if intake else "",
            "guarantee_amount": fields.get("LOT-003", ""),
            "offered_amount": f"{proposal.offered_amount_rial:,.0f}" if proposal.offered_amount_rial is not None else "",
        })
    fields["_SESSION_PROPOSALS"] = proposals

    if profile.winner_proposal_id:
        participant = profile.winner_proposal.participant
        participant_data = _participant_payload(participant)
        if not profile.beneficiary_id:
            fields["_BENEFICIARY"] = participant_data

    if not profile.official_contract_id:
        draft = getattr(lot, "contract_draft", None)
        if draft:
            fields["_CONTRACT"] = {
                "number": "",
                "subject": draft.subject,
                "signed_date": "",
                "start_date": draft.start_date,
                "end_date": draft.end_date,
                "amount_rial": str(draft.amount_rial),
                "monthly_amount": f"{draft.amount_rial:,.0f}",
                "investment_commitment_rial": str(draft.investment_commitment_rial or ""),
                "status": "پیش‌نویس قرارداد برنده مزایده",
                "signed_state": "در گردش امضا",
            }
    return fields


@transaction.atomic
def generate_complete_document(*, lot, document_type, actor, ip_address=None):
    profile, _ = AuctionLotProfile.objects.get_or_create(lot=lot)
    if document_type == AuctionDocumentInstance.DocumentType.SAMPLE_CONTRACT and not profile.winner_proposal_id:
        raise ValidationError("نمونه قرارداد تکمیل‌شده فقط پس از ثبت برنده قابل تولید است.")

    snapshot = build_lot_snapshot(lot)
    fields = _enrich_fields(lot, build_field_registry(snapshot))
    source = source_for(document_type=document_type, family=profile.template_family)
    raw_source = source_bytes(source)

    if document_type == AuctionDocumentInstance.DocumentType.SAMPLE_CONTRACT:
        payload, extension = render_contract_pdf(source_bytes=raw_source, family=profile.template_family, fields=fields)
        mime = "application/pdf"
    else:
        payload, extension = render_docx_from_source(source=source, document_type=document_type, fields=fields)
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    snap_hash = snapshot_hash(snapshot)
    output_sha = hashlib.sha256(payload).hexdigest()
    filename = f"auction-{lot.period.identity}-{lot.space.code}-{document_type.lower()}.{extension}"
    stored = store_document(
        uploaded=SimpleUploadedFile(filename, payload, content_type=mime),
        title=f"{AuctionDocumentInstance.DocumentType(document_type).label} — فضای {lot.space.code}",
        document_type=f"AUCTION_GENERATED_{document_type}", entity_type="AuctionLot", entity_id=lot.pk,
        user=actor, reference=lot.period.identity, document_date=lot.period.planned_date,
        notes=f"UAT_DRAFT; template={source.version}; source_sha={source.source_sha256}; snapshot={snap_hash}; output={output_sha}",
        ip_address=ip_address,
    )
    instance = AuctionDocumentInstance.objects.create(
        period=lot.period, lot=lot, document_type=document_type, template_family=profile.template_family,
        template_version=source.version, template_source=source, source_sha256=source.source_sha256,
        snapshot=snapshot, snapshot_sha256=snap_hash, document=stored, output_sha256=output_sha, generated_by=actor,
    )
    AuditEvent.objects.create(
        actor=actor, action="AUCTION_DOCUMENT_GENERATED", entity_type="AuctionLot", entity_id=str(lot.pk),
        after={"instance_id": instance.pk, "document_instance_id": instance.instance_id, "document_type": document_type,
               "template_source_id": source.pk, "template_version": instance.template_version,
               "source_sha256": instance.source_sha256, "snapshot_sha256": snap_hash,
               "output_sha256": output_sha, "status": instance.status}, ip_address=ip_address,
    )
    return instance
