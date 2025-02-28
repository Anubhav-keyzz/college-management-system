from django.urls import path
from . import views
from users.views import login_view, logout_view

urlpatterns = [
    path('', lambda r: __import__('django.shortcuts', fromlist=['redirect']).redirect('dashboard'), name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/',   views.export_pdf,   name='export_pdf'),
]
