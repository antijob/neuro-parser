import replicate
import time
import logging
from nltk.tokenize import word_tokenize
from django.conf import settings

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


def predict_is_incident(text, prompt, max_new_tokens=512, retries=3):
    if not text or not prompt:
        return False

    # Tolkenize text
    tokens = word_tokenize(text)
    cut_text = " ".join(tokens[:500] + tokens[-500:])

    attempt = 0
    while attempt < retries:
        try:
            model_input = {
                "prompt": cut_text,
                "system_prompt": prompt + SYSTEM_LLM_PROMPT_EXTRA,
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
                settings.REPLICATE_MODEL_NAME,
                input=model_input
            ):
                return event

        except replicate.exceptions.ReplicateError as e:
            logger.error(
                "Replicate API error occurred on attempt %d/%d: %s", attempt + 1, retries, e)
            attempt += 1
            time.sleep(2)  # wait for 2 seconds before retrying
        except Exception as e:
            logger.error(
                "Unexpected error occurred on attempt %d/%d: %s", attempt + 1, retries, e)
            attempt += 1
            time.sleep(2)  # wait for 2 seconds before retrying

    return False
