import re
import pathlib
import base64
import os

from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.utils import pluralize_ru


User = get_user_model()
register = template.Library()


@register.filter()
def level_prefix(value, level):
    """Добавляет перед начение префикс соответствующий уровню"""
    prefix = '&nbsp; ' * level * 3
    return mark_safe(f'{prefix} {value}')


@register.filter()
def pdf_local_styles(styles):
    """Добавляет к параметру базовый полный путь папки стилей"""
    return os.path.join(settings.BASE_DIR, 'storage', 'static', styles)


@register.filter()
def pdf_static_image(image):
    """Кодирует изображение в base64"""
    with open(os.path.join(settings.BASE_DIR, 'storage', 'static', image), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    

@register.filter()
def pdf_media_image(image):
    """Кодирует изображение в base64"""
    with open(os.path.join(settings.BASE_DIR, 'storage', 'media', image), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


@register.filter()
def add_btn(value):
    return mark_safe('<button class="btn btn-success px-3"><i class="bi bi-plus-lg"></i> %s</button>' % value)

@register.filter()
def change_btn(value):
    return mark_safe('<button class="btn btn-primary px-3"><i class="bi bi-pencil me-1"></i> %s</button>' % value)


@register.filter()
def del_btn(value):
    return mark_safe('<button class="btn btn-danger px-3"><i class="bi bi-trash me-1"></i> %s</button>' % value)


@register.filter()
def stylize_count(value, alert=False):
    """Стилизация цифр указывающих на количество"""
    ai = ' <i class="bi bi-exclamation-triangle text-danger"></i>'
    if value and isinstance(value, int) and value > 0: 
        return mark_safe('<span class="small">(%s)</span>' % value)
    return mark_safe('<span class="fw-light small">(%s)%s</span>' % (value, ai if alert else ''))


@register.filter()
def file_icon(filename):
    """Выводит иконку файла соответствующий расширению"""
    if filename:
        ext = pathlib.Path(filename).suffix
        if ext:
            ext = 'jpg' if ext.lower()[1:] == 'jpeg' else ext.lower()[1:]
            return mark_safe('<i class="bi bi-filetype-%s me-1 text-dark bold"></i>' % ext)
    return filename


@register.filter()
def prepend_filetype_icon(filename):
    """Перед названием, вместе с ним, выводит иконку файла соответствующий расширению"""
    if filename:
        ext = pathlib.Path(filename).suffix
        if ext:
            ext = 'jpg' if ext.lower()[1:] == 'jpeg' else ext.lower()[1:]
            return mark_safe('<i class="bi bi-filetype-%s me-1"></i>%s' % (ext, filename))
    return mark_safe('<i bi bi-file-earmark me-1"></i>%s' % (ext, filename))


@register.filter()
def action_icon(action):
    """Возвращает код иконки указанного строкой действия"""
    action_icons = {
        'ФИЛЬТР': '<span class="text-nowrap"><i class="bi bi-sliders"></i> Фильтр</span>',
        'ДОБАВИТЬ': '<span class="text-nowrap"><i class="bi bi-plus-circle"></i> Добавить</span>',
        'ДОБ.': '<span class="text-nowrap"><i class="bi bi-plus-lg"></i></span>',
        'ИЗМЕНИТЬ': '<i class="bi bi-pencil"></i>',
        'УДАЛИТЬ': '<i class="bi bi-x-lg"></i>',
        'ОБНОВИТЬ': '<i class="bi bi-arrow-clockwise"></i>',
        }
    if isinstance(action, str):
        if action.upper() in action_icons:
            return mark_safe(action_icons[action.upper()])
    return action


@register.filter()
def bool_show(value):
    """Визуализация логического значения текстом"""
    if value == None:
        return mark_safe('<span class="badge bg-warning text-expressive-white">'+_('НЕИЗВЕСТНО')+'</span>')
    if (not value is None) and isinstance(value, bool):
        if value: 
            return mark_safe('<span class="badge bg-success">'+_('ДА')+'</span>')
        else: 
            return mark_safe('<span class="badge bg-danger">'+_('НЕТ')+'</span>')
    return value


@register.filter()
def bool_icon(value):
    """Визуализация логического значения иконками"""
    if (not value is None) and isinstance(value, bool):
        if value: 
            return mark_safe('<i class="bi-check-circle-fill text-success"></i>')
        else: 
            return mark_safe('<i class="bi-x-circle-fill text-danger"></i>')
    return value


@register.filter()
def highlight(text, search):
    """Выделение цветом найденной подстроки"""
    if search:
        rgx = re.compile(re.escape(search), re.IGNORECASE)
        return mark_safe(
            rgx.sub(
                lambda m: '<span style="background:#ffffbb">{}</span>'.format(m.group()),
                str(text)
            )
        )
    return text


@register.filter()
def filter_none(value):
    return '' if value == None else value


@register.filter()
def calc_total(arr, key):
    """Подсчитывает сумму значений указанного ключа в массиве словарей"""
    result = 0
    for row in arr:
        if (key in row) and row[key]:
            result = result + row[key]
    return result


@register.filter()
def lookup(d, key):
    return d[key]


@register.filter()
def plural(val, data):
    if val and data:
        return "%s %s" % (val, pluralize_ru(val, data))
