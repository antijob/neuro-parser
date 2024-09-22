from django.core.management.base import BaseCommand
from server.apps.core.models import IncidentType, Article
from server.core.incident_predictor.predictors.llama import LlamaPredictor
import logging


class Command(BaseCommand):
    help = 'Test LlamaPredictor with given incident ID and article URL'

    def add_arguments(self, parser):
        parser.add_argument('incident_id', type=int,
                            help='ID of the IncidentType')
        parser.add_argument('article_url', type=str, help='URL of the Article')

    def handle(self, *args, **kwargs):
        incident_id = kwargs['incident_id']
        article_url = kwargs['article_url']

        # Получение объекта IncidentType
        incident_type = IncidentType.objects.filter(id=incident_id).first()
        if not incident_type:
            self.stderr.write(f'IncidentType with ID {incident_id} not found')
            return

        # Получение объекта Article
        article = Article.objects.filter(url=article_url).first()
        if not article:
            self.stderr.write(f'Article with URL {article_url} not found')
            return

        # Создание предиктора и тестирование
        predictor = LlamaPredictor(incident_type)
        try:
            is_incident = predictor.is_incident(article)
            self.stdout.write(f'Prediction for article: {is_incident}')
        except Exception as e:
            logging.error(f'Error testing predictor: {e}')
            self.stderr.write(f'Error testing predictor: {e}')
