
from django.utils.functional import cached_property
from django.forms.models import model_to_dict


class PrevNextByPK():
    def prev(self):
        """Возвращает предыдущую к текущей запись"""
        if self.pk:
            return self.__class__.objects.filter(pk__lt=self.pk).order_by('-pk').first()
        
    def next(self):
        """Возвращает следующую к текущей запись"""
        if self.pk:
            return self.__class__.objects.filter(pk__gt=self.pk).order_by('pk').first()
        
        
class InvalidateCachedPropertiesMixin():
    """Миксин для чистки кешированных свойств при сохранении или обновлении из БД"""
    def refresh_from_db(self, *args, **kwargs):
        self.invalidate_cached_properties()
        return super().refresh_from_db(*args, **kwargs)
            
    def invalidate_cached_properties(self):
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, cached_property):
                self.__dict__.pop(key, None)

    def save(self, *args, **kwargs):
        self.invalidate_cached_properties()
        return super().save(*args, **kwargs)
    

class ModelDiffMixin(object):
    '''
    Миксин, который отслеживает значения полей модели и предоставляет 
    некоторые возможности чтобы узнать, какие поля были изменены
    '''
    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    def refresh_from_db(self, using=None, fields=None):
        super().refresh_from_db(using, fields)
        self.__initial = self._dict