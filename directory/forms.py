from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.forms import SetPasswordForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from dal import forward

from common.form.widgets import ModelSelect2ForwardExtras
from users.forms import UserCreationForm
from .models import *


def _helper():
    helper = FormHelper()
    helper.form_tag = False
    helper.include_media = False
    return helper


class OfficeForm(forms.ModelForm):
    """Форма добавления/редактирования должности"""
    class Meta:
        model = Office
        fields = [
            's_district',
            's_office_type',
            'office_name',
            'phone_number1',
            'phone_number2',
            'e_mail',
            'address_actual',
            'address_legal',
            ]
        widgets = {
            's_district': ModelSelect2ForwardExtras(
                url='directory:autocomplete_district', attrs={ 'data-theme': 'bootstrap-5' }),
            'phone_number1': forms.TextInput(attrs={'data-inputmask': "'mask': '+7 999 999-99-99'"}),
            'phone_number2': forms.TextInput(attrs={'data-inputmask': "'mask': '+7 999 999-99-99'"}),
            'address_actual': forms.Textarea(attrs={ 'rows': 1, 'data-height-auto': True }),
            'address_legal': forms.Textarea(attrs={ 'rows': 1, 'data-height-auto': True }),
            }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                's_district',
                's_office_type',
                'office_name',
                'address_actual',
                'address_legal',
                Row(
                    Column('phone_number1', css_class='col-4'),
                    Column('phone_number2', css_class='col-4'),
                    Column('e_mail', css_class='col-4')
                ),
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                ),
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit: 
            obj.save()
        return obj


class EmployeeAddForm(forms.ModelForm):
    """Форма добавления сотрудника"""
    username = forms.CharField(label=_('Логин'))
    password1 = forms.CharField(label=_('Пароль'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label=_('Повтор пароля'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    
    class Meta:
        model = Employee
        fields = [
            's_office',
            'employee_name', 
            'phone_number',
            'e_mail',
            's_role', 
            'username', 
            'password1', 'password2', 
            'is_active'
            ]
        widgets = {
            's_office': ModelSelect2ForwardExtras(url='directory:autocomplete_office', attrs={ 'data-theme': 'bootstrap-5' }),
            'phone_number': forms.TextInput(attrs={'data-inputmask': "'mask': '+7 999 999-99-99'"}),
            }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                's_office',
                'employee_name', 
                Row(Column('phone_number'), Column('e_mail')), 
                Row(Column('username'), Column('s_role')), 
                Row(Column('password1'), Column('password2')), 
                'is_active',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )

    def is_valid(self):
        if super().is_valid():
            self.user_form = UserCreationForm(self.data)
            if not self.user_form.is_valid():
                for field, error in self.user_form.errors.items():
                    self.add_error(field, error)
        return self.is_bound and not self.errors
    
    def save(self, commit=True):
        with transaction.atomic():
            employee = super().save(commit=False)
            employee.user = self.user_form.save()
            if commit: 
                employee.save()
            return employee
        

class EmployeeChangeForm(forms.ModelForm):
    """Форма редактирования профиля сотрудника"""
    class Meta:
        model = Employee
        fields = [
            's_office',
            'employee_name', 
            'phone_number',
            'e_mail',
            's_role', 
            'is_active',
            ]
        widgets = {
            's_office': ModelSelect2ForwardExtras(url='directory:autocomplete_office', attrs={ 'data-theme': 'bootstrap-5' }),
            'phone_number': forms.TextInput(attrs={'data-inputmask': "'mask': '+7 999 999-99-99'"}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                's_office',
                'employee_name', 
                Row(Column('phone_number'), Column('e_mail')), 
                Row(Column('s_role', css_class='col-6')), 
                'is_active',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )


class PasswordChangeForm(SetPasswordForm):
    """Форма смены пароля пользователя без ввода старого пароля"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, user=kwargs.pop('user'), **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                'new_password1',
                'new_password2',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )


class MaterialForm(forms.ModelForm):
    """Форма добавления/редактирования материала"""
    class Meta:
        model = Material
        fields = [
            'material_code',
            'material_name',
            's_unit_measure',
            'cost_value',
            'labor_cost',
            'cost_work'
            ]
        widgets = {
            's_unit_measure': ModelSelect2ForwardExtras(
                url='directory:autocomplete_unit_measure', attrs={ 'data-theme': 'bootstrap-5' }),
            'material_name': forms.Textarea(attrs={ 'rows': 2, 'data-height-auto': True })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                'material_code',
                'material_name',
                's_unit_measure',
                'cost_value',
                'labor_cost',
                'cost_work',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit: 
            obj.save()
        return obj
    

class WorkForm(forms.ModelForm):
    """Форма добавления/редактирования должности"""
    class Meta:
        model = Work
        fields = [
            'work_code',
            'work_name'
            ]
        widgets = {
            'work_name': forms.Textarea(attrs={ 'rows': 2, 'data-height-auto': True })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                'work_code',
                'work_name',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit: 
            obj.save()
        return obj