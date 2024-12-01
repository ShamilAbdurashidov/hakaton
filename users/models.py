from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.utils.functional import cached_property
from django.db import models

from config.casbin import check_str_perm
from common.utils import has_related_object
from common.mixins import InvalidateCachedPropertiesMixin


class UserManager(DjangoUserManager):
    pass


class User(InvalidateCachedPropertiesMixin, AbstractUser):
    """Пользователь"""
    class Meta:
        managed = True
        db_table = 'user'
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    objects = UserManager()

    @cached_property
    def is_employee(self):
        return has_related_object(self, 'employee')

    @cached_property
    def is_superuser_or_admin(self):
        if self.is_superuser:
            return True
        if self.is_employee and self.employee.is_admin:
            return True
        return False
    
    @cached_property
    def full_name(self):
        if self.is_employee:
            return self.employee.employee_name
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    def check_perm(self, perm):
        return check_str_perm(self, perm)