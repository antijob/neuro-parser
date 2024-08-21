import logging
import datetime

from server.libs.morphy import normalize_text
from server.libs import llama

from server.apps.core.models import IncidentType, Article, MediaIncident

from transformers import AutoTokenizer, BertForSequenceClassification

from server.settings.components.common import MODELS_DIR

import re
import tqdm
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rate_with_model_and_tokenizer(normalized_text, model, tokenizer):
    try:
        encoding = tokenizer(
            normalized_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        )
        input_ids = encoding["input_ids"]
        dataset = torch.utils.data.TensorDataset(
            input_ids,
        )
        model_iter = torch.utils.data.DataLoader(
            dataset, batch_size=1, shuffle=False)

        predictions_pos = 0
        predictions_neg = 0
        for text in tqdm.tqdm(model_iter):
            outputs = model(text[0])
            predictions_pos += outputs.logits[0][1].item()
            predictions_neg += outputs.logits[0][0].item()
        logits = torch.tensor([predictions_neg, predictions_pos])
        probabilities = torch.nn.functional.softmax(logits, dim=0)
        return probabilities.tolist()
    except Exception as e:
        logger.error(f"Error in rate_with_model_and_tokenizer: {e}")
        return [0, 0]  # Default value if an error occurs


# THERE SHOULD BE 2 pipelines

# 1 -- unique url pipeline
# 2 -- urls batch pipeline

class IncidentPredictor:
    current_incident_type: IncidentType
    tokenizer: any
    model: any
    is_llm_setup: bool

    def setup_incident_type(self, it: IncidentType):
        try:
            self.current_incident_type = it

            self.is_llm_setup = False
            if it.model_path:
                model_directory = MODELS_DIR.joinpath(it.model_path)

                if not model_directory.exists() or not model_directory.is_dir():
                    raise FileNotFoundError(
                        f"Model directory {model_directory} does not exist or is not a directory.")

                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_directory, use_fast=False)
                self.model = BertForSequenceClassification.from_pretrained(
                    model_directory
                )
                self.model.eval()
            elif it.llm_prompt:
                self.is_llm_setup = True
        except Exception as e:
            logger.error(f"Error in setup_incident_type: {e}", exc_info=True)

    # Как-то надо в этом месте отмечать, что article -- mutable

    def _is_incident(self, article: Article = None) -> bool:
        try:
            normalized_text = normalize_text(article.text)
            if self.is_llm_setup:
                response = llama.predict_is_incident(
                    normalized_text,
                    self.current_incident_type.llm_prompt,
                )
                article.rate[self.current_incident_type.description] = 'LLM_RESP: ' + response.data
                article.save()

                is_incident = bool(re.search(r'[+]', response.data))
                return is_incident
            else:
                relevance = rate_with_model_and_tokenizer(
                    normalized_text, self.model, self.tokenizer
                )
                article.rate[self.current_incident_type.description] = relevance
                article.save()
                is_incident = bool(
                    relevance[0] - relevance[1] > self.current_incident_type.treshold)
                # Assuming threshold logic is correct, consider explaining it
                return is_incident
        except Exception as e:
            logger.error("Error in _is_incident: %s: %s",
                         e.__class__.__name__, e.args)
            return False

    def _create_incident(self, article: Article) -> MediaIncident:
        try:
            return MediaIncident.objects.create(
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
