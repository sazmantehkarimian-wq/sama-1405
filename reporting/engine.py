"""Single official output engine for filtered canonical querysets."""
from io import BytesIO
from pathlib import Path
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment, Border, Side, Font
from openpyxl.utils import get_column_letter
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import arabic_reshaper
from bidi.algorithm import get_display

HEADERS=['سازمان فرهنگی هنری شهرداری تهران','مدیریت اقتصادی و املاک','اداره املاک و مستغلات']
FIELD_MAP={
 'code':('کد فضا',lambda s:s.code),'name':('نام فضا / مرکز',lambda s:s.name or '—'),
 'status':('وضعیت',lambda s:s.get_status_display()),'region':('منطقه',lambda s:s.region.name if s.region else '—'),
 'current_usage':('کاربری',lambda s:s.current_usage or '—'),'area':('مساحت (مترمربع)',lambda s:s.area if s.area is not None else '—'),
}
DEFAULT_FIELDS=tuple(FIELD_MAP)
BASE=Path(__file__).resolve().parents[1]
LOGO=BASE/'design_system/static/design_system/img/organization-logo.png'
FONT=BASE/'design_system/static/design_system/fonts/Vazirmatn-Regular.ttf'

def columns(selected=None):
 selected=[key for key in (selected or DEFAULT_FIELDS) if key in FIELD_MAP]
 return selected or list(DEFAULT_FIELDS)
def rows(spaces,selected=None):
 keys=columns(selected)
 for s in spaces: yield [FIELD_MAP[key][1](s) for key in keys]
def excel(spaces,blank_columns=(),selected=None):
 keys=columns(selected); wb=Workbook(); ws=wb.active; ws.title='فضاها'; ws.sheet_view.rightToLeft=True
 total=len(keys)+len(blank_columns)
 for line in HEADERS: ws.append([line]); ws.merge_cells(start_row=ws.max_row,start_column=1,end_row=ws.max_row,end_column=total)
 if LOGO.exists():
  logo=ExcelImage(str(LOGO));logo.width=64;logo.height=64;ws.add_image(logo,'A1')
 ws.append([FIELD_MAP[x][0] for x in keys]+list(blank_columns)); header=ws.max_row
 for row in rows(spaces,keys):ws.append(row+['']*len(blank_columns))
 ws.freeze_panes=f'A{header+1}'; ws.auto_filter.ref=f'A{header}:{ws.cell(ws.max_row,total).coordinate}'
 side=Side(style='thin',color='888888')
 for row in ws.iter_rows(min_row=header):
  for c in row:c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True);c.border=Border(left=side,right=side,top=side,bottom=side)
 for c in ws[header]:c.font=Font(name='Vazirmatn',bold=True)
 for col in ws.columns:
  letter=get_column_letter(col[0].column); ws.column_dimensions[letter].width=min(42,max(14,max(len(str(c.value or '')) for c in col)+2))
 out=BytesIO(); wb.save(out); return out.getvalue()

def tabular_excel(title,labels,data):
 """Official Excel 2019-compatible output for typed operational domain reports."""
 wb=Workbook();ws=wb.active;ws.title=str(title)[:31];ws.sheet_view.rightToLeft=True
 total=max(1,len(labels))
 for line in HEADERS:
  ws.append([line]);ws.merge_cells(start_row=ws.max_row,start_column=1,end_row=ws.max_row,end_column=total)
 if LOGO.exists():
  logo=ExcelImage(str(LOGO));logo.width=64;logo.height=64;ws.add_image(logo,'A1')
 ws.append(list(labels));header=ws.max_row
 for values in data:ws.append(list(values))
 ws.freeze_panes=f'A{header+1}';ws.auto_filter.ref=f'A{header}:{ws.cell(max(header,ws.max_row),total).coordinate}'
 side=Side(style='thin',color='888888')
 for row in ws.iter_rows(min_row=header):
  for cell in row:
   cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True);cell.border=Border(left=side,right=side,top=side,bottom=side)
 for cell in ws[header]:cell.font=Font(name='Vazirmatn',bold=True)
 for column in ws.columns:ws.column_dimensions[get_column_letter(column[0].column)].width=min(42,max(14,max(len(str(cell.value or '')) for cell in column)+2))
 out=BytesIO();wb.save(out);return out.getvalue()
def _rtl(paragraph):
 paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
 pPr=paragraph._p.get_or_add_pPr();bidi=OxmlElement('w:bidi');bidi.set(qn('w:val'),'1');pPr.append(bidi)
def docx(spaces,blank_columns=(),selected=None):
 keys=columns(selected); doc=Document();sec=doc.sections[0];sec.orientation=WD_ORIENT.LANDSCAPE;sec.page_width,sec.page_height=sec.page_height,sec.page_width
 header=sec.header.paragraphs[0]
 if LOGO.exists(): header.add_run().add_picture(str(LOGO),width=Mm(18))
 header.add_run('\n'+'\n'.join(HEADERS));_rtl(header)
 table=doc.add_table(rows=1,cols=len(keys)+len(blank_columns));table.style='Table Grid'
 labels=[FIELD_MAP[x][0] for x in keys]+list(blank_columns)
 for i,h in enumerate(labels):table.rows[0].cells[i].text=h;_rtl(table.rows[0].cells[i].paragraphs[0])
 table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
 for row in rows(spaces,keys):
  cells=table.add_row().cells
  for i,v in enumerate(row+['']*len(blank_columns)):cells[i].text=str(v);_rtl(cells[i].paragraphs[0])
 footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
 footer.add_run('صفحه ');field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
 out=BytesIO();doc.save(out);return out.getvalue()
def _fa(value):return get_display(arabic_reshaper.reshape(str(value)))
def pdf(spaces,selected=None,blank_columns=()):
 keys=columns(selected);out=BytesIO();pdfmetrics.registerFont(TTFont('Vazirmatn',str(FONT)))
 doc=SimpleDocTemplate(out,pagesize=landscape(A4),rightMargin=12*mm,leftMargin=12*mm,topMargin=10*mm,bottomMargin=12*mm,title='گزارش رسمی املاک')
 style=ParagraphStyle('fa',fontName='Vazirmatn',fontSize=9,leading=14,alignment=TA_CENTER)
 story=[]
 if LOGO.exists():story.append(Image(str(LOGO),width=18*mm,height=18*mm))
 for line in HEADERS:story.append(Paragraph(_fa(line),style))
 story.append(Spacer(1,5*mm))
 data=[[_fa(FIELD_MAP[x][0]) for x in keys]+[_fa(x) for x in blank_columns]]
 data += [[_fa(v) for v in row]+['']*len(blank_columns) for row in rows(spaces,keys)]
 table=Table(data,repeatRows=1,hAlign='CENTER')
 table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Vazirmatn'),('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.5,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f1edf2')),('LEADING',(0,0),(-1,-1),12)]));story.append(table)
 def numbered_page(canvas,document):
  canvas.saveState();canvas.setFont('Vazirmatn',8);canvas.drawCentredString(landscape(A4)[0]/2,6*mm,_fa(f'صفحه {document.page}'));canvas.restoreState()
 doc.build(story,onFirstPage=numbered_page,onLaterPages=numbered_page);return out.getvalue()
