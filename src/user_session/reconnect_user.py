from flask import session
from extensions import app, socketio
from src.db_management.db_configurations import redis_get, redis_set, redis_users_sessions
from src.user_session.common import get_identifier_and_role
from passkeys_pairs_generation import generate_passkeys_pairs_on_demand, get_passkeys_pairs_and_timer



# Listening for socket messages to mark user reconnected
@socketio.on('reconnect_user')
def handle_reconnect_user(data):
    """
    Handles user reconnection after a temporary disconnection state.
    
    If the user was marked as "disconnecting", the status is reset to
    "active" and passkeys pairs are regenerated only if required.
    
    Args:
        data (dict): Payload containing user identification data.
        
    Returns:
        dict: Reconnection status information.
    """
    
    identifier, role, user_id, advisor_id = get_identifier_and_role(data)
    
    if identifier and role:
        active_key = f"active_status:{role}:{identifier}"
        
        # Check if the status was "disconnecting"
        current_status = redis_get(redis_users_sessions, active_key)
        
        if current_status == "disconnecting":
            # Reset the status to "active"
            redis_set(redis_users_sessions, active_key, "active")
            
            app.logger.info(f"{identifier} reconnected. Status reset to active.")
            
            # Regenerate passkeys pairs only if necessary
            if role == 'client':
                
                # First check if passkeys pairs really need to be regenerated
                current_passwords = get_passkeys_pairs_and_timer(user_id, advisor_id)
                if not current_passwords['user_passkey'] or current_passwords['user_ttl'] <= 0:
                    generate_passkeys_pairs_on_demand(user_id, advisor_id)
            
            return {"status": "reconnected"}
        
        return {"status": "already_active"}