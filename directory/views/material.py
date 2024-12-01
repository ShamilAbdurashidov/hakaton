from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.forms import MaterialForm
from directory.filters import MaterialFilterForm
from directory.models import Material


@login_required
def material(request):
    """Каркас страницы"""
    return render(request, 'directory/material/material.html', {
        'ff': MaterialFilterForm(),
        'page_title': _('Материалы')
        })


@login_required
def material_listing(request):
    """Ajax. Список"""
    ff = MaterialFilterForm(request.GET)
    paginator = Paginator(ff.qs, get_count_per_page(request=request))
    return render(request, 'directory/material/material_listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'ff': ff,
        'count': ff.qs.count()
        })


@login_required
def material_add(request):
    """Ajax. Добавление"""
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return material_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/material/material_add.html', { 'form': MaterialForm() })


@login_required
def material_change(request, material_pk):
    """Ajax. Редактирование"""
    m = get_object_or_404(Material, pk=material_pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=m)
        if form.is_valid():
            form.save()
            return material_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/material/material_change.html', {
        'form': MaterialForm(instance=m),
        'm': m
        })


@login_required
@deletion_error_capture
def material_delete_complete(request, material_pk):
    """Ajax. Удаление"""
    m = get_object_or_404(Material, pk=material_pk)
    m.delete()
    return material_listing(request=request)