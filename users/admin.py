# Register CustomUser model with Django admin panel

"""
users/admin.py — Register CustomUser with Django's admin panel.

We extend Django's built-in UserAdmin so that our extra fields
(role, phone, address, date_of_birth) appear in the admin UI,
while retaining all the default user management features.
"""

from django.contrib import admin                         # Django admin framework
from django.contrib.auth.admin import UserAdmin          # Built-in UserAdmin configuration
from .models import CustomUser                           # Our custom user model


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser.

    list_display  — columns shown in the user list view
    list_filter   — sidebar filters (filter by role)
    fieldsets     — groups of fields shown on the user detail/edit page.
                    We append our custom fields to Django's default fieldsets.
    """

    # Columns shown in the admin user list table
    list_display = ['username', 'email', 'role', 'first_name', 'last_name']

    # Add a sidebar filter so admins can quickly filter users by role
    list_filter = ['role']

    # Append an 'Extra' section to the default UserAdmin fieldsets
    # that includes our CMS-specific profile fields
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {
            'fields': ('role', 'phone', 'address', 'date_of_birth')
        }),
    )
