from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from common.utils import get_count_per_page
from common.decorators import deletion_error_capture
from directory.forms import EmployeeAddForm, EmployeeChangeForm, PasswordChangeForm
from directory.filters import EmployeeFilterForm
from directory.models import Employee


@login_required
def employees(request):
    """Каркас страницы"""
    return render(request, 'directory/employees/employees.html', {
        'ff': EmployeeFilterForm(request.GET),
        'page_title': _('Пользователи')
        })


@login_required
def employees_listing(request):
    """Ajax. Список"""
    ff = EmployeeFilterForm(request.GET)
    paginator = Paginator(ff.qs, get_count_per_page(request=request))
    return render(request, 'directory/employees/employees_listing.html', {
        'data': paginator.get_page(request.GET.get('page')),
        'ff': ff,
        'count': ff.qs.count()
        })


@login_required
def employees_add(request):
    """Ajax. Добавление"""
    if request.method == 'POST':
        form = EmployeeAddForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return employees_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })  
    return render(request, 'directory/employees/employees_add.html', { 'form': EmployeeAddForm(user=request.user) })


@login_required
def employees_change(request, employee_pk):
    """Ajax. Редактирование"""
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == 'POST':
        form = EmployeeChangeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return employees_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/employees/employees_change.html', {
        'form': EmployeeChangeForm(instance=employee),
        'employee': employee
        })


@login_required
def employees_change_password(request, employee_pk):
    """Ajax. Смена пароля"""
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, user=employee.user)
        if form.is_valid():
            form.save()
            return employees_listing(request=request)
        return JsonResponse({ 'success': False, 'errors': form.errors })
    return render(request, 'directory/employees/employees_change_password.html', {
        'form': PasswordChangeForm(user=employee),
        'employee': employee
        })


@login_required
@deletion_error_capture
def employees_delete_complete(request, employee_pk):
    """Ajax. Удаление"""
    employee = get_object_or_404(Employee, pk=employee_pk)
    employee.delete()
    return employees_listing(request=request)