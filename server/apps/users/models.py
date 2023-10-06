# -*- coding: utf-8 -*-

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from server.apps.users.managers import UserManager


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField('Email адрес', unique=True)
    is_staff = models.BooleanField(
        'Сотрудник',
        default=False,
    )
    is_active = models.BooleanField(
        'Активный',
        default=True,
    )
    first_name = models.CharField('Имя', max_length=30, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    biography = models.TextField('Биография', null=True, blank=True)
    date_joined = models.DateTimeField('Дата регистрации', default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        abstract = True

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractUser):
    """
    Custom fully featured User model.

    Email and password are required. Other fields are optional.
    """

    class Meta(AbstractBaseUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return '[{}] {}'.format(self.email, self.get_full_name())
