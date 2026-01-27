# Django project settings and configuration
# Database, installed apps, middleware, templates

"""
settings.py — Central Django configuration for the College Management System.

All project-wide settings are defined here: database, installed apps,
middleware, templates, static/media file paths, authentication, etc.
"""

from pathlib import Path  # Used to build OS-independent file paths

# ─── Base Directory ───────────────────────────────────────────────────────────
# Build paths inside the project like: BASE_DIR / 'subdir'
# resolve().parent.parent goes up two levels from this file to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ─────────────────────────────────────────────────────────────────
# SECURITY WARNING: keep the secret key secret in production!
# Used for cryptographic signing of cookies, CSRF tokens, sessions, etc.
SECRET_KEY = 'django-insecure-cms-college-2024-changeme'

# SECURITY WARNING: don't run with DEBUG=True in production.
# When True, Django shows detailed error pages instead of 500 pages.
DEBUG = True

# Hosts/domains that this Django site is allowed to serve.
# '*' means any host — restrict this in production to your real domain.
ALLOWED_HOSTS = ['*']

# ─── Installed Applications ───────────────────────────────────────────────────
# Django built-in apps + our custom CMS apps.
INSTALLED_APPS = [
    'django.contrib.admin',        # Admin interface at /django-admin/
    'django.contrib.auth',         # Authentication framework
    'django.contrib.contenttypes', # Generic relations between models
    'django.contrib.sessions',     # Session storage (used for login state)
    'django.contrib.messages',     # Flash messages (success/error notifications)
    'django.contrib.staticfiles',  # Static file management (CSS, JS)
    # CMS custom apps:
    'core',        # Dashboard, export (Excel/PDF)
    'users',       # CustomUser model and auth views
    'courses',     # Course management
    'classes',     # Classroom management
    'attendance',  # Attendance tracking
    'assignments', # Assignment creation, submission, grading
]

# ─── Middleware ───────────────────────────────────────────────────────────────
# Middleware is executed in order for every request/response cycle.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # HTTPS redirect, security headers
    'django.contrib.sessions.middleware.SessionMiddleware',      # Enables session support
    'django.middleware.common.CommonMiddleware',                 # URL normalization (trailing slash, etc.)
    'django.middleware.csrf.CsrfViewMiddleware',                 # CSRF protection on POST requests
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # Attaches request.user to every request
    'django.contrib.messages.middleware.MessageMiddleware',      # Enables flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    # Adds X-Frame-Options header
]

# ─── URL Configuration ────────────────────────────────────────────────────────
# The root URL configuration module (college_management/urls.py)
ROOT_URLCONF = 'college_management.urls'

# ─── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    # Look for templates in the top-level 'templates/' directory
    'DIRS': [BASE_DIR / 'templates'],
    # Also auto-discover templates in each app's 'templates/' subdirectory
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',    # Adds 'debug' variable to templates
            'django.template.context_processors.request',  # Adds 'request' to templates
            'django.contrib.auth.context_processors.auth', # Adds 'user' and 'perms' to templates
            'django.contrib.messages.context_processors.messages',  # Adds 'messages' to templates
        ]
    },
}]

# ─── WSGI Application ─────────────────────────────────────────────────────────
# Entry point for WSGI-compatible web servers (e.g., gunicorn, uWSGI)
WSGI_APPLICATION = 'college_management.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
# Using SQLite for development — switch to PostgreSQL/MySQL in production
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',  # Database file stored in the project root
}}

# ─── Authentication ───────────────────────────────────────────────────────────
# Use our custom user model instead of Django's built-in User
AUTH_USER_MODEL = 'users.CustomUser'

# Redirect users to login page if they access a @login_required view
LOGIN_URL = '/login/'
# After a successful login, redirect here
LOGIN_REDIRECT_URL = '/dashboard/'
# After logout, redirect here
LOGOUT_REDIRECT_URL = '/login/'

# ─── Static & Media Files ─────────────────────────────────────────────────────
# URL prefix for static assets (CSS, JS, images bundled with the project)
STATIC_URL = '/static/'
# Directories where Django looks for static files during development
STATICFILES_DIRS = [BASE_DIR / 'static']

# URL prefix for user-uploaded media files (assignment files, submissions)
MEDIA_URL = '/media/'
# Filesystem location where uploaded files are stored
MEDIA_ROOT = BASE_DIR / 'media'

# ─── Miscellaneous ────────────────────────────────────────────────────────────
# Default primary key type for models that don't specify one explicitly
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation rules — empty list means no complexity rules enforced.
# In production, add validators like MinimumLengthValidator, etc.
AUTH_PASSWORD_VALIDATORS = []
