from openpyxl.styles import NamedStyle, Alignment, Side, Border, Font, PatternFill
from copy import copy


data_style = NamedStyle(name="data")
data_style.font = Font(name='Times New Roman', size=9, bold=False)
data_style.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
data_style.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

head_style = copy(data_style)
head_style.name = 'head'
head_style.font = Font(name='Times New Roman', size=10, bold=True)
head_style.fill = PatternFill("solid", fgColor="00b7dee8")