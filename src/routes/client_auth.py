from flask import jsonify, request, session
from src.routes.login import login_required
from extensions import app, otp_manager
from src.authentification.jwt_requirement import jwt_required
from src.db_management.db_configurations import users_db_cursor, users_tablename, advisors_tablename, users_advisors_tablename, redis_users_sessions
from passkeys_pairs_generation import generate_passkeys_pairs_on_demand, get_passkeys_pairs_and_timer


@app.route("/client-auth")
@login_required(role='advisor')
@jwt_required(otp_manager)
def client_auth():
    """
    Handles client selection and authentication from the advisor dashboard.
    
    Manages selection state, triggers password generation if needed,
    and returns client and advisor contextual data.
    
    Returns:
        dict or Response: Client authentication data or error message.
    """
    
    advisor_id = session.get('advisor_id')
    user_id = request.args.get('user_id')
    
    # Remove the selection status for all previously selected customers
    pattern = f"selection_status:{advisor_id}:*"
    existing_selection_keys = list(redis_users_sessions.scan_iter(pattern))
    for key in existing_selection_keys:
        if key.decode('utf-8').split(':')[-1] != user_id:
            redis_users_sessions.delete(key)
    
    # Handle the case where no customer is selected
    if user_id is None or user_id == "" or user_id == "Empty" or user_id == "None" or user_id == "0":
        return jsonify({"message": "No customer selected"})
    
    # Update selection status in Redis
    selection_key = f"selection_status:{advisor_id}:{user_id}"
    redis_users_sessions.set(selection_key, "selected")
    
    # Generate passwords on demand
    if selection_key != f"selection_status:{advisor_id}:Empty" :
        passwords = get_passkeys_pairs_and_timer(user_id, advisor_id)
        if not passwords['user_passkey'] or passwords['user_ttl'] <= 0:
            generate_passkeys_pairs_on_demand(user_id, advisor_id)
    
    
    # Load customer and advisor details
    query = f"""
        SELECT us.first_name, us.last_name, ad.first_name, ad.last_name, us.location_street, us.location_postcode, us.location_city, us.email
        FROM {users_tablename} us
        JOIN {users_advisors_tablename} ua ON us.user_id = ua.user_id
        JOIN {advisors_tablename} ad ON ad.advisor_id = ua.advisor_id
        WHERE us.user_id = %s AND ad.advisor_id = %s
    """
    users_db_cursor.execute(query, (user_id, advisor_id))
    user_info = users_db_cursor.fetchone()
    
    if not user_info:
        return "User or advisor not found", 404
    
    client_data = get_passkeys_pairs_and_timer(user_id=user_id, advisor_id=advisor_id)
    advisor_client_data = get_passkeys_pairs_and_timer(user_id=user_id, advisor_id=advisor_id)
    
    return {
        "client_name": f"{user_info[0]} {user_info[1]}",
        "client_address": f"{user_info[4]}",
        "client_city": f"{user_info[5]} - {user_info[6]}",
        "client_email": f"{user_info[7]}",
        "advisor_name": f"{user_info[2]} {user_info[3]}",
        "advisor_client": advisor_client_data,
        "client": client_data
    }