"""Custom exception handling for the REST API."""

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Normalize DRF error responses to a consistent ``{"detail": "..."}`` shape.

    Args:
        exc: Exception raised during request handling.
        context: DRF exception context (request, view, etc.).

    Returns:
        DRF ``Response`` with normalized error body, or None if unhandled.
    """
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict):
        detail = response.data.get("detail")
        if detail is not None and len(response.data) == 1:
            response.data = {"detail": str(detail)}
    return response
