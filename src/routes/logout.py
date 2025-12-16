from flask import jsonify, redirect, session, url_for
from extensions import app, otp_manager
from src.db_management.db_configurations import redis_users_sessions



# Logout redirect route
@app.route('/logout')
def logout():
    """
    Handles user logout and session cleanup.
    
    Removes JWT tokens, Redis session keys, audits the logout event,
    and clears the Flask session.
    
    Returns:
        Response: Redirect to login page.
    """
    
    # Retrieves the session or header token
    token = session.get('jwt_token')
    user_id = session.get('user_id')
    advisor_id = session.get('advisor_id')
    role = session.get('role')
    
    if not token:
        return jsonify({'message': 'No tokens to delete'}), 400
    
    # Audit the disconnection before deleting the keys
    otp_manager._audit_logout(user_id, advisor_id)
    
    # Identifies associated Redis keys
    redis_key = f"otp:{user_id or advisor_id}"
    connection_key = f"connection_status:{role}:{user_id or advisor_id}"
    selection_key = f"selection_status:{advisor_id}:{user_id}"
    active_key = f"active_status:{role}:{user_id or advisor_id}"
    
    # Delete keys in Redis
    otp_manager.redis.delete(redis_key)
    redis_users_sessions.delete(connection_key)
    redis_users_sessions.delete(selection_key)
    redis_users_sessions.delete(active_key)
    
    session.clear()  # Delete all session data
    
    return redirect(url_for('login'))