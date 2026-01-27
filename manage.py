# Entry point for Django management commands
# Run: python manage.py runserver

#!/usr/bin/env python
"""
manage.py — Django's command-line utility for administrative tasks.

This is the entry point for all Django management commands, e.g.:
  python manage.py runserver
  python manage.py migrate
  python manage.py createsuperuser
"""

import os   # Used to set environment variables
import sys  # Used to read command-line arguments (sys.argv)


def main():
    """
    Main function: configure Django settings and dispatch management commands.

    1. Sets the DJANGO_SETTINGS_MODULE env variable so Django knows
       which settings file to load (college_management/settings.py).
    2. Imports and calls execute_from_command_line(), which parses sys.argv
       and runs the appropriate management command.
    """
    # Tell Django which settings module to use for this project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management.settings')

    try:
        # Import Django's management command runner
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Raise a clear error if Django is not installed in the environment
        raise ImportError(
            "Couldn't import Django. Install it: pip install django"
        ) from exc

    # Pass command-line arguments (e.g. 'runserver', 'migrate') to Django
    execute_from_command_line(sys.argv)


# Only run main() when this script is executed directly (not imported as a module)
if __name__ == '__main__':
    main()
