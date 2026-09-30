import re
import jdatetime
DATE_RE=re.compile(r'^(13|14)\d{2}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$')
def normalize_jalali(value):
 if value in (None,''): return ''
 text=str(value).strip().replace('-','/').replace('.','/')
 text=text.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789'))
 parts=text.split('/')
 if len(parts)==3: text='/'.join([parts[0].zfill(4),parts[1].zfill(2),parts[2].zfill(2)])
 if not DATE_RE.match(text): raise ValueError(f'Invalid Jalali date: {value}')
 y,m,d=map(int,text.split('/')); jdatetime.date(y,m,d)
 return text
def today_jalali(): return jdatetime.date.today().strftime('%Y/%m/%d')
