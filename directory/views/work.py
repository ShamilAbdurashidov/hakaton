from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.forms import WorkForm
from directory.filters import WorkFilterForm
from directory.models import Work


@login_required
def work(request):
    """Каркас страницы"""
    return render(request, 'directory/work/work.html', {
        'ff': WorkFilterForm(),
        'page_title': _('Работы')
        })


@login_required
def work_listing(request):
    """Ajax. Список"""
    ff = WorkFilterForm(request.GET)
    paginator = Paginator(ff.qs, get_count_per_page(request=request))
    return render(request, 'directory/work/work_listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'ff': ff,
        'count': ff.qs.count()
        })


@login_required
def work_add(request):
    """Ajax. Добавление"""
    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            form.save()
            return work_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/work/work_add.html', { 'form': WorkForm() })


@login_required
def work_change(request, work_pk):
    """Ajax. Редактирование"""
    w = get_object_or_404(Work, pk=work_pk)
    if request.method == 'POST':
        form = WorkForm(request.POST, instance=w)
        if form.is_valid():
            form.save()
            return work_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/work/work_change.html', {
        'form': WorkForm(instance=w),
        'w': w
        })


@login_required
@deletion_error_capture
def work_delete_complete(request, work_pk):
    """Ajax. Удаление"""
    w = get_object_or_404(Work, pk=work_pk)
    w.delete()
    return work_listing(request=request)