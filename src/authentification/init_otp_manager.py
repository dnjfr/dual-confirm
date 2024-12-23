import os
from src.authentification.key_rotation import KeyRotationManager
from src.authentification.otp_manager import OTPManager


# Initializing the OTP Manager
def init_otp_management(redis_connection, audit_db_connection, users_db_connection):
    """
    Initializes the OTP manager with key rotation
    """
    # Generate an initial secret key
    initial_secret = os.getenv('JWT_SECRET')
    
    # Creates the key rotation manager
    key_rotation_manager = KeyRotationManager(initial_secret)
    
    # Create OTP Manager
    otp_manager = OTPManager(
        redis_connection,
        key_rotation_manager,
        audit_db_connection,
        users_db_connection
    )
    
    return otp_manager