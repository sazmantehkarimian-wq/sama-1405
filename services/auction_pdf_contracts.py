import io
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from django.core.exceptions import ValidationError
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


_FONT_NAME = 'SamaVazirmatn'
_FONT_PATH = Path(settings.BASE_DIR) / 'design_system/static/design_system/fonts/Vazirmatn-Regular.ttf'


def _font():
    if _FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_FONT_NAME, str(_FONT_PATH)))
    return _FONT_NAME


def _rtl(value):
    text = str(value or '').strip()
    if not text:
        return ''
    return get_display(arabic_reshaper.reshape(text))


def _overlay_page(page_width, page_height, placements):
    stream=io.BytesIO()
    c=canvas.Canvas(stream,pagesize=(page_width,page_height))
    font=_font()
    for item in placements:
        text=str(item.get('text') or '').strip()
        if not text:
            continue
        x=item['x']; top=item['top']; width=item['width']; height=item.get('height',13); size=item.get('size',7.2)
        y=page_height-top-height+2
        c.setFillColorRGB(1,1,1)
        c.rect(x,y-1,width,height+2,fill=1,stroke=0)
        c.setFillColorRGB(0,0,0)
        c.setFont(font,size)
        shown=_rtl(text)
        while size > 5.2 and pdfmetrics.stringWidth(shown,font,size) > width-2:
            size-=0.3
            c.setFont(font,size)
        c.drawRightString(x+width-1,y+2,shown)
    c.save(); stream.seek(0)
    return PdfReader(stream).pages[0]


def _common_commercial(fields):
    beneficiary=fields.get('_BENEFICIARY') or {}
    contract=fields.get('_CONTRACT') or {}
    winner=fields.get('_WINNER') or {}
    return [
        # Page 1 - only deterministic SAMA-owned data; other blanks intentionally remain blank.
        {'x':493,'top':213,'width':81,'text':fields.get('ORG-REP-NAME')},
        {'x':404,'top':213,'width':76,'text':fields.get('ORG-REP-TITLE')},
        {'x':474,'top':235,'width':101,'text':beneficiary.get('name') or winner.get('name')},
        {'x':424,'top':235,'width':49,'text':beneficiary.get('father_name')},
        {'x':333,'top':235,'width':91,'text':beneficiary.get('birth_certificate_number')},
        {'x':265,'top':235,'width':66,'text':beneficiary.get('birth_date')},
        {'x':130,'top':235,'width':72,'text':beneficiary.get('identity_number')},
        {'x':48,'top':235,'width':80,'text':beneficiary.get('address')},
        {'x':505,'top':255,'width':69,'text':beneficiary.get('phone')},
        {'x':430,'top':255,'width':75,'text':beneficiary.get('mobile')},
        {'x':268,'top':275,'width':61,'text':fields.get('SPACE-001')},
        {'x':165,'top':275,'width':71,'text':fields.get('SPACE-004')},
        {'x':98,'top':275,'width':69,'text':fields.get('SPACE-006')},
        {'x':492,'top':298,'width':82,'text':fields.get('SPACE-005')},
        {'x':414,'top':322,'width':62,'text':contract.get('start_date')},
        {'x':358,'top':322,'width':45,'text':contract.get('end_date')},
        {'x':315,'top':391,'width':56,'text':winner.get('amount') or contract.get('monthly_amount')},
        {'x':143,'top':506,'width':75,'text':fields.get('ORG-008')},
    ]


def _common_cafe(fields):
    beneficiary=fields.get('_BENEFICIARY') or {}
    contract=fields.get('_CONTRACT') or {}
    winner=fields.get('_WINNER') or {}
    return [
        {'x':503,'top':202,'width':78,'text':fields.get('ORG-REP-NAME')},
        {'x':430,'top':202,'width':73,'text':fields.get('ORG-REP-TITLE')},
        {'x':452,'top':223,'width':129,'text':beneficiary.get('name') or winner.get('name')},
        {'x':402,'top':223,'width':48,'text':beneficiary.get('father_name')},
        {'x':298,'top':223,'width':103,'text':beneficiary.get('birth_certificate_number')},
        {'x':228,'top':223,'width':69,'text':beneficiary.get('birth_date')},
        {'x':163,'top':223,'width':63,'text':beneficiary.get('identity_number')},
        {'x':90,'top':223,'width':72,'text':beneficiary.get('address')},
        {'x':505,'top':244,'width':72,'text':beneficiary.get('phone')},
        {'x':431,'top':244,'width':73,'text':beneficiary.get('mobile')},
        {'x':431,'top':263,'width':140,'text':fields.get('SPACE-002')},
        {'x':104,'top':263,'width':88,'text':fields.get('SPACE-006')},
        {'x':478,'top':287,'width':101,'text':fields.get('SPACE-005')},
        {'x':395,'top':310,'width':88,'text':contract.get('start_date')},
        {'x':364,'top':310,'width':34,'text':contract.get('end_date')},
        {'x':83,'top':379,'width':160,'text':winner.get('amount') or contract.get('monthly_amount')},
        {'x':77,'top':577,'width':78,'text':fields.get('ORG-008')},
    ]


def render_contract_pdf(*, source_bytes, family, fields):
    reader=PdfReader(io.BytesIO(source_bytes))
    if not reader.pages:
        raise ValidationError('نمونه قرارداد PDF فاقد صفحه است.')
    writer=PdfWriter()
    placements=_common_cafe(fields) if family == 'CAFE' else _common_commercial(fields)
    for index,page in enumerate(reader.pages):
        if index == 0:
            width=float(page.mediabox.width); height=float(page.mediabox.height)
            overlay=_overlay_page(width,height,placements)
            page.merge_page(overlay)
        writer.add_page(page)
    out=io.BytesIO(); writer.write(out)
    return out.getvalue(), 'pdf'
