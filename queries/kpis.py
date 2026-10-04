"""Canonical, explainable KPI definitions shared by cards and drill-downs."""
from dataclasses import dataclass

from django.urls import reverse

from domains.contracts.models import Contract
from domains.operations.models import Alert, Appraisal, WorkflowInstance
from domains.properties.models import CommercialSpace, MotherProperty


@dataclass(frozen=True)
class KPI:
    key: str
    title: str
    description: str
    count: int
    url: str
    tone: str


def dashboard_kpis():
    active = CommercialSpace.objects.filter(status="ACTIVE")
    definitions = (
        ("properties", "املاک مادر", "کل رکوردهای مرجع ملک", MotherProperty.objects.all(), reverse("mother-list"), "plum"),
        ("active", "فضاهای فعال", "فضاهای در چرخه بهره‌برداری", active, f'{reverse("space-list")}?status=ACTIVE', "green"),
        ("inactive", "خارج از چرخه", "فضاهای خارج‌شده از چرخه", CommercialSpace.objects.filter(status="OUT_OF_CYCLE"), f'{reverse("space-list")}?status=OUT_OF_CYCLE', "slate"),
        ("contracts", "سوابق قرارداد", "قراردادهای تاریخی و عملیاتی", Contract.objects.all(), reverse("domain-list", args=["contracts"]), "terracotta"),
        ("without_contract", "فاقد قرارداد", "فضاهای فعال بدون سابقه قرارداد", active.filter(contracts__isnull=True), f'{reverse("space-list")}?status=ACTIVE&contract_presence=empty', "amber"),
        ("without_appraisal", "فاقد کارشناسی", "فضاهای فعال بدون سابقه کارشناسی", active.filter(appraisals__isnull=True), f'{reverse("space-list")}?status=ACTIVE&appraisal_presence=empty', "plum"),
        ("alerts", "نیازمند پیگیری", "موارد باز و مختومه‌نشده", Alert.objects.exclude(status="RESOLVED"), f'{reverse("domain-list", args=["alerts"])}?state=OPEN', "red"),
        ("workflows", "فرایندهای باز", "گردش‌های عملیاتی جاری", WorkflowInstance.objects.filter(state="OPEN"), f'{reverse("domain-list", args=["workflows"])}?state=OPEN', "teal"),
    )
    return [KPI(key, title, description, queryset.distinct().count(), url, tone) for key, title, description, queryset, url, tone in definitions]


def scoped_counts(spaces):
    active = spaces.filter(status="ACTIVE")
    return {
        "space_count": spaces.count(),
        "active_count": active.count(),
        "inactive_count": spaces.filter(status="OUT_OF_CYCLE").count(),
        "property_count": MotherProperty.objects.filter(space_links__space__in=spaces).distinct().count(),
        "contract_count": Contract.objects.filter(space__in=spaces).count(),
        "appraisal_count": Appraisal.objects.filter(space__in=spaces).count(),
        "without_contract_count": active.filter(contracts__isnull=True).count(),
        "without_appraisal_count": active.filter(appraisals__isnull=True).count(),
        "workflow_count": WorkflowInstance.objects.filter(space__in=spaces, state="OPEN").count(),
        "alert_count": Alert.objects.filter(space__in=spaces).exclude(status="RESOLVED").count(),
    }
