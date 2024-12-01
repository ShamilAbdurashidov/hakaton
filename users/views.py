from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.conf import settings

from users.forms import *


def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return JsonResponse({ 'redirect_url': settings.LOGIN_REDIRECT_URL })
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'users/login.html', { 'form': LoginForm() })


@login_required
def logout(request):
    auth_logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def password_change(request):
    """Ajax. Смена пароля текущего пользователя"""
    if request.method == 'POST':
        form = PassChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return JsonResponse({ 'success': True, 'message': _('Новый пароль успешно установлен') })
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'users/password_change.html', { 'form': PassChangeForm(user=request.user) })