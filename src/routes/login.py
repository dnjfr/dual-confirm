from functools import wraps
import bcrypt
from flask import abort, redirect, render_template, url_for, request, session
from extensions import app, socketio, otp_manager
from src.db_management.db_configurations import users_db_cursor, users_advisors_tablename,  users_passwords_db_cursor, users_passwords_tablename, advisors_passwords_db_cursor ,advisors_passwords_tablename, redis_users_sessions, redis_set, redis_get
from src.user_session.validate_socketio_session import validate_socketio_session
from passwords_generation import generate_password_on_demand, get_password_and_timer

# Length of a session before disconnection
session_duration = 900



# Listening to the connection
@socketio.on('connect')
def handle_connect():
    # Check the session before allowing the connection
    if not validate_socketio_session():
        return False  # Rejects the connection

# Login decorator
def login_required(role=None):
    def decorated(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check the connection
            if 'logged_in' not in session:
                return redirect(url_for('login', next=request.url))
            
            # Check role if specified
            if role and session.get('role') != role:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorated


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    
    # If the user is already logged in, check the validity of the token
    if 'logged_in' in session:
        user_id = session.get('user_id')
        advisor_id = session.get('advisor_id')
        role = session.get('role')
        token = session.get('jwt_token')
        
        # Check if token still exists in Redis
        redis_key = f"otp:{user_id or advisor_id}"
        stored_token = redis_get(redis_users_sessions, redis_key)
        
        if not stored_token:
            # Token no longer exists in Redis, invalidate session
            session.clear()
            return redirect(url_for('login'))
        
        # Check token validity
        try:
            payload = otp_manager._decode_token(token)
            if not payload:
                session.clear()
                return redirect(url_for('login'))
            
            # Redirect to the appropriate dashboard
            if role == 'client':
                return redirect(url_for('client_dashboard'))
            elif role == 'advisor':
                return redirect(url_for('advisor_dashboard'))
        except Exception:
            session.clear()
            return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        # Customer verification
        client_query = f"""
            SELECT user_id, password
            FROM {users_passwords_tablename}
            WHERE user_id = %s
        """
        users_passwords_db_cursor.execute(client_query, (username,))
        client_result = users_passwords_db_cursor.fetchone()
        
        if client_result and bcrypt.checkpw(password, client_result[1].encode('utf-8')):
            advisor_query = f"""
                SELECT advisor_id 
                FROM {users_advisors_tablename} 
                WHERE user_id = %s
            """
            users_db_cursor.execute(advisor_query, (username,))
            advisor_result = users_db_cursor.fetchone()
            
            if advisor_result:
                
                otp_result = otp_manager.generate_otp(user_id=username)
                
                session.clear() 
                session['logged_in'] = True
                session['role'] = 'client'
                session['user_id'] = client_result[0]
                session['advisor_id'] = advisor_result[0]
                session['jwt_token'] = otp_result
                
                # Generate passwords on demand
                passwords = get_password_and_timer(session['user_id'], session['advisor_id'])
                if not passwords['user_pwd'] or passwords['user_ttl'] <= 0:
                    generate_password_on_demand(session['user_id'], session['advisor_id'])
                    
                # Add connection state in Redis
                connection_key = f"connection_status:{session['role']}:{username}"
                redis_set(redis_users_sessions, connection_key, "connected", ex=session_duration)                  

                # Add activity state in Redis
                active_key = f"active_status:{session['role']}:{username}"
                redis_set(redis_users_sessions, active_key, "active")
                    
                return redirect(url_for('client_dashboard'))
            
            else:
                message = "No advisors associated with this user."
        
        # Advisor check
        advisor_query = f"""
            SELECT advisor_id, password
            FROM {advisors_passwords_tablename} 
            WHERE advisor_id = %s
        """
        advisors_passwords_db_cursor.execute(advisor_query, (username,))
        advisor_result = advisors_passwords_db_cursor.fetchone()
        
        if advisor_result and bcrypt.checkpw(password, advisor_result[1].encode('utf-8')):
            otp_result = otp_manager.generate_otp(advisor_id=username)
            
            session.clear() 
            session['logged_in'] = True
            session['role'] = 'advisor'
            session['advisor_id'] = advisor_result[0]
            session['jwt_token'] = otp_result
            
            # Add connection state in Redis
            connection_key = f"connection_status:{session['role']}:{username}"
            redis_set(redis_users_sessions, connection_key, "connected", ex=session_duration)
            
            # Add activity state in Redis
            active_key = f"active_status:{session['role']}:{username}"
            redis_set(redis_users_sessions, active_key, "active")
            
            return redirect(url_for('advisor_dashboard'))
        
        # Si échec
        message = "Incorrect username or password."
        otp_manager._audit_otp_generation(
            username, 
            None, 
            status='login_failed_wrong_password'
        )
    
    return render_template('login.html', message=message)

