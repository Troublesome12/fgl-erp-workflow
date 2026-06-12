"""Role-based permission classes for Django REST Framework views."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from workflow.models import UserRole


class HasRole(BasePermission):
    """Grant access only when the authenticated user's role is allowed.

    Attributes:
        allowed_roles: Tuple of ``UserRole`` value strings permitted for the view.
    """

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check whether the request user's role is in the allowed set.

        Args:
            request: Incoming HTTP request with an authenticated user.
            view: DRF view being accessed; may override ``allowed_roles``.

        Returns:
            True if the user is authenticated and their role is allowed; False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        roles = getattr(view, "allowed_roles", self.allowed_roles)
        return request.user.role in roles


def role_permission(*roles: UserRole) -> type[HasRole]:
    """Build a permission class restricted to the given roles.

    Args:
        *roles: One or more ``UserRole`` enum members.

    Returns:
        A ``HasRole`` subclass with ``allowed_roles`` set to the role value strings.
    """

    class _RolePermission(HasRole):
        allowed_roles = tuple(r.value for r in roles)

    return _RolePermission
