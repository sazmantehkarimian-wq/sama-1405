def format_rial(value):
 return 'ثبت نشده' if value is None else f'{int(value):,} ریال'
def display(value,empty='—'):
 return empty if value is None or value=='' else value
