import os

from django.conf import settings
import numpy as np
import joblib
from server.apps.core.incident_types import IncidentType
from server.apps.core.logic.grabber.classificator.cosine import rate_with_model_and_tokenizer

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


def predict_is_incident(normalized_text, incident_type):
    tokenizer = incident_type.get_tokenizer()
    model = incident_type.get_model()
    model.eval()

    relevance = (rate_with_model_and_tokenizer(
                    normalized_text, 
                    model, 
                    tokenizer)
                 * settings.RELEVANCE_TRESHOLD)

    return relevance > settings.RELEVANCE_TRESHOLD # it's working this way in project, don't know why


def predict_incident_type(normalized_text):
    for incident_type in IncidentType.objects.exclude(zip_file__in=['',None]):
        if predict_is_incident(normalized_text, incident_type):
            return incident_type

    return None
