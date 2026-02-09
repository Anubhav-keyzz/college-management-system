"""
classes/apps.py — Application configuration for the 'classes' app.
"""
from django.apps import AppConfig


class ClassesConfig(AppConfig):
    """App config for 'classes' — uses BigAutoField as the default PK type."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "classes"
