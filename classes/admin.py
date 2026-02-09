# Register Classroom model with Django admin panel

"""
classes/admin.py — Register Classroom with Django's admin panel.
"""

from django.contrib import admin  # Django admin framework
from .models import Classroom     # Classroom model from this app


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Classroom model.

    list_display      — columns shown in the classroom list table
    filter_horizontal — nicer dual-list widget for the 'students' ManyToMany field
    """

    # Columns shown in the admin classroom list
    list_display = ['name', 'section', 'course', 'teacher']

    # Dual-panel widget for selecting multiple students more comfortably
    filter_horizontal = ['students']
