from flask import session
from flask_socketio import emit
from extensions import socketio
from src.db_management.db_configurations import users_db_cursor, users_tablename, advisors_tablename, users_advisors_tablename, redis_users_sessions, redis_get
from passwords_generation import get_password_and_timer


@socketio.on('request_update')
def handle_request_update(data=None):
    """
    Handles real-time password updates via Socket.IO.
    
    The function validates the session role (advisor or client),
    verifies access permissions, retrieves user and advisor data,
    and emits updated password information to the client.
    
    Args:
    data (dict, optional): Payload containing request context.
    """
    
    # Verification of received data
    if not data or not isinstance(data, dict):
        # Do not emit anything if this is a first load or missing data
        return
    try:
        # For the advisor: check the customer's selection
        if session.get('role') == 'advisor':
            user_id = data.get('user_id')
            advisor_id = session.get('advisor_id')
            
            # Check if the customer is really selected for this advisor
            selection_key = f"selection_status:{advisor_id}:{user_id}"
            if redis_get(redis_users_sessions, selection_key) != "selected":
                emit('update_passwords', {"error": "Unselected client"})
                return
        
        # For the client: checks that the ID matches their session
        if session.get('role') == 'client':
            user_id = session.get('user_id')
            advisor_id = session.get('advisor_id')
        
        query = f"""
            SELECT us.first_name, us.last_name, ad.first_name, ad.last_name, ad.advisor_id, us.user_id
            FROM {users_tablename} us 
            JOIN {users_advisors_tablename} ua ON us.user_id = ua.user_id
            JOIN {advisors_tablename} ad ON ad.advisor_id = ua.advisor_id
            WHERE us.user_id= %s
        """
        
        users_db_cursor.execute(query, (user_id,))
        user_info = users_db_cursor.fetchone()
        
        if not user_info:
            raise ValueError(f"User with user_id {user_id} not found.")
        
        advisor_id = user_info[4]
        
        # Retrieve passwords and TTL for user and advisor
        client_data = get_password_and_timer(user_id=user_id, advisor_id=advisor_id)
        advisor_client_data = get_password_and_timer(user_id=user_id, advisor_id=advisor_id)
            
        # Send updated data to the client via Socket.IO
        emit('update_passwords', {
            "client": client_data,
            "advisor_client": advisor_client_data,
            "client_user_name": f"{user_info[0]} {user_info[1]}",
            "advisor_user_name": f"{user_info[2]} {user_info[3]}"
        })
    except Exception as e:
        emit('update_passwords', {"error": str(e)})