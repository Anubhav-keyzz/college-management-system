# Assignments app URL patterns

"""
assignments/urls.py — URL patterns for the assignments app.
Mounted under /assignments/ by the root URL configuration.
"""

from django.urls import path  # URL pattern builder
from . import views           # Views defined in assignments/views.py

urlpatterns = [
    # List all assignments visible to the current user (/assignments/)
    path('', views.assignment_list, name='assignment_list'),

    # Detail view for a single assignment (/assignments/<pk>/)
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),

    # Create a new assignment — teachers and admins only (/assignments/create/)
    path('create/', views.create_assignment, name='create_assignment'),

    # Edit an existing assignment (/assignments/<pk>/edit/)
    path('<int:pk>/edit/', views.edit_assignment, name='edit_assignment'),

    # Delete an assignment (/assignments/<pk>/delete/)
    path('<int:pk>/delete/', views.delete_assignment, name='delete_assignment'),

    # Student submits their work for an assignment (/assignments/<pk>/submit/)
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),

    # Teacher grades a specific submission (/assignments/grade/<sub_id>/)
    path('grade/<int:sub_id>/', views.grade_submission, name='grade_submission'),
]
