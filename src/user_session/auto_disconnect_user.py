import time
from flask import session
from extensions import app
from src.db_management.db_configurations import redis_users_sessions, redis_get
from src.routes.logout import logout


# Inactivity timeout delay
inacitivy_time_out = 180


# Automatically disconnect a user when status is "disconnecting" and countdown to 0 function
def auto_disconnect_user(user_id, advisor_id, role):
    """
    Disconnect a user when status is "disconnecting" and countdown to 0
    """
    
    identifier = user_id if role == 'client' else advisor_id
    
    # Key to check user activity status
    connection_key = f"connection_status:{role}:{identifier}"
    active_key = f"active_status:{role}:{identifier}"
    
    # Timeout trigger
    print("Wait 180 seconds")
    time.sleep(inacitivy_time_out)
    
    # Check both statuses
    current_active_status = redis_get(redis_users_sessions, active_key)
    current_connection_status = redis_get(redis_users_sessions,connection_key)
    
    if current_active_status == "disconnecting" or current_connection_status == "disconnecting":
        print("Déconnection")
        # The user has not returned, we are logging out
        with app.test_request_context('/logout'):
            # Using mocked session with user information
            session['user_id'] = user_id
            session['advisor_id'] = advisor_id
            session['role'] = role
            session['jwt_token'] = redis_get(redis_users_sessions, f"otp:{identifier}")
            
            # Call the logout function
            logout()
        
        app.logger.info(f"Automatic disconnection for {identifier}")