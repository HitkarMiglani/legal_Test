"""
Custom exception classes for LuminaryAI
"""
from typing import Optional, Dict, Any

class LuminaryException(Exception):
    """Base exception for LuminaryAI"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary"""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details
        }

class AuthenticationError(LuminaryException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTH_ERROR", details)

class AuthorizationError(LuminaryException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Authorization failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)

class ValidationError(LuminaryException):
    """Input validation errors"""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        if field:
            details = details or {}
            details['field'] = field
        super().__init__(message, "VALIDATION_ERROR", details)

class DocumentProcessingError(LuminaryException):
    """Document processing errors"""
    
    def __init__(self, message: str, document_id: str = None, details: Dict[str, Any] = None):
        if document_id:
            details = details or {}
            details['document_id'] = document_id
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", details)

class AIServiceError(LuminaryException):
    """AI service related errors"""
    
    def __init__(self, message: str, service: str = None, details: Dict[str, Any] = None):
        if service:
            details = details or {}
            details['service'] = service
        super().__init__(message, "AI_SERVICE_ERROR", details)

class DatabaseError(LuminaryException):
    """Database related errors"""
    
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        if operation:
            details = details or {}
            details['operation'] = operation
        super().__init__(message, "DATABASE_ERROR", details)

class RateLimitError(LuminaryException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: Dict[str, Any] = None):
        if retry_after:
            details = details or {}
            details['retry_after'] = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR", details)

class NotFoundError(LuminaryException):
    """Resource not found errors"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, details: Dict[str, Any] = None):
        if resource_type or resource_id:
            details = details or {}
            if resource_type:
                details['resource_type'] = resource_type
            if resource_id:
                details['resource_id'] = resource_id
        super().__init__(message, "NOT_FOUND_ERROR", details)

