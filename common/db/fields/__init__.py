from django.db import models

from common.form.fields import FormattedDecimalFormField


class FormattedDecimalField(models.DecimalField):
    def formfield(self, **kwargs):
        kwargs.update({ 'form_class': FormattedDecimalFormField })
        return super().formfield(**kwargs)



class JsonField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, dict):
            return value
        return super().from_db_value(value, expression, connection)