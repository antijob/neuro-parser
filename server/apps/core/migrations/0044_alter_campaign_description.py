# Generated by Django 3.2 on 2021-04-27 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20210302_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='description',
            field=models.TextField(verbose_name='Текст'),
        ),
    ]
