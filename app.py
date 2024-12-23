
import os
from extensions import app, socketio

from src.user_session.validate_socketio_session import validate_socketio_session
from src.user_session.heartbeat import handle_heartbeat
from src.user_session.check_session_duration import handle_check_session_duration
from src.user_session.disconnect_user import handle_disconnect_user
from src.user_session.auto_disconnect_user import auto_disconnect_user
from src.user_session.reconnect_user import handle_reconnect_user

from src.routes.home import home
from src.routes.login import login_required, login
from src.routes.logout import logout
from src.routes.client_dashboard import client_dashboard
from src.routes.advisor_dashboard import advisor_dashboard
from src.routes.client_auth import client_auth

from src.request_upadate.request_update import handle_request_update 



if __name__ == '__main__':
    cert_dir = os.path.join(os.path.dirname(__file__), 'ssl_certificates')
    context = (
        os.path.join(cert_dir, 'cert.pem'),
        os.path.join(cert_dir, 'key.pem')
    )
    socketio.run(app, host='0.0.0.0', port=443, ssl_context=context, debug=False)
