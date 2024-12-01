import xlwt
import copy


# Границы заголовков
hb = xlwt.Borders()
hb.left = xlwt.Borders.MEDIUM
hb.right = xlwt.Borders.MEDIUM
hb.top = xlwt.Borders.MEDIUM
hb.bottom = xlwt.Borders.MEDIUM

# Границы данных
b = xlwt.Borders()
b.left = xlwt.Borders.THIN
b.right = xlwt.Borders.THIN
b.top = xlwt.Borders.THIN
b.bottom = xlwt.Borders.THIN

# Серый фон
gp = xlwt.Pattern()
gp.pattern = xlwt.Pattern.SOLID_PATTERN
gp.pattern_fore_colour = xlwt.Style.colour_map['white']

# Центрирование
cal = xlwt.Alignment()
cal.horz = xlwt.Alignment.HORZ_CENTER
cal.vert = xlwt.Alignment.VERT_CENTER
cal.wrap = 1
cal.shri = 1
cal.inde = 1
cal.merg = 2

title_style = xlwt.XFStyle()
#title_style.font.bold = True
#title_style.font.name = 'Times New Roman'
title_style.font.height = 280
title_style.alignment = cal

head_style = xlwt.XFStyle()
head_style.pattern = gp
head_style.font.bold = True
#head_style.font.name = 'Times New Roman'
#head_style.font.height = 210
head_style.alignment = cal
head_style.borders = hb

h2 = xlwt.XFStyle()
h2.font.bold = True
#h2.font.name = 'Times New Roman'
h2.font.height = 260
h2.alignment = cal

h3 = xlwt.XFStyle()
h3.font.bold = True
#h3.font.name = 'Times New Roman'
h3.font.height = 210
h3.alignment = cal

data_style = xlwt.XFStyle()
#data_style.font.name = 'Times New Roman'
data_style.alignment = cal
data_style.borders = b

small_right_style = xlwt.XFStyle()
small_right_style.font.height = 200
small_right_style.alignment = copy.deepcopy(cal)
small_right_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT

total_style = copy.deepcopy(head_style)
total_style.borders = copy.deepcopy(b)
total_style.borders.top = xlwt.Borders.DOUBLE