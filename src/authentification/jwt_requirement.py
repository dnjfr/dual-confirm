from functools import wraps
from flask import redirect, current_app, session, url_for
from src.db_management.db_configurations import redis_users_sessions, redis_get


def jwt_required(otp_manager):
    """
    Decorator factory that secures Flask routes using JWT-based OTP validation.
    
    This decorator verifies that:
    - A JWT token exists in the user session
    - The token is present in Redis
    - The token is valid and not expired
    - The token matches the expected identity based on the user role (advisor or client)
    
    If any validation step fails, the user session is cleared and
    the request is redirected to the login page.
    
    Args:
    otp_manager (OTPManager): Instance responsible for decoding and validating OTP JWT tokens.
    
    Returns:
    callable: A decorator that wraps a Flask route with JWT authentication logic.
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_app.logger.debug("Entry in jwt_required")
            
            token = session.get('jwt_token')
            user_id = session.get('user_id')
            advisor_id = session.get('advisor_id')
            role = session.get('role')
            
            if not token:
                current_app.logger.error("No token found")
                session.clear()
                return redirect(url_for('login'))
            
            # Check token existence in Redis
            redis_key = f"otp:{user_id or advisor_id}"
            stored_token = redis_get(redis_users_sessions, redis_key)
            
            if not stored_token:
                current_app.logger.error("Token not found in Redis")
                session.clear()
                return redirect(url_for('login'))
            
            # Validation adapted according to the role
            if role == 'advisor':
                validation_result = otp_manager.validate_otp(token=token, advisor_id=advisor_id)
            elif role == 'client':
                validation_result = otp_manager.validate_otp(token=token, user_id=user_id)
            else:
                current_app.logger.error("Invalid role")
                session.clear()
                return redirect(url_for('login'))
            
            if not validation_result:
                current_app.logger.error(f"Invalid token for role {role}")
                session.clear()
                return redirect(url_for('login'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
