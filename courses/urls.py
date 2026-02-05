# Course app URL patterns

"""
courses/urls.py — URL patterns for the courses app.
Mounted under /courses/ by the root URL configuration.
"""

from django.urls import path  # URL pattern builder
from . import views           # Views defined in courses/views.py

urlpatterns = [
    # List all courses (/courses/)
    path('', views.course_list, name='course_list'),

    # Detail view for a single course (/courses/<pk>/)
    path('<int:pk>/', views.course_detail, name='course_detail'),

    # Create a new course — admin only (/courses/create/)
    path('create/', views.create_course, name='create_course'),

    # Edit an existing course — admin only (/courses/<pk>/edit/)
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),

    # Delete a course — admin only (/courses/<pk>/delete/)
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
]
