import logging

from typing import Optional
import datetime

from server.apps.core.models import IncidentType, Article, MediaIncident
from libs.handler import HandlerRegistry

from predictors.base_predictor import PredictorBase
from predictors.bert import BertPredictor
from predictors.llama import LlamaPredictor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# THERE SHOULD BE 2 pipelines

# 1 -- unique url pipeline
# 2 -- urls batch pipeline


class IncidentPredictor:
    registry = HandlerRegistry[PredictorBase]()
    registry.register(BertPredictor)
    registry.register(LlamaPredictor)

    @classmethod
    def make_predictor(cls, incident_type: IncidentType) -> Optional[PredictorBase]:
        try:
            predictor = cls.registry.choose(incident_type)
            return predictor(incident_type)
        except Exception as e:
            logger.error(f"Error in setup_incident_type: {e}", exc_info=True)

    @staticmethod
    def create_incident(
        article: Article, incident_type: IncidentType
    ) -> Optional[MediaIncident]:
        try:
            media_incident = MediaIncident.objects.create(
                urls=[article.url],
                status=MediaIncident.UNPROCESSED,
                title=article.any_title(),
                public_title=article.any_title(),
                create_date=article.publication_date or datetime.date.today(),
                description=article.text,
                related_article=article,
                public_description=article.text,
                incident_type=incident_type,
                region=article.region,
                country=article.country,
            )
            return media_incident
        except Exception as e:
            logger.error(f"Error in create_incident: {e}")
            return None

    @classmethod
    def predict_batch(cls, batch: list[Article]) -> list[MediaIncident]:
        try:
            result_incidents: list[MediaIncident] = []
            for incident_type in IncidentType.objects.all():
                if not incident_type.is_active:
                    continue

                predictor = cls.make_predictor(incident_type)
                for article in batch:
                    is_incident, rate = predictor.is_incident(article)
                    if is_incident:
                        incident = cls.create_incident(article, incident_type)
                        if incident is not None:
                            result_incidents.append(incident)
                    if rate:
                        article.rate[incident_type.description] = rate
                        article.save()
            return result_incidents
        except Exception as e:
            logger.error(f"Error in predict_batch: {e}")
            raise

    @classmethod
    def predict(cls, article: Article) -> list[MediaIncident]:
        return cls.predict_batch([article])
