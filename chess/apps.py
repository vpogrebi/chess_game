"""Django application configuration for the chess app.

This module defines the AppConfig class for the chess application,
specifying app metadata and default behavior.

Configuration includes:
- App name and label
- Default primary key field type
- Application-specific settings

"""

from django.apps import AppConfig


class ChessConfig(AppConfig):
    """Configuration class for the chess application.
    
    Defines app-specific settings and metadata for Django
    to properly recognize and configure the chess application.
    
    Attributes:
        default_auto_field: Default primary key field type for models.
        name: Python dotted path to the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chess'
