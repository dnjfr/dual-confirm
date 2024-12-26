from flask import session
from extensions import app, socketio
from src.db_management.db_configurations import redis_get, redis_set, redis_users_sessions
from passwords_generation import generate_password_on_demand, get_password_and_timer



# Listening for socket messages to mark user reconnected
@socketio.on('reconnect_user')
def handle_reconnect_user(data):
    user_id = data.get('user_id')
    advisor_id = data.get('advisor_id')
    role = session.get('role')
    identifier = user_id if role == 'client' else advisor_id
    
    if identifier and role:
        active_key = f"active_status:{role}:{identifier}"
        
        # Check if the status was "disconnecting"
        current_status = redis_get(redis_users_sessions, active_key)
        
        if current_status == "disconnecting":
            # Reset the status to "active"
            redis_set(redis_users_sessions, active_key, "active")
            
            app.logger.info(f"{identifier} reconnected. Status reset to active.")
            
            # Regenerate passwords only if necessary
            if role == 'client':
                advisor_id = session.get('advisor_id')
                # First check if passwords really need to be regenerated
                current_passwords = get_password_and_timer(user_id, advisor_id)
                if not current_passwords['user_pwd'] or current_passwords['user_ttl'] <= 0:
                    generate_password_on_demand(user_id, advisor_id)
            
            return {"status": "reconnected"}
        
        return {"status": "already_active"}