"""Custom middleware for the chess application.

This module provides custom middleware classes for handling
request/response processing specific to the chess application.

Currently includes:
- DebugMiddleware: Simple middleware for debugging requests

"""

from typing import Any, Callable
from django.http import HttpRequest, HttpResponse
class DebugMiddleware:
    """Simple debug middleware for request/response logging.
    
    A basic middleware implementation that can be used for debugging
    HTTP requests and responses in the chess application.
    
    Attributes:
        get_response: The next middleware or view callable.
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and return the response.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            HttpResponse: The response from the next middleware or view.
        """
        response = self.get_response(request)
        return response
