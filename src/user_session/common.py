from flask import session

def get_identifier_and_role(data):
    """
    Get identifier and role, preferring session data over socket data.
    """
    
    user_id = session.get('user_id') or data.get('user_id')
    advisor_id = session.get('advisor_id') or data.get('advisor_id')
    role = session.get('role')
    identifier = user_id if role == 'client' else advisor_id
    return identifier, role, user_id, advisor_id