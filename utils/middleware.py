"""
Middleware for LuminaryAI Flask app
"""
import time
import uuid
from functools import wraps
from flask import request, g
from utils.logger import logger
from utils.exceptions import RateLimitError
from config import Config

# In-memory rate limit store
rate_limit_store = {}


def request_logging_middleware(app):
    """Add request logging middleware"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())
        g.user_id = None
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'endpoint': request.endpoint,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
        )
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'endpoint': request.endpoint,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user_id': getattr(g, 'user_id', None)
            }
        )
        
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler"""
        from utils.exceptions import LuminaryException
        from flask import jsonify
        
        request_id = getattr(g, 'request_id', 'unknown')
        
        if isinstance(e, LuminaryException):
            logger.error(
                f"LuminaryException: {e.message}",
                extra={
                    'request_id': request_id,
                    'error_code': e.error_code,
                    'details': e.details,
                    'exception_type': type(e).__name__
                },
                exc_info=True
            )
            return jsonify(e.to_dict()), 400
        
        # Generic exception
        logger.error(
            f"Unhandled exception: {str(e)}",
            extra={
                'request_id': request_id,
                'exception_type': type(e).__name__,
                'endpoint': request.endpoint if request else None,
                'path': request.path if request else None
            },
            exc_info=True
        )
        
        return jsonify({
            'error': 'INTERNAL_SERVER_ERROR',
            'message': 'An internal error occurred',
            'request_id': request_id
        }), 500
