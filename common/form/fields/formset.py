from django import forms
from django.core.exceptions import ValidationError

from common.form.widgets import FormsetWidget


class FormsetValidationError(ValidationError):
    def __init__(self, message, code=None, params=None):
        super().__init__(message, code, params)
        self.errors = message


class FormsetFormMixin():
    def add_error(self, field, error): 
        if not isinstance(error, FormsetValidationError):
            return super().add_error(field, error)
        for row in error.errors:
            for field, error_list in row.items():
                if field not in self._errors:
                    self._errors[field] = self.error_class(renderer=self.renderer)
                self._errors[field].extend(error_list)
                if field in self.cleaned_data:
                    del self.cleaned_data[field]


class FormsetField(forms.Field):
    widget = FormsetWidget

    def __init__(self, formset_class, *args, **kwargs):
        self.formset_class = formset_class
        self.formset_initial = kwargs.pop('formset_initial', None)
        self.formset_queryset = kwargs.pop('formset_queryset', None)
        self.form_kwargs = kwargs.pop('form_kwargs', {})
        self.widget_params = kwargs.pop('widget_params', {})
        kwargs.update({ 'required': False , 'label': ''})
        super().__init__(*args, **kwargs)

    def validate(self, value):
        if not value.is_valid():
            errors = []
            for i, errors_dict in enumerate(list(value.errors)):
                tmp_dict = {}
                for key, val in errors_dict.items():

                    if key.startswith(value.prefix):
                        tmp_dict["%s" % (key)] = val
                    else:
                        tmp_dict["%s-%s-%s" % (value.prefix, i, key)] = val

                errors.append(tmp_dict)
            raise FormsetValidationError(errors)
        self.formset = value

    def clean(self, value):
        return super().clean(value).cleaned_data

    def widget_attrs(self, widget):
        return {
            'formset_class': self.formset_class,
            'initial': self.formset_initial,
            'queryset': self.formset_queryset,
            'form_kwargs' :  self.form_kwargs,
            'extra_params': self.widget_params
            }
    
    