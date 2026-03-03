"""
core/apps.py — Application configuration for the 'core' app.

The core app provides the dashboard, login/logout routing, and
data export views (Excel and PDF). It has no custom models.
"""
from django.apps import AppConfig  # Base class for app configuration


class CoreConfig(AppConfig):
    """App config for 'core' — uses BigAutoField as the default PK type."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
