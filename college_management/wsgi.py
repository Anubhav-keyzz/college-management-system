# WSGI configuration for deployment

"""
college_management/wsgi.py — WSGI application entry point.

WSGI (Web Server Gateway Interface) is the standard Python interface
between web servers (e.g., gunicorn, uWSGI, Apache mod_wsgi) and
Django. This file exposes the 'application' callable that the server
uses to forward HTTP requests to Django.
"""

import os  # Used to set the DJANGO_SETTINGS_MODULE environment variable

from django.core.wsgi import get_wsgi_application  # Creates the WSGI app object

# Tell Django which settings module to use before building the application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management.settings')

# Build and expose the WSGI application callable.
# Production servers import 'application' from this module.
application = get_wsgi_application()
