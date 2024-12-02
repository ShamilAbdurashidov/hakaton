from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import F, DecimalField
from django.db.models.functions import Coalesce    

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.models import Task, TaskMaterial
from tasks.forms import TaskMaterialForm


@login_required
def task_material_listing(request, task_pk):
    """Ajax. Список"""
    task = get_object_or_404(Task, pk=task_pk)
    data = (
        task.task_material_list
        .annotate(
            unit_measure=F('s_material__s_unit_measure__unit_name'),
            m_cost_value=F('s_material__cost_value'),
            cost_value_total=Coalesce(F('material_count'), 0, output_field=DecimalField()) * F('s_material__cost_value'),
            m_cost_work=F('s_material__cost_work'),
            cost_work_total=Coalesce(F('s_material__cost_work'), 0, output_field=DecimalField()) * Coalesce(F('s_material__labor_cost'), 0, output_field=DecimalField())
            )
        .select_related()
        )
    paginator = Paginator(data, get_count_per_page(request=request))
    return render(request, 'tasks/task_material/task_material_listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'count': data.count(),
        'task': task
        })


@login_required
def task_material_add(request, task_pk):
    """Ajax. Добавление"""
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = TaskMaterialForm(request.POST)
        if form.is_valid():
            form.save(task=task)
            return task_material_listing(request=request, task_pk=task_pk)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'tasks/task_material/task_material_add.html', { 
        'form': TaskMaterialForm(),
        'task': task
        })


@login_required
def task_material_change(request, task_material_pk):
    """Ajax. Редактирование"""
    m = get_object_or_404(TaskMaterial, pk=task_material_pk)
    task = m.d_task
    if request.method == 'POST':
        form = TaskMaterialForm(request.POST, instance=m)
        if form.is_valid():
            form.save(task=task)
            return task_material_listing(request=request, task_pk=task.pk)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'tasks/task_material/task_material_change.html', {
        'form': TaskMaterialForm(instance=m),
        'm': m,
        'task': task
        })


@login_required
@deletion_error_capture
def task_material_delete_complete(request, task_material_pk):
    """Ajax. Удаление"""
    m = get_object_or_404(TaskMaterial, pk=task_material_pk)
    task = m.d_task
    m.delete()
    return task_material_listing(request=request, task_pk=task.pk)