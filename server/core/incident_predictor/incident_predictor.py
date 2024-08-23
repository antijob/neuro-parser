import logging
import datetime
import asyncio

from server.libs import llama, bert
from server.apps.core.models import IncidentType, Article, MediaIncident
from server.apps.bot.services.inc_post import mediaincident_post

from transformers import AutoTokenizer, BertForSequenceClassification

from server.settings.components.common import MODELS_DIR, REPLICATE_MODEL_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# THERE SHOULD BE 2 pipelines

# 1 -- unique url pipeline
# 2 -- urls batch pipeline


class IncidentPredictor:
    current_incident_type: IncidentType
    tokenizer: any
    model: any
    is_llm_setup: bool

    def setup_incident_type(self, incident_type: IncidentType):
        try:
            self.current_incident_type = incident_type

            self.is_llm_setup = False
            if incident_type.model_path:
                model_directory = MODELS_DIR.joinpath(incident_type.model_path)

                if not model_directory.exists() or not model_directory.is_dir():
                    raise FileNotFoundError(
                        f"Model directory {model_directory} does not exist or is not a directory.")

                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_directory, use_fast=False
                )
                self.model = BertForSequenceClassification.from_pretrained(
                    model_directory
                )
                self.model.eval()
            elif incident_type.llm_prompt:
                self.is_llm_setup = True
        except Exception as e:
            logger.error(f"Error in setup_incident_type: {e}", exc_info=True)

    # Как-то надо в этом месте отмечать, что article -- mutable

    def _is_incident(self, article: Article = None) -> bool:
        try:
            if self.is_llm_setup:
                return llama.predict_is_incident_llama(
                    self,
                    article,
                    self.current_incident_type.llm_prompt,
                    REPLICATE_MODEL_NAME
                )
            else:
                return bert.predict_is_incident_bert(self, article, self.model, self.tokenizer)
        except Exception as e:
            logger.error("Error in _is_incident: %s: %s",
                         e.__class__.__name__, e.args)
            return False

    def _create_incident(self, article: Article) -> MediaIncident:
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
                incident_type=self.current_incident_type,
                region=article.region,
                country=article.country,
            )
            try:
                asyncio.run(mediaincident_post(media_incident))
            except Exception as e:
                logger.error(f"Error in _create_incident - mediaincident_post: {e}")
            return media_incident
        except Exception as e:
            logger.error(f"Error in _create_incident: {e}")
            return None  # Default value if an error occurs

    def predict_batch(self, batch: list[Article]) -> int:
        try:
            incidents_count: int = 0
            for incident_type in IncidentType.objects.all():
                if not incident_type.is_active:
                    continue

                self.setup_incident_type(incident_type)
                for article in batch:
                    if self._is_incident(article):
                        self._create_incident(article)
                        incidents_count += 1
            return incidents_count
        except Exception as e:
            logger.error(f"Error in predict_batch: {e}")
            raise
