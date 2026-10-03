"""Application service for durable report definitions and immutable snapshots."""
from urllib.parse import urlencode
import hashlib
from django.core.files.base import ContentFile
from django.db import transaction
from domains.identity.models import ArchivedReportSnapshot, AuditEvent, SavedReport
from queries.spaces import filter_spaces
from queries.mother_properties import filter_mother_properties
from reporting.engine import columns, excel, layout_columns, MOTHER_FIELD_MAP

FILTER_KEYS = ("q", "identifier", "property_name", "logic", "code", "code_op", "status", "region_id", "center_id", "usage", "usage_op", "beneficiary", "beneficiary_op", "contract", "contract_op", "area_min", "area_max", "address_presence", "sort", "blank_rows")
MULTI_KEYS = {"status", "region_id", "center_id", "sort"}

def normalized_report_definition(data):
    domain=data.get("domain","commercial_spaces");field_map=MOTHER_FIELD_MAP if domain=="mother_properties" else None
    fields = columns(data.getlist("field"),field_map)
    blanks = [value.strip() for value in data.getlist("blank") if value.strip()][:8]
    filters = {}
    for key in FILTER_KEYS:
        values = [value.strip() for value in data.getlist(key) if value.strip()]
        if values: filters[key] = values if key in MULTI_KEYS else values[-1]
    sorting = filters.get("sort", [])
    grouping = [value for value in data.getlist("group") if value in {"status", "region", "center", "current_usage"}]
    requested_layout=data.getlist("layout")
    layout=[f"{kind}:{value}" for kind,value in layout_columns(requested_layout,fields,blanks,field_map)] if requested_layout else []
    orientation=data.get("orientation","landscape") if data.get("orientation") in {"landscape","portrait"} else "landscape"
    return {"domain":domain,"fields": fields, "blank_columns": blanks, "layout":layout,"orientation":orientation,"filters": filters, "sorting": sorting,"grouping": grouping}

def save_report(*, owner, name, data, ip_address=None):
    definition = normalized_report_definition(data)
    with transaction.atomic():
        report = SavedReport.objects.create(owner=owner, name=name, domain=definition["domain"], fields=definition["fields"], filters=definition["filters"], sorting=definition["sorting"], grouping=definition["grouping"], blank_columns=definition["blank_columns"],layout=definition["layout"],orientation=definition["orientation"])
        AuditEvent.objects.create(actor=owner, action="REPORT_DEFINITION_CREATE", entity_type="SavedReport", entity_id=str(report.pk), after=definition, ip_address=ip_address)
    return report

def report_query_string(report):
    pairs = []
    for key,value in report.filters.items():
        pairs.extend((key,item) for item in value) if isinstance(value,list) else pairs.append((key,value))
    pairs += [("field", value) for value in report.fields] + [("blank", value) for value in report.blank_columns]
    if report.layout:pairs += [("layout",value) for value in report.layout]
    if report.orientation!='landscape':pairs.append(("orientation",report.orientation))
    return urlencode(pairs)

def archive_report(*, report, actor, ip_address=None):
    definition = {"filters": report.filters, "fields": report.fields, "sorting": report.sorting, "grouping": report.grouping, "blank_columns": report.blank_columns,"layout":report.layout,"orientation":report.orientation}
    mother=report.domain=="mother_properties";queryset = filter_mother_properties(report.filters) if mother else filter_spaces(report.filters)
    row_count = queryset.count()
    try:blank_rows=max(0,min(50,int(report.filters.get('blank_rows',0) or 0)))
    except (TypeError,ValueError):blank_rows=0
    payload = excel(queryset, report.blank_columns, report.fields,report.layout,report.orientation,MOTHER_FIELD_MAP if mother else None,'املاک مادر' if mother else 'فضاها',blank_rows=blank_rows)
    digest = hashlib.sha256(payload).hexdigest()
    with transaction.atomic():
        snapshot = ArchivedReportSnapshot(report=report, generated_by=actor, query_context=definition, row_count=row_count, sha256=digest)
        snapshot.file.save(f"report-{report.pk}-{digest[:12]}.xlsx", ContentFile(payload), save=False)
        snapshot.save()
        AuditEvent.objects.create(actor=actor, action="REPORT_SNAPSHOT_CREATE", entity_type="ArchivedReportSnapshot", entity_id=str(snapshot.pk), after={"sha256": digest, "row_count": row_count}, ip_address=ip_address)
    return snapshot
