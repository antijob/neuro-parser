# -*- coding: utf-8 -*-

from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.forms import UserCreationForm

from server.apps.users.models import User


class CustomSignupForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Пароль',
            },
        )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Подтверждение пароля',
            },
        )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-user',
                    'placeholder': 'Имя',
                },
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-user',
                    'placeholder': 'Фамилия',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-user',
                    'placeholder': 'Email адрес',
                },
            ),
        }


class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)

        self.fields['login'].widget = forms.EmailInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Email адрес',
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Пароль',
        })
        self.fields['remember'].widget = forms.CheckboxInput(attrs={
            'class': 'custom-control-input',
        })
