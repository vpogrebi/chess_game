"""Root URL configuration for the chess project.

This module defines the main URL patterns that route requests
to the appropriate applications. It includes the Django admin interface
and forwards all other requests to the chess application.

URL structure:
- /admin/ - Django admin interface
- / - All chess-related URLs (delegated to chess.urls)

"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chess.urls')),
]
