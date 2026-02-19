"""
assignments/apps.py — Application configuration for the 'assignments' app.
"""
from django.apps import AppConfig


class AssignmentsConfig(AppConfig):
    """App config for 'assignments' — uses BigAutoField as the default PK type."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "assignments"
