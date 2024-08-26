from typing import Any
from server.apps.core.models import IncidentType, Article


class PredictorBase:
    def __init__(self, incident_type: IncidentType):
        self.incident_type = incident_type

    def is_incident(self, article: Article) -> tuple[bool, Any]:
        pass
