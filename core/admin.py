# Core admin registration

"""
core/admin.py — Admin configuration for the core app.

The core app has no custom models, so no admin registrations are needed here.
Django's built-in admin is still accessible for other apps via the
/django-admin/ URL defined in college_management/urls.py.
"""

from django.contrib import admin  # noqa: F401 — imported for convention; nothing to register
