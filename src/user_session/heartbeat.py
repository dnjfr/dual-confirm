from extensions import app, socketio
from src.user_session.common import get_identifier_and_role
from src.db_management.db_configurations import redis_set, redis_users_sessions

# Listening for socket messages to mark the active user
@socketio.on('heartbeat')
def handle_heartbeat(data):
    identifier, role = get_identifier_and_role(data)

    if identifier and role:
        active_key = f"active_status:{role}:{identifier}"
        redis_set(redis_users_sessions, active_key, "active")
        app.logger.debug(f"Active status refreshed for {identifier} (Role: {role})")