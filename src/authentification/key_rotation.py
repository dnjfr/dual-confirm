import logging
import secrets
import threading
import time
from datetime import datetime


class KeyRotationManager:
    """
    Manages periodic rotation of JWT secret keys.
    
    This class maintains both a current and a previous secret key
    to allow seamless JWT validation during key rotation.
    A background daemon thread automatically rotates the key
    at a configurable interval.
    """

    def __init__(self, initial_secret, rotation_interval_hours=24):
        """
        Initializes the key rotation manager and starts the rotation thread.
        
        Args:
        initial_secret (str): Initial JWT signing secret.
        rotation_interval_hours (int): Interval in hours between key rotations.
        """
        
        self.current_secret = initial_secret
        self.previous_secret = None
        self.rotation_interval = rotation_interval_hours
        self.last_rotation = datetime.now()
        
        # Start the periodic rotation thread
        self.rotation_thread = threading.Thread(target=self._periodic_rotation, daemon=True)
        self.rotation_thread.start()


    def _periodic_rotation(self):
        """
        Background thread responsible for rotating JWT secret keys periodically.
        
        The thread sleeps for the configured rotation interval and then
        triggers a key rotation to generate a new signing secret.
        """
        
        while True:
            # Attend l'intervalle de rotation
            time.sleep(self.rotation_interval * 3600)
            
            # Rotation des clés
            self.rotate_secret()


    def rotate_secret(self):
        """
        Rotates the JWT signing secret.
        
        The current secret is moved to `previous_secret` to ensure
        backward compatibility for already issued tokens,
        and a new secure secret is generated.
        """
        
        logging.info("JWT Secret Key Rotation")
        
        # Keep the old key as the previous key
        self.previous_secret = self.current_secret
        
        # Generate a new secret key
        self.current_secret = secrets.token_hex(32)
        self.last_rotation = datetime.now()