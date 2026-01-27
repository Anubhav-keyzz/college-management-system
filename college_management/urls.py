# Main URL configuration
# Routes requests to appropriate app URLs

"""
college_management/urls.py — Root URL configuration for the CMS project.

Django routes incoming HTTP requests by matching their path against the
patterns listed in urlpatterns (top-to-bottom). Each entry delegates
further routing to the app's own urls.py via include().
"""

from django.contrib import admin                          # Django admin site
from django.urls import path, include                    # URL routing helpers
from django.conf import settings                         # Access to project settings
from django.conf.urls.static import static               # Serve media files in development

urlpatterns = [
    # ── Django built-in admin panel ──────────────────────────────────────────
    # Accessible at /django-admin/ (renamed to avoid conflicts with CMS admin)
    path('django-admin/', admin.site.urls),

    # ── Core app: dashboard, login/logout, exports ────────────────────────────
    path('', include('core.urls')),

    # ── Users app: user list, create, edit, delete, profile ──────────────────
    path('users/', include('users.urls')),

    # ── Courses app: course CRUD ───────────────────────────────────────────────
    path('courses/', include('courses.urls')),

    # ── Classes app: classroom CRUD ───────────────────────────────────────────
    path('classes/', include('classes.urls')),

    # ── Attendance app: attendance sessions & reports ─────────────────────────
    path('attendance/', include('attendance.urls')),

    # ── Assignments app: assignment CRUD, submissions, grading ────────────────
    path('assignments/', include('assignments.urls')),

# During development, also serve user-uploaded media files (MEDIA_ROOT)
# under the MEDIA_URL prefix. In production, a web server (nginx) handles this.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
