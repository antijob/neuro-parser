# Generated by Django 3.1.3 on 2020-11-24 10:53

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20200828_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediaincident',
            name='duplicate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='duplicates', to='core.mediaincident', verbose_name='Дубликат'),
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='Заголовок')),
                ('summary', models.TextField(verbose_name='Краткое описание')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Текст')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.campaign', verbose_name='Кампания')),
            ],
        ),
        migrations.CreateModel(
            name='DocGenerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Текст')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.campaign', verbose_name='Кампания')),
            ],
        ),
    ]
