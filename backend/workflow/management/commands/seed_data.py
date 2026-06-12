"""Management command to populate demo users and sample billing data."""

from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from workflow.models import (
    BillingRequest,
    Invoice,
    InvoiceStatus,
    RequestStatus,
    ReviewNote,
    User,
    UserRole,
)
from workflow.services.workflow import log_audit

SEED_USERS: list[tuple[str, str, UserRole]] = [
    ("sales@fgl.demo", "demo1234", UserRole.SALES),
    ("accounts@fgl.demo", "demo1234", UserRole.ACCOUNTS),
    ("management@fgl.demo", "demo1234", UserRole.MANAGEMENT),
]

SEED_REQUESTS: list[tuple[str, Decimal, str, str, str]] = [
    ("Acme Corp", Decimal("150000.00"), "May 2026", "Monthly cloud hosting — May 2026", RequestStatus.PENDING),
    ("Beta Industries", Decimal("85000.50"), "May 2026", "Managed services retainer", RequestStatus.PENDING),
    ("Gamma Ltd", Decimal("220000.00"), "June 2026", "Enterprise license renewal", RequestStatus.PENDING),
    ("Delta Systems", Decimal("45000.00"), "April 2026", "Support package — Q2", RequestStatus.APPROVED),
    ("Echo Partners", Decimal("310000.00"), "May 2026", "Custom development milestone 2", RequestStatus.APPROVED),
    ("Foxtrot Co", Decimal("12000.00"), "May 2026", "Duplicate billing — rejected", RequestStatus.REJECTED),
]


class Command(BaseCommand):
    """Seed demo users, billing requests, invoices, and audit logs on first run."""

    help = "Seed demo users and billing requests"

    def handle(self, *args: Any, **options: Any) -> None:
        """Create seed data when the database has no users yet.

        Args:
            *args: Positional arguments from the management command runner.
            **options: Keyword options from the management command runner.

        Returns:
            None. Writes status messages to stdout.
        """
        if User.objects.exists():
            self.stdout.write(self.style.WARNING("Database already seeded — skipping"))
            return

        users: dict[str, User] = {}
        for email, password, role in SEED_USERS:
            user = User.objects.create_user(email=email, password=password, role=role)
            users[email] = user

        sales_user = users["sales@fgl.demo"]
        accounts_user = users["accounts@fgl.demo"]
        invoice_counter = 0

        for client_name, amount, period, description, request_status in SEED_REQUESTS:
            billing_request = BillingRequest.objects.create(
                created_by=sales_user,
                client_name=client_name,
                amount=amount,
                billing_period=period,
                description=description,
                status=request_status,
            )

            log_audit(
                entity_type="BillingRequest",
                entity_id=billing_request.id,
                actor=sales_user,
                action="CREATED",
                detail=f"Seed: billing request for {client_name}",
            )

            if request_status == RequestStatus.APPROVED:
                invoice_counter += 1
                invoice = Invoice.objects.create(
                    request=billing_request,
                    invoice_number=f"INV-2026-{invoice_counter:04d}",
                    amount=amount,
                    status=InvoiceStatus.ISSUED,
                )
                ReviewNote.objects.create(
                    request=billing_request,
                    reviewed_by=accounts_user,
                    decision="APPROVED",
                    note="Approved during seed data setup.",
                )
                log_audit(
                    entity_type="BillingRequest",
                    entity_id=billing_request.id,
                    actor=accounts_user,
                    action="APPROVED",
                    detail="Seed: request approved",
                )
                log_audit(
                    entity_type="Invoice",
                    entity_id=invoice.id,
                    actor=accounts_user,
                    action="INVOICE_ISSUED",
                    detail=f"Seed: invoice {invoice.invoice_number} issued",
                )
            elif request_status == RequestStatus.REJECTED:
                ReviewNote.objects.create(
                    request=billing_request,
                    reviewed_by=accounts_user,
                    decision="REJECTED",
                    note="Duplicate entry — please consolidate with existing request.",
                )
                log_audit(
                    entity_type="BillingRequest",
                    entity_id=billing_request.id,
                    actor=accounts_user,
                    action="REJECTED",
                    detail="Seed: request rejected as duplicate",
                )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully"))
