from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.models import Task
from tasks.forms import TaskForm
from tasks.filters import TaskFilterForm


@login_required
def home(request):
    """Каркас страницы"""
    parent_id = request.GET.get('parent')
    return render(request, 'tasks/home.html', {
        'ff': TaskFilterForm(initial={ 'parent': parent_id }),
        'parent': Task.objects.get(pk=parent_id) if parent_id else None,
        'page_title': _('Задачи')
        })


@login_required
def listing(request):
    """Ajax. Список"""
    ff = TaskFilterForm(request.GET)
    paginator = Paginator(ff.qs, get_count_per_page(request=request))
    return render(request, 'tasks/listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'ff': ff,
        'count': ff.qs.count()
        })


@login_required
def add(request):
    """Ajax. Добавление"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'tasks/add.html', { 
        'form': TaskForm() 
        })


@login_required
def change(request, task_pk):
    """Ajax. Редактирование"""
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'tasks/change.html', {
        'form': TaskForm(instance=task),
        'task': task
        })


@login_required
@deletion_error_capture
def delete_complete(request, task_pk):
    """Ajax. Удаление"""
    task = get_object_or_404(Task, pk=task_pk)
    task.delete()
    return listing(request=request)