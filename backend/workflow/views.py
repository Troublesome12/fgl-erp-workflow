"""Django REST Framework API views for the ERP billing workflow."""

from decimal import Decimal
from typing import Any

from django.db.models import Sum
from django.utils import timezone as django_tz
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workflow.models import AuditLog, BillingRequest, Invoice, RequestStatus, UserRole
from workflow.permissions import role_permission
from workflow.serializers import (
    AuditLogSerializer,
    BillingRequestCreateSerializer,
    BillingRequestDetailSerializer,
    BillingRequestSerializer,
    InvoiceMetricsSerializer,
    InvoiceSerializer,
    LoginSerializer,
    ReviewActionSerializer,
)
from workflow.services.workflow import approve_request, create_billing_request, reject_request


class HealthView(APIView):
    """Liveness probe endpoint for container orchestration."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Return a simple health status payload.

        Args:
            request: Incoming HTTP request.

        Returns:
            JSON response ``{"status": "ok"}``.
        """
        return Response({"status": "ok"})


class LoginView(APIView):
    """Issue a JWT access token for demo users."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Authenticate credentials and return token metadata.

        Args:
            request: HTTP request with ``email`` and ``password`` in the body.

        Returns:
            JSON with ``access_token``, ``token_type``, ``role``, and ``email``.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class BillingRequestListCreateView(APIView):
    """List the current Sales user's requests or create a new one."""

    def get_permissions(self) -> list[BasePermission]:
        """Restrict all methods to the Sales role.

        Returns:
            List containing a single Sales role permission instance.
        """
        return [role_permission(UserRole.SALES)()]

    def get(self, request: Request) -> Response:
        """Return billing requests created by the authenticated Sales user.

        Args:
            request: Authenticated HTTP request.

        Returns:
            JSON list of serialized billing requests ordered newest first.
        """
        queryset = (
            BillingRequest.objects.filter(created_by=request.user)
            .select_related("created_by")
            .order_by("-created_at")
        )
        return Response(BillingRequestSerializer(queryset, many=True).data)

    def post(self, request: Request) -> Response:
        """Create a new pending billing request.

        Args:
            request: Authenticated HTTP request with billing request fields.

        Returns:
            HTTP 201 with the serialized created billing request.
        """
        serializer = BillingRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        billing_request = create_billing_request(user=request.user, **serializer.validated_data)
        billing_request = BillingRequest.objects.select_related("created_by").get(pk=billing_request.pk)
        return Response(
            BillingRequestSerializer(billing_request).data,
            status=status.HTTP_201_CREATED,
        )


class BillingRequestPendingView(APIView):
    """Accounts review queue of all pending billing requests."""

    permission_classes = [role_permission(UserRole.ACCOUNTS)]

    def get(self, request: Request) -> Response:
        """Return all billing requests in PENDING status.

        Args:
            request: Authenticated Accounts user request.

        Returns:
            JSON list of pending billing requests ordered oldest first.
        """
        queryset = (
            BillingRequest.objects.filter(status=RequestStatus.PENDING)
            .select_related("created_by")
            .order_by("created_at")
        )
        return Response(BillingRequestSerializer(queryset, many=True).data)


