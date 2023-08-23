# 
# API AUTH
# with token from env
# 

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings


class TokenUser(AnonymousUser):
    @property
    def is_authenticated(self):
        return True


class EnvTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if settings.API_TOKEN and token != f'Token {settings.API_TOKEN}':
            return None

        user = TokenUser()
        return (user, None)