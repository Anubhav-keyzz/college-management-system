# Attendance app URL patterns

"""
attendance/urls.py — URL patterns for the attendance app.
Mounted under /attendance/ by the root URL configuration.
"""

from django.urls import path  # URL pattern builder
from . import views           # Views defined in attendance/views.py

urlpatterns = [
    # List all attendance sessions visible to the current user (/attendance/)
    path('', views.attendance_list, name='attendance_list'),

    # Take (record) attendance for a specific classroom (/attendance/take/<class_id>/)
    path('take/<int:class_id>/', views.take_attendance, name='take_attendance'),

    # View an attendance summary report for a classroom (/attendance/report/<class_id>/)
    path('report/<int:class_id>/', views.attendance_report, name='attendance_report'),

    # View the records for a specific session (/attendance/session/<session_id>/)
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
]
