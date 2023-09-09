from transformers import AutoTokenizer, BertForSequenceClassification
from django.db import models
from server.settings.components.common import BASE_DIR, MODELS_DIR


class IncidentType(models.Model):
    model_path = models.CharField(max_length=100, null=True)
    treshold = models.PositiveIntegerField('Treshold для модели', default=1)
    description = models.CharField('Вид ограничения', max_length=128, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = None
        self.model = None

    @property
    def model_directory(self):
        if not self.model_path:
            return None
        return MODELS_DIR.joinpath(self.model_path)

    def get_tokenizer(self):
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_directory, use_fast=False)
        return self.tokenizer

    def get_model(self):
        if self.model is None:
            self.model = BertForSequenceClassification.from_pretrained(self.model_directory)
            self.model.eval()
        return self.model

    @classmethod
    def get_choices(cls):
        return [(incident_type.id, incident_type.description) for incident_type in cls.objects.all()]

    def __str__(self):
        return str(self.description)

    class Meta:
        verbose_name = 'Тип инцидента'
        verbose_name_plural = 'Типы инцидентов'
