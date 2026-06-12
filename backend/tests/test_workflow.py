import pytest
from rest_framework.exceptions import ValidationError

from workflow.models import RequestStatus
from workflow.services.workflow import validate_transition


def test_valid_pending_to_approved():
    validate_transition(RequestStatus.PENDING, RequestStatus.APPROVED)


def test_valid_pending_to_rejected():
    validate_transition(RequestStatus.PENDING, RequestStatus.REJECTED)


def test_invalid_approved_to_pending():
    with pytest.raises(ValidationError):
        validate_transition(RequestStatus.APPROVED, RequestStatus.PENDING)


def test_invalid_rejected_to_approved():
    with pytest.raises(ValidationError):
        validate_transition(RequestStatus.REJECTED, RequestStatus.APPROVED)
