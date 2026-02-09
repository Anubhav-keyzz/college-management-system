# Classes app URL patterns

"""
classes/urls.py — URL patterns for the classes (Classroom) app.
Mounted under /classes/ by the root URL configuration.
"""

from django.urls import path  # URL pattern builder
from . import views           # Views defined in classes/views.py

urlpatterns = [
    # List all classrooms visible to the current user (/classes/)
    path('', views.class_list, name='class_list'),

    # Detail view for a single classroom (/classes/<pk>/)
    path('<int:pk>/', views.class_detail, name='class_detail'),

    # Create a new classroom — admin only (/classes/create/)
    path('create/', views.create_class, name='create_class'),

    # Edit an existing classroom — admin only (/classes/<pk>/edit/)
    path('<int:pk>/edit/', views.edit_class, name='edit_class'),

    # Delete a classroom — admin only (/classes/<pk>/delete/)
    path('<int:pk>/delete/', views.delete_class, name='delete_class'),
]
