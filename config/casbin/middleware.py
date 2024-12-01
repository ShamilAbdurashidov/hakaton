from django.core.exceptions import PermissionDenied
from django.urls import resolve

from . import check_perm


class CasbinMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.check_permission(request):
            self.require_permission()
        return self.get_response(request)

    def check_permission(self, request):
        url_info = resolve(request.path_info)
        if not url_info.namespace:
            if not url_info.url_name: # media
                return True
            return check_perm(request.user, url_info.url_name, None, request.method) 
        return check_perm(request.user, url_info.namespace, url_info.url_name, request.method)

    def require_permission(self):
        raise PermissionDenied
