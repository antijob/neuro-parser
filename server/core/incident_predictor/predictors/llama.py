from typing import Any
import replicate
import time
import logging
import re

from server.apps.core.models import IncidentType, Article

from .base_predictor import PredictorBase
from server.settings.components.common import REPLICATE_MODEL_NAME


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_LLM_PROMPT_EXTRA = "Ты - модель, которая отвечает на вопросы только символами `+` или `-`.  Если вопрос подразумевает утвердительный ответ, ответь `+`.\
Если вопрос подразумевает отрицательный ответ, ответь `-`.\
Ответ должен состоять только из одного символа `+` или `-`, без дополнительного текста."

# Code use llama model for text classification.
# Text summarization for economy price.
# Main llama_promt use in system pront for priority.

# TODO: convert to async


class LlamaPredictor(PredictorBase):
    def __init__(
        self,
        incident_type: IncidentType,
        model: str = REPLICATE_MODEL_NAME,
        max_new_tokens: int = 512,
        retries: int = 3,
    ):
        self.incident_type = incident_type
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.retries = retries

    @classmethod
    def can_handle(cls, incident_type: IncidentType) -> bool:
        return incident_type.llm_prompt is not None

    def is_incident(self, article: Article) -> tuple[bool, Any]:
        if not self.incident_type.llm_prompt or not article.text:
            return False, None

        title = article.any_title()
        full_text = title + article.text

        # Обрезаем текст, оставляя 500 символов до и 500 после
        cut_text = full_text[:500] + full_text[-500:]

        attempt = 0
        system_prompt = self.incident_type.llm_prompt + SYSTEM_LLM_PROMPT_EXTRA
        while attempt < self.retries:
            try:
                model_input = {
                    "prompt": cut_text,
                    "system_prompt": system_prompt,
                    "max_new_tokens": self.max_new_tokens,
                    "top_p": 0.95,
                    "max_tokens": 512,
                    "temperature": 0.7,
                    "length_penalty": 1,
                    "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                    "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                    "presence_penalty": 0,
                    "log_performance_metrics": False,
                }

                prediction = replicate.predictions.create(
                    model=self.model,
                    input=model_input,
                    stream=True,
                )

                for event in prediction.stream():
                    is_incident = bool(re.search(r"\+", event.data))
                    rate = "LLM_RESP: " + prediction.id
                    return is_incident, rate

            except replicate.exceptions.ReplicateError as e:
                logger.error(
                    "Replicate API error occurred on attempt %d/%d: %s",
                    attempt + 1,
                    self.retries,
                    e,
                )
            except Exception as e:
                logger.error(
                    "Unexpected error occurred on attempt %d/%d: %s",
                    attempt + 1,
                    self.retries,
                    e,
                )
            attempt += 1
            time.sleep(2)
        return False, None
