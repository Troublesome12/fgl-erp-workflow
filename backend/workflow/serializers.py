"""Django REST Framework serializers for request/response validation and shaping."""

from decimal import Decimal
from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from workflow.models import AuditLog, BillingRequest, Invoice, ReviewNote, User


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and return a JWT access token payload."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        """Authenticate the user and build the token response.

        Args:
            attrs: Validated input containing ``email`` and ``password``.

        Returns:
            Dict with ``access_token``, ``token_type``, ``role``, and ``email``.

        Raises:
            serializers.ValidationError: If credentials are invalid.
        """
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password")
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "token_type": "bearer",
            "role": user.role,
            "email": user.email,
        }


class BillingRequestCreateSerializer(serializers.ModelSerializer):
    """Validate input for creating a new billing request."""

    class Meta:
        model = BillingRequest
        fields = ("client_name", "amount", "billing_period", "description")

    def validate_amount(self, value: Decimal) -> Decimal:
        """Ensure the billing amount is positive.

        Args:
            value: Submitted amount in BDT.

        Returns:
            The validated decimal amount.

        Raises:
            serializers.ValidationError: If amount is zero or negative.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value


class BillingRequestSerializer(serializers.ModelSerializer):
    """Serialize a billing request for list and mutation responses."""

    creator_email = serializers.SerializerMethodField()

    class Meta:
        model = BillingRequest
        fields = (
            "id",
            "created_by",
            "client_name",
            "amount",
            "billing_period",
            "description",
            "status",
            "created_at",
            "updated_at",
            "creator_email",
        )

    def get_creator_email(self, obj: BillingRequest) -> str | None:
        """Return the email of the Sales user who created the request.

        Args:
            obj: Billing request instance.

        Returns:
            Creator email, or None if the relation is not loaded.
        """
        if hasattr(obj, "created_by") and obj.created_by:
            return obj.created_by.email
        return None


class ReviewNoteSerializer(serializers.ModelSerializer):
    """Serialize an Accounts review note on a billing request."""

    request_id = serializers.IntegerField(source="request.id", read_only=True)
    reviewed_by = serializers.IntegerField(source="reviewed_by_id", read_only=True)
    reviewer_email = serializers.SerializerMethodField()

    class Meta:
        model = ReviewNote
        fields = (
            "id",
            "request_id",
            "reviewed_by",
            "decision",
            "note",
            "reviewed_at",
            "reviewer_email",
        )

    def get_reviewer_email(self, obj: ReviewNote) -> str | None:
        """Return the email of the reviewer.

        Args:
            obj: Review note instance.

        Returns:
            Reviewer email, or None if unavailable.
        """
        return obj.reviewed_by.email if obj.reviewed_by else None


class InvoiceSerializer(serializers.ModelSerializer):
    """Serialize an invoice with denormalized request context."""

    request_id = serializers.IntegerField(source="request.id", read_only=True)
    client_name = serializers.SerializerMethodField()
    billing_period = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
            "id",
            "request_id",
            "invoice_number",
            "amount",
            "issued_at",
            "status",
            "client_name",
            "billing_period",
        )

    def get_client_name(self, obj: Invoice) -> str | None:
        """Return the client name from the linked billing request.

        Args:
            obj: Invoice instance.

        Returns:
            Client name string, or None if the request relation is missing.
        """
        return obj.request.client_name if obj.request else None

    def get_billing_period(self, obj: Invoice) -> str | None:
        """Return the billing period from the linked billing request.

        Args:
            obj: Invoice instance.

        Returns:
            Billing period string, or None if the request relation is missing.
        """
        return obj.request.billing_period if obj.request else None


class BillingRequestDetailSerializer(BillingRequestSerializer):
    """Extended billing request payload including review notes and invoice."""

    review_notes = ReviewNoteSerializer(many=True, read_only=True)
    invoice = serializers.SerializerMethodField()

    class Meta(BillingRequestSerializer.Meta):
        fields = (*BillingRequestSerializer.Meta.fields, "review_notes", "invoice")

    def get_invoice(self, obj: BillingRequest) -> dict[str, Any] | None:
        """Return nested invoice data when the request has been approved.

        Args:
            obj: Billing request instance.

        Returns:
            Serialized invoice dict, or None when no invoice exists yet.
        """
        try:
            return InvoiceSerializer(obj.invoice).data
        except Invoice.DoesNotExist:
            return None


class ReviewActionSerializer(serializers.Serializer):
    """Validate approve/reject payload from Accounts users."""

    note = serializers.CharField(min_length=1)


class InvoiceMetricsSerializer(serializers.Serializer):
    """Serialize management dashboard summary metrics."""

    total_pending = serializers.IntegerField()
    total_approved_this_month = serializers.IntegerField()
    total_invoiced_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_invoices = serializers.IntegerField()


class AuditLogSerializer(serializers.ModelSerializer):
    """Serialize an append-only audit log entry."""

    actor_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "entity_type",
            "entity_id",
            "actor_id",
            "action",
            "detail",
            "timestamp",
            "actor_email",
        )

    def get_actor_email(self, obj: AuditLog) -> str | None:
        """Return the email of the user who performed the action.

        Args:
            obj: Audit log instance.

        Returns:
            Actor email, or None if unavailable.
        """
        return obj.actor.email if obj.actor else None
