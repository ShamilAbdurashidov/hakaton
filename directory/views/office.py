from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.forms import OfficeForm
from directory.filters import OfficeFilterForm
from directory.models import Office


@login_required
def office(request):
    """Каркас страницы"""
    return render(request, 'directory/office/office.html', {
        'ff': OfficeFilterForm(),
        'page_title': _('Организации')
        })


@login_required
def office_listing(request):
    """Ajax. Список"""
    ff = OfficeFilterForm(request.GET)
    paginator = Paginator(ff.qs, get_count_per_page(request=request))
    return render(request, 'directory/office/office_listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'ff': ff,
        'count': ff.qs.count()
        })


@login_required
def office_add(request):
    """Ajax. Добавление"""
    if request.method == 'POST':
        form = OfficeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return office_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/office/office_add.html', { 'form': OfficeForm(user=request.user) })


@login_required
def office_change(request, office_pk):
    """Ajax. Редактирование"""
    obj = get_object_or_404(Office, pk=office_pk)
    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            return office_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/office/office_change.html', {
        'form': OfficeForm(instance=obj, user=request.user),
        'obj': obj
        })


@login_required
@deletion_error_capture
def office_delete_complete(request, office_pk):
    """Ajax. Удаление"""
    obj = get_object_or_404(Office, pk=office_pk)
    obj.delete()
    return office_listing(request=request)