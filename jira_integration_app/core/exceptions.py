"""
Custom exceptions and error handling utilities for the Jira Integration App.
"""
from typing import Dict, Any, Optional
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class JiraBotError(Exception):
    """Base exception class for JiraBot application."""
    def __init__(self, message: str, code: str = "error", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ScrumUpdateError(JiraBotError):
    """Raised when there's an error with scrum updates."""
    pass


class AuthenticationError(JiraBotError):
    """Raised when there's an authentication error."""
    pass


class IntegrationError(JiraBotError):
    """Raised when there's an error with external integrations (Jira, OpenAI)."""
    pass


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Custom exception handler for REST framework views.
    
    Args:
        exc: The caught exception
        context: Additional context about the error
        
    Returns:
        Response object with appropriate error details
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If this is our custom exception
    if isinstance(exc, JiraBotError):
        return Response(
            {
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                    'details': exc.details
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # If this is an unexpected exception
    if response is None:
        return Response(
            {
                'error': {
                    'code': 'internal_error',
                    'message': 'An unexpected error occurred',
                    'details': {'original_error': str(exc)}
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
