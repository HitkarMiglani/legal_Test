"""
Authentication module for LuminaryAI
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config

class AuthManager:
    """Handle user authentication and authorization"""
    
    def __init__(self):
        self.secret_key = Config.JWT_SECRET
        self.algorithm = Config.JWT_ALGORITHM
        self.expiration_hours = Config.JWT_EXPIRATION_HOURS
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: int, username: str, role: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def decode_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
    
    def token_required(self, f):
        """Decorator to protect routes with JWT authentication"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # Check for token in headers
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'message': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            
            try:
                payload = self.decode_token(token)
                request.current_user = payload
            except Exception as e:
                return jsonify({'message': str(e)}), 401
            
            return f(*args, **kwargs)
        
        return decorated
    
    def role_required(self, allowed_roles):
        """Decorator to check user role"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not hasattr(request, 'current_user'):
                    return jsonify({'message': 'Authentication required'}), 401
                
                user_role = request.current_user.get('role')
                if user_role not in allowed_roles:
                    return jsonify({'message': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            
            return decorated
        
        return decorator

# Global auth manager instance
auth_manager = AuthManager()
