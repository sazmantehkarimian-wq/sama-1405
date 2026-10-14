import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
REGISTRY_PATH = ROOT / "design_system" / "registry" / "sama_ds_registry_v1.0.json"


def _registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _all_codes(registry):
    codes = []
    for family, items in registry["families"].items():
        for item in items:
            if isinstance(item, dict):
                codes.append(item["code"])
            else:
                codes.append(item)
    return codes


def test_registry_is_governing_single_source_of_truth():
    registry = _registry()
    assert registry["design_system"] == "SAMA-DS"
    assert registry["version"] == "1.0.0"
    assert registry["status"] == "APPROVED_GOVERNING_BASELINE"
    governance = registry["governance"]
    assert governance["single_source_of_truth"] is True
    assert governance["no_local_reinvention"] is True
    assert governance["delta_only_migration"] is True
    assert governance["frozen_component_changes_require_approval"] is True
    assert governance["report_engine_required_for_official_output"] is True


def test_registry_codes_are_unique_and_canonical():
    codes = _all_codes(_registry())
    assert len(codes) == len(set(codes))
    code_pattern = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-\d{2}$|^[A-Z]{3}$")
    invalid = [code for code in codes if not code_pattern.match(code)]
    assert invalid == []


def test_required_design_families_and_core_variants_exist():
    registry = _registry()
    required_families = {
        "foundation", "buttons", "titles", "fields", "forms", "surfaces",
        "tables", "search_filter", "toolbars", "navigation", "feedback",
        "overlays", "patterns", "pages", "reports",
    }
    assert required_families <= set(registry["families"])
    codes = set(_all_codes(registry))
    required_codes = {
        "BTN-PRI-01", "BTN-SEC-01", "BTN-OUT-01", "BTN-TBL-01",
        "TTL-PAGE-01", "FRM-SECT-01", "TBL-MGT-01", "SRC-FRE-01",
        "FLT-MUL-01", "TBR-PAGE-01", "TBR-TBL-01", "TBR-FRM-01",
        "TAB-MOD-01", "BDG-STA-01", "EMP-STD-01", "MNU-ACT-01",
        "PAT-MGT-01", "PAT-FORM-01", "PAGE-MGT-01", "PAGE-FORM-01",
        "RPT-PDF-LIST-01", "RPT-XLS-LIST-01", "RPT-PRT-OFFICIAL-01",
    }
    assert required_codes <= codes


def test_baseinfo_has_explicit_registry_mapping_for_every_approved_area():
    mappings = _registry()["module_mappings"]
    expected = {
        "baseinfo.organization",
        "baseinfo.regions_centers",
        "baseinfo.contacts",
        "baseinfo.commissions",
        "baseinfo.bank_accounts",
    }
    assert set(mappings) == expected
    all_codes = set(_all_codes(_registry()))
    for module, codes in mappings.items():
        assert codes, module
        assert set(codes) <= all_codes, module


def test_baseinfo_management_pages_share_the_same_management_contract():
    mappings = _registry()["module_mappings"]
    for module in (
        "baseinfo.regions_centers",
        "baseinfo.contacts",
        "baseinfo.commissions",
        "baseinfo.bank_accounts",
    ):
        codes = set(mappings[module])
        assert {"PAGE-MGT-01", "PAT-MGT-01", "TBL-MGT-01", "BTN-PRI-01", "BTN-OUT-01"} <= codes


def test_baseinfo_organization_uses_form_contract_not_management_table():
    codes = set(_registry()["module_mappings"]["baseinfo.organization"])
    assert {"PAGE-FORM-01", "PAT-FORM-01", "FRM-SECT-01", "PNL-SEC-01", "TBR-FRM-01"} <= codes
    assert "TBL-MGT-01" not in codes


def test_governing_documents_are_present():
    assert (ROOT / "authority" / "reference" / "MD رجیستری اجرایی Design System سما — GOVERNING BASELINE v1.0.md").exists()
    assert (ROOT / "docs" / "BASEINFO_DESIGN_SYSTEM_COMPLIANCE_MATRIX.md").exists()
