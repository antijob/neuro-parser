# -*- coding: utf-8 -*-
import random

from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand
from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.enums import Gender

from server.apps.core.models import UserIncident
from server.apps.users.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        generic = Generic('ru')
        russia = RussiaSpecProvider()

        try:
            User.objects.create_superuser(
                email='',
                password='',
                first_name='Saul',
                last_name='Goodman',
            )
        except:
            pass

        print('Generating users...')
        for i in range(50):
            try:
                gender = random.choice([Gender.MALE, Gender.FEMALE])
                User.objects.create(
                    email=generic.person.email(),
                    password='',
                    first_name=generic.person.name(gender=gender),
                    last_name=generic.person.surname(gender=gender),
                )
            except:
                pass

        print('Verifying email addresses for all accounts...')
        EmailAddress.objects.all().update(verified=True)

        print('Generating 40 incidents...')
        for i in range(50):
            UserIncident.objects.create(
                title=russia.generate_sentence(),
                description=''.join(russia.generate_sentence() for _ in range(3)),
                status=0,
            )
