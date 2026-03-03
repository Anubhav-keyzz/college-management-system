# Core URL patterns - login, logout, dashboard

"""
core/urls.py — URL patterns for the core app.

These paths are mounted at the project root (/) by the root URL configuration.
Includes the login and logout views re-exported from the users app.
"""

from django.urls import path           # URL pattern builder
from . import views                    # Core views (dashboard, exports)
from users.views import login_view, logout_view  # Auth views live in users app


urlpatterns = [
    # Root URL: immediately redirect to the dashboard
    # Uses a lambda to avoid importing redirect at module level
    path(
        '',
        lambda r: __import__(
            'django.shortcuts', fromlist=['redirect']
        ).redirect('dashboard'),
        name='home',
    ),

    # Login page — renders the form and authenticates on POST (/login/)
    path('login/', login_view, name='login'),

    # Logout — clears session and redirects to login page (/logout/)
    path('logout/', logout_view, name='logout'),

    # Main dashboard — role-specific summary page (/dashboard/)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Export all CMS data as a styled Excel file — admin only (/export/excel/)
    path('export/excel/', views.export_excel, name='export_excel'),

    # Export all CMS data as a formatted PDF — admin only (/export/pdf/)
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
