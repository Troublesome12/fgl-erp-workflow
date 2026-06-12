"""Core billing workflow business logic and state transitions."""

from datetime import datetime, timezone
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from workflow.models import (
    AuditLog,
    BillingRequest,
    Invoice,
    InvoiceStatus,
    RequestStatus,
    ReviewNote,
    User,
    UserRole,
)

VALID_TRANSITIONS: dict[str, set[str]] = {
    RequestStatus.PENDING: {RequestStatus.APPROVED, RequestStatus.REJECTED},
    RequestStatus.APPROVED: set(),
    RequestStatus.REJECTED: set(),
}


def validate_transition(current: str, target: str) -> None:
    """Ensure a billing request status change is allowed.

    Args:
        current: Current ``RequestStatus`` value.
        target: Desired ``RequestStatus`` value.

    Returns:
        None.

    Raises:
        ValidationError: If the transition is not permitted by the state machine.
    """
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(f"Cannot transition from {current} to {target}")


def log_audit(
    *,
    entity_type: str,
    entity_id: int,
    actor: User,
    action: str,
    detail: str,
) -> AuditLog:
    """Append an immutable audit log entry.

    Args:
        entity_type: Model name of the affected entity (e.g. ``"BillingRequest"``).
        entity_id: Primary key of the affected entity.
        actor: User who performed the action.
        action: Short action code (e.g. ``"CREATED"``, ``"APPROVED"``).
        detail: Human-readable description of the event.

    Returns:
        The persisted ``AuditLog`` instance.
    """
    return AuditLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        action=action,
        detail=detail,
    )


def generate_invoice_number() -> str:
    """Generate the next sequential invoice number for the current year.

    Returns:
        Invoice number string in ``INV-{YEAR}-{NNNN}`` format.
    """
    year = datetime.now(timezone.utc).year
    prefix = f"INV-{year}-"
    count = Invoice.objects.filter(invoice_number__startswith=prefix).count()
    return f"{prefix}{count + 1:04d}"


@transaction.atomic
def create_billing_request(
    *,
    user: User,
    client_name: str,
    amount: Decimal,
    billing_period: str,
    description: str,
) -> BillingRequest:
    """Create a pending billing request and record a CREATED audit entry.

    Args:
        user: Authenticated Sales user creating the request.
        client_name: Client being billed.
        amount: Billing amount in BDT.
        billing_period: Human-readable period label (e.g. ``"June 2026"``).
        description: Free-text description of the charge.

    Returns:
        The newly created ``BillingRequest`` in ``PENDING`` status.

    Raises:
        PermissionDenied: If ``user`` is not in the Sales role.
    """
    if user.role != UserRole.SALES:
        raise PermissionDenied("Only Sales can create requests")

    request = BillingRequest.objects.create(
        created_by=user,
        client_name=client_name,
        amount=amount,
        billing_period=billing_period,
        description=description,
        status=RequestStatus.PENDING,
    )

    log_audit(
        entity_type="BillingRequest",
        entity_id=request.id,
        actor=user,
        action="CREATED",
        detail=f"Billing request created for {client_name} — {amount} BDT ({billing_period})",
    )
    return request


@transaction.atomic
def approve_request(*, request_id: int, user: User, note: str) -> BillingRequest:
    """Approve a pending request, issue an invoice, and write audit entries.

    Args:
        request_id: Primary key of the billing request to approve.
        user: Authenticated Accounts user performing the review.
        note: Mandatory review note explaining the approval.

    Returns:
        The updated ``BillingRequest`` in ``APPROVED`` status.

    Raises:
        PermissionDenied: If ``user`` is not in the Accounts role.
        NotFound: If no billing request exists for ``request_id``.
        ValidationError: If the request is not in ``PENDING`` status.
    """
    if user.role != UserRole.ACCOUNTS:
        raise PermissionDenied("Only Accounts can approve requests")

    try:
        request = BillingRequest.objects.select_for_update().get(pk=request_id)
    except BillingRequest.DoesNotExist:
        raise NotFound("Request not found") from None

    validate_transition(request.status, RequestStatus.APPROVED)

    request.status = RequestStatus.APPROVED
    request.save(update_fields=["status", "updated_at"])

    ReviewNote.objects.create(
        request=request,
        reviewed_by=user,
        decision="APPROVED",
        note=note,
    )

    invoice = Invoice.objects.create(
        request=request,
        invoice_number=generate_invoice_number(),
        amount=request.amount,
        status=InvoiceStatus.ISSUED,
    )

    log_audit(
        entity_type="BillingRequest",
        entity_id=request.id,
        actor=user,
        action="APPROVED",
        detail=f"Request approved by Accounts. Note: {note}",
    )
    log_audit(
        entity_type="Invoice",
        entity_id=invoice.id,
        actor=user,
        action="INVOICE_ISSUED",
        detail=f"Invoice {invoice.invoice_number} issued for {request.amount} BDT",
    )
    return request


@transaction.atomic
def reject_request(*, request_id: int, user: User, note: str) -> BillingRequest:
    """Reject a pending request and write audit entries.

    Args:
        request_id: Primary key of the billing request to reject.
        user: Authenticated Accounts user performing the review.
        note: Mandatory review note explaining the rejection.

    Returns:
        The updated ``BillingRequest`` in ``REJECTED`` status.

    Raises:
        PermissionDenied: If ``user`` is not in the Accounts role.
        NotFound: If no billing request exists for ``request_id``.
        ValidationError: If the request is not in ``PENDING`` status.
    """
    if user.role != UserRole.ACCOUNTS:
        raise PermissionDenied("Only Accounts can reject requests")

    try:
        request = BillingRequest.objects.select_for_update().get(pk=request_id)
    except BillingRequest.DoesNotExist:
        raise NotFound("Request not found") from None

    validate_transition(request.status, RequestStatus.REJECTED)

    request.status = RequestStatus.REJECTED
    request.save(update_fields=["status", "updated_at"])

    ReviewNote.objects.create(
        request=request,
        reviewed_by=user,
        decision="REJECTED",
        note=note,
    )

    log_audit(
        entity_type="BillingRequest",
        entity_id=request.id,
        actor=user,
        action="REJECTED",
        detail=f"Request rejected by Accounts. Note: {note}",
    )
    return request
