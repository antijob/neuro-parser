import pytest


@pytest.mark.django_db
def test_get_media_incidents(api_client):
    response = api_client.get("/api/media-incidents/")
    assert response.status_code == 200
    assert response.json() == []  # Change this based on actual data
