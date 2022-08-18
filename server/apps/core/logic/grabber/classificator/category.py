import os

from django.conf import settings
import numpy as np
import joblib

DATA_DIR = os.path.join(settings.BASE_DIR, 'server', 'apps',
                        'core', 'logic', 'grabber', 'classificator', 'data')


def predict(normalized_text):
    if not normalized_text:
        return 0

    clf = joblib.load(os.path.join(DATA_DIR, 'cats.pkl'))
    words_list = joblib.load(os.path.join(DATA_DIR, 'cats_words_list.pkl'))
    matrix20 = np.empty([0, len(words_list)])
    vector = np.zeros([len(words_list)])
    for idx, word_from_all_words in enumerate(words_list):
        vector[idx] = normalized_text.count(word_from_all_words)
    matrix20 = np.vstack((matrix20, vector))
    clf_pred = clf.predict(matrix20)
    return clf_pred[0]
