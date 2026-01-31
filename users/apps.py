"""
users/apps.py — Application configuration for the 'users' app.

Django uses AppConfig subclasses to store metadata about each installed
application and to hook into application startup via ready().
"""

from django.apps import AppConfig  # Base class for app configuration


class UsersConfig(AppConfig):
    """
    Configuration class for the users application.

    default_auto_field — specifies the default primary key type for all
                         models in this app (BigAutoField = 64-bit integer).
    name               — the Python dotted path used in INSTALLED_APPS.
    """

    # Use a 64-bit auto-incrementing integer as the default primary key
    default_auto_field = "django.db.models.BigAutoField"

    # The import name of the application (must match entry in INSTALLED_APPS)
    name = "users"
