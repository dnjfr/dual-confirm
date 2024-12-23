import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from src.db_management.db_configurations import users_db_connection, audit_db_connection, redis_users_sessions
from src.authentification.init_otp_manager import init_otp_management

load_dotenv(override=True)



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET")
app.logger.setLevel(logging.DEBUG)


# Initialisation JWT
otp_manager = init_otp_management(redis_users_sessions, audit_db_connection, users_db_connection)