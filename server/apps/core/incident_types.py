from transformers import AutoTokenizer, BertForSequenceClassification
from django.db import models
from server.settings.components.common import BASE_DIR, MODELS_DIR


class IncidentType(models.Model):
    model_path = models.CharField(max_length=100, null=True)
    treshold = models.PositiveIntegerField('Treshold для модели', default=1)
    description = models.CharField('Название модели', max_length=128, null=True, blank=True)
    chat_gpt_prompt = models.TextField('Chat-GPR промпт', null=True, blank=True)

    should_sent_to_bot = models.BooleanField(default=True, verbose_name='Показывать в боте')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def model_directory(self):
        if not self.model_path:
            return None
        return MODELS_DIR.joinpath(self.model_path)

    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(self.model_directory, use_fast=False)
        return tokenizer

    def get_model(self):
        model  = BertForSequenceClassification.from_pretrained(self.model_directory)
        model.eval()
        return model

    @classmethod
    def get_choices(cls):
        return [(incident_type.id, incident_type.description) for incident_type in cls.objects.all()]

    def __str__(self):
        return str(self.description)

    class Meta:
        verbose_name = 'Тип инцидента'
        verbose_name_plural = 'Типы инцидентов'
