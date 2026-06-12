import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def seeded_db(db):
    call_command("seed_data")
    return db


def login(client: APIClient, email: str, password: str = "demo1234") -> str:
    response = client.post("/api/auth/login", {"email": email, "password": password}, format="json")
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return token
