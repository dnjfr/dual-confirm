from flask import render_template, session
from src.routes.login import login_required
from extensions import app, otp_manager
from src.authentification.jwt_requirement import jwt_required
from src.db_management.db_configurations import users_db_cursor, users_tablename, advisors_tablename, users_advisors_tablename


@app.route("/advisor-dashboard")
@login_required(role='advisor')
@jwt_required(otp_manager)
def advisor_dashboard():
    """
    Renders the advisor dashboard.
    
    Loads advisor information and the list of associated clients.
    
    Returns:
        Response: Rendered advisor dashboard page.
    """
    
    advisor_id = session.get('advisor_id')
    
    if not advisor_id:
        return "advisor_id required in query parameters", 400
    
    # Load clients associated with the advisor
    users_advisors_query = f"""
        SELECT us.user_id, us.first_name, us.last_name
        FROM {users_tablename} us
        JOIN {users_advisors_tablename} ua ON us.user_id = ua.user_id
        WHERE ua.advisor_id = %s
    """
    users_db_cursor.execute(users_advisors_query, (advisor_id,))
    users_advisors_result = users_db_cursor.fetchall()
    
    # General information from the advisor
    advisor_query = f"""
        SELECT first_name, last_name
        FROM {advisors_tablename}
        WHERE advisor_id = %s
    """
    users_db_cursor.execute(advisor_query, (advisor_id,))
    advisor_info = users_db_cursor.fetchone()
    
    if not advisor_info:
        return "Advisor not found", 404
    
    advisor_name = f"{advisor_info[0]} {advisor_info[1]}"
    
    return render_template("advisor_dashboard.html", advisor_name=advisor_name, clients=users_advisors_result)