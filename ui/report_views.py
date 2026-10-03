from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from domains.identity.models import SavedReport
from queries.spaces import filter_spaces
from queries.mother_properties import filter_mother_properties
from reporting.engine import FIELD_MAP, MOTHER_FIELD_MAP, output_table, excel, pdf, docx
from services.reports import save_report, archive_report, report_query_string


def _domain(request):
    return 'mother_properties' if request.GET.get('domain') == 'mother_properties' or request.POST.get('domain') == 'mother_properties' else 'commercial_spaces'


def _field_map(domain):
    return MOTHER_FIELD_MAP if domain == 'mother_properties' else FIELD_MAP


def _query(request, domain):
    return filter_mother_properties(request.GET)[:5000] if domain == 'mother_properties' else filter_spaces(request.GET)[:5000]


def _title(domain):
    return 'املاک مادر' if domain == 'mother_properties' else 'فضاهای تجاری'


def _blank_rows(request):
    try:
        return max(0, min(50, int(request.GET.get('blank_rows') or request.POST.get('blank_rows') or 0)))
    except (TypeError, ValueError):
        return 0


@login_required
def report_builder(request):
    domain = _domain(request)
    field_map = _field_map(domain)
    return render(request, 'ui/report_builder.html', {
        'fields': [(key, label) for key, (label, _) in field_map.items()],
        'saved': SavedReport.objects.filter(owner=request.user),
        'report_domain': domain,
        'report_title': _title(domain),
        'report_domains': [
            ('commercial_spaces', 'فضاهای تجاری'),
            ('mother_properties', 'املاک مادر'),
        ],
    })


@login_required
def report_preview(request):
    domain = _domain(request)
    labels, rows = output_table(
        _query(request, domain)[:100],
        request.GET.getlist('layout'),
        request.GET.getlist('field'),
        request.GET.getlist('blank'),
        _field_map(domain),
        blank_rows=_blank_rows(request),
    )
    return render(request, 'ui/report_preview.html', {
        'labels': labels,
        'rows': rows,
        'query': request.GET.urlencode(),
        'export_prefix': 'mother-properties' if domain == 'mother_properties' else '',
        'report_domain': domain,
    })


@login_required
def report_save(request):
    if request.method != 'POST':
        return redirect('report-builder')
    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'نام گزارش الزامی است.')
        return redirect(f"/reports/?domain={_domain(request)}")
    report = save_report(owner=request.user, name=name, data=request.POST, ip_address=request.META.get('REMOTE_ADDR'))
    messages.success(request, 'تعریف زنده گزارش ذخیره شد.')
    return redirect(f"/reports/?domain={report.domain}")


@login_required
def report_open(request, report_id):
    report = get_object_or_404(SavedReport, pk=report_id, owner=request.user)
    query = report_query_string(report)
    return redirect(f"/reports/preview/?domain={report.domain}&{query}")


@login_required
def report_archive(request, report_id):
    if request.method != 'POST':
        return redirect('report-builder')
    report = get_object_or_404(SavedReport, pk=report_id, owner=request.user)
    snapshot = archive_report(report=report, actor=request.user, ip_address=request.META.get('REMOTE_ADDR'))
    messages.success(request, f'نسخه ثابت با {snapshot.row_count} ردیف و اثر انگشت {snapshot.sha256[:12]} ثبت شد.')
    return redirect(f"/reports/?domain={report.domain}")


def _export(request, domain, kind):
    field_map = _field_map(domain)
    query = _query(request, domain)
    blanks = request.GET.getlist('blank')
    selected = request.GET.getlist('field')
    layout = request.GET.getlist('layout')
    orientation = request.GET.get('orientation', 'landscape')
    blank_rows = _blank_rows(request)
    title = _title(domain)
    if kind == 'xlsx':
        payload = excel(query, blanks, selected, layout, orientation, field_map, title, blank_rows=blank_rows)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif kind == 'docx':
        payload = docx(query, blanks, selected, layout, orientation, field_map, blank_rows=blank_rows)
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        payload = pdf(query, selected, blanks, layout, orientation, field_map, blank_rows=blank_rows)
        content_type = 'application/pdf'
    prefix = 'mother-properties' if domain == 'mother_properties' else 'spaces'
    return HttpResponse(payload, content_type=content_type, headers={'Content-Disposition': f'attachment; filename="{prefix}.{kind}"'})


@login_required
def spaces_excel(request): return _export(request, 'commercial_spaces', 'xlsx')
@login_required
def spaces_docx(request): return _export(request, 'commercial_spaces', 'docx')
@login_required
def spaces_pdf(request): return _export(request, 'commercial_spaces', 'pdf')
@login_required
def mother_excel(request): return _export(request, 'mother_properties', 'xlsx')
@login_required
def mother_docx(request): return _export(request, 'mother_properties', 'docx')
@login_required
def mother_pdf(request): return _export(request, 'mother_properties', 'pdf')
