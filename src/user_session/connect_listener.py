from extensions import socketio
from src.user_session.validate_socketio_session import validate_socketio_session

# Listening to the connection
@socketio.on('connect')
def handle_connect():
    # Check the session before allowing the connection
    if not validate_socketio_session():
        return False  # Rejects the connection