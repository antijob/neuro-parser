# Generated by Django 3.2.21 on 2023-09-22 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_auto_20230919_1402'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='algorithm',
        ),
        migrations.RemoveField(
            model_name='source',
            name='banned',
        ),
        migrations.AddField(
            model_name='incidenttype',
            name='should_sent_to_bot',
            field=models.BooleanField(default=True, verbose_name='Показывать в боте'),
        ),
    ]
