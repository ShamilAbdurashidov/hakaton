from functools import lru_cache

from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from django.utils.functional import cached_property
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from common.mixins import InvalidateCachedPropertiesMixin


User = settings.AUTH_USER_MODEL


class District(models.Model):
    '''
    Район/Город
    '''
    district_name = models.CharField(_('Наименование'), max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 's_district'
        ordering = ['pk']
        verbose_name = _('Район/Город')
        verbose_name_plural = _('Районы/Города')

    def __str__(self):
        return self.district_name


class OfficeType(models.Model):
    """Тип организации"""
    type_name = models.CharField(_('Наименование'), max_length=30, unique=True)

    class Meta:
        managed = False
        db_table = 's_office_type'
        ordering = ['pk']
        verbose_name = _('Тип организации')
        verbose_name_plural = _('Тип организаций')

    def __str__(self):
        return self.type_name
    
    @classmethod
    def grbs(cls):
        """ГРБС"""
        return cls.objects.get(pk=1)
    

class Office(models.Model):
    '''
    Организации
    '''
    s_district = models.ForeignKey(District, verbose_name=_('Город/Район'), on_delete=models.PROTECT, blank=True, null=True)
    office_name = models.CharField(_('Наименование'), max_length=255)
    s_office_type = models.ForeignKey(
        OfficeType, verbose_name=_('Тип организации'), related_name="offices", on_delete = models.PROTECT)
    phone_number1 = models.CharField(_('Номер телефона #1'), max_length=20, blank=True, null=True)
    phone_number2 = models.CharField(_('Номер телефона #2'), max_length=20, blank=True, null=True)
    e_mail = models.EmailField(_('Email'), max_length=70, blank=True, null=True)
    address_actual = models.CharField(_('Адрес фактический'), max_length=255, blank=True, null=True)
    address_legal = models.CharField(_('Адрес юридический'), max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_office'
        ordering = ['-pk']
        verbose_name = _('Организация')
        verbose_name_plural = _('Организации')

    def __str__(self):
        return self.office_name


class Role(models.Model):
    """Роль"""
    role_name = models.CharField(_('Наименование'), max_length=70, unique=True)

    class Meta:
        managed = False
        db_table = 's_role'
        ordering = ['pk']
        verbose_name = _('Роль')
        verbose_name_plural = _('Роли')

    def __str__(self):
        return self.role_name
        
    @classmethod
    @lru_cache()
    def admin(cls):
        """Администратор"""
        return cls.objects.get(pk=1)
    

class Employee(InvalidateCachedPropertiesMixin, models.Model):
    """Сотрудник(пользователь)"""
    user = models.OneToOneField(User, verbose_name=_('Пользователь'), related_name='employee', on_delete=models.CASCADE)
    s_office = models.ForeignKey(Office, verbose_name=_('Организация'), on_delete=models.PROTECT)
    s_role = models.ForeignKey(Role, verbose_name=_('Роль'), on_delete=models.PROTECT)
    employee_name = models.CharField(_('ФИО'), max_length=70)
    phone_number = models.CharField(_('Телефон'), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_('Активность'), default=True)
    e_mail = models.EmailField(_('Email'), max_length=70, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_employee'
        ordering = ['-pk']
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')

    def __str__(self):
        return self.employee_name
    
    @cached_property
    def is_admin(self):
        """Сотрудник админ?"""
        return self.s_role == Role.admin()
    
    @property
    def role(self):
        """Роль"""
        return str(self.s_role)
    
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.user.delete()
            super().delete(*args, **kwargs)
            
    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.user.is_active = self.is_active
            self.user.first_name = self.employee_name
            self.user.save()
            super().save(*args, **kwargs)


class UnitMeasure(models.Model):
    """Единица измерения"""
    unit_name = models.CharField(_('Наименование'), max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 's_unit_measure'
        ordering = ['pk']
        verbose_name = _('Единица измерения')
        verbose_name_plural = _('Единицы измерений')

    def __str__(self):
        return self.unit_name
    

class Work(models.Model):
    """Работа"""
    work_code = models.CharField(_('Шифр'), max_length=30)
    work_name = models.CharField(_('Наименование'), max_length=255)

    class Meta:
        managed = False
        db_table = 's_work'
        ordering = ['-pk']
        verbose_name = _('Работа')
        verbose_name_plural = _('Работы')

    def __str__(self):
        return f'[{self.work_code}] {self.work_name}'


class Material(models.Model):
    """Материал"""
    material_code = models.CharField(_('Шифр'), max_length=30)
    material_name = models.CharField(_('Наименование'), max_length=255)
    s_unit_measure = models.ForeignKey(UnitMeasure, verbose_name=_('Единица измерения'), on_delete=models.PROTECT)
    cost_value = models.DecimalField(_('Себестоимость материала'), max_digits=15, decimal_places=2)
    labor_cost = models.DecimalField(_('Трудозатраты, часы'), max_digits=15, decimal_places=2, blank=True, null=True)
    cost_work = models.DecimalField(_('Себестоимость трудозатрат'), max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_material'
        ordering = ['-pk']
        verbose_name = _('Материал')
        verbose_name_plural = _('Материалы')

    def __str__(self):
        return f'[{self.material_code}] {self.material_name}'
    

class Task(MPTTModel):
    """Задача"""
    parent = TreeForeignKey(
        'self', verbose_name=_('Родительская запись'), related_name='children', on_delete=models.PROTECT, 
        blank=True, null=True)
    s_employee = models.ForeignKey(Employee, verbose_name=_('Ответственный'), on_delete=models.PROTECT, blank=True, null=True)
    s_work = models.ForeignKey(Work, verbose_name=_('Работа'), on_delete=models.PROTECT, blank=True, null=True)
    task_name = models.CharField(_('Наименование'), max_length=255)
    date_start = models.DateField(_('Дата'), blank=True, null=True)
    date_stop = models.DateField(_('Плановя дата'), blank=True, null=True)
    date_fact = models.DateField(_('Фактическая дата'), blank=True, null=True)
    date_add = models.DateTimeField(_('Дата и время добавления'), auto_now_add=True, editable=False)

    class Meta:
        managed = True
        db_table = 'd_task'
        ordering = ['-pk']
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')

    class MPTTMeta:
        order_insertion_by = ['task_name']

    def __str__(self):
        level = ' - ' * self.level
        return f'{level} {self.task_name}'
    

class TaskMaterial(models.Model):
    """Материал к работе"""
    d_task = models.ForeignKey(Task, verbose_name=_('Задача'), related_name='task_material_list', on_delete=models.PROTECT)
    s_material = models.ForeignKey(Material, verbose_name=_('Материал'), on_delete=models.PROTECT)
    material_count = models.DecimalField(_('Количество'), max_digits=15, decimal_places=2, blank=True, null=True)
    material_cost = models.DecimalField(_('Стоимость материала'), max_digits=15, decimal_places=2, blank=True, null=True)
    labor_cost = models.DecimalField(_('Трудозатраты'), max_digits=15, decimal_places=2, blank=True, null=True)
    work_cost = models.DecimalField(_('Стоимость работ'), max_digits=15, decimal_places=2, blank=True, null=True)
    material_count_fact = models.DecimalField(_('Фактически сделано'), max_digits=15, decimal_places=2, blank=True, null=True)
    material_cost_total = models.DecimalField(_('Стоимость работ итого'), max_digits=15, decimal_places=2, blank=True, null=True)
    work_cost_total = models.DecimalField(_('Стоимость трудозатрат итого'), max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'd_task_material'
        ordering = ['-pk']
        verbose_name = _('Материал к работе')
        verbose_name_plural = _('Материалы к работам')
