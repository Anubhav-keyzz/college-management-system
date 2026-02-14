"""
attendance/apps.py — Application configuration for the 'attendance' app.
"""
from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    """App config for 'attendance' — uses BigAutoField as the default PK type."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "attendance"
