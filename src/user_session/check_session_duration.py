from extensions import socketio
from typing import cast
from src.db_management.db_configurations import redis_set, redis_users_sessions
from src.user_session.common import get_identifier_and_role
from src.user_session.auto_disconnect_user import auto_disconnect_user



# Session duration check route
@socketio.on('check_session_duration')
def handle_check_session_duration(data):
    """
    Checks the remaining session time and triggers logout if necessary.
    This function is called periodically from the frontend.
    """
    try:
        identifier, role, user_id, advisor_id = get_identifier_and_role(data)

        if identifier and role:
            connection_key = f"connection_status:{role}:{identifier}"
            
            # Check the TTL of the connection
            session_duration_ttl = cast(int, redis_users_sessions.ttl(connection_key))
            
            # If the TTL is less than 90 seconds and is a valid number
            if isinstance(session_duration_ttl, (int, float)) and session_duration_ttl <= 90:
                # The session has already expired or is about to expire
                redis_set(redis_users_sessions, connection_key, "disconnecting")
                print("Session expired or about to expire")
                socketio.start_background_task(
                    auto_disconnect_user, 
                    user_id, 
                    advisor_id, 
                    role
                )
    except Exception as e:
        print(f"Error checking session duration: {e}")