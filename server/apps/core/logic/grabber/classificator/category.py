import os

from django.conf import settings
import numpy as np
import joblib
from server.apps.core.incident_types import IncidentType
from server.apps.core.logic.grabber.classificator.cosine import rate_with_model_and_tokenizer
import server.apps.core.logic.grabber.classificator.chat_gpt as chat_gpt


def predict_is_incident(normalized_text, incident_type):
    tokenizer = incident_type.get_tokenizer()
    model = incident_type.get_model()
    model.eval()

    relevance = rate_with_model_and_tokenizer(
                    normalized_text, 
                    model, 
                    tokenizer)

    return relevance > incident_type.treshold


def predict_incident_type(normalized_text):
    types = []
    for incident_type in IncidentType.objects.all():
        if incident_type.chat_gpt_prompt:
            is_incident = chat_gpt.predict_is_incident(
                normalized_text, 
                incident_type.chat_gpt_prompt, 
                incident_type.description)
            if is_incident:
                types.append(incident_type)

            continue
        if not incident_type.model_path:
            continue
        if predict_is_incident(normalized_text, incident_type):
            types.append(incident_type)
    return types