class BillingRequestDetailView(APIView):
    """Retrieve a single billing request with notes, invoice, and audit context."""

    permission_classes = [role_permission(UserRole.SALES, UserRole.ACCOUNTS, UserRole.MANAGEMENT)]

    def get(self, request: Request, pk: int) -> Response:
        """Return full detail for one billing request.

        Args:
            request: Authenticated HTTP request.
            pk: Primary key of the billing request.

        Returns:
            Serialized billing request detail, or 404/403 on failure.
        """
        try:
            billing_request = (
                BillingRequest.objects.select_related("created_by")
                .prefetch_related("review_notes__reviewed_by", "invoice__request")
                .get(pk=pk)
            )
        except BillingRequest.DoesNotExist:
            return Response({"detail": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == UserRole.SALES and billing_request.created_by_id != request.user.id:
            return Response({"detail": "Cannot view this request"}, status=status.HTTP_403_FORBIDDEN)

        return Response(BillingRequestDetailSerializer(billing_request).data)


class ReviewApproveView(APIView):
    """Approve a pending billing request and auto-create an invoice."""

    permission_classes = [role_permission(UserRole.ACCOUNTS)]

    def post(self, request: Request, request_id: int) -> Response:
        """Approve a billing request with a mandatory review note.

        Args:
            request: Authenticated Accounts user request with ``note`` in body.
            request_id: Primary key of the billing request to approve.

        Returns:
            Serialized billing request in APPROVED status.
        """
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        approve_request(request_id=request_id, user=request.user, note=serializer.validated_data["note"])
        billing_request = BillingRequest.objects.select_related("created_by").get(pk=request_id)
        return Response(BillingRequestSerializer(billing_request).data)


class ReviewRejectView(APIView):
    """Reject a pending billing request."""

    permission_classes = [role_permission(UserRole.ACCOUNTS)]

    def post(self, request: Request, request_id: int) -> Response:
        """Reject a billing request with a mandatory review note.

        Args:
            request: Authenticated Accounts user request with ``note`` in body.
            request_id: Primary key of the billing request to reject.

        Returns:
            Serialized billing request in REJECTED status.
        """
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reject_request(request_id=request_id, user=request.user, note=serializer.validated_data["note"])
        billing_request = BillingRequest.objects.select_related("created_by").get(pk=request_id)
        return Response(BillingRequestSerializer(billing_request).data)


class InvoiceListView(APIView):
    """List all issued invoices for Management."""

    permission_classes = [role_permission(UserRole.MANAGEMENT)]

    def get(self, request: Request) -> Response:
        """Return all invoices ordered by issue date descending.

        Args:
            request: Authenticated Management user request.

        Returns:
            JSON list of serialized invoices.
        """
        queryset = Invoice.objects.select_related("request").order_by("-issued_at")
        return Response(InvoiceSerializer(queryset, many=True).data)


class InvoiceDetailView(APIView):
    """Retrieve a single invoice by primary key."""

    permission_classes = [role_permission(UserRole.MANAGEMENT)]

    def get(self, request: Request, pk: int) -> Response:
        """Return one invoice with linked request context.

        Args:
            request: Authenticated Management user request.
            pk: Primary key of the invoice.

        Returns:
            Serialized invoice, or HTTP 404 if not found.
        """
        try:
            invoice = Invoice.objects.select_related("request").get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(InvoiceSerializer(invoice).data)


class InvoiceMetricsView(APIView):
    """Management dashboard aggregate metrics."""

    permission_classes = [role_permission(UserRole.MANAGEMENT)]

    def get(self, request: Request) -> Response:
        """Compute summary counts and totals for the management dashboard.

        Args:
            request: Authenticated Management user request.

        Returns:
            JSON object with pending count, monthly approvals, invoiced value, and invoice count.
        """
        now = django_tz.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        metrics: dict[str, Any] = {
            "total_pending": BillingRequest.objects.filter(status=RequestStatus.PENDING).count(),
            "total_approved_this_month": BillingRequest.objects.filter(
                status=RequestStatus.APPROVED,
                updated_at__gte=month_start,
            ).count(),
            "total_invoiced_value": Invoice.objects.aggregate(total=Sum("amount"))["total"]
            or Decimal("0"),
            "total_invoices": Invoice.objects.count(),
        }
        return Response(InvoiceMetricsSerializer(metrics).data)


class AuditTrailView(APIView):
    """Read-only audit history for a given entity."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, entity_type: str, entity_id: int) -> Response:
        """Return chronological audit log entries for an entity.

        Args:
            request: Authenticated HTTP request (any role).
            entity_type: Model name filter (e.g. ``"BillingRequest"``).
            entity_id: Primary key of the entity.

        Returns:
            JSON list of audit entries, or HTTP 404 when none exist.
        """
        logs = (
            AuditLog.objects.filter(entity_type=entity_type, entity_id=entity_id)
            .select_related("actor")
            .order_by("timestamp")
        )
        if not logs.exists():
            return Response({"detail": "No audit records found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(AuditLogSerializer(logs, many=True).data)
