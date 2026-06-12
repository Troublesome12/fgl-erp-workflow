import pytest

from tests.conftest import login


@pytest.mark.django_db
def test_audit_trail_for_billing_request(api_client, seeded_db):
    login(api_client, "sales@fgl.demo")

    create_response = api_client.post(
        "/api/requests",
        {
            "client_name": "Audit Test Co",
            "amount": "12000.00",
            "billing_period": "June 2026",
            "description": "Audit trail test",
        },
        format="json",
    )
    request_id = create_response.json()["id"]

    audit_response = api_client.get(f"/api/audit/BillingRequest/{request_id}")
    assert audit_response.status_code == 200
    logs = audit_response.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "CREATED"
    assert logs[0]["actor_email"] == "sales@fgl.demo"
