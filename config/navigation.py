from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def top_left_menu(context, variables):
    return [
        {
            'name': _('ЗАДАЧИ'),
            'url': reverse('tasks:home'),
            'match': r'^/?tasks',
            'logged': True
        },
        {
            'name': _('СПРАВОЧНИКИ'),
            'url': '/#',
            'match': r'^/?(directory)',
            'logged': True,
            'sub': [
                {
                    'name': _('Организации'),
                    'url': reverse('directory:office'),
                    'match': r'^/?directory/office(?!_type)',
                    'logged': True
                },
                {
                    'name': _('Сотрудники'),
                    'url': reverse('directory:employees'),
                    'match': r'^/?directory/employees',
                    'logged': True
                },
                {
                    'name': _('Материалы'),
                    'url': reverse('directory:material'),
                    'match': r'^/?directory/material',
                    'logged': True
                },
                {
                    'name': _('Работы'),
                    'url': reverse('directory:work'),
                    'match': r'^/?directory/work',
                    'logged': True
                }
            ]
        }
    ]
        

def top_right_menu(context, variables):
    user = context['request'].user

    return [
        {
            'name': '''
                <div class="float-start lh-1">
                    {full_name}
                    <div class="small text-muted lh-1 text-truncate" style="max-width: 300px;" title="{role}">{role}</div>
                </div>
                '''.format(full_name=user.full_name, role=str(user.employee.s_office) if user.is_employee else _('Не сотрудник организации')),
            'url': '/#',
            'logged': True,
            'sub': [
                {
                    'name': _('Сменить пароль'),
                    'url': reverse('users:password_change'),
                    'logged': True,
                    'class': 'modal-link',
                    'data': { 'data-modal-size': 'modal-md' }
                },
                {
                    'name': _('Выход'),
                    'url': reverse('users:logout'),
                    'class': 'text-danger',
                    'logged': True
                }
            ]
        },
    ]