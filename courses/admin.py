# Register Course model with Django admin panel

"""
courses/admin.py — Register Course model with Django's admin panel.
"""

from django.contrib import admin  # Django admin framework
from .models import Course        # Course model from this app


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Course model.

    list_display      — columns shown in the course list table
    filter_horizontal — shows a nicer dual-list widget for the 'students'
                        ManyToMany field instead of a plain multi-select box
    """

    # Columns visible in the admin course list
    list_display = ['code', 'name', 'teacher', 'credits']

    # Use a horizontal filter widget for the ManyToMany 'students' field
    # (makes selecting many students much easier than a plain list)
    filter_horizontal = ['students']
