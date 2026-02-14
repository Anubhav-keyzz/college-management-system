# Register Attendance models with Django admin panel

"""
attendance/admin.py — Register attendance models with Django's admin panel.

Uses a TabularInline so that AttendanceRecords can be edited
directly inside the AttendanceSession admin page.
"""

from django.contrib import admin   # Django admin framework
from .models import AttendanceSession, AttendanceRecord  # Our two attendance models


class RecordInline(admin.TabularInline):
    """
    Inline editor for AttendanceRecord within the AttendanceSession admin page.

    TabularInline renders each record as a row in a compact table,
    allowing admins to view/edit all records for a session on one page.

    extra=0 means no empty blank rows are shown by default.
    """
    model = AttendanceRecord
    extra = 0  # Don't show empty extra rows


@admin.register(AttendanceSession)
class SessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for AttendanceSession.

    list_display — columns shown in the session list table
    inlines      — embed the RecordInline so records are editable within the session
    """
    list_display = ['classroom', 'date', 'taken_by']
    inlines = [RecordInline]  # Show all attendance records inside the session page
