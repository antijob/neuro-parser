# Generated by Django 3.2.12 on 2023-08-09 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_default_incident_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidenttype',
            name='treshold',
            field=models.PositiveIntegerField(default=1, verbose_name='Treshold для модели'),
        ),
    ]