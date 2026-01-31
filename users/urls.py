# User app URL patterns

"""
users/urls.py — URL patterns for the users app.

These paths are mounted under /users/ by the root URL configuration.
"""

from django.urls import path  # URL pattern builder
from . import views            # Views defined in users/views.py

urlpatterns = [
    # List all users — admin only (/users/)
    path('', views.user_list, name='user_list'),

    # Create a new user — admin only (/users/create/)
    path('create/', views.create_user, name='create_user'),

    # Edit an existing user by primary key — admin only (/users/<pk>/edit/)
    path('<int:pk>/edit/', views.edit_user, name='edit_user'),

    # Delete a user by primary key — admin only (/users/<pk>/delete/)
    path('<int:pk>/delete/', views.delete_user, name='delete_user'),

    # View / update the currently logged-in user's own profile (/users/profile/)
    path('profile/', views.profile, name='profile'),
]
