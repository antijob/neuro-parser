from transformers import AutoTokenizer, BertForSequenceClassification
from django.db import models
from server.settings.components.common import BASE_DIR, MODELS_DIR
from server.apps.core.logic.grabber.classificator.cosine import rate_with_model_and_tokenizer
import server.apps.core.logic.grabber.classificator.chat_gpt as chat_gpt


class IncidentType(models.Model):
    model_path = models.CharField(max_length=100, null=True)
    treshold = models.FloatField('Treshold для модели', default=1)
    description = models.CharField(
        'Название модели', max_length=128, null=True, blank=True)
    chat_gpt_prompt = models.TextField('Chat-GPR промпт', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активный', default=False)
    should_sent_to_bot = models.BooleanField(
        default=True, verbose_name='Показывать в боте')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def model_directory(self):
        if not self.model_path:
            return None
        return MODELS_DIR.joinpath(self.model_path)

    def get_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_directory, use_fast=False)
        return tokenizer

    def get_model(self):
        model = BertForSequenceClassification.from_pretrained(
            self.model_directory)
        model.eval()
        return model

    def process_batch(self, batch):
        if self.chat_gpt_prompt:
            return self.process_batch_gpt(batch)
        if self.model_path:
            return self.process_batch_model(batch)
        return None

    def process_batch_model(self, batch):
        incidents_count = 0
        tokenizer = self.get_tokenizer()
        model = self.get_model()
        for art in batch:
            relevance = rate_with_model_and_tokenizer(
                art.normalized_text(),
                model,
                tokenizer)

            if relevance[0]-relevance[1] > self.treshold:
                art.create_incident_with_type(self)
                incidents_count += 1

        return incidents_count

    def process_batch_gpt(self, batch):
        incidents_count = 0
        for art in batch:
            if self.chat_gpt_prompt:
                is_incident = chat_gpt.predict_is_incident(
                    art.normalized_text(),
                    self.chat_gpt_prompt,
                    self.description,
                    art)
                if is_incident:
                    art.create_incident_with_type(self)
                    incidents_count += 1
                    continue

        return incidents_count

    @classmethod
    def get_choices(cls):
        return [(incident_type.id, incident_type.description) for incident_type in cls.objects.all()]

    def __str__(self):
        return str(self.description)

    class Meta:
        verbose_name = 'Тип инцидента'
        verbose_name_plural = 'Типы инцидентов'
