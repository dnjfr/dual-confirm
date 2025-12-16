from extensions import app, socketio
from src.user_session.common import get_identifier_and_role
from src.db_management.db_configurations import redis_set, redis_users_sessions


@socketio.on('heartbeat')
def handle_heartbeat(data):
    """
    Refreshes the user's activity status.
    
    This function is triggered periodically by the frontend to
    indicate that the user is still active and prevent automatic logout.
    
    Args:
        data (dict): Payload containing user identification data.
    """
    
    identifier, role, _, _ = get_identifier_and_role(data)
    
    if identifier and role:
        active_key = f"active_status:{role}:{identifier}"
        redis_set(redis_users_sessions, active_key, "active")
        app.logger.debug(f"Active status refreshed for {identifier} (Role: {role})")