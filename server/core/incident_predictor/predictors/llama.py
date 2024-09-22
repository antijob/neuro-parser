from typing import Any
import replicate
import logging
import re

from server.apps.core.models import IncidentType, Article

from .base_predictor import PredictorBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Code use llama model for text classification.
# Text summarization for economy price.
# Main llama_promt use in system pront for priority.

# TODO: convert to async


class LlamaPredictor(PredictorBase):
    def __init__(
        self,
        incident_type: IncidentType,
        max_new_tokens: int = 512,
        retries: int = 3,
    ):
        self.incident_type = incident_type
        self.max_new_tokens = max_new_tokens
        self.retries = retries

    @classmethod
    def can_handle(cls, incident_type: IncidentType) -> bool:
        return incident_type.llm_prompt is not None

    def is_incident(self, article: Article) -> tuple[bool, Any]:
        if not self.incident_type.llm_prompt or not article.text or len(article.text) < 200:
            return False, None

        title = article.any_title()
        full_text = remove_emoji(title + article.text)

        # Обрезаем текст, оставляя 500 символов до и 500 после
        cut_text = full_text[:500] + full_text[-500:]

        system_prompt = self.incident_type.llm_prompt + \
            self.incident_type.llm_system_prompt
        try:
            model_input = {
                "prompt": cut_text,
                "system_prompt": system_prompt,
                "max_new_tokens": 512,
                "top_p": 0.95,
                "max_tokens": 512,
                "temperature": 0,
                "length_penalty": 1,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": self.incident_type.llm_template,
                "presence_penalty": 0,
                "log_performance_metrics": False,
            }

            prediction = replicate.predictions.create(
                model=self.incident_type.llm_model_name,
                input=model_input,
                stream=True,
            )

            is_incident = False
            rate = None
            output = ""

            for event in prediction.stream():
                output += event.data

            is_incident = bool(re.search(r"\+", output))
            rate = "LLM_RESP: " + prediction.id
            return is_incident, rate

        except replicate.exceptions.ReplicateError as e:
            logger.error(
                "Replicate API error occurred: %s", e,
            )
        except Exception as e:
            logger.error(
                "Unexpected error occurred: %s", e,
            )

        return False, None


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
