"""
Custom Exceptions
Application-specific exception classes
"""
from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """Authorization failed"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """Data validation error"""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class DatabaseError(AppException):
    """Database operation error"""
    
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceError(AppException):
    """External service error"""
    
    def __init__(self, message: str = "External service error"):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class RateLimitError(AppException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class WebhookError(AppException):
    """Webhook operation error"""
    
    def __init__(self, message: str = "Webhook error occurred"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentError(AppException):
    """Agent operation error"""
    
    def __init__(self, message: str = "Agent error occurred"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_exception(exc: AppException) -> HTTPException:
    """
    Convert application exception to HTTP exception
    
    Args:
        exc: Application exception
        
    Returns:
        HTTP exception
    """
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )