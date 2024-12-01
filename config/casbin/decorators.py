from functools import wraps

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from . import check_str_perm


def check_perm(perm):
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if not check_str_perm(request.user, perm):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': _('Доступ запрещен')})
                else:
                    raise PermissionDenied
            return function(request, *args, **kwargs)
        return wrap
    return decorator