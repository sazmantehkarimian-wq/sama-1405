from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Alignment,Border,Side,Font
from docx import Document
from docx.enum.section import WD_ORIENT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
HEADERS=['سازمان فرهنگی هنری شهرداری تهران','مدیریت اقتصادی و املاک','اداره املاک و مستغلات']
FIELDS=[('code','کد فضا'),('name','نام فضا / مرکز'),('status','وضعیت'),('region','منطقه'),('current_usage','کاربری'),('area','مساحت')]
def rows(spaces):
 for s in spaces: yield [s.code,s.name,s.get_status_display(),s.region.name if s.region else '—',s.current_usage or '—',s.area if s.area is not None else '—']
def excel(spaces,blank_columns=()):
 wb=Workbook(); ws=wb.active; ws.title='فضاها'; ws.sheet_view.rightToLeft=True
 for line in HEADERS: ws.append([line]); ws.merge_cells(start_row=ws.max_row,start_column=1,end_row=ws.max_row,end_column=len(FIELDS)+len(blank_columns))
 ws.append([x[1] for x in FIELDS]+list(blank_columns)); header=ws.max_row
 for row in rows(spaces):ws.append(row+['']*len(blank_columns))
 ws.freeze_panes=f'A{header+1}'; ws.auto_filter.ref=f'A{header}:L{ws.max_row}'
 side=Side(style='thin',color='888888')
 for row in ws.iter_rows(min_row=header):
  for c in row:c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True);c.border=Border(left=side,right=side,top=side,bottom=side)
 for c in ws[header]:c.font=Font(bold=True)
 for col,w in {'A':14,'B':28,'C':16,'D':16,'E':22,'F':14}.items():ws.column_dimensions[col].width=w
 out=BytesIO(); wb.save(out); return out.getvalue()
def docx(spaces,blank_columns=()):
 doc=Document(); sec=doc.sections[0];sec.orientation=WD_ORIENT.LANDSCAPE;sec.page_width,sec.page_height=sec.page_height,sec.page_width
 for line in HEADERS:p=doc.add_paragraph(line);p.alignment=1
 table=doc.add_table(rows=1,cols=len(FIELDS)+len(blank_columns));table.style='Table Grid'
 for i,h in enumerate([x[1] for x in FIELDS]+list(blank_columns)):table.rows[0].cells[i].text=h
 for row in rows(spaces):
  cells=table.add_row().cells
  for i,v in enumerate(row+['']*len(blank_columns)):cells[i].text=str(v)
 out=BytesIO();doc.save(out);return out.getvalue()
def pdf(spaces):
 out=BytesIO(); c=canvas.Canvas(out,pagesize=landscape(A4)); width,height=landscape(A4);y=height-45
 for line in HEADERS:c.drawCentredString(width/2,y,line);y-=18
 for s in spaces:
  if y<40:c.showPage();y=height-40
  c.drawString(35,y,f'{s.code} | {s.name} | {s.get_status_display()}');y-=15
 c.save();return out.getvalue()
