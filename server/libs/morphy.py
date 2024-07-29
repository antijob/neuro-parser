import string
import logging

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_nltk_initialized = False
_cached_stop_words = {}

def initialize_nltk_resources():
    global _nltk_initialized, _cached_stop_words
    if not _nltk_initialized:
        try:
            nltk.download("punkt")
            nltk.download("stopwords")
            _cached_stop_words['russian'] = set(stopwords.words("russian"))
            _nltk_initialized = True
            logger.info("NLTK resources initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLTK resources: {e}")
            raise

def normalize_text(text, language='russian'):
    try:
        initialize_nltk_resources()
    except Exception as e:
        logger.error(f"Error during NLTK initialization: {e}")
        return ""

    try:
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Tokenize text
        tokens = set(word_tokenize(text.lower()))

        # Remove stop words
        stop_words = _cached_stop_words.get(language, set())
        tokens = tokens - stop_words
        normalized_list = " ".join(tokens)

        return normalized_list
    except Exception as e:
        logger.error(f"Error normalizing text: {e}")
        return ""
