import pytest


@pytest.mark.django_db
def test_get_incident_types(api_client):
    response = api_client.get("/api/incident-types/")
    assert response.status_code == 200
    assert response.json() == []  # Change this based on actual data
