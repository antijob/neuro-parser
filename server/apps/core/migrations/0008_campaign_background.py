# Generated by Django 3.0.3 on 2020-03-25 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200320_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='background',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Фон для кампании'),
        ),
    ]
