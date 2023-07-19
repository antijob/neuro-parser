# Generated by Django 3.2.12 on 2023-07-18 19:25

from django.db import migrations, models
import django.db.models.deletion
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_add_dataleaks'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Вид ограничения')),
                ('zip_file', models.FileField(blank=True, null=True, upload_to=pathlib.PurePosixPath('/code/models/zip_data'))),
            ],
            options={
                'verbose_name': 'Тип инцидента',
                'verbose_name_plural': 'Типы инцидентов',
            },
        ),
        migrations.AlterField(
            model_name='mediaincident',
            name='incident_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.incidenttype'),
        ),
        migrations.AlterField(
            model_name='userincident',
            name='incident_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.incidenttype'),
        ),
    ]
