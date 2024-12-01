from django import forms

from .formset import FormsetField, FormsetFormMixin


class FormattedDecimalFormField(forms.DecimalField):
    widget = forms.TextInput

    def to_python(self, value):
        if value and isinstance(value, str):
            value = ''.join(value.split()).replace(',', '.')
        return super().to_python(value)
    
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget) or {}
        attrs.update({ 'data-formatted-number': True })
        return attrs
    
