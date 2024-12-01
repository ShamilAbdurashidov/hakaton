from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.forms import SetPasswordForm
from django.db import transaction

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from dal import forward

from common.form.widgets import ModelSelect2ForwardExtras, ModelSelect2MultipleForwardExtras
from common.form.formsets import ModelFormSet
from common.form.fields import FormsetField, FormsetFormMixin
from directory.models import Task, TaskMaterial


def _helper():
    helper = FormHelper()
    helper.form_tag = False
    helper.include_media = False
    return helper


class TaskMaterialForm(forms.ModelForm):
    """Форма добавления/редактирования материала к задаче"""
    class Meta:
        model = TaskMaterial
        fields = [
            's_material',
            'material_count',
            'material_cost',
            'labor_cost',
            'work_cost',
            'material_count_fact',
            'material_cost_total',
            'work_cost_total',
            ]
        widgets = {
            's_material': ModelSelect2ForwardExtras(url='directory:autocomplete_material', attrs={ 'data-theme': 'bootstrap-5' }),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                's_material',
                'material_count',
                'material_cost',
                'labor_cost',
                'work_cost',
                'material_count_fact',
                'material_cost_total',
                'work_cost_total',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
        )

    def save(self, task, commit=True):
        obj = super().save(commit=False)
        obj.d_task = self.task
        if commit: 
            obj.save()
        return obj
    

class TaskMaterialSubForm(TaskMaterialForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                's_material',
                'material_count',
                'material_cost',
                'labor_cost',
                'work_cost',
                'material_count_fact',
                'material_cost_total',
                'work_cost_total',
                css_class="subform bg-light shadow-sm border p-3 my-3"
            )
        )


class TaskForm(FormsetFormMixin, forms.ModelForm):
    """Форма добавления/редактирования задачи"""
    class Meta:
        model = Task
        fields = [
            'parent',
            's_employee',
            's_work',
            'task_name',
            'date_start',
            'date_stop',
            'date_fact'
            ]
        widgets = {
            'task_name': forms.Textarea(attrs={ 'rows': 2, 'data-height-auto': True }),
            's_employee': ModelSelect2ForwardExtras(
                url='directory:autocomplete_employee', 
                #forward=[forward.Const('1', 'is_active')],
                attrs={ 'data-theme': 'bootstrap-5' }),
            's_work': ModelSelect2ForwardExtras(
                url='directory:autocomplete_work', attrs={ 'data-theme': 'bootstrap-5' }),
            'date_start': forms.NumberInput(attrs={ 'type': 'date' }),
            'date_stop': forms.NumberInput(attrs={ 'type': 'date' }),
            'date_fact': forms.NumberInput(attrs={ 'type': 'date' })
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['parent'] = forms.ModelChoiceField(
                label=_('Родительская запись'),
                queryset=Task.objects.all(),
                widget=ModelSelect2ForwardExtras(url='directory:autocomplete_task', attrs={ 'data-theme': 'bootstrap-5' }),
                required=False
                )
        else:
            self.fields['parent'] = forms.ModelChoiceField(
                label=_('Родительская запись'),
                queryset=Task.objects.all().exclude(pk__in=[o.pk for o in self.instance.get_descendants(include_self=True)]),
                widget=ModelSelect2ForwardExtras(
                    url='directory:autocomplete_task', 
                    forward=[
                        forward.Const(self.instance.pk, 'self'),
                        forward.Const(True, 'exclude_children')
                        ],
                    unselect_if_forward_changed=True,
                    attrs={ 'data-theme': 'bootstrap-5' }
                    ),
                required=False
                )
            

        task_material_list_formset = forms.modelformset_factory(TaskMaterial, 
            form=TaskMaterialSubForm, formset=ModelFormSet, extra=1, can_delete=True)
        
        if self.instance.pk:
            self.fields['task_material_list'] = FormsetField(task_material_list_formset, 
                form_kwargs={ 'empty_permitted': True },
                formset_queryset=self.instance.task_material_list.all())
            
        else:
            self.fields['task_material_list'] = FormsetField(task_material_list_formset,
                form_kwargs={ 'empty_permitted': True },
                formset_queryset=TaskMaterial.objects.none())
            
            
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                'parent',
                'task_name',
                Row(
                    Column('date_start', css_class='col-4'),
                    Column('date_stop', css_class='col-4'),
                    Column('date_fact', css_class='col-4'),
                ),
                's_employee',
                's_work',
                Div(
                    HTML('''<h5 class="mb-1">Материалы</h5>'''),
                    'task_material_list',
                    css_class="bg-secondary bg-opacity-10 px-4 pt-3 pb-1 mt-4 border shadow shadow-sm"
                ),
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
                
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit: 
            with transaction.atomic():
                #obj.labor_cost = 
                #это поле вычисляется след образом, в таблице s_material есть поле labor_cost его нужно 
                #умножить на Количество(material_count), то что ввели и записать значение.
                #material_cost_total - это material_count*на Стоимость материала - ручной ввод
                #work_cost_total - это labor_cost*Стоимость работ - ручной ввод
                obj.save()
                if obj.s_work:
                    self.fields['task_material_list'].formset.save(d_employee=obj)
        return obj