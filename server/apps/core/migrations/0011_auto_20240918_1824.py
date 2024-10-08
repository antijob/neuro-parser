# Generated by Django 3.2.21 on 2024-09-18 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_article_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidenttype',
            name='llm_model_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='LLM модель'),
        ),
        migrations.AddField(
            model_name='incidenttype',
            name='llm_system_promt',
            field=models.TextField(blank=True, default='Ты - модель, которая отвечает на вопросы только символами `+` или `-`.  Если вопрос подразумевает утвердительный ответ, ответь `+`.Если вопрос подразумевает отрицательный ответ, ответь `-`.Ответ должен состоять только из одного символа `+` или `-`, без дополнительного текста. Отвечать по пунктам не нужно, отвечай на общий контекст текста.', null=True, verbose_name='LLM системный промпт'),
        ),
        migrations.AddField(
            model_name='incidenttype',
            name='llm_template',
            field=models.TextField(blank=True, default='<|begin_of_text|><|start_header_id|>system<|end_header_id|>{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>', null=True, verbose_name='LLM шаблон'),
        ),
    ]
