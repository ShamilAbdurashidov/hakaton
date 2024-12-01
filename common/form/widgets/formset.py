from django import forms
from django.forms import BaseModelFormSet

from crispy_forms.utils import render_crispy_form


class FormsetWidget(forms.Widget):
    class Media:
        js = (
            'common/formset_expand.js',
        )

    def render(self, name, value, **kwargs):
        if value is None:
            try:
                value = self.attrs['formset_class'](
                    prefix=name, initial=self.attrs['initial'], queryset=self.attrs['queryset'], form_kwargs=self.attrs['form_kwargs'])
            except:
                value = self.attrs['formset_class'](
                    prefix=name, initial=self.attrs['initial'], form_kwargs=self.attrs['form_kwargs'])
        
        tag = self.attrs['extra_params'].get('formset_tag') or 'div'

        return '''
            <{tag} class="formset expand" data-prefix="{prefix}">{form_html}</{tag}>
            '''.format(tag=tag, prefix=value.prefix, form_html=render_crispy_form(
                value, helper=value.forms[0].helper if len(value.forms) > 0 else None))

    def value_from_datadict(self, data, files, name, **kwargs):
        try:
            return self.attrs['formset_class'](
                data=data, files=files, 
                prefix=name, initial=self.attrs['initial'], queryset=self.attrs['queryset'], form_kwargs=self.attrs['form_kwargs'])
        except:
            return self.attrs['formset_class'](
                data=data, files=files, 
                prefix=name, initial=self.attrs['initial'], form_kwargs=self.attrs['form_kwargs'])