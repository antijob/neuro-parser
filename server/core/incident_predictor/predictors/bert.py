from server.settings.components.common import MODELS_DIR
from transformers import AutoTokenizer, BertForSequenceClassification
from .base_predictor import PredictorBase
import logging

from typing import Any
import tqdm
import torch
from server.libs.morphy import normalize_text

from server.apps.core.models import IncidentType, Article


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Code use llama model for text classification.
# Text summarization for economy price.
# Main llama_promt use in system pront for priority.

# TODO: convert to async


class BertPredictor(PredictorBase):
    def __init__(self, incident_type: IncidentType):
        model_directory = MODELS_DIR.joinpath(incident_type.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_directory, use_fast=False)
        self.model = BertForSequenceClassification.from_pretrained(
            model_directory)
        self.model.eval()

        self.incident_type = incident_type

    @classmethod
    def can_handle(cls, incident_type: IncidentType) -> bool:
        if incident_type.model_path:
            model_directory = MODELS_DIR.joinpath(incident_type.model_path)

            if not model_directory.exists() or not model_directory.is_dir():
                raise FileNotFoundError(
                    f"Model directory {model_directory} does not exist"
                    "or is not a directory."
                )
            return True
        return False

    def is_incident(self, article: Article) -> tuple[bool, Any]:
        normalized_text = normalize_text(article.text)
        try:
            encoding = self.tokenizer(
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
                dataset, batch_size=1, shuffle=False
            )

            predictions_pos = 0.0
            predictions_neg = 0.0
            for text in tqdm.tqdm(model_iter):
                outputs = self.model(text[0])
                predictions_pos += outputs.logits[0][1].item()
                predictions_neg += outputs.logits[0][0].item()

            logits = torch.tensor([predictions_neg, predictions_pos])
            probabilities = torch.nn.functional.softmax(logits, dim=0).tolist()

            is_incident = (
                probabilities[0] > self.incident_type.treshold
            )
            rate = probabilities

            return is_incident, rate

        except Exception as e:
            logger.error(f"Error in predict_is_incident_bert: {e}")
            return False, None
