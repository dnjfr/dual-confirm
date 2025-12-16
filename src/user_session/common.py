from flask import session

def get_identifier_and_role(data):
    """
    Resolves the active identifier and role for the current session.
    
    The function prioritizes Flask session data over Socket.IO payload
    data to determine the correct user or advisor context.
    
    Args:
        data (dict): Socket.IO payload.
        
    Returns:
        tuple: (identifier, role, user_id, advisor_id)
    """
    
    user_id = session.get('user_id') or data.get('user_id')
    advisor_id = session.get('advisor_id') or data.get('advisor_id')
    role = session.get('role')
    identifier = user_id if role == 'client' else advisor_id
    return identifier, role, user_id, advisor_id