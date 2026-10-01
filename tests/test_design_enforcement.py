import re
from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_prohibited_legacy_and_ui_patterns_absent():
 paths=list((ROOT/'ui').rglob('*'))+list((ROOT/'design_system').rglob('*.css'))
 text='\n'.join(p.read_text(errors='ignore') for p in paths if p.is_file() and p.suffix in {'.html','.css','.js','.py'})
 for pattern in ['app-sidebar','data-ui-version="3','window.print()','Tahoma','Arial','Segoe UI','ستون 17','testclient']:
  assert pattern not in text
def test_no_remote_runtime_assets_or_inline_styles():
 for p in (ROOT/'ui/templates').rglob('*.html'):
  text=p.read_text();assert 'https://' not in text and ' style=' not in text
def test_colors_live_only_in_tokens():
 app=(ROOT/'design_system/static/design_system/css/app.css').read_text()
 colors=set(re.findall(r'#[0-9a-fA-F]{3,8}',app));assert colors <= {'#fff','#000'}

def test_official_product_name_and_account_navigation_are_enforced():
 templates='\n'.join(p.read_text() for p in (ROOT/'ui/templates').rglob('*.html'))
 for obsolete in ('سامانه مدیریت امور قراردادها','سامانه مدیریت قراردادها','سامانه جامع مدیریت املاک','SAMA NEXT','SAMA Next'):
  assert obsolete not in templates
 assert '<span class="brand-title">سما</span>' in (ROOT/'ui/templates/ui/base.html').read_text()
 base=(ROOT/'ui/templates/ui/base.html').read_text()
 nav=base.split('<nav class="topnav"',1)[1].split('</nav>',1)[0]
 assert '>خروج<' not in nav
 assert 'class="account"' in base and 'aria-current="page"' in base

def test_official_report_engine_has_only_organizational_identity_and_rtl_contract():
 engine=(ROOT/'reporting/engine.py').read_text()
 assert "HEADERS=['سازمان فرهنگی هنری شهرداری تهران','مدیریت اقتصادی و املاک','اداره املاک و مستغلات']" in engine
 for forbidden in ('سامانه مدیریت قراردادها','SAMA NEXT','SMK'):
  assert forbidden not in engine
 assert 'sheet_view.rightToLeft=True' in engine and "w:bidiVisual" in engine
 assert 'data=[list(reversed(row)) for row in data]' in engine

def test_design_system_has_semantic_sections_and_shared_components():
 tokens=(ROOT/'design_system/static/design_system/css/tokens.css').read_text()
 app=(ROOT/'design_system/static/design_system/css/app.css').read_text()
 for section in ('dashboard','spaces','contracts','appraisals','auctions','utilities','workflows','documents','alerts','reports','users'):
  assert f'--section-{section}' in tokens and f'.section-{section}' in tokens
 for component in ('.filter-panel','.account-menu','.tabs','.empty','.badge','.button.compact','.kpis','.page-header'):
  assert component in app

def test_authentication_and_filters_do_not_leak_default_ui():
 login=(ROOT/'ui/templates/ui/login.html').read_text();password=(ROOT/'ui/templates/ui/password_change.html').read_text();forms=(ROOT/'ui/forms.py').read_text();spaces=(ROOT/'ui/templates/ui/space_list.html').read_text()
 assert 'form.as_div' not in login+password
 assert all(label in login+password+forms for label in ('نام کاربری','گذرواژه','گذرواژه فعلی','گذرواژه جدید','تکرار گذرواژه جدید'))
 assert '<select name="region_id" multiple' not in spaces and '<select name="center_id" multiple' not in spaces
 assert 'فیلترهای ذخیره‌شده' in spaces and 'ذخیره فیلتر جاری' in spaces

def test_templates_do_not_define_ad_hoc_visual_css():
 for path in (ROOT/'ui/templates').rglob('*.html'):
  text=path.read_text();assert '<style' not in text and ' style=' not in text


def test_header_and_dossier_navigation_geometry_contracts():
 app=(ROOT/'design_system/static/design_system/css/app.css').read_text()
 base=(ROOT/'ui/templates/ui/base.html').read_text()
 for contract in ('grid-template-areas:"brand nav account"','justify-content:center','align-items:center','flex-wrap:nowrap'):
  assert contract in app
 assert base.index('class="brand-shell"') < base.index('class="topnav"') < base.index('class="account"')
 assert '.tabs{display:flex;direction:rtl;justify-content:center;align-items:center;flex-wrap:nowrap' in app

def test_dossier_is_read_only_and_operations_use_shared_specialist_workspace():
 dossier=(ROOT/'ui/templates/ui/space_detail.html').read_text()
 for endpoint in ('add-contract','add-appraisal','add-utility','upload-document','add-movement','add-alert','workflow-create'):
  assert f"url '{endpoint}'" not in dossier
 assert "url 'operation-create'" in dossier
 operation=(ROOT/'ui/templates/ui/operation_form.html').read_text()
 assert '<style' not in operation and ' style=' not in operation
 for action in ('contract','appraisal','document','utility','movement','workflow','alert','beneficiary'):
  assert f"action == '{action}'" in operation
