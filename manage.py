#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This script provides Django's management capabilities for the chess project,
allowing administrators to run commands like migrate, runserver, createsuperuser,
and custom management commands.

Usage:
    python manage.py <command> [options]

Common commands:
- runserver: Start the development server
- migrate: Apply database migrations
- createsuperuser: Create an admin user
- collectstatic: Gather static files

"""

from typing import Any
import os
import sys


def main() -> None:
    """Run administrative tasks.
    
    Sets up the Django environment and executes management commands
    from the command line. Handles Django import errors and provides
    helpful error messages for common setup issues.
    
    Raises:
        ImportError: If Django cannot be imported or is not properly configured.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chess_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
