from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm, AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *


User = get_user_model()


def _helper():
    helper = FormHelper()
    helper.form_tag = False
    helper.include_media = False
    return helper 


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = DjangoUserCreationForm.Meta.fields


class UserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = User
        fields = DjangoUserCreationForm.Meta.fields


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.TextInput(
            attrs={ 'placeholder': _('Имя пользователя'), 'class': 'form-control form-control-lg' })
        self.fields['password'].widget = forms.PasswordInput(
            attrs={ 'placeholder': _('Пароль'), 'class': 'form-control form-control-lg' })

        self.helper = _helper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div('username', css_class="mt-5 pt-1"),
            Div('password', css_class="mt-5 py-1"),
            Div(Submit('submit', _('Войти'), css_class="w-100 btn-darkprimary btn-lg fs-5"), css_class="mt-4"),
            )


class PassChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = _helper()
        self.helper.layout = Layout(
            Div(
                'old_password',
                'new_password1',
                'new_password2',
                Row(Column(Submit('submit', _('Сохранить'), css_class="my-2 px-3"))),
                css_class='my-2 px-4 py-3 border bg-secondary bg-opacity-10'
                )
            )
        