from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Exists, F, OuterRef
from django.utils.functional import cached_property

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from dal import forward 

from common.form.widgets import ModelSelect2ForwardExtras
from directory.models import Task


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


class TaskFilterForm(forms.Form):
    """Форма-фильтр на странице Задач"""
    q = _q_field(_('Поиск по наименованию'))

    parent = forms.ModelChoiceField(queryset=Task.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Task.objects.all()
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
            parent = self.cleaned_data['parent']
            if parent:
                self.queryset = self.queryset.filter(parent=parent)
            else:
                self.queryset = self.queryset.filter(parent__isnull=True)

            q = self.cleaned_data['q']
            if q:
                self.queryset = self.queryset.filter(task_name__icontains=q)

            return (self.queryset
                .annotate(
                    has_children=Exists(Task.objects.filter(parent=OuterRef('pk'))),
                    employee_name=F('s_employee__employee_name'),
                    work_name=F('s_work__work_name')
                    )
                .order_by('task_name')
                )
        
        return self.queryset.none()