"""Application service for durable report definitions and immutable snapshots."""
from urllib.parse import urlencode
import hashlib
from django.core.files.base import ContentFile
from django.db import transaction
from domains.identity.models import ArchivedReportSnapshot, AuditEvent, SavedReport
from queries.spaces import filter_spaces
from reporting.engine import columns, excel

FILTER_KEYS = ("q", "code", "status", "region_id", "center_id", "usage", "sort")

def normalized_report_definition(data):
    fields = columns(data.getlist("field"))
    blanks = [value.strip() for value in data.getlist("blank") if value.strip()][:8]
    filters = {key: data.get(key, "").strip() for key in FILTER_KEYS if data.get(key, "").strip()}
    return {"fields": fields, "blank_columns": blanks, "filters": filters, "sorting": [filters.get("sort", "code")], "grouping": []}

def save_report(*, owner, name, data, ip_address=None):
    definition = normalized_report_definition(data)
    with transaction.atomic():
        report = SavedReport.objects.create(owner=owner, name=name, domain="commercial_spaces", fields=definition["fields"], filters=definition["filters"], sorting=definition["sorting"], grouping=definition["grouping"], blank_columns=definition["blank_columns"])
        AuditEvent.objects.create(actor=owner, action="REPORT_DEFINITION_CREATE", entity_type="SavedReport", entity_id=str(report.pk), after=definition, ip_address=ip_address)
    return report

def report_query_string(report):
    pairs = list(report.filters.items()) + [("field", value) for value in report.fields] + [("blank", value) for value in report.blank_columns]
    return urlencode(pairs)

def archive_report(*, report, actor, ip_address=None):
    definition = {"filters": report.filters, "fields": report.fields, "sorting": report.sorting, "grouping": report.grouping, "blank_columns": report.blank_columns}
    queryset = filter_spaces(report.filters)
    row_count = queryset.count()
    payload = excel(queryset, report.blank_columns, report.fields)
    digest = hashlib.sha256(payload).hexdigest()
    with transaction.atomic():
        snapshot = ArchivedReportSnapshot(report=report, generated_by=actor, query_context=definition, row_count=row_count, sha256=digest)
        snapshot.file.save(f"report-{report.pk}-{digest[:12]}.xlsx", ContentFile(payload), save=False)
        snapshot.save()
        AuditEvent.objects.create(actor=actor, action="REPORT_SNAPSHOT_CREATE", entity_type="ArchivedReportSnapshot", entity_id=str(snapshot.pk), after={"sha256": digest, "row_count": row_count}, ip_address=ip_address)
    return snapshot
