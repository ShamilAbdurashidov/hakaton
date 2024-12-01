from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import ProtectedError, RestrictedError


def deletion_error_capture(function):
    '''
    Перехватывает ошибку удаления объекта 
    '''
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except (ProtectedError, RestrictedError) as e:
            err_msg = _('Удаление невозможно, имеются зависимые связи')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': err_msg})
            messages.warning(request, err_msg)
            return redirect(request.META.get('HTTP_REFERER'))
    return wrap