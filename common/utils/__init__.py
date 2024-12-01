import datetime

from django.db import models
from django.conf import settings


def get_count_per_page(request):
    key = getattr(settings, 'PAGINATOR_COUNT_PER_PAGE_KEY', 'count_per_page')
    count_per_page = request.GET.get(key)
    if count_per_page:
        request.session[key] = int(count_per_page)
    if not key in request.session:
        request.session[key] = int(getattr(settings, 'PAGINATOR_COUNT_PER_PAGE', 20))
    return request.session[key]
    

def has_related_object(obj, related_name):
    return hasattr(obj, related_name) and getattr(obj, related_name) is not None


def get_pk_or_default(param, default):
    if isinstance(param, models.Model):
        return param.pk
    elif not param:
        return default
    return param


def get_week_dates(base_date, start_day, end_day=None):
    """
    Возвращает всю неделю дат на основе заданной даты, ограниченной start_day и end_day.
    Если значение end_day равно None, вернет только start_day.
    """
    monday = base_date - datetime.timedelta(days=base_date.isoweekday() - 1)
    week_dates = [monday + datetime.timedelta(days=i) for i in range(7)]
    return week_dates[start_day - 1:end_day or start_day]


def get_dates_in_range(start_date, end_date):
    """Возвращает все даты в указанном диапазоне"""
    return [(start_date + datetime.timedelta(days=x)) for x in range(0, (end_date - start_date).days + 1)]


def get_times_in_range(start_time, end_time, interval):
    """Возвращает все времена в указанном диапазоне времен суток с указанным интервалом"""
    start_time = datetime.timedelta(hours=start_time.hour , minutes=start_time.minute)
    end_time = datetime.timedelta(hours=end_time.hour , minutes=end_time.minute)
    times = []
    time = start_time
    while time <= end_time:
        times.append(datetime.datetime.strptime(str(time), "%H:%M:%S").time())
        time = time + datetime.timedelta(minutes=int(interval))
    return times


def get_yesterday(date=None):
    if date is None:
        date = datetime.date.today()
    return (date - datetime.timedelta(days=1))

def get_prev_month_start_date():
    """Возвращает дату начала предыдущего месяца"""
    return get_prev_month_end_date().replace(day=1)


def get_prev_month_end_date():
    """Возвращает дату конца предыдущего месяца"""
    return datetime.date.today().replace(day=1) - datetime.timedelta(days=1)


def add_years(d, years):
    """Добавляет к указанной дате указанные года и возвращает ответ"""
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))
        

def pluralize_ru(value, arg):
    """
    Аналог pluralize для русского языка, позволяющий дописывать к числу заданное слово в нужном падеже
    Пример использования: pluralize_ru(3, 'день,дня,дней') [1 день, 2 дня, 10 дней]
    """
    if value and arg:
        args = arg.split(",")
        number = abs(int(value))
        a = number % 10
        b = number % 100
        if (a == 1) and (b != 11):
            return args[0]
        elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
            return args[1]
        else:
            return args[2]
        

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip