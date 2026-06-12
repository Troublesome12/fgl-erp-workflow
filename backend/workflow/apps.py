"""Django application configuration for the workflow app."""

from django.apps import AppConfig


class WorkflowConfig(AppConfig):
    """Register the ``workflow`` application with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "workflow"
