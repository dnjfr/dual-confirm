import os
from src.authentification.key_rotation import KeyRotationManager
from src.authentification.otp_manager import OTPManager


def init_otp_management(redis_connection, audit_db_connection, users_db_connection):
    """
    Initializes and wires the OTP management system.
    
    This function creates a key rotation manager and an OTP manager
    using the provided Redis and database connections.
    
    Args:
    redis_connection (redis.Redis): Redis connection used for OTP storage.
    audit_db_connection (psycopg2.connection): Database connection for audit logs.
    users_db_connection (psycopg2.connection): Database connection for user data.
    
    Returns:
    OTPManager: Fully initialized OTP manager instance.
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