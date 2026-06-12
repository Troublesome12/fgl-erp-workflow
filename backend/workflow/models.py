"""Django ORM models for the ERP billing workflow domain.

Defines users, billing requests, review notes, invoices, and append-only audit logs
used by the Sales → Accounts → Management approval pipeline.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserRole(models.TextChoices):
    """Application roles that control API access and workflow actions."""

    SALES = "SALES", "Sales"
    ACCOUNTS = "ACCOUNTS", "Accounts"
    MANAGEMENT = "MANAGEMENT", "Management"


class RequestStatus(models.TextChoices):
    """Lifecycle states for a billing request."""

    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class InvoiceStatus(models.TextChoices):
    """Lifecycle states for an issued invoice."""

    ISSUED = "ISSUED", "Issued"
    PAID = "PAID", "Paid"


class UserManager(BaseUserManager):
    """Custom manager for email-based user creation."""

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> "User":
        """Create and persist a user with a hashed password.

        Args:
            email: Unique login email address.
            password: Plain-text password to hash, or None for an unusable password.
            **extra_fields: Additional model fields (e.g. ``role``).

        Returns:
            The newly created ``User`` instance.

        Raises:
            ValueError: If ``email`` is empty.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Authenticated user identified by email with a single application role."""

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        """Return the user's email address.

        Returns:
            Email string used as the human-readable identifier.
        """
        return self.email


class BillingRequest(models.Model):
    """Sales-submitted billing request awaiting Accounts review."""

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="billing_requests")
    client_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_requests"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return client name and current status.

        Returns:
            Formatted label, e.g. ``"Acme Corp (PENDING)"``.
        """
        return f"{self.client_name} ({self.status})"


class ReviewNote(models.Model):
    """Accounts review decision and note attached to a billing request."""

    request = models.ForeignKey(BillingRequest, on_delete=models.CASCADE, related_name="review_notes")
    reviewed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="review_notes")
    decision = models.CharField(max_length=20)
    note = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review_notes"

    def __str__(self) -> str:
        """Return decision and parent request id.

        Returns:
            Formatted label, e.g. ``"APPROVED on request 3"``.
        """
        return f"{self.decision} on request {self.request_id}"


class Invoice(models.Model):
    """Invoice auto-generated when a billing request is approved."""

    request = models.OneToOneField(BillingRequest, on_delete=models.PROTECT, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.ISSUED)

    class Meta:
        db_table = "invoices"
        ordering = ["-issued_at"]

    def __str__(self) -> str:
        """Return the unique invoice number.

        Returns:
            Invoice number string, e.g. ``"INV-2026-0001"``.
        """
        return self.invoice_number


class AuditLog(models.Model):
    """Append-only record of a workflow action for auditability."""

    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField()
    actor = models.ForeignKey(User, on_delete=models.PROTECT, related_name="audit_logs")
    action = models.CharField(max_length=50)
    detail = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["timestamp"]

    def __str__(self) -> str:
        """Return action and target entity reference.

        Returns:
            Formatted label, e.g. ``"APPROVED on BillingRequest:3"``.
        """
        return f"{self.action} on {self.entity_type}:{self.entity_id}"
