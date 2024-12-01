from django.db.models import Q, OuterRef, Exists

from dal import autocomplete
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView

from directory.models import District, Office, Employee, UnitMeasure, Task, Work, Material


class TaskAutocomplete(Select2ViewMixin, BaseQuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Task.objects.none()
        qs = Task.objects.all()

        self_pk = self.forwarded.get('self')
        exclude_children = self.forwarded.get('exclude_children')
        if self_pk and exclude_children:
            current = Task.objects.get(pk=self_pk)
            qs = qs.exclude(pk__in=[o.pk for o in current.get_descendants(include_self=True)])

        if self.q:
            qs = qs.filter(task_name__icontains=self.q)

        return qs
    

    def get_results(self, context):
        return [
            {
                'id': self.get_result_value(result),
                'text': self.get_result_label(result),
                'selected_text': self.get_selected_result_label(result),
            } for result in context['object_list']
        ]
    
    def get_result_label(self, item):
        return str(item)

    def get_selected_result_label(self, item):
        return str(item)
    

class WorkAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Work.objects.none()
        qs = Work.objects.all()
        if self.q:
            qs = qs.filter(work_code__icontains=self.q, work_name__icontains=self.q)
        return qs
    
class MaterialAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Material.objects.none()
        qs = Material.objects.all()
        if self.q:
            qs = qs.filter(material_code__icontains=self.q, material_name__icontains=self.q)
        return qs


class DistrictAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return District.objects.none()
        qs = District.objects.all()
        if self.q:
            qs = qs.filter(district_name__icontains=self.q)
        return qs
    

class UnitMeasureAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return UnitMeasure.objects.none()
        qs = UnitMeasure.objects.all()
        if self.q:
            qs = qs.filter(unit_name__icontains=self.q)
        return qs
    

class OfficeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Office.objects.none()
        
        qs = Office.objects.all()
        
        s_office_type = self.forwarded.get('s_office_type')
        if s_office_type:
            qs = qs.filter(s_office_type=s_office_type)

        if self.q:
            qs = qs.filter(office_name__icontains=self.q)
        return qs


class EmployeeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Employee.objects.none()
        qs = Employee.objects.all()
        
        is_active = self.forwarded.get('is_active')
        if is_active:
            qs = qs.filter(is_active=bool(is_active))

        if self.q:
            qs = qs.filter(
                Q(employee_name__icontains=self.q)
                | Q(phone_number__icontains=self.q)
                | Q(user__username__icontains=self.q)
                )
        return qs
