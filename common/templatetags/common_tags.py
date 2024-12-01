from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from .breadcrumb_tag import Breadcrumbs


register = template.Library()


@register.simple_tag(takes_context=True)
def model_parents_pathway(context, current):
    """Выстраивает путь предков от текущего и наверх"""
    parts = []
    query = context['request'].GET.copy()
    while(current):
        query['parent'] = current.pk
        parts.append(f'<li class="breadcrumb-item small"><a href="?{query.urlencode()}">{str(current)}</a></li>' )
        current = current.parent
    if 'parent' in query:
        del query['parent']
    parts.append(f'<li class="breadcrumb-item small"><a href="?{query.urlencode()}">Все</a></li>' )
    return mark_safe(''.join(reversed(parts)))


@register.simple_tag(takes_context=True)
def url_qs(context, **kwargs):
    query = context['request'].GET.copy()
    for key in kwargs:
        if key in query:
            query.pop(key)
    query.pop('_', None)
    query.update(kwargs)
    return query.urlencode()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.update(kwargs)
    return query.urlencode()


@register.simple_tag()
def page_range(objects):
    c = 5
    if objects.paginator.num_pages <= 2 * c:
        return objects.paginator.page_range
    if objects.number <= c + 1:
        n = range(1, c * 2 + 2)
    elif objects.number > objects.paginator.num_pages - (c + 1):
        n = range(objects.paginator.num_pages - 2 * c, objects.paginator.num_pages + 1)
    else:
        n = range(objects.number - c, objects.number + (c + 1))
    return list(n)


@register.simple_tag(takes_context=True)
def per_page_changer(context, base_url, counts, target=None):
    key = getattr(settings, 'PAGINATOR_COUNT_PER_PAGE_KEY', 'count_per_page')
    data_target = 'data-target="%s"' % target if target else ''
    changer = '<select class="count_per_page form-select form-select-sm" style="width:70px" %s>' % data_target
    changer += '<option value="">---</option>'
    for count in counts.split(' '):
        url = "%s?%s" % (base_url, url_replace(context, count_per_page=count))
        selected = ''
        if (key in context['request'].session) and (context['request'].session[key] == int(count)):
            selected = 'selected=selected'
        changer += '<option value="%s" %s>%s</option>' % (url, selected, count)
    changer += '</select>'
    return mark_safe(changer)