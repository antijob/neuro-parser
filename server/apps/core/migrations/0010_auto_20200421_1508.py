# Generated by Django 3.0.5 on 2020-04-21 15:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200416_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='create_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='incident',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.MediaIncident', verbose_name='Инцидент'),
        ),
        migrations.AlterField(
            model_name='article',
            name='relevance',
            field=models.IntegerField(blank=True, null=True, verbose_name='Оценка релевантности'),
        ),
        migrations.AlterField(
            model_name='article',
            name='text',
            field=models.TextField(blank=True, default='', verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.TextField(blank=True, default='', verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.URLField(max_length=300, unique=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.URLField(unique=True, verbose_name='URL списка новостей'),
        ),
    ]
