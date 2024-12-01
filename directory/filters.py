from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Exists, F
from django.utils.functional import cached_property

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from dal import forward 

from common.form.widgets import ModelSelect2ForwardExtras
from directory.models import *


def _helper():
    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.form_show_labels = False
    helper.include_media = False
    return helper

def _q_field(placeholder=None, css_class=''):
    return forms.CharField(widget=forms.TextInput(
        attrs={ 'placeholder': placeholder, 'class': f'form-control {css_class}' }), required=False)

def _office_field(label, required=False, queryset=None, show_label=None, css_class='', forward=None):
    return forms.ModelChoiceField(
        label=label if show_label else '',
        queryset=queryset if queryset else Office.objects.all(), 
        widget=ModelSelect2ForwardExtras(
            url='directory:autocomplete_office', 
            forward=forward if forward else [],
            unselect_if_forward_changed=True,
            attrs={ 'data-theme': 'bootstrap-5', 'data-placeholder': label, 'class': f'form-select {css_class}'}),
        required=required)


class OfficeFilterForm(forms.Form):
    """Форма-фильтр на странице организаций"""
    q = _q_field(_('Поиск по наименованию'))

    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        widget=ModelSelect2ForwardExtras(
            url='directory:autocomplete_district', 
            attrs={ 'data-theme': 'bootstrap-5', 'data-placeholder': _('--- Населенный пункт ---') }),
        required=False)

    office_type = forms.ModelChoiceField(
        empty_label=_('--- Тип организации ---'), queryset=OfficeType.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Office.objects.all()
        self.helper = _helper()
        self.helper.layout = Layout(
            Row(
                Column('q', css_class="col"),
                Column('district', css_class='col-4'),
                Column('office_type', css_class='col-3'),
                Column(Submit('submit', _('Показать'), css_class="btn btn-secondary px-3"), css_class="col-auto")
                )
            )

    @cached_property
    def qs(self):
        if self.is_valid():
            s_office_type = self.cleaned_data['office_type']
            if s_office_type:
                self.queryset = self.queryset.filter(s_office_type=s_office_type)

            s_district = self.cleaned_data['district']
            if s_district:
                self.queryset = self.queryset.filter(s_district=s_district)

            q = self.cleaned_data['q']
            if q:
                self.queryset = self.queryset.filter(office_name__icontains=q)

            return (self.queryset
                    .annotate(district_name=F('s_district__district_name'))
                    .select_related('s_office_type')
                    .order_by('-pk')
                    )
        return self.queryset.none()


class EmployeeFilterForm(forms.Form):
    """Форма-фильтр на странице списка сотрудников"""
    q = _q_field(_('Поиск по ФИО, логину, контактным данным'))
    office = _office_field(_('--- Организация ---'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Employee.objects.all()
        self.helper = _helper()
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='col'),
                Column('office', css_class='col-4'),
                Column(Submit('submit', _('Показать'), css_class="btn btn-secondary px-3"), css_class="col-auto")
                )
            )

    @cached_property
    def qs(self):
        if self.is_valid():
            s_office = self.cleaned_data['office']
            if s_office:
                self.queryset = self.queryset.filter(s_office=s_office)

            q = self.cleaned_data['q']
            if q:
                self.queryset = self.queryset.filter(
                    Q(employee_name__icontains=q) 
                    |  Q(user__username__icontains=q) 
                    |  Q(phone_number__icontains=q) 
                    |  Q(e_mail__icontains=q) 
                    )
                
            return self.queryset.select_related('s_office', 's_role', 'user')
        
        return self.queryset.none()
    

class MaterialFilterForm(forms.Form):
    """Форма-фильтр на странице материалов"""
    q = _q_field(_('Поиск по наименованию и шифру'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Material.objects.all()
        self.helper = _helper()
        self.helper.layout = Layout(
            Row(
                Column('q', css_class="col-5"),
                Column(Submit('submit', _('Показать'), css_class="btn btn-secondary px-3"), css_class="col-auto")
                )
            )

    @cached_property
    def qs(self):
        if self.is_valid():
            q = self.cleaned_data['q']
            if q:
                self.queryset = self.queryset.filter(
                    Q(material_code__icontains=q)
                    & Q(material_name__icontains=q)
                    )
            return self.queryset.select_related('s_unit_measure')
        return self.queryset.none()
    

class WorkFilterForm(forms.Form):
    """Форма-фильтр на странице работ"""
    q = _q_field(_('Поиск по наименованию и шифру'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Work.objects.all()
        self.helper = _helper()
        self.helper.layout = Layout(
            Row(
                Column('q', css_class="col-5"),
                Column(Submit('submit', _('Показать'), css_class="btn btn-secondary px-3"), css_class="col-auto")
                )
            )

    @cached_property
    def qs(self):
        if self.is_valid():
            q = self.cleaned_data['q']
            if q:
                self.queryset = self.queryset.filter(
                    Q(work_code__icontains=q)
                    & Q(work_name__icontains=q)
                    )
            return self.queryset
        return self.queryset.none()