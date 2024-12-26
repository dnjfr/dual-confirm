from flask import session

def get_identifier_and_role(data):
    """
    Get identifier and role from data and session.
    """
    user_id = data.get('user_id')
    advisor_id = data.get('advisor_id')
    role = session.get('role')
    identifier = user_id if role == 'client' else advisor_id
    return identifier, role