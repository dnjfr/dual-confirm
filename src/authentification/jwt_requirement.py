from functools import wraps
from flask import redirect, current_app, session, url_for
from src.db_management.db_configurations import redis_users_sessions, redis_get

# Decorator connection
def jwt_required(otp_manager):
    """
    Decorator to secure routes with JWT

    Args:
    otp_manager (OTPManager): OTP manager instance
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
