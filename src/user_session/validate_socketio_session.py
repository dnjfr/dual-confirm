from flask import session



# Session validation for Socket.IO function
def validate_socketio_session():
    """
    Validates the current Socket.IO session.
    
    The function checks that the user is logged in and has a valid role
    defined in the Flask session.
    
    Returns:
        bool: True if the session is valid, False otherwise.
    """
    
    try:
        # Retrieve session information
        session_data = session.get('logged_in')
        role = session.get('role')
        
        # Checks that the session is active and has a role defined
        return session_data is not None and role is not None
    except Exception as e:
        print(f"Socket.IO session validation error: {e}")
        return False

