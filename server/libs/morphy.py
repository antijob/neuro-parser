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
