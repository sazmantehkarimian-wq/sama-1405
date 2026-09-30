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
