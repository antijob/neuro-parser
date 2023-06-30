import re

import pymorphy2

import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('stopwords')


USEFULL_GRAMMEMES = ['NOUN', 'VERB', 'ADJF', 'ADJS', 'INFN',
                     'PRTF', 'PRTS', 'GRND', 'ADVB']
morphy = pymorphy2.MorphAnalyzer().parse


def normalize_words(words):
    normalized_words = []
    for word in words:
        if not word:
            continue
        normalized_word = morphy(word)[0]
        normalized_words.append(normalized_word.normal_form)
    return normalized_words


def normalize_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Токенизировать текст
    tokens = word_tokenize(text.lower())

    # Убрать стоп-слова
    stop_words = set(stopwords.words('russian'))

    tokens = [token for token in tokens if token not in stop_words]

    normalized_list = ' '.join(tokens)

    return normalized_list
