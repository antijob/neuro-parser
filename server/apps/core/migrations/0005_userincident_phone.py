# Generated by Django 3.0.3 on 2020-03-18 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200313_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='userincident',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Телефон'),
        ),
    ]
