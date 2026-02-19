# Register Assignment and Submission models with admin panel

"""
assignments/admin.py — Register Assignment and AssignmentSubmission
                       with Django's admin panel.
"""

from django.contrib import admin                           # Django admin framework
from .models import Assignment, AssignmentSubmission       # Our assignment models


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Assignment.
    Shows the key fields in the list view so admins can quickly scan assignments.
    """
    # Columns shown in the admin assignment list table
    list_display = ['title', 'classroom', 'uploaded_by', 'due_date', 'max_marks']


@admin.register(AssignmentSubmission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for AssignmentSubmission.
    Shows submission metadata and grading status at a glance.
    """
    # Columns shown in the admin submission list table
    list_display = ['assignment', 'student', 'submitted_at', 'is_graded', 'marks']
