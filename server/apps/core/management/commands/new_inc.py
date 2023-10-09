from django.core.management.base import BaseCommand
from datetime import date
from server.apps.core.models import MediaIncident
from server.apps.core.incident_types import IncidentType


class Command(BaseCommand):
    help = 'Creates and saves an instance of BaseIncident'

    def handle(self, *args, **kwargs):
        # Create a new instance of BaseIncident
        new_incident = MediaIncident(
            title="Sample Incident",
            description="This is a sample incident description.",
            status=MediaIncident.UNPROCESSED,
            create_date=date.today(),
            region="RU-MOW",  # Choose the appropriate region code
            # incident_type=None,  # You can pass an IncidentType instance if needed
            incident_type=IncidentType.objects.get(id=2),  # You can pass an IncidentType instance if needed
            count=1,
            tags=["tag1", "tag2"],  # Add tags as a list
            urls=["http://example.com", "http://example.org"],  # Add URLs as a list
            public_title="Public Title",
            public_description="Public description for the incident."
        )

        # Save the instance to the database
        new_incident.save()

        print('Successfully created and saved an incident.')
