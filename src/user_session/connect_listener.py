from extensions import socketio
from src.user_session.validate_socketio_session import validate_socketio_session


@socketio.on('connect')
def handle_connect():
    """
    Validates a Socket.IO connection request.
    
    The connection is accepted only if the associated Flask session
    is valid; otherwise, the connection is rejected.
    """
    
    if not validate_socketio_session():
        return False  # Rejects the connection