import pytest

from tests.conftest import login


@pytest.mark.django_db
def test_login_success(api_client, seeded_db):
    response = api_client.post(
        "/api/auth/login",
        {"email": "sales@fgl.demo", "password": "demo1234"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "SALES"


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, seeded_db):
    response = api_client.post(
        "/api/auth/login",
        {"email": "sales@fgl.demo", "password": "wrong"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_sales_cannot_access_invoices(api_client, seeded_db):
    login(api_client, "sales@fgl.demo")
    response = api_client.get("/api/invoices")
    assert response.status_code == 403
