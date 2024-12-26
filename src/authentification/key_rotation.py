import logging
import secrets
import threading
import time
from datetime import datetime

# Key Rotation Manager
class KeyRotationManager:
    def __init__(self, initial_secret, rotation_interval_hours=24):
        """
        JWT Secret Key Rotation Manager

        Args:
        initial_secret (str): Initial secret key
        rotation_interval_hours (int): Key rotation interval
        """
        self.current_secret = initial_secret
        self.previous_secret = None
        self.rotation_interval = rotation_interval_hours
        self.last_rotation = datetime.now()
        
        # Start the periodic rotation thread
        self.rotation_thread = threading.Thread(target=self._periodic_rotation, daemon=True)
        self.rotation_thread.start()
    
    # Thread for periodic key rotation
    def _periodic_rotation(self):
        """
        Thread for periodic key rotation
        """
        while True:
            # Attend l'intervalle de rotation
            time.sleep(self.rotation_interval * 3600)
            
            # Rotation des clés
            self.rotate_secret()
    
    # Key rotation function
    def rotate_secret(self):
        """
        Rotates secret keys
        """
        logging.info("JWT Secret Key Rotation")
        
        # Keep the old key as the previous key
        self.previous_secret = self.current_secret
        
        # Generate a new secret key
        self.current_secret = secrets.token_hex(32)
        self.last_rotation = datetime.now()