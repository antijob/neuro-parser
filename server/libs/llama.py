import replicate
import time
import logging
import re

from nltk.tokenize import word_tokenize
from server.libs.morphy import normalize_text

from server.apps.core.models import IncidentType, Article

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_LLM_PROMPT_EXTRA = 'Ты - модель, которая отвечает на вопросы только символами `+` или `-`.  Если вопрос подразумевает утвердительный ответ, ответь `+`.\
Если вопрос подразумевает отрицательный ответ, ответь `-`.\
Ответ должен состоять только из одного символа `+` или `-`, без дополнительного текста.'

# Code use llama model for text classification.
# Text summarization for economy price.
# Main llama_promt use in system pront for priority.

# TODO: convert to async


def predict_is_incident_llama(incident: IncidentType, article: Article,  model: str, max_new_tokens=512, retries=3) -> bool:
    if not incident.llm_prompt or not article.text:
        return False

    # Normalize text
    normalized_text = normalize_text(article.text)

    # Tokenize text
    tokens = word_tokenize(article.any_title + normalized_text)
    cut_text = " ".join(tokens[:500] + tokens[-500:])

    attempt = 0
    while attempt < retries:
        try:
            model_input = {
                "prompt": cut_text,
                "system_prompt":  SYSTEM_LLM_PROMPT_EXTRA + incident.llm_prompt,
                "max_new_tokens": max_new_tokens,
                "top_p": 0.95,
                "max_tokens": 512,
                "temperature": 0.7,
                "length_penalty": 1,
                "stop_sequences": "<|end_of_text|>,<|eot_id|>",
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 0,
                "log_performance_metrics": False
            }

            for event in replicate.stream(
                model,
                input=model_input
            ):
                # save rate
                article.rate[incident.current_incident_type.description] = 'LLM_RESP: ' + event.data
                article.save()

                return bool(re.search(r'\+', event.data))

        except replicate.exceptions.ReplicateError as e:
            logger.error(
                "Replicate API error occurred on attempt %d/%d: %s", attempt + 1, retries, e)
        except Exception as e:
            logger.error(
                "Unexpected error occurred on attempt %d/%d: %s", attempt + 1, retries, e)
        attempt += 1
        time.sleep(2)
    return False
