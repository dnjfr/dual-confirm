from flask import render_template, session
from src.routes.login import login_required
from extensions import app, otp_manager
from src.authentification.jwt_requirement import jwt_required
from src.db_management.db_configurations import users_db_cursor, users_tablename, advisors_tablename, users_advisors_tablename
from passwords_generation import get_password_and_timer


@app.route("/client-dashboard")
@login_required(role='client')
@jwt_required(otp_manager)
def client_dashboard():
    """
    Renders the client dashboard.
    
    Displays advisor details, client information,
    and current authentication credentials.
    
    Returns:
        Response: Rendered client dashboard page.
    """
    
    user_id = session.get('user_id')
    
    if not user_id:
        raise ValueError("Aucun user_id n'a été fourni.")
    
    query = f"""
        SELECT us.first_name, us.last_name, ad.first_name, ad.last_name, ad.advisor_id, us.user_id, us.location_street, us.location_postcode, us.location_city, us.email
        FROM {users_tablename} us 
        JOIN {users_advisors_tablename} ua ON us.user_id = ua.user_id
        JOIN {advisors_tablename} ad ON ad.advisor_id = ua.advisor_id
        WHERE us.user_id= %s
    """
    
    users_db_cursor.execute(query, (user_id,))
    user_info = users_db_cursor.fetchone()
    
    if not user_info:
        return "User ot found", 404
    
    client_user_name = f"{user_info[0]} {user_info[1]}"
    advisor_user_name = f"{user_info[2]} {user_info[3]}"
    client_address = f"{user_info[6]}"
    client_city = f"{user_info[7]} - {user_info[8]}"
    client_email = f"{user_info[9]}"
    client_data = get_password_and_timer(user_id=user_info[5], advisor_id=user_info[4])
    
    return render_template(
        "client_dashboard.html",
        client=client_data,
        advisor_client=client_data,
        client_user_name=client_user_name,
        advisor_user_name=advisor_user_name,
        client_address=client_address,
        client_city=client_city,
        client_email=client_email
    )