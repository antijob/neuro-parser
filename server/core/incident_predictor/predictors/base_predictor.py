from abc import ABC, abstractmethod
from typing import Any

from server.apps.core.models import IncidentType, Article
from libs.handler import Handler


class PredictorBase(Handler):
    def __init__(self, incident_type: IncidentType):
        self.incident_type = incident_type

    @abstractmethod
    def is_incident(self, article: Article) -> tuple[bool, Any]:
        """
        Abstract method that must be implemented by subclasses
        to process an incident from the article.
        """
        pass
