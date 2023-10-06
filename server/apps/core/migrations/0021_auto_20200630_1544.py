# Generated by Django 3.0.6 on 2020-06-30 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20200630_1112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediaincident',
            name='public',
        ),
        migrations.RemoveField(
            model_name='userincident',
            name='public',
        ),
        migrations.AlterField(
            model_name='mediaincident',
            name='status',
            field=models.IntegerField(choices=[(0, 'Не обработан'), (1, 'Отклонен'), (2, 'Принят'), (3, 'Коммуникации'), (4, 'В работе'), (5, 'Выполнен'), (6, 'Удален')], default=0, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='userincident',
            name='status',
            field=models.IntegerField(choices=[(0, 'Не обработан'), (1, 'Отклонен'), (2, 'Принят'), (3, 'Коммуникации'), (4, 'В работе'), (5, 'Выполнен'), (6, 'Удален')], default=0, verbose_name='Статус'),
        ),
    ]
