import logging
from typing import Union
import datetime

from server.libs.morphy import normalize_text
from server.libs import chat_gpt

from server.apps.core.models import IncidentType, Article, MediaIncident
from server.apps.bot.services.inc_post import mediaincident_post

from transformers import AutoTokenizer, BertForSequenceClassification

from server.settings.components.common import MODELS_DIR


# COSINE.PY
import os
import tqdm

from django.conf import settings

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
        model_iter = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)

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
    is_gpt_setup: bool

    def setup_incident_type(self, it: IncidentType):
        try:
            self.current_incident_type = it

            self.is_gpt_setup = False
            if it.model_path:
                model_directory = MODELS_DIR.joinpath(it.model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_directory, use_fast=False
                )
                self.model = BertForSequenceClassification.from_pretrained(
                    model_directory
                )
                self.model.eval()
            elif it.chat_gpt_prompt:
                self.is_gpt_setup = True
        except Exception as e:
            logger.error(f"Error in setup_incident_type: {e}")

    # Как-то надо в этом месте отмечать, что article -- mutable
    def _is_incident(self, article: Article = None) -> bool:
        if article is None:
            return False
        try:
            normalized_text = normalize_text(article.text)
            if self.is_gpt_setup:
                return chat_gpt.predict_is_incident(
                    normalized_text,
                    self.current_incident_type.chat_gpt_prompt,
                    self.current_incident_type.description,
                    article,
                )
            else:
                relevance = rate_with_model_and_tokenizer(
                    normalized_text, self.model, self.tokenizer
                )
                article.rate[self.current_incident_type.description] = relevance
                article.save()

                return relevance[0] - relevance[1] > self.current_incident_type.treshold
        except Exception as e:
            logger.error(f"Error in _is_incident: {e}")
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
                mediaincident_post(media_incident)
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

    # def predict(self, article: Article) -> Union[MediaIncident, None]:
    #     try:
    #         for incident_type in IncidentType.objects.all():
    #             if not incident_type.is_active:
    #                 continue

    #             self.setup_incident_type(incident_type)
    #             normalized_text = normalize_text(article.text)

    #             if self.is_gpt_setup:
    #                 is_incident = chat_gpt.predict_is_incident(
    #                     normalized_text,
    #                     incident_type.chat_gpt_prompt,
    #                     incident_type.description,
    #                     article,
    #                 )
    #                 if is_incident:
    #                     return self._create_incident(article)

    #             if not incident_type.model_path:
    #                 continue
    #             if is_incident:
    #                 return self._create_incident(article)
    #     except Exception as e:
    #         print(f"Error in predict: {e}")
    #     return None
