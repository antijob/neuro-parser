import re

import pymorphy2


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
    words = re.split(r'[^\w]', text)
    normalized_list = []
    for word in words:
        if not word:
            continue
        normalized_word = morphy(word)[0]
        if normalized_word.tag.POS in USEFULL_GRAMMEMES:
            normalized_list += [normalized_word.normal_form]
    return normalized_list
