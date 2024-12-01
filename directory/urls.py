from django.urls import path
from directory import views

app_name = 'directory'

urlpatterns = [
    path('autocomplete/office', views.OfficeAutocomplete.as_view(), name='autocomplete_office'),
    path('autocomplete/employee', views.EmployeeAutocomplete.as_view(), name='autocomplete_employee'),
    path('autocomplete/district', views.DistrictAutocomplete.as_view(), name='autocomplete_district'),
    path('autocomplete/unit_measure', views.UnitMeasureAutocomplete.as_view(), name='autocomplete_unit_measure'),
    path('autocomplete/task', views.TaskAutocomplete.as_view(), name='autocomplete_task'),
    path('autocomplete/work', views.WorkAutocomplete.as_view(), name='autocomplete_work'),
    path('autocomplete/material', views.MaterialAutocomplete.as_view(), name='autocomplete_material'),

    path('office', views.office, name='office'),
    path('office/listing', views.office_listing, name='office_listing'),
    path('office/add', views.office_add, name='office_add'),
    path('office/<int:office_pk>/change', views.office_change, name='office_change'),
    path('office/<int:office_pk>/delete_complete', views.office_delete_complete, name='office_delete_complete'),

    path('employees', views.employees, name='employees'),
    path('employees/listing', views.employees_listing, name='employees_listing'),
    path('employees/add', views.employees_add, name='employees_add'),
    path('employees/<int:employee_pk>/change', views.employees_change, name='employees_change'),
    path('employees/<int:employee_pk>/change_password', views.employees_change_password, name='employees_change_password'),
    path('employees/<int:employee_pk>/delete_complete', views.employees_delete_complete, name='employees_delete_complete'),

    path('material', views.material, name='material'),
    path('material/listing', views.material_listing, name='material_listing'),
    path('material/add', views.material_add, name='material_add'),
    path('material/<int:material_pk>/change', views.material_change, name='material_change'),
    path('material/<int:material_pk>/delete_complete', views.material_delete_complete, name='material_delete_complete'),
    
    path('work', views.work, name='work'),
    path('work/listing', views.work_listing, name='work_listing'),
    path('work/add', views.work_add, name='work_add'),
    path('work/<int:work_pk>/change', views.work_change, name='work_change'),
    path('work/<int:work_pk>/delete_complete', views.work_delete_complete, name='work_delete_complete'),
    
]