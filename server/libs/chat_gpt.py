import openai
from nltk.tokenize import word_tokenize
from django.conf import settings
import logging
import time

openai.api_key = settings.CHAT_GPT_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict_is_incident(text, prompt, model_name, article=None, max_tokens=10, retries=3):
    if not text or not prompt:
        logger.error("Text and prompt must be provided")
        return False
    
    cut_text = " ".join(word_tokenize(text)[:max_tokens])
    attempt = 0
    while attempt < retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": ""},
                    {"role": "assistant", "content": cut_text},
                ],
            )
            result = response["choices"][0]["message"]["content"]
            
            if article:
                article.rate[model_name] = result
                article.save()
            
            if result.endswith("."):
                result = result[:-1]
            
            return result == model_name

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error occurred on attempt {attempt + 1}/{retries}: {e}")
            attempt += 1
            time.sleep(2)  # wait for 2 seconds before retrying
        except Exception as e:
            logger.error(f"Unexpected error occurred on attempt {attempt + 1}/{retries}: {e}")
            attempt += 1
            time.sleep(2)  # wait for 2 seconds before retrying
    
    return False
