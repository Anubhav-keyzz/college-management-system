"""
courses/apps.py — Application configuration for the 'courses' app.
"""
from django.apps import AppConfig  # Base class for app configuration


class CoursesConfig(AppConfig):
    """App config for 'courses' — uses BigAutoField as the default PK type."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"
