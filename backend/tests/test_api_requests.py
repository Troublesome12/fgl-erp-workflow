import pytest
from rest_framework.test import APIClient

from tests.conftest import login


@pytest.mark.django_db
def test_create_and_list_request(api_client, seeded_db):
    login(api_client, "sales@fgl.demo")

    create_response = api_client.post(
        "/api/requests",
        {
            "client_name": "Test Client",
            "amount": "50000.00",
            "billing_period": "June 2026",
            "description": "Integration test request",
        },
        format="json",
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "PENDING"
    assert created["client_name"] == "Test Client"

    list_response = api_client.get("/api/requests")
    assert list_response.status_code == 200
    ids = [r["id"] for r in list_response.json()]
    assert created["id"] in ids


@pytest.mark.django_db
def test_approve_creates_invoice(api_client, seeded_db):
    sales_client = APIClient()
    accounts_client = APIClient()
    mgmt_client = APIClient()

    login(sales_client, "sales@fgl.demo")
    login(accounts_client, "accounts@fgl.demo")

    create_response = sales_client.post(
        "/api/requests",
        {
            "client_name": "Approve Test Co",
            "amount": "75000.00",
            "billing_period": "June 2026",
            "description": "Approve flow test",
        },
        format="json",
    )
    request_id = create_response.json()["id"]

    approve_response = accounts_client.post(
        f"/api/reviews/{request_id}/approve",
        {"note": "Looks good — approved for testing."},
        format="json",
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "APPROVED"

    login(mgmt_client, "management@fgl.demo")
    invoices_response = mgmt_client.get("/api/invoices")
    assert invoices_response.status_code == 200
    invoice_request_ids = [inv["request_id"] for inv in invoices_response.json()]
    assert request_id in invoice_request_ids


@pytest.mark.django_db
def test_get_request_detail_without_invoice(api_client, seeded_db):
    login(api_client, "sales@fgl.demo")

    create_response = api_client.post(
        "/api/requests",
        {
            "client_name": "Detail Test Co",
            "amount": "25000.00",
            "billing_period": "June 2026",
            "description": "Detail view test",
        },
        format="json",
    )
    request_id = create_response.json()["id"]

    detail_response = api_client.get(f"/api/requests/{request_id}")
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data["id"] == request_id
    assert data["invoice"] is None
    assert data["review_notes"] == []


@pytest.mark.django_db
def test_reject_request(api_client, seeded_db):
    sales_client = APIClient()
    accounts_client = APIClient()

    login(sales_client, "sales@fgl.demo")
    login(accounts_client, "accounts@fgl.demo")

    create_response = sales_client.post(
        "/api/requests",
        {
            "client_name": "Reject Test Co",
            "amount": "1000.00",
            "billing_period": "June 2026",
            "description": "Reject flow test",
        },
        format="json",
    )
    request_id = create_response.json()["id"]

    reject_response = accounts_client.post(
        f"/api/reviews/{request_id}/reject",
        {"note": "Amount incorrect — please resubmit."},
        format="json",
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "REJECTED"
