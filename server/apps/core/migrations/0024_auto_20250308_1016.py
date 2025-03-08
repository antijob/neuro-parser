# Generated by Django 3.2.21 on 2025-03-08 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_source_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_incorrect',
            field=models.BooleanField(default=False, verbose_name='Некорректная статья'),
        ),
        migrations.AlterField(
            model_name='article',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='article', to='core.source', verbose_name='Источник'),
        ),
    ]
