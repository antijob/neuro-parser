# Generated by Django 3.2.21 on 2024-05-27 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20240527_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='country',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
        migrations.AlterField(
            model_name='source',
            name='region',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.region'),
        ),
    ]
