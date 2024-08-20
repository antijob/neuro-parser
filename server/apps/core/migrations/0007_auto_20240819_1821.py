# Generated by Django 3.2.21 on 2024-08-19 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20240805_1949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidenttype',
            name='chat_gpt_prompt',
        ),
        migrations.AddField(
            model_name='incidenttype',
            name='llm_prompt',
            field=models.TextField(blank=True, null=True, verbose_name='LLM промпт'),
        ),
    ]
