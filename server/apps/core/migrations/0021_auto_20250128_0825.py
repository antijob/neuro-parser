# Generated by Django 3.2.21 on 2025-01-28 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_proxy_error_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxy',
            name='error_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Тип ошибки'),
        ),
        migrations.AlterField(
            model_name='proxy',
            name='last_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последняя проверка'),
        ),
    ]
