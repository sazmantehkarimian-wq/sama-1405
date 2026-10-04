from pathlib import Path
import pytest
from django.contrib.auth import get_user_model
from domains.properties.models import Region, Center, CommercialSpace

@pytest.mark.django_db
def test_regions_workspace_live_context_and_no_special_duplicate(client):
 user=get_user_model().objects.create_user('visual',password='x');client.force_login(user)
 region=Region.objects.create(code='6',name='منطقه ۶')
 regular=Center.objects.create(name='مرکز عادی',region=region)
 special=Center.objects.create(name='مرکز خاص',region=region,is_special=True)
 CommercialSpace.objects.create(code='1',name='عادی',status='ACTIVE',region=region,center=regular,source_row=1,source_classification='authority')
 CommercialSpace.objects.create(code='2',name='خاص',status='ACTIVE',region=region,center=special,source_row=2,source_classification='authority')
 assert client.get('/regions/').status_code==200
 regular_page=client.get(f'/regions/{region.pk}/').content.decode()
 special_page=client.get(f'/regions/special/{special.pk}/').content.decode()
 assert 'عادی' in regular_page and 'خاص' not in regular_page
 assert 'خاص' in special_page and 'عادی' not in special_page

def test_frozen_templates_have_no_inline_style_or_hex():
 templates=Path('ui/templates').rglob('*.html')
 bad=[]
 for path in templates:
  text=path.read_text()
  if 'style=' in text or '#' in text and ('href="#' not in text): bad.append(str(path))
 assert not bad

def test_picker_has_complete_single_select_close_contract():
 script=Path('design_system/static/design_system/js/app.js').read_text()
 assert "item.addEventListener('click'" in script
 assert "event.key==='Escape'" in script
 assert "!picker.contains(event.target)" in script
 assert "aria-expanded','false'" in script
