import time
import jwt
from datetime import datetime, timedelta
import secrets
import threading
import logging
from flask import request
from src.db_management.db_configurations import session_audit_tablename, users_advisors_tablename


# OTP and JWT token manager
class OTPManager:
    def __init__(self, redis_connection, key_rotation_manager, audit_db_connection, users_db_connection):
        """
        OTP and JWT token manager

        Args:
        redis_connection (redis.Redis): Redis connection
        key_rotation_manager (KeyRotationManager): Key rotation manager
        audit_db_connection (psycopg2.connection): Audit database connection
        """
        self.redis = redis_connection
        self.key_rotation_manager = key_rotation_manager
        self.audit_db_connection = audit_db_connection
        self.users_db_connection = users_db_connection
        
        # Configuring periodic cleaning of expired OTPs
        self.cleanup_thread = threading.Thread(target=self._periodic_otp_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    # Retrieve the advisor_id associated with a user_id function
    def _get_advisor_id(self, user_id):
        """
        Retrieves the advisor_id associated with a user_id

        Args:
        user_id (str): User ID

        Returns:
        str or None: The ID of the associated advisor
        """
        try:
            with self.users_db_connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT advisor_id 
                    FROM {users_advisors_tablename}
                    WHERE user_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logging.error(f"Error retrieving advisor_id: {e}")
            return None
    
    # OTP Generation function
    def generate_otp(self, user_id=None, advisor_id=None, expiration_minutes=15):
        """
        Generate an OTP and store it in cache with JWT

        Storage:
        - Redis key: "otp:{user_id}"
        - user_id (str, optional): Client user ID
        - advisor_id (str, optional): Advisor ID
        - Expiration: Based on the validity period of the OTP
        """
        
        if not user_id and not advisor_id:
            raise ValueError("You must provide either a user_id or an advisor_id.")
        
        if user_id and not advisor_id:
            advisor_id = self._get_advisor_id(user_id)
        
        if not advisor_id:
            raise ValueError("Unable to determine an associated advisor_id.")
        
        redis_key = f"otp:{user_id or advisor_id}"
        
        # Determine which ID to use and retrieves the advisor_id if necessary
        if user_id:
            advisor_id = self._get_advisor_id(user_id)
        
        # Check for the existence of a valid OTP
        existing_token = self.redis.get(redis_key)
        if existing_token:
            try:
                # Attempt to decode with current or previous key
                payload = self._decode_token(existing_token)
                if payload:
                    return payload
            except jwt.InvalidTokenError:
                # Invalid token, we continue the generation
                pass
        
        # Generate a new OTP
        otp = secrets.token_urlsafe(16)
        now = datetime.now()
        expiration = now + timedelta(minutes=expiration_minutes)
        
        payload = {
            'user_id': user_id,
            'advisor_id': advisor_id,
            'otp': otp,
            'exp': expiration,
            'iat': now.timestamp()
        }
        logging.debug(f"Payload généré: {payload}")
        # Encode with current key
        jwt_token = jwt.encode(
            payload, 
            self.key_rotation_manager.current_secret, 
            algorithm='HS256'
        )
        
        # Storage in Redis
        self.redis.setex(
            redis_key, 
            int(expiration_minutes * 60), 
            jwt_token
        )
        
        # Generation Audit
        self._audit_otp_generation(user_id, advisor_id)
        
        # Disconnection audit
        self._audit_logout(user_id, advisor_id)
        
        return jwt_token
    
    # Decode a token
    def _decode_token(self, token):
        """
        Decode a JWT token by trying different keys

        Strategy:
        1. Try with current key
        2. If fail, try with previous key

        Returns:
        dict: Decoded Payload or None
        """
        try:
            # Try with the current key
            payload = jwt.decode(
                token, 
                self.key_rotation_manager.current_secret, 
                algorithms=['HS256']
            )
            logging.debug(f"Token decoded successfully : {payload}")
            return payload
        except jwt.ExpiredSignatureError:
            logging.error("The token has expired")
            return None
        except jwt.InvalidTokenError as e:
            # Try with previous key if available
            if self.key_rotation_manager.previous_secret:
                try:
                    payload = jwt.decode(
                        token, 
                        self.key_rotation_manager.previous_secret, 
                        algorithms=['HS256']
                    )
                    logging.debug(f"Token decoded with previous key: {payload}")
                    return payload
                except Exception as e:
                    logging.error(f"Error with previous key: {e}")
                    return None
            return None
    
    # OTP Verification
    def validate_otp(self, token, user_id=None, advisor_id=None):
        payload = self._decode_token(token)
        
        if not payload:
            return False
        
        now = datetime.now()
        exp = payload.get('exp')
        iat = payload.get('iat')

        # Expiration Check
        if not exp or now > datetime.fromtimestamp(exp):
            logging.error(f"Token expired: exp={exp}, now={now}")
            return False

        # Vérification du timestamp initial
        if not iat or now < datetime.fromtimestamp(iat):
            logging.error(f"Invalid token timestamp: iat={iat}, now={now}")
            return False
        
        # Advisor case:
        # - Must have an advisor_id
        # - Must NOT have a user_id 
        if advisor_id is not None:
            return (
                payload.get('advisor_id') == advisor_id and 
                payload.get('user_id') is None
            )
        
        # Client case:
        # - Must have a user_id
        # - Must have an advisor_id
        if user_id is not None:
            return (
                payload.get('user_id') == user_id and 
                payload.get('advisor_id') is not None
            )

        # If no ID is specified, the token is considered valid.
        return False
    
    # Periodic cleaning of expired OTPs
    def _periodic_otp_cleanup(self):
        """
        Periodically clean expired OTPs in Redis

        Strategy:
        - Loop through all OTP keys
        - Delete expired ones
        - Run every hour
        """
        while True:
            try:
                # Wait one hour between each cleaning
                time.sleep(3600)
                
                # Browse and delete expired OTPs
                otp_keys = self.redis.keys("otp:*")
                for key in otp_keys:
                    token = self.redis.get(key)
                    if token:
                        try:
                            # Attempt to decode the token
                            payload = self._decode_token(token)
                            if not payload:
                                # Token expired or invalid, delete
                                self.redis.delete(key)
                        except Exception as e:
                            logging.error(f"Error while cleaning {key}: {e}")
            except Exception as e:
                logging.error(f"Error in periodic cleaning of OTPs: {e}")
    
    # OTP Generation Audit Function
    def _audit_otp_generation(self, user_id, advisor_id, status='success'):
        try:
            role = 'advisor' if not user_id else 'client'
            with self.audit_db_connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {session_audit_tablename} (
                        user_id, 
                        advisor_id, 
                        role, 
                        login_timestamp, 
                        ip_address, 
                        user_agent, 
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, 
                    advisor_id, 
                    role, 
                    datetime.now(), 
                    request.remote_addr, 
                    request.user_agent.string, 
                    status
                ))
                self.audit_db_connection.commit()
        except Exception as e:
            logging.error(f"OTP Audit Error: {e}")
    
    
    # Logout audit function
    def _audit_logout(self, user_id, advisor_id):
        try:
            with self.audit_db_connection.cursor() as cursor:
                # Retrieve the last login record for this user
                cursor.execute(f"""
                    SELECT login_timestamp 
                    FROM {session_audit_tablename} 
                    WHERE (user_id = %s OR advisor_id = %s) 
                    ORDER BY login_timestamp DESC 
                    LIMIT 1
                """, (user_id, advisor_id))
                
                login_record = cursor.fetchone()
                
                if login_record:
                    login_timestamp = login_record[0]
                    logout_timestamp = datetime.now()
                    session_duration = logout_timestamp - login_timestamp
                    
                    # Update session record with logout and duration
                    cursor.execute(f"""
                        UPDATE {session_audit_tablename} 
                        SET logout_timestamp = %s, 
                            session_duration = %s 
                        WHERE login_timestamp = %s 
                        AND (user_id = %s OR advisor_id = %s)
                    """, (
                        logout_timestamp, 
                        session_duration, 
                        login_timestamp,
                        user_id, 
                        advisor_id
                    ))
                    
                    self.audit_db_connection.commit()
            
        except Exception as e:
            logging.error(f"Error while auditing logout: {e}")