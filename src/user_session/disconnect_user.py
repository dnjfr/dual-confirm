from extensions import socketio
from src.db_management.db_configurations import redis_set, redis_users_sessions
from src.user_session.common import get_identifier_and_role
from src.user_session.auto_disconnect_user import auto_disconnect_user


@socketio.on('disconnect_user')
def handle_disconnect_user(data):
    """
    Marks a user as inactive and initiates a logout countdown.
    
    The function updates the activity status to "disconnecting"
    and starts a background task to automatically disconnect
    the user after the inactivity timeout.
    
    Args:
        data (dict): Payload containing user identification data.
    """
    
    identifier, role, user_id, advisor_id = get_identifier_and_role(data)
    
    if identifier and role:
        active_key = f"active_status:{role}:{identifier}"
        
        # Change activity status from "active" to "disconnecting"
        redis_set(redis_users_sessions, active_key, "disconnecting")
        
        # Start a thread for automatic disconnection
        socketio.start_background_task(
            auto_disconnect_user,
            user_id, 
            advisor_id, 
            role
        )
        
        print(f"{identifier} is expiring. Logout countdown begins.")
